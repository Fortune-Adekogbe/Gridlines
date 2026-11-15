"""The four interactive views of the Gridlines dashboard."""

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from grid_charts import AMBER, BLUE, COLORS, CYAN, GREEN, TECH_COLORS, line_trace, render, styled
from grid_data import (
    NORMAL_FREQUENCY, comparison_delta,
    daily_axis, date_window, frequency_summary, hour_label, partial_hourly_measurement,
    voltage_observation,
)
from grid_repository import load_hourly, load_plant_comparison, load_plant_statistics
from grid_state import query_values


@dataclass
class ViewContext:
    daily: pd.DataFrame
    hourly_dates: list[date]
    start: date
    end: date
    daily_page: object = None

    @property
    def reports(self):
        return date_window(self.daily, self.start, self.end)

    @property
    def days(self):
        return (self.end - self.start).days + 1


def formatted(value, decimals=0):
    return "—" if value is None or pd.isna(value) else f"{value:,.{decimals}f}"


def page_heading(title, description):
    st.title(title)
    st.caption(description)


def metric(column, title, value, unit, note, delta=None, *, decimals=0, help_text=None, border=True):
    with column.container(border=border):
        st.metric(title, f"{formatted(value, decimals)} {unit}" if value is not None else "—", delta=None if delta is None else f"{delta:+.1f}% vs previous period", delta_color="off", help=help_text)
        st.caption(note)


def generation_label(row, field, label):
    if not partial_hourly_measurement(row, field):
        return label
    return {
        "Maximum generation": "Maximum observed generation",
        "Highest peak generation": "Highest observed generation",
    }.get(label, f"Observed {label.lower()}")


def excluded_reading_details(excluded, key):
    if excluded.empty:
        return
    details = st.expander("Excluded readings", key=key, on_change="rerun")
    if details.open:
        with details:
            st.caption("These original source readings are excluded from charts and calculations. Hourly profiles leave gaps at those readings.")
            rows = excluded.drop_duplicates(["date", "hour", "plant", "raw_mw"]).sort_values(["date", "hour", "plant"])
            st.table(pd.DataFrame({
                "Day": rows["date"].map(lambda day: day.strftime("%d %b %Y")),
                "Hour (WAT)": rows["hour"].map(hour_label),
                "Reading": rows.apply(lambda row: "Grid total" if row["aggregate"] else row["plant"], axis=1),
                "Original MW": rows["raw_mw"].map(lambda value: formatted(value, 2)),
                "Reason": rows["quality_reason"],
            }), alt="Original generation readings excluded from calculations, with their reporting date, hour, and reason.")


def use_daily_interval(start, end):
    st.session_state["window"] = (start, end)
    st.session_state["preset"] = "Custom"
    st.session_state["day"] = end
    st.session_state["compare_day"] = None


def daily_coverage_notice(context, fields, label, key):
    if context.reports[fields].notna().any(axis=None):
        return
    available = context.daily.loc[context.daily[fields].notna().any(axis=1), "date"]
    if available.empty:
        st.info(f"{label} are unavailable in the connected daily collection.")
        return
    latest = available.max()
    start = max(available.min(), latest - timedelta(days=29))
    st.info(f"{label} are available through {latest.strftime('%d %b %Y')}. This interval has no daily observations for these measurements.")
    st.button("View latest daily reports", key=key, on_click=use_daily_interval, args=(start, latest))


