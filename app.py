"""Streamlit entry point for the Gridlines explorer."""

from datetime import timedelta

import pandas as pd
import streamlit as st

from grid_repository import DataUnavailable, load_catalog, load_daily, refresh_data
from grid_state import initial_state, query_values
from grid_views import ViewContext, daily_explorer, grid_conditions, overview, power_plants


def initialize_filters(earliest, latest, hourly_dates):
    parameters = {key: st.query_params.get_all(key) if key == "plant" else st.query_params[key] for key in st.query_params}
    # Empty query parameters on a native page switch should preserve the session.
    external_change = bool(parameters) and parameters != st.session_state.get("_last_query")
    if "window" not in st.session_state or external_change:
        values, notices = initial_state(parameters, earliest, latest)
        available = [day for day in hourly_dates if values["window"][0] <= day <= values["window"][1]]
        if "day" not in parameters and available:
            values["day"] = available[-1]
        for key, value in values.items():
            st.session_state[key] = value
        if parameters.get("plant"):
            st.session_state["_plants_initialized"] = True
        st.session_state["_filter_notices"] = notices
        if values["window"] == (earliest, latest):
            st.session_state["preset"] = "All history"
        else:
            st.session_state["preset"] = "Custom"
        st.session_state["_last_query"] = parameters
    if len(st.session_state["window"]) == 2:
        start, end = st.session_state["window"]
        st.session_state["window"] = (max(earliest, min(start, latest)), max(earliest, min(end, latest)))


def apply_preset(earliest, latest, history_bounds):
    preset = st.session_state["preset"]
    durations = {"7 days": 7, "30 days": 30, "90 days": 90, "1 year": 365}
    if preset == "All history":
        st.session_state["window"] = history_bounds
    elif preset in durations:
        st.session_state["window"] = (max(earliest, latest - timedelta(days=durations[preset] - 1)), latest)


def custom_interval():
    st.session_state["preset"] = "Custom"


def all_history_bounds(earliest, latest, daily, view="", metric="Generation"):
    fields = []
    if view == "conditions":
        fields = ["frequency_low", "frequency_high", "frequency_0600", "frequency_peak", "frequency_trough"]
    elif view == "" and metric == "Energy":
        fields = ["energy_generated", "energy_sent"]
    if fields:
        available = daily.loc[daily[fields].notna().any(axis=1), "date"]
        if not available.empty:
            return available.min(), available.max()
    return earliest, latest


def sidebar_filters(earliest, latest, daily, hourly_dates, daily_fetched, catalog_fetched, history_bounds):
    with st.sidebar:
        st.selectbox("Reporting interval", ["7 days", "30 days", "90 days", "1 year", "All history", "Custom"], key="preset", on_change=apply_preset, args=(earliest, latest, history_bounds), persist_state="session")
        window = st.date_input("Dates", min_value=earliest, max_value=latest, key="window", on_change=custom_interval, format="DD/MM/YYYY", persist_state="session")
        if not isinstance(window, tuple) or len(window) != 2:
            st.info("Select an end date to complete the reporting interval.")
            st.stop()
        start, end = window
        if start > end:
            st.error("Choose an end date on or after the start date.")
            st.stop()
        if not start <= st.session_state["day"] <= end:
            available = [day for day in hourly_dates if start <= day <= end]
            st.session_state["day"] = available[-1] if available else end
        comparison = st.session_state.get("compare_day")
        if comparison is not None and not start <= comparison <= end:
            st.session_state["compare_day"] = None
        st.divider()
        st.markdown("**Report coverage**")
        st.caption(f"Daily summaries · {daily['date'].max().strftime('%d %b %Y') if not daily.empty else 'Unavailable'}")
        st.caption(f"Hourly profiles · {hourly_dates[-1].strftime('%d %b %Y') if hourly_dates else 'Unavailable'}")
        st.caption(f"Available history · {earliest.strftime('%d %b %Y')} – {latest.strftime('%d %b %Y')}")
        st.caption(f"Daily reports fetched · {pd.Timestamp(daily_fetched).strftime('%d %b, %H:%M WAT')}")
        st.caption(f"Hourly index fetched · {pd.Timestamp(catalog_fetched).strftime('%d %b, %H:%M WAT')}")
        if st.button("Refresh reports", key="refresh_reports", width="stretch", help="Fetch the latest reports and refresh the ten-minute data cache."):
            refresh_data()
            st.rerun()
        st.divider()
        st.caption("Reporting times use West Africa Time (Africa/Lagos).")
        st.caption("The address bar contains a shareable link to your current view and filters.")
    return start, end


