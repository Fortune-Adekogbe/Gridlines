"""URL state shared by the dashboard's pages."""

from datetime import date


def initial_state(parameters, earliest, latest):
    notices = []
    default_start = earliest

    def parsed_day(key, default):
        raw = parameters.get(key)
        if not raw:
            return default
        try:
            value = date.fromisoformat(raw)
            if not earliest <= value <= latest:
                raise ValueError
            return value
        except (ValueError, TypeError):
            notices.append(f"The shared {key.replace('_', ' ')} was outside the available dates or unreadable. A default was applied.")
            return default

    start = parsed_day("start", default_start)
    end = parsed_day("end", latest)
    if start > end:
        start, end = default_start, latest
        notices.append("The shared date interval was reversed. All history was selected.")
    day = parsed_day("day", end)
    if not start <= day <= end:
        day = end
        notices.append("The shared day was outside the selected interval. The interval's latest day was selected.")
    compare_day = parsed_day("compare_day", None)
    if compare_day is not None and not start <= compare_day <= end:
        compare_day = None
        notices.append("The comparison day was outside the selected interval.")
    raw_plants = parameters.get("plant", [])
    if isinstance(raw_plants, str):
        raw_plants = [raw_plants]
    plants = list(dict.fromkeys(raw_plants))[:5]
    try:
        hour = int(parameters.get("hour", 6))
        if not 0 <= hour <= 24:
            raise ValueError
    except (TypeError, ValueError):
        hour = 6
        notices.append("The shared hour was unreadable. 06:00 was selected.")
    return {
        "window": (start, end), "day": day, "compare_day": compare_day,
        "plants": plants, "selected_hour": hour,
        "overview_metric": parameters.get("metric", "Generation"),
        "technology": parameters.get("technology", "All technologies"),
    }, notices


def query_values(state):
    start, end = state["window"]
    values = {"start": start.isoformat(), "end": end.isoformat()}
    for key in ("day", "compare_day"):
        value = state.get(key)
        if value is not None:
            values[key] = value.isoformat()
    if state.get("plants"):
        values["plant"] = list(state["plants"])
    values["hour"] = str(state.get("selected_hour", 6))
    values["metric"] = state.get("overview_metric", "Generation")
    values["technology"] = state.get("technology", "All technologies")
    return values