def overview(context):
    page_heading("Grid overview", "Explore Nigeria’s reported electricity generation, energy, and grid frequency.")
    daily_coverage_notice(context, ["energy_generated", "energy_sent"], "Daily energy reports", "latest_energy_interval")
    hourly, _ = load_hourly(context.start, context.end, aggregates_only=True)
    reports = context.reports
    cards = st.grid(4, min_column_width=220, border=True, key="overview_metrics")
    columns = [cards.cell() for _ in range(4)]
    energy_totals = reports[["energy_generated", "energy_sent"]].sum(min_count=1)
    largest_energy = energy_totals.abs().max()
    if largest_energy >= 1_000_000:
        divisor, energy_unit, decimals = 1_000_000, "TWh", 2
    elif largest_energy >= 1_000:
        divisor, energy_unit, decimals = 1_000, "GWh", 2
    else:
        divisor, energy_unit, decimals = 1, "MWh", 0
    for column, field, label in zip(columns[:2], ("energy_generated", "energy_sent"), ("Energy generated", "Energy sent out")):
        values = reports[field].dropna()
        total = energy_totals[field]
        value = None if pd.isna(total) else total / divisor
        details = None if value is None else f"Reported total: {total:,.2f} MWh."
        if details is not None and divisor != 1:
            details += f" 1 {energy_unit} = {divisor:,} MWh."
        metric(column, label, value, energy_unit, f"{len(values):,} / {context.days:,} reporting days", comparison_delta(context.daily, field, context.start, context.end), decimals=decimals, help_text=details, border=False)
    peaks = reports["peak"].dropna()
    peak_label = "Maximum generation"
    if not peaks.empty:
        peak_row = reports.loc[reports["peak"].idxmax()]
        peak_label = generation_label(peak_row, "peak", peak_label)
    metric(columns[2], peak_label, None if peaks.empty else peaks.max(), "MW", f"{len(peaks):,} / {context.days:,} reporting days", comparison_delta(context.daily, "peak", context.start, context.end, "max"), border=False)
    mean = None if hourly.grid.empty else hourly.grid["mw"].mean()
    metric(columns[3], "Mean hourly generation", mean, "MW", f"{hourly.grid['mw'].count():,} / {context.days * 24:,} accepted grid hours", border=False)

    if st.session_state.get("overview_metric") not in ("Generation", "Energy"):
        st.session_state["overview_metric"] = "Generation"
        st.info("The shared metric was unavailable. Generation was selected.")
    st.segmented_control("Measurement", ["Generation", "Energy"], key="overview_metric", selection_mode="single", required=True, persist_state="session")
    frame = daily_axis(context.daily, context.start, context.end)
    figure = go.Figure()
    if st.session_state["overview_metric"] == "Generation":
        st.subheader("Generation through time")
        for field, label, color in (("peak", "Peak generation", CYAN), ("trough", "Off-peak generation", AMBER), ("grid_0600", "Grid at 06:00", BLUE)):
            if not frame[field].notna().any():
                continue
            frame[f"{field}_source"] = frame["provenance"].map(lambda value: value.get(field, "Unavailable") if isinstance(value, dict) else "Unavailable")
            figure.add_trace(line_trace(frame, "date", field, label, color, source=f"{field}_source", markers=True))
        unit = "MW"
    else:
        st.subheader("Energy through time")
        for field, label, color in (("energy_generated", "Generated", CYAN), ("energy_sent", "Sent out", AMBER)):
            frame[f"{field}_source"] = frame["provenance"].map(lambda value: value.get(field, "Unavailable") if isinstance(value, dict) else "Unavailable")
            figure.add_trace(line_trace(frame, "date", field, label, color, source=f"{field}_source", markers=True, unit="MWh"))
        unit = "MWh per reporting day"
        st.caption("Generated and sent-out energy follow the values published in each daily report.")
    event = render(styled(figure, unit, 400), "overview_trend", selectable=True, alt="Daily generation or energy over the selected reporting interval, with visible gaps for missing days.")
    points = event.selection.points
    if points:
        selected = pd.Timestamp(points[-1]["x"]).date()
        if context.start <= selected <= context.end:
            st.session_state["day"] = selected
    actions = st.columns([2, 1])
    with actions[0]:
        st.caption(f"Inspect a day · {st.session_state['day'].strftime('%d %b %Y')}")
    with actions[1]:
        if st.button("Open daily explorer →", key="open_daily", width="stretch"):
            st.switch_page(context.daily_page, query_params=query_values(st.session_state))

    left, right = st.columns([3, 2])
    with left.container(border=True):
        st.subheader("The daily generation pattern")
        if hourly.grid.empty:
            st.info("Hourly generation observations are unavailable for this interval.")
        else:
            matrix = hourly.grid.pivot(index="date", columns="hour", values="mw").reindex(index=pd.date_range(context.start, context.end).date)
            heatmap = go.Figure(go.Heatmap(x=[hour_label(hour) for hour in matrix.columns], y=matrix.index, z=matrix.to_numpy(), colorscale=[[0, "#182B3A"], [0.5, "#237A8C"], [1, CYAN]], colorbar=dict(title="MW", thickness=10), hovertemplate="%{y} · %{x}<br>%{z:,.1f} MW<extra></extra>", hoverongaps=False))
            heatmap.update_yaxes(type="date", autorange="reversed")
            render(styled(heatmap, height=330, hovermode="closest"), "overview_heatmap", alt="Heatmap of reported grid generation by reporting day and hour. Blank cells indicate missing observations.")
    with right.container(border=True):
        st.subheader("In this interval")
        if not peaks.empty:
            peak_row = reports.loc[reports["peak"].idxmax()]
            st.metric(generation_label(peak_row, "peak", "Highest peak generation"), f"{peak_row['peak']:,.0f} MW")
            st.caption(f"{peak_row['date'].strftime('%d %b %Y')} · {hour_label(peak_row['peak_hour'])}")
        consecutive = frame["peak"].diff()
        if consecutive.notna().any():
            position = consecutive.abs().idxmax()
            st.metric("Largest adjacent-day peak change", f"{consecutive.loc[position]:+,.0f} MW")
            st.caption(frame.loc[position, "date"].strftime("%d %b %Y"))
        excursions, days, observations = frequency_summary(reports)
        st.metric("Days with frequency excursions", f"{excursions} / {days}")
        st.caption(f"{observations:,} reported observations · reference band 49.75–50.25 Hz")
        difference = reports["energy_generated"] - reports["energy_sent"]
        if difference.notna().any():
            st.caption(f"Difference between generated and sent-out energy · {difference.sum():,.0f} MWh across {difference.notna().sum():,} paired reporting days.")
    excluded_reading_details(hourly.excluded, "overview_exclusions")


