"""Normalize source reports and calculate coverage-aware grid statistics."""

from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
import math
import re
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from grid_quality import screen_hourly


DAILY_FIELDS = {
    "energy_generated": "Energy Generated (MWh)",
    "energy_sent": "Energy Sent Out (MWh)",
    "peak": "Peak Generation (MW)",
    "trough": "Off-Peak Generation (MW)",
    "grid_0600": "Grid @ 06:00 (MW)",
    "frequency_peak": "Frequency @ Peak Generation (Hz)",
    "frequency_trough": "Frequency @ Off-Peak Generation (Hz)",
    "frequency_0600": "Frequency @ 06:00 (Hz)",
    "frequency_high": "Highest Frequency (Hz)",
    "frequency_low": "Lowest Frequency (Hz)",
}
REPORT_GROUPS = [
    ("peak", "peak_hour", "frequency_peak"),
    ("trough", "trough_hour", "frequency_trough"),
    ("grid_0600", "frequency_0600"),
    ("frequency_high", "frequency_high_hour"),
    ("frequency_low", "frequency_low_hour"),
    ("energy_generated",),
    ("energy_sent",),
    ("voltage_high",),
    ("voltage_low",),
]
HOUR_FIELDS = {
    "peak_hour": "Peak Generation Hour",
    "trough_hour": "Off-Peak Generation Hour",
    "frequency_high_hour": "Hour @ Highest Frequency",
    "frequency_low_hour": "Hour @ Lowest Frequency",
}
DAILY_COLUMNS = [
    "date", *DAILY_FIELDS, *HOUR_FIELDS, "voltage_high", "voltage_low",
    "sources", "provenance", "conflicts", "report_count", "hourly_hours", "hourly_excluded_hours",
]
HOURLY_COLUMNS = [
    "date", "hour", "timestamp", "plant", "technology", "mw", "source",
    "raw_label", "conflict", "aggregate", "raw_mw", "quality_reason",
]
ALIASES = {
    "DADINKOWA G": "DADINKOWA",
    "DADINKOWA G.S (HYDRO)": "DADINKOWA",
    "KASHIMBILA GS": "KASHIMBILA",
}
TECHNOLOGIES = {
    "DADINKOWA": "Hydro",
    "KASHIMBILA": "Hydro",
    "ZUNGERU": "Hydro",
}
AGGREGATES = {"HOUR TOTAL", "ZTOTAL", "TOTAL"}
NORMAL_FREQUENCY = (49.75, 50.25)


@dataclass
class HourlyData:
    grid: pd.DataFrame
    plants: pd.DataFrame
    coverage: pd.DataFrame
    notes: list[str]
    excluded: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=HOURLY_COLUMNS))


def number(value):
    """Return a finite numeric observation, preserving a reported zero."""
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(str(value).strip().replace(",", ""))
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def reporting_date(value):
    try:
        parsed = pd.Timestamp(value)
        return None if pd.isna(parsed) else parsed.date()
    except (TypeError, ValueError, OverflowError):
        return None


@lru_cache(maxsize=256, typed=True)
def hour_number(value):
    """Parse report hour labels, retaining 24:00 on its reporting date."""
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip().upper()
    text = re.sub(r"\s*(HOURS?|HRS?|H)\s*$", "", text).strip()
    if re.fullmatch(r"\d{1,2}:00(?::00)?", text):
        hour = int(text.split(":")[0])
    elif re.fullmatch(r"\d{3,4}", text):
        hour = int(text) // 100 if int(text) % 100 == 0 else -1
    else:
        parsed = number(text)
        if parsed is None or not parsed.is_integer():
            return None
        hour = int(parsed)
    return hour if 0 <= hour <= 24 else None


def hour_label(hour):
    if pd.isna(hour):
        return "Unavailable"
    parsed = hour_number(hour)
    return f"{parsed:02d}:00" if parsed is not None else str(hour).strip()


def source_name(document):
    metadata = document.get("metadata") or {}
    return str(metadata.get("source", "Source unspecified"))


def report_order(document):
    metadata = document.get("metadata") or {}
    for key in ("updated_at", "scraped_at", "retrieved_at", "timestamp"):
        raw_timestamp = metadata.get(key)
        if raw_timestamp is None:
            continue
        try:
            timestamp = pd.Timestamp(raw_timestamp)
            if not pd.isna(timestamp):
                return timestamp.timestamp(), str(document.get("_id", ""))
        except (ValueError, TypeError, OverflowError):
            pass
    object_id = document.get("_id")
    generated = getattr(object_id, "generation_time", None)
    return (generated.timestamp() if generated else 0), str(object_id or "")


