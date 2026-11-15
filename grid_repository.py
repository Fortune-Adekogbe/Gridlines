"""Read-only MongoDB access for the dashboard."""

from datetime import datetime, timedelta
import os
from pathlib import Path
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo

import certifi
from dotenv import load_dotenv
import pandas as pd
import pymongo
from pymongo.errors import PyMongoError
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from grid_data import DAILY_FIELDS, HOUR_FIELDS, HourlyData, backfill_daily, common_plant_hours, normalize_daily, normalize_hourly, plant_summary, reporting_date


HOURLY_TOTAL_FIELDS = ["date", "metadata", "Hour Total", "zTOTAL", "TOTAL"]


class DataUnavailable(RuntimeError):
    pass


def setting(name, default=None):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except (FileNotFoundError, StreamlitSecretNotFoundError):
        return default


@st.cache_resource(show_spinner=False)
def database():
    load_dotenv(Path(__file__).with_name(".env"))
    uri = setting("MONGODB_URI")
    if not uri:
        username, password = setting("MONGODB_USERNAME"), setting("MONGODB_PASSWORD")
        if not username or not password:
            raise DataUnavailable("Add MONGODB_USERNAME and MONGODB_PASSWORD to the environment or Streamlit secrets to connect to the reports.")
        uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@bloomstore.gnv8c.mongodb.net/?retryWrites=true&w=majority"
    try:
        client = pymongo.MongoClient(
            uri, serverSelectionTimeoutMS=8000, connectTimeoutMS=5000,
            socketTimeoutMS=20000, tlsCAFile=certifi.where(),
        )
        return client[setting("MONGODB_DATABASE", "power_track")]
    except PyMongoError:
        raise DataUnavailable("The database connection could not be initialized. Check the connection settings and retry.") from None


def read_documents(collection, query, projection=None):
    try:
        return list(database()[collection].find(query, projection).max_time_ms(15000))
    except PyMongoError:
        raise DataUnavailable("The reports are temporarily unavailable. Check database access and retry.") from None


def retrieved_at():
    return datetime.now(ZoneInfo("Africa/Lagos")).isoformat(timespec="seconds")


@st.cache_data(ttl=600, max_entries=4, show_spinner=False)
def load_daily():
    fields = [*DAILY_FIELDS.values(), *HOUR_FIELDS.values(), "Highest Voltage", "Lowest Voltage", "date", "metadata"]
    documents = read_documents("gridlines", {}, dict.fromkeys(fields, 1))
    invalid_dates = sum(reporting_date(document.get("date")) is None for document in documents)
    daily = normalize_daily(documents)
    totals = read_documents("gridmoments", {}, dict.fromkeys(HOURLY_TOTAL_FIELDS, 1))
    hourly = normalize_hourly(totals)
    daily = backfill_daily(daily, hourly.grid)
    return daily, retrieved_at(), invalid_dates


@st.cache_data(ttl=600, max_entries=4, show_spinner=False)
def load_catalog():
    documents = read_documents("gridmoments", {}, {"date": 1})
    dates = sorted({day for document in documents if (day := reporting_date(document.get("date"))) is not None})
    return dates, retrieved_at()


def range_query(start, end):
    return {"$or": [
        {"date": {"$gte": start.isoformat(), "$lt": (end + timedelta(days=1)).isoformat()}},
        {"date": {"$gte": datetime.combine(start, datetime.min.time()), "$lt": datetime.combine(end + timedelta(days=1), datetime.min.time())}},
    ]}


@st.cache_data(ttl=600, max_entries=4, show_spinner=False)
def load_hourly(start, end, aggregates_only=False, selected_plants=None):
    projection = None
    if aggregates_only:
        projection = dict.fromkeys(HOURLY_TOTAL_FIELDS, 1)
    return normalize_hourly(read_documents("gridmoments", range_query(start, end), projection), selected_plants=selected_plants), retrieved_at()


def date_batches(start, end):
    """Bound the number of raw station observations held in memory at once."""
    current = start
    while current <= end:
        batch_end = min(current + timedelta(days=89), end)
        yield current, batch_end
        current = batch_end + timedelta(days=1)


@st.cache_data(ttl=600, max_entries=4, show_spinner=False)
def load_plant_statistics(start, end):
    summaries, grids, coverages, exclusions = [], [], [], []
    notes = set()
    fetched_times = []
    for batch_start, batch_end in date_batches(start, end):
        hourly, fetched = load_hourly(batch_start, batch_end)
        fetched_times.append(fetched)
        summaries.append(plant_summary(hourly.plants, ((batch_end - batch_start).days + 1) * 24))
        grids.append(hourly.grid)
        coverages.append(hourly.coverage)
        exclusions.append(hourly.excluded)
        notes.update(note for note in hourly.notes if not note.startswith("The source contains"))
    summary = pd.concat(summaries, ignore_index=True)
    if not summary.empty:
        summary["total_mw"] = summary["mean_mw"] * summary["observations"]
        summary = summary.groupby(["plant", "technology"], as_index=False).agg(total_mw=("total_mw", "sum"), observations=("observations", "sum"))
        summary["mean_mw"] = summary["total_mw"] / summary["observations"]
        summary["coverage"] = summary["observations"] / (((end - start).days + 1) * 24) * 100
        summary = summary.drop(columns="total_mw").sort_values("mean_mw", ascending=False).reset_index(drop=True)
    grid = pd.concat(grids, ignore_index=True)
    coverage = pd.concat(coverages, ignore_index=True)
    zero_count = int(grid["mw"].eq(0).sum())
    if zero_count:
        notes.add(f"The source contains {zero_count:,} zero-valued grid readings at elapsed reporting hours. They are retained as reported and included in recorded-hour coverage.")
    excluded = pd.concat(exclusions, ignore_index=True)
    details = HourlyData(grid, grid.iloc[:0].copy(), coverage, sorted(notes), excluded)
    return summary, details, min(fetched_times)


@st.cache_data(ttl=600, max_entries=8, show_spinner=False)
def load_plant_comparison(start, end, selected):
    daily_parts, hourly_parts = [], []
    common_hours = 0
    for batch_start, batch_end in date_batches(start, end):
        hourly, _ = load_hourly(batch_start, batch_end, selected_plants=selected)
        common = common_plant_hours(hourly.plants, selected)
        if common.empty:
            continue
        common_hours += len(common) // len(selected)
        daily_parts.append(common.groupby(["date", "plant"], as_index=False)["mw"].mean())
        hourly_parts.append(common.groupby(["hour", "plant"], as_index=False).agg(total_mw=("mw", "sum"), observations=("mw", "count")))
    if not daily_parts:
        return pd.DataFrame(columns=["date", "plant", "mw"]), pd.DataFrame(columns=["hour", "plant", "mw"]), 0
    daily = pd.concat(daily_parts, ignore_index=True)
    profile = pd.concat(hourly_parts, ignore_index=True).groupby(["hour", "plant"], as_index=False)[["total_mw", "observations"]].sum()
    profile["mw"] = profile["total_mw"] / profile["observations"]
    return daily, profile.drop(columns=["total_mw", "observations"]), common_hours


def refresh_data():
    load_daily.clear()
    load_catalog.clear()
    load_hourly.clear()
    load_plant_statistics.clear()
    load_plant_comparison.clear()