def choose_day(value):
    st.session_state["day"] = value


def daily_explorer(context):
    page_heading("Daily explorer", "Follow an hourly generation profile and inspect the plants contributing at each reported hour.")
    available = [day for day in context.hourly_dates if context.start <= day <= context.end]
    current = st.session_state["day"]
    previous = [day for day in available if day < current]
    following = [day for day in available if day > current]
    controls = st.columns([2, 1, 1, 2])
    with controls[0]:
        st.date_input("Reporting day", min_value=context.start, max_value=context.end, key="day", format="DD/MM/YYYY", persist_state="session")
    with controls[1]:
        st.button("← Previous", key="previous_day", disabled=not previous, on_click=choose_day, args=(previous[-1] if previous else current,), width="stretch")
    with controls[2]:
        st.button("Next →", key="next_day", disabled=not following, on_click=choose_day, args=(following[0] if following else current,), width="stretch")
    if st.session_state.get("compare_day") not in [None, *available]:
        st.session_state["compare_day"] = None
        st.info("The comparison day has no hourly report in this interval. Choose an available day.")
    with controls[3]:
        st.selectbox("Compare with", [None, *available], key="compare_day", format_func=lambda day: "Choose a comparison day" if day is None else day.strftime("%d %b %Y"), persist_state="session")
    current = st.session_state["day"]
    hourly, _ = load_hourly(current, current)
    grid, plants = hourly.grid, hourly.plants
    if grid.empty and plants.empty:
        st.info("An hourly generation profile is unavailable for this reporting day. Choose another day or use Previous and Next to move between available reports.")
        daily_report_details(context, current)
        return
    hours = sorted(set(grid["hour"]) | set(plants["hour"]))
    observed = int(grid["mw"].count())
    cards = st.columns(4)
    report = context.daily.loc[context.daily["date"] == current]
    peak = None if report.empty else report.iloc[0]["peak"]
    off_peak = None if report.empty else report.iloc[0]["trough"]
    peak_label, trough_label = "Peak generation", "Off-peak generation"
    note = current.strftime("%d %b %Y")
    if not report.empty:
        peak_label = generation_label(report.iloc[0], "peak", peak_label)
        trough_label = generation_label(report.iloc[0], "trough", trough_label)
    metric(cards[0], "Mean observed generation", None if not observed else grid["mw"].mean(), "MW", f"{observed} / 24 accepted grid hours")
    metric(cards[1], peak_label, peak, "MW", note)
    metric(cards[2], trough_label, off_peak, "MW", note)
    metric(cards[3], "Plants reporting", plants.loc[plants["mw"].notna(), "plant"].nunique(), "", note)
    st.subheader("Hourly grid profile")
    figure = go.Figure()
    axis = pd.DataFrame({"hour": range(min(hours), max(hours) + 1)})
    profile = axis.merge(grid[["hour", "mw", "source"]], on="hour", how="left")
    figure.add_trace(line_trace(profile, "hour", "mw", current.strftime("%d %b"), CYAN, source="source", markers=True))
    compare_day = st.session_state.get("compare_day")
    exclusions = [hourly.excluded]
    if compare_day is not None:
        compared, _ = load_hourly(compare_day, compare_day, aggregates_only=True)
        exclusions.append(compared.excluded)
        comparison = axis.merge(compared.grid[["hour", "mw", "source"]], on="hour", how="left")
        figure.add_trace(line_trace(comparison, "hour", "mw", compare_day.strftime("%d %b"), AMBER, source="source", dashed=True, markers=True))
    if st.session_state.get("selected_hour") not in hours:
        st.session_state["selected_hour"] = hours[0]
    st.select_slider("Inspect contributions at", options=hours, key="selected_hour", format_func=hour_label, persist_state="session")
    hour = st.session_state["selected_hour"]
    figure.add_vline(x=hour, line_dash="dot", line_color=AMBER, opacity=0.7)
    figure = styled(figure, "MW", 350)
    figure.update_xaxes(tickvals=hours, ticktext=[hour_label(value) for value in hours], title_text="Reporting hour · WAT")
    render(figure, "daily_profile", alt="Selected-day hourly grid generation, with an optional comparison day and a marker at the selected hour.")

    left, right = st.columns([3, 2])
    selected = plants.loc[plants["hour"].eq(hour) & plants["mw"].notna()].sort_values("mw", ascending=False)
    with left.container(border=True):
        st.subheader(f"Plant contributions at {hour_label(hour)}")
        if selected.empty:
            st.info("Station observations are unavailable at this hour.")
        else:
            bar = go.Figure(go.Bar(x=selected["mw"], y=selected["plant"], orientation="h", marker_color=[TECH_COLORS[value] for value in selected["technology"]], customdata=selected[["source"]], hovertemplate="%{y}<br>%{x:,.1f} MW<br>Source: %{customdata[0]}<extra></extra>"))
            bar.update_yaxes(autorange="reversed")
            bar.update_xaxes(title_text="MW")
            render(styled(bar, height=max(360, 24 * len(selected)), hovermode="closest"), "daily_contributions", alt="Power plants ranked by observed MW at the selected reporting hour.")
    with right.container(border=True):
        st.subheader("Observed generation mix")
        if not selected.empty and selected["mw"].sum() > 0 and selected["mw"].ge(0).all():
            mix = selected.groupby("technology")["mw"].sum()
            pie = go.Figure(go.Pie(labels=mix.index, values=mix.values, hole=0.7, marker_colors=[TECH_COLORS[value] for value in mix.index], textinfo="percent", hovertemplate="%{label}<br>%{value:,.1f} MW · %{percent}<extra></extra>"))
            render(styled(pie, height=300, hovermode="closest"), "daily_mix", alt="Technology shares of the sum of observed plant output at the selected hour.")
            st.caption(f"Shares of {selected['mw'].sum():,.1f} MW observed across {len(selected)} plants.")
        else:
            st.caption("Generation shares require a positive observed station total.")
        reported = grid.loc[grid["hour"].eq(hour) & grid["mw"].notna()]
        if not selected.empty and not reported.empty:
            grid_total = reported.iloc[0]["mw"]
            station_total = selected["mw"].sum()
            st.metric("Reported grid total", f"{grid_total:,.1f} MW")
            st.metric("Sum of observed plants", f"{station_total:,.1f} MW")
            st.caption(f"Grid total minus station sum · {grid_total - station_total:+,.1f} MW. Station reporting coverage and source totals can differ.")
        st.caption("Technology labels use explicit source names and the station alias registry. Other station labels appear as Unclassified.")
    if not plants.empty:
        st.subheader("Every plant, hour by hour")
        matrix = plants.pivot(index="plant", columns="hour", values="mw").reindex(columns=hours)
        order = matrix.mean(axis=1).sort_values(ascending=False).index
        matrix = matrix.loc[order]
        heatmap = go.Figure(go.Heatmap(x=[hour_label(value) for value in matrix.columns], y=matrix.index, z=matrix.to_numpy(), colorscale=[[0, "#182532"], [0.4, "#285D71"], [1, CYAN]], colorbar=dict(title="MW", thickness=10), hovertemplate="%{y} · %{x}<br>%{z:,.1f} MW<extra></extra>", hoverongaps=False))
        heatmap.update_yaxes(autorange="reversed")
        render(styled(heatmap, height=max(400, len(matrix) * 22), hovermode="closest"), "daily_plant_heatmap", alt="Plant-by-hour generation heatmap. Blank cells show missing observations and reported zeros retain the lowest color.")
    daily_report_details(context, current)
    excluded_reading_details(pd.concat(exclusions, ignore_index=True), "daily_exclusions")