def normalize_daily(documents):
    reports = {}
    for document in sorted(documents, key=report_order, reverse=True):
        day = reporting_date(document.get("date"))
        if day is not None:
            reports.setdefault(day, []).append(document)
    rows = []
    for day, documents_for_day in reports.items():
        row: dict[str, Any] = {key: None for key in DAILY_COLUMNS}
        row.update(date=day, sources=[], provenance={}, conflicts=[], report_count=len(documents_for_day))
        observations = []
        for document in documents_for_day:
            observation = {key: number(document.get(field)) for key, field in DAILY_FIELDS.items()}
            for key, field in HOUR_FIELDS.items():
                raw_hour = document.get(field)
                parsed_hour = hour_number(raw_hour)
                observation[key] = parsed_hour if parsed_hour is not None else raw_hour
            observation["voltage_high"] = document.get("Highest Voltage") or None
            observation["voltage_low"] = document.get("Lowest Voltage") or None
            observations.append((observation, source_name(document)))
        for group in REPORT_GROUPS:
            primary = group[0]
            candidates = [(observation, source) for observation, source in observations if observation[primary] is not None]
            if not candidates:
                candidates = [(observation, source) for observation, source in observations if any(observation.get(key) is not None for key in group)]
            if not candidates:
                continue
            chosen, source = candidates[0]
            for key in group:
                row[key] = chosen.get(key)
                row["provenance"][key] = source
            row["sources"].append(source)
            values = {str(observation[primary]) for observation, _ in candidates}
            if len(values) > 1:
                row["conflicts"].append({"field": primary, "observations": [
                    {"value": observation[primary], "source": observed_source}
                    for observation, observed_source in candidates
                ]})
        row["sources"] = ", ".join(sorted(set(row["sources"])))
        rows.append(row)
    result = pd.DataFrame(rows, columns=DAILY_COLUMNS)
    for column in DAILY_FIELDS:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    return result.sort_values("date").reset_index(drop=True)


def plant_identity(label):
    normalized = re.sub(r"\s+", " ", str(label).strip().upper())
    plant = ALIASES.get(normalized, normalized)
    technology = TECHNOLOGIES.get(plant, "Unclassified")
    for marker, name in (("HYDRO", "Hydro"), ("GAS/STEAM", "Gas / steam"), ("GAS", "Gas"), ("STEAM", "Steam")):
        if marker in normalized:
            technology = name
            break
    return plant, technology


def station_profiles(document):
    """Recover dotted station names split into MongoDB field paths by updates."""
    profiles = []

    def collect(label, profile, depth):
        leaves = {key: value for key, value in profile.items() if not isinstance(value, dict)}
        if leaves:
            profiles.append((label, leaves, depth))
        for key, value in profile.items():
            if isinstance(value, dict):
                collect(f"{label}.{key}", value, depth + 1)

    for label, profile in document.items():
        if label not in ("_id", "date", "metadata") and isinstance(profile, dict):
            collect(label, profile, 0)
    # Dotted update paths contain the refreshed profile when a stale literal key
    # also exists in the same document.
    return sorted(profiles, key=lambda profile: profile[2], reverse=True)