def sync_url():
    values = query_values(st.session_state)
    current = {key: st.query_params.get_all(key) if key == "plant" else st.query_params[key] for key in st.query_params}
    if current != values:
        st.query_params.from_dict(values)
    st.session_state["_last_query"] = values


def run_app():
    st.set_page_config(page_title="GRIDLINES · Nigerian grid explorer", page_icon="⚡", layout="wide", initial_sidebar_state="auto")
    st.html("""
        <style>
        .stMainBlockContainer { max-width: 1540px; padding-top: 2rem; padding-bottom: 3rem; }
        h1 { letter-spacing: -0.045em; font-weight: 650; }
        h3 { letter-spacing: -0.025em; }
        [data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; font-size: clamp(1.3rem, 2.1vw, 2.3rem); }
        [data-testid="stMetricLabel"] { color: #A9BACB; }
        [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 12px; }
        [data-testid="stSidebar"] { border-right: 1px solid #253242; }
        [data-testid="stSidebar"] h1 { color: #57D8DC; font-size: 2rem; }
        [data-testid="stMultiSelect"] [data-tag],
        [data-testid="stMultiSelect"] [data-tag] button { color: #0D131B; }
        @media (max-width: 700px) {
            .stMainBlockContainer { padding: 4rem 1rem 1rem; }
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
            [data-testid="stColumn"] { min-width: min(100%, 280px); }
        }
        </style>
    """)
    with st.sidebar:
        st.title("GRIDLINES")
        st.caption("A view of the Nigerian grid's performance through lines (read time).")
    try:
        with st.spinner("Loading grid reports…"):
            daily, daily_fetched, invalid_dates = load_daily()
            hourly_dates, catalog_fetched = load_catalog()
        dates = sorted(set(daily["date"]) | set(hourly_dates))
        if not dates:
            st.title("GRIDLINES")
            st.info("The connected collections have no reports with readable dates yet.")
            if st.button("Retry loading reports"):
                refresh_data()
                st.rerun()
            return
        earliest, latest = dates[0], dates[-1]
        initialize_filters(earliest, latest, hourly_dates)
        context = ViewContext(daily, hourly_dates, earliest, latest)
        pages = [
            st.Page(lambda: overview(context), title="Overview", icon=":material/monitoring:", default=True),
            st.Page(lambda: daily_explorer(context), title="Daily explorer", icon=":material/schedule:", url_path="daily"),
            st.Page(lambda: power_plants(context), title="Power plants", icon=":material/factory:", url_path="plants"),
            st.Page(lambda: grid_conditions(context), title="Grid conditions", icon=":material/waves:", url_path="conditions"),
        ]
        context.daily_page = pages[1]
        page = st.navigation(pages, position="top")
        history_bounds = all_history_bounds(
            earliest, latest, daily,
            view=page.url_path, metric=st.session_state.get("overview_metric"),
        )
        if st.session_state["preset"] == "All history":
            st.session_state["window"] = history_bounds
        context.start, context.end = sidebar_filters(
            earliest, latest, daily, hourly_dates, daily_fetched, catalog_fetched, history_bounds,
        )
        for notice in st.session_state.pop("_filter_notices", []):
            st.info(notice)
        if invalid_dates:
            st.warning(f"{invalid_dates:,} daily records have unreadable dates. Coverage reflects the readable reports.")
        page.run()
        sync_url()
    except DataUnavailable as error:
        st.error(str(error))
        if st.button("Retry connection"):
            refresh_data()
            st.rerun()


if __name__ == "__main__":
    run_app()