def daily_report_details(context, day):
    report = context.daily.loc[context.daily["date"] == day]
    if report.empty:
        st.caption("A daily summary report is unavailable for this date.")
        return
    row = report.iloc[0]
    with st.expander("Daily measurements"):
        fields = [
            ("Peak generation", "peak", "MW", "peak_hour"),
            ("Off-peak generation", "trough", "MW", "trough_hour"),
            ("Grid at 06:00", "grid_0600", "MW", None),
            ("Energy generated", "energy_generated", "MWh", None),
            ("Energy sent out", "energy_sent", "MWh", None),
        ]
        st.table(pd.DataFrame([{
            "Measurement": generation_label(row, field, label), "Value": formatted(row[field], 2), "Unit": unit,
            "Reported hour": hour_label(row[time]) if time else ("06:00" if field == "grid_0600" else "Daily report"),
            "Source": row["provenance"].get(field, "Unavailable"),
        } for label, field, unit, time in fields]))


def power_plants(context):
    page_heading("Power plants", "Compare observed output and reporting coverage across the stations connected to the grid.")
    with st.spinner("Loading station profiles…"):
        all_stations, details, _ = load_plant_statistics(context.start, context.end)
    if all_stations.empty:
        st.info("Station-level profiles are unavailable for this interval. Choose a different reporting interval.")
        excluded_reading_details(details.excluded, "plant_exclusions")
        return
    technologies = ["All technologies", *sorted(all_stations["technology"].unique())]
    if st.session_state.get("technology") not in technologies:
        st.session_state["technology"] = "All technologies"
        st.info("The shared technology filter was unavailable in this interval. All technologies were selected.")
    st.selectbox("Generation technology", technologies, key="technology", persist_state="session")
    summary = all_stations if st.session_state["technology"] == "All technologies" else all_stations.loc[all_stations["technology"] == st.session_state["technology"]]
    st.subheader("Mean observed generation")
    st.caption("Ranked by the mean of available MW observations. Coverage is shown for each station.")
    leaders = summary.head(12)
    chart = go.Figure(go.Bar(x=leaders["mean_mw"], y=leaders["plant"], orientation="h", marker_color=[TECH_COLORS[value] for value in leaders["technology"]], customdata=leaders[["plant", "coverage", "observations"]], hovertemplate="%{y}<br>%{x:,.1f} MW<br>%{customdata[1]:.1f}% coverage · %{customdata[2]:,} observations<extra></extra>"))
    chart.update_yaxes(autorange="reversed")
    chart.update_xaxes(title_text="Mean observed MW")
    event = render(styled(chart, height=max(350, len(leaders) * 28), hovermode="closest"), "plant_ranking", selectable=True, alt="Top twelve power plants ranked by mean observed MW, with coverage available on hover.")
    options = summary["plant"].tolist()
    selected = st.session_state.get("plants", [])
    retained = [plant for plant in selected if plant in options]
    if selected != retained:
        st.info("Some selected plants have no observations matching this interval and technology. The available selections were retained.")
    if "_plants_initialized" not in st.session_state:
        retained = retained or options[:2]
        st.session_state["_plants_initialized"] = True
    if event.selection.points:
        plant = event.selection.points[-1]["customdata"][0]
        if plant in options and plant != st.session_state.get("_last_rank_selection"):
            retained = list(dict.fromkeys([*retained, plant]))[-5:]
            st.session_state["_last_rank_selection"] = plant
    else:
        st.session_state.pop("_last_rank_selection", None)
    st.session_state["plants"] = retained
    st.multiselect("Compare power plants", options, key="plants", max_selections=5, placeholder="Search and select up to five plants", persist_state="session")
    selected = st.session_state["plants"]
    if selected:
        with st.spinner("Comparing common reporting hours…"):
            daily_comparison, profiles, common_count = load_plant_comparison(context.start, context.end, tuple(selected))
        st.caption(f"Comparison uses {common_count:,} common reporting hours · {common_count / (context.days * 24):.1%} of the selected interval.")
        if daily_comparison.empty:
            st.info("The selected plants have no common observed reporting hours. Adjust the plants or reporting interval.")
        else:
            left, right = st.columns(2)
            with left.container(border=True):
                st.subheader("Generation by reporting day")
                figure = go.Figure()
                for index, plant in enumerate(selected):
                    daily = daily_comparison.loc[daily_comparison["plant"] == plant, ["date", "mw"]]
                    daily = daily_axis(daily, context.start, context.end)
                    figure.add_trace(line_trace(daily, "date", "mw", plant, COLORS[index]))
                render(styled(figure, "Mean observed MW"), "plant_daily_trends", alt="Daily mean generation of selected plants, calculated over common observed reporting hours.")
            with right.container(border=True):
                st.subheader("Typical hourly profile")
                figure = go.Figure()
                for index, plant in enumerate(selected):
                    profile = profiles.loc[profiles["plant"] == plant, ["hour", "mw"]]
                    axis = pd.DataFrame({"hour": range(int(profiles["hour"].min()), int(profiles["hour"].max()) + 1)})
                    profile = axis.merge(profile, on="hour", how="left")
                    figure.add_trace(line_trace(profile, "hour", "mw", plant, COLORS[index], markers=True))
                figure = styled(figure, "Mean observed MW")
                ticks = sorted(profiles["hour"].unique())
                figure.update_xaxes(tickvals=ticks[::2], ticktext=[hour_label(value) for value in ticks[::2]], title_text="Reporting hour · WAT")
                render(figure, "plant_hourly_profiles", alt="Mean generation by reporting hour for selected plants, using their common observations.")
    with st.expander("All station statistics"):
        table = summary.rename(columns={"plant": "Power plant", "technology": "Technology", "mean_mw": "Mean observed MW", "observations": "Observed hours", "coverage": "Coverage (%)"})
        st.table(table.round(1))
    excluded_reading_details(details.excluded, "plant_exclusions")