def normalize_hourly(documents, as_of=None, selected_plants=None):
    as_of = as_of or datetime.now(ZoneInfo("Africa/Lagos"))
    if as_of.tzinfo is not None:
        as_of = as_of.astimezone(ZoneInfo("Africa/Lagos"))
    observations = {}
    notes = set()
    pending = set()
    for document in sorted(documents, key=report_order, reverse=True):
        day = reporting_date(document.get("date"))
        if day is None:
            notes.add("A report with an unreadable date was skipped.")
            continue
        timestamps = {hour: pd.Timestamp(day) + pd.Timedelta(hours=hour) for hour in range(25)}
        for label, profile, depth in station_profiles(document):
            if depth:
                notes.add("Nested MongoDB station profiles were recovered. Refreshed nested fields take precedence over conflicting literal station keys in the same report.")
            normalized = re.sub(r"\s+", " ", label.strip().upper())
            aggregate = normalized in AGGREGATES
            plant, technology = plant_identity(label)
            if selected_plants is not None and not aggregate and plant not in selected_plants:
                continue
            for key, value in profile.items():
                hour = hour_number(key)
                mw = number(value)
                if hour is None or mw is None:
                    continue
                if day == as_of.date() and hour > as_of.hour and mw == 0:
                    pending.add((day, hour))
                    continue
                identity = (day, hour, plant)
                row = {
                    "date": day, "hour": hour,
                    "timestamp": timestamps[hour],
                    "plant": plant, "technology": technology, "mw": mw,
                    "source": source_name(document), "raw_label": label,
                    "conflict": False, "aggregate": aggregate,
                    "raw_mw": mw, "quality_reason": "",
                }
                if identity in observations:
                    if observations[identity]["mw"] != mw:
                        observations[identity]["conflict"] = True
                else:
                    observations[identity] = row
    if pending:
        notes.add(f"{len(pending)} future zero-filled hourly slots on {as_of.date().isoformat()} are pending observations. Elapsed-hour zeros are retained as reported.")
    frame = pd.DataFrame(observations.values(), columns=HOURLY_COLUMNS)
    if frame.empty:
        return HourlyData(frame.copy(), frame.copy(), pd.DataFrame(columns=["date", "hours", "plants", "conflicts"]), sorted(notes))
    frame = frame.sort_values(["date", "hour", "plant"]).reset_index(drop=True)
    plants = frame.loc[~frame["aggregate"]].copy()
    grid = frame.loc[frame["aggregate"]].copy()
    # Both aggregate labels occur in the archive. Prefer the explicit hourly total.
    priority = {"HOUR TOTAL": 0, "ZTOTAL": 1, "TOTAL": 2}
    grid["priority"] = grid["plant"].map(priority)
    aggregate_conflicts = grid.groupby(["date", "hour"])["mw"].transform("nunique").gt(1)
    grid.loc[aggregate_conflicts, "conflict"] = True
    grid = grid.sort_values("priority").drop_duplicates(["date", "hour"]).drop(columns="priority")
    grid = grid.sort_values(["date", "hour"]).reset_index(drop=True)
    grid, plants, excluded = screen_hourly(grid, plants)
    zero_readings = int(grid["mw"].eq(0).sum())
    if zero_readings:
        notes.add(f"The source contains {zero_readings:,} zero-valued grid readings at elapsed reporting hours. They are retained as reported and included in recorded-hour coverage.")
    dates = sorted(set(frame["date"]))
    coverage = pd.DataFrame({"date": dates})
    coverage["hours"] = coverage["date"].map(grid.loc[grid["mw"].notna()].groupby("date")["hour"].nunique()).fillna(0).astype(int)
    coverage["plants"] = coverage["date"].map(plants.groupby("date")["plant"].nunique()).fillna(0).astype(int)
    coverage["conflicts"] = coverage["date"].map(frame.groupby("date")["conflict"].sum()).fillna(0).astype(int)
    return HourlyData(grid, plants, coverage, sorted(notes), excluded)


def date_window(frame, start, end):
    return frame.loc[frame["date"].between(start, end)].copy()


def backfill_daily(daily, grid):
    """Fill missing daily generation measurements from national hourly totals."""
    if grid.empty:
        return daily.copy()
    missing_days = sorted(set(grid["date"]) - set(daily["date"]))
    added = normalize_daily([{"date": day} for day in missing_days])
    added["report_count"] = 0
    frames = [frame for frame in (daily, added) if not frame.empty]
    result = pd.concat(frames, ignore_index=True).sort_values("date").reset_index(drop=True)

    valid = grid.loc[grid["mw"].notna()]
    positive = valid.loc[valid["mw"].ne(0)]
    patch = valid.groupby("date")["mw"].max().to_frame("peak")
    patch["trough"] = positive.groupby("date")["mw"].min()
    patch["grid_0600"] = valid.loc[valid["hour"].eq(6)].set_index("date")["mw"]
    sources = valid.groupby("date")["source"].agg(lambda values: ", ".join(sorted(set(values))))
    hours = valid.groupby("date")["hour"].nunique()
    result["hourly_hours"] = result["date"].map(hours).fillna(0).astype(int)
    excluded_hours = grid.loc[grid["mw"].isna()].groupby("date")["hour"].nunique()
    result["hourly_excluded_hours"] = result["date"].map(excluded_hours).fillna(0).astype(int)
    times = {}
    if not valid.empty:
        times["peak"] = valid.loc[valid.groupby("date")["mw"].idxmax()].set_index("date")["hour"]
    if not positive.empty:
        times["trough"] = positive.loc[positive.groupby("date")["mw"].idxmin()].set_index("date")["hour"]

    for field in ("peak", "trough", "grid_0600"):
        missing = result[field].isna()
        result.loc[missing, field] = result.loc[missing, "date"].map(patch[field])
        filled = missing & result[field].notna()
        for index in result.index[filled]:
            day = result.at[index, "date"]
            source = sources.loc[day]
            count = int(hours.loc[day])
            coverage = f" · {count}/24 accepted hours" if count < 24 else ""
            result.at[index, "provenance"] = {
                **result.at[index, "provenance"], field: f"{source} · hourly totals{coverage}",
            }
            if field in times:
                result.at[index, f"{field}_hour"] = times[field].loc[day]
            existing_sources = result.at[index, "sources"].split(", ")
            result.at[index, "sources"] = ", ".join(sorted({*existing_sources, *source.split(", ")} - {""}))
    return result


def partial_hourly_measurement(row, measurement):
    if measurement not in ("peak", "trough"):
        return False
    provenance = row.get("provenance")
    source = provenance.get(measurement, "") if isinstance(provenance, dict) else ""
    hours = row.get("hourly_hours")
    return "hourly totals" in source and hours is not None and pd.notna(hours) and hours < 24


def daily_axis(frame, start, end):
    """Insert missing calendar days so line charts visibly break at data gaps."""
    calendar = pd.DataFrame({"date": pd.date_range(start, end).date})
    return calendar.merge(date_window(frame, start, end), on="date", how="left")


def period_statistic(frame, field, start, end, operation="sum"):
    values = date_window(frame, start, end)[field].dropna()
    expected = (end - start).days + 1
    value = None if values.empty else float(values.agg(operation))
    return value, len(values), expected


def comparison_delta(frame, field, start, end, operation="sum"):
    duration = pd.Timedelta(days=(end - start).days + 1)
    if field in ("peak", "trough"):
        compared = date_window(frame, start - duration, end)
        if any(partial_hourly_measurement(row, field) for _, row in compared.iterrows()):
            return None
    current, count, expected = period_statistic(frame, field, start, end, operation)
    previous, previous_count, _ = period_statistic(frame, field, start - duration, start - pd.Timedelta(days=1), operation)
    if count != expected or previous_count != expected or previous in (None, 0) or current is None:
        return None
    return (current / previous - 1) * 100


def plant_summary(plants, expected_hours):
    plants = plants.loc[plants["mw"].notna()]
    if plants.empty:
        return pd.DataFrame(columns=["plant", "technology", "mean_mw", "observations", "coverage"])
    result = plants.groupby(["plant", "technology"], as_index=False).agg(mean_mw=("mw", "mean"), observations=("mw", "count"))
    result["coverage"] = result["observations"] / expected_hours * 100
    return result.sort_values("mean_mw", ascending=False).reset_index(drop=True)


def common_plant_hours(plants, selected):
    if not selected:
        return plants.iloc[:0].copy()
    chosen = plants.loc[plants["plant"].isin(selected) & plants["mw"].notna()]
    counts = chosen.groupby(["date", "hour"])["plant"].nunique()
    common = counts.loc[counts == len(selected)].reset_index()[["date", "hour"]]
    return chosen.merge(common, on=["date", "hour"], how="inner")


def frequency_summary(daily):
    fields = ["frequency_low", "frequency_high", "frequency_peak", "frequency_trough", "frequency_0600"]
    observations = daily[fields]
    observed = observations.notna().any(axis=1)
    excursions = ((observations < NORMAL_FREQUENCY[0]) | (observations > NORMAL_FREQUENCY[1])).any(axis=1)
    return int(excursions.sum()), int(observed.sum()), int(observations.notna().sum().sum())


def voltage_observation(value):
    if not isinstance(value, str):
        return None, "", ""
    match = re.search(r"([\d,]+(?:\.\d+)?)\s*kV\b", value, flags=re.IGNORECASE)
    voltage = number(match.group(1)) if match else number(value)
    parts = [part.strip() for part in value.split("@")]
    return voltage, parts[1] if len(parts) > 1 else "", " @ ".join(parts[2:])