def grid_conditions(context):
    page_heading("Grid conditions", "Inspect reported frequency observations and voltage extremes across the selected interval.")
    daily_coverage_notice(context, ["frequency_low", "frequency_high", "frequency_peak", "frequency_trough", "frequency_0600"], "Frequency reports", "latest_frequency_interval")
    reports = context.reports
    excursions, days, observations = frequency_summary(reports)
    cards = st.columns(3)
    metric(cards[0], "Days with observed excursions", excursions, "", f"{days} reporting days with frequency observations")
    metric(cards[1], "Frequency reporting days", days, "", f"{context.days} selected days")
    metric(cards[2], "Frequency observations", observations, "", "Daily extrema and generation snapshots")
    st.subheader("Reported frequency")
    st.caption("Normal operating reference 49.75–50.25 Hz · nominal frequency 50 Hz.")
    st.markdown("[Frequency reference published by NERC](https://nerc.gov.ng/media/nerc-publishes-october-operational-performance-factsheet/)")
    frame = daily_axis(context.daily, context.start, context.end)
    figure = go.Figure()
    fields = [
        ("frequency_low", "Daily lowest", AMBER), ("frequency_high", "Daily highest", CYAN),
        ("frequency_0600", "At 06:00", BLUE), ("frequency_peak", "At peak generation", GREEN),
        ("frequency_trough", "At off-peak generation", "#DB9AC5"),
    ]
    for field, label, color in fields:
        frame[f"{field}_source"] = frame["provenance"].map(lambda value: value.get(field, "Unavailable") if isinstance(value, dict) else "Unavailable")
        figure.add_trace(line_trace(frame, "date", field, label, color, source=f"{field}_source", markers=True, unit="Hz"))
    figure.add_hrect(y0=NORMAL_FREQUENCY[0], y1=NORMAL_FREQUENCY[1], fillcolor=GREEN, opacity=0.09, line_width=0)
    figure.add_hline(y=50, line_dash="dot", line_color="#8296AC")
    for bound in NORMAL_FREQUENCY:
        figure.add_hline(y=bound, line_dash="dash", line_color=GREEN, opacity=0.45)
    event = render(styled(figure, "Hz", 400), "frequency_chart", selectable=True, alt="Daily frequency extrema and snapshots with a shaded 49.75 to 50.25 Hz reference band and a nominal 50 Hz line.")
    if event.selection.points:
        selected = pd.Timestamp(event.selection.points[-1]["x"]).date()
        if context.start <= selected <= context.end:
            st.session_state["day"] = selected
    st.date_input("Inspect a reporting day", min_value=context.start, max_value=context.end, key="day", format="DD/MM/YYYY", persist_state="session")
    day = st.session_state["day"]
    row = reports.loc[reports["date"] == day]
    if row.empty or row.iloc[0]["report_count"] == 0:
        st.info("A daily grid-condition report is unavailable for this date.")
    else:
        row = row.iloc[0]
        left, right = st.columns(2)
        with left.container(border=True):
            st.subheader("Frequency extremes")
            for title, field, hour_field in (("Highest reported frequency", "frequency_high", "frequency_high_hour"), ("Lowest reported frequency", "frequency_low", "frequency_low_hour")):
                st.metric(title, f"{formatted(row[field], 2)} Hz")
                st.caption(f"{hour_label(row[hour_field])} WAT · {row['provenance'].get(field, 'Source unavailable')}")
        with right.container(border=True):
            st.subheader("Voltage observations")
            for title, field in (("Highest reported voltage", "voltage_high"), ("Lowest reported voltage", "voltage_low")):
                value, location, time = voltage_observation(row[field])
                st.metric(title, f"{formatted(value, 2)} kV" if value is not None else "—")
                if location or time:
                    st.caption(" · ".join(part for part in (location, time) if part))
                st.caption(str(row[field]) if row[field] is not None else "Observation unavailable")
                st.caption(row["provenance"].get(field, "Source unavailable"))
    if st.button("Explore this day’s generation →"):
        st.switch_page(context.daily_page, query_params=query_values(st.session_state))

