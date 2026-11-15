"""Exclude audited source spikes without changing or guessing source values."""

from datetime import date
from functools import lru_cache
import json
from pathlib import Path

import pandas as pd


@lru_cache(maxsize=1)
def reviewed_readings():
    with Path(__file__).with_name("generation_exclusions.json").open(encoding="utf-8") as source:
        records = json.load(source)["plant_readings"]
    by_date = {}
    for record in records:
        by_date.setdefault(date.fromisoformat(record["date"]), []).append(record)
    return by_date


def screen_hourly(grid, plants):
    """Retain source readings in raw_mw and use NaN for excluded observations.

    A dated, value-specific list avoids treating a plant upgrade, a new national
    record, or an upstream correction as another occurrence of an old error.
    National totals are screened even when callers load aggregate fields only.
    """
    grid, plants = grid.copy(), plants.copy()
    bad_hours = {}
    available_dates = set(grid["date"]) | set(plants["date"])
    for day in available_dates & reviewed_readings().keys():
        for record in reviewed_readings()[day]:
            plant_mask = (
                plants["date"].eq(day) & plants["hour"].eq(record["hour"])
                & plants["plant"].eq(record["plant"])
                & plants["raw_mw"].sub(record["mw"]).abs().lt(0.000001)
            )
            if plant_mask.any():
                plants.loc[plant_mask, "quality_reason"] = (
                    f"Audited isolated spike above twice the {record['capacity_reference']:g} MW "
                    "capacity reference and twice the other positive readings that day."
                )
                bad_hours.setdefault((day, record["hour"]), set()).add(record["plant"])
            total_mask = (
                grid["date"].eq(day) & grid["hour"].eq(record["hour"])
                & grid["raw_mw"].sub(record["grid_mw"]).abs().lt(0.000001)
            )
            grid.loc[total_mask, "quality_reason"] = (
                "Audited hourly total associated with an extreme plant spike."
            )
    for (day, hour), names in bad_hours.items():
        mask = grid["date"].eq(day) & grid["hour"].eq(hour)
        grid.loc[mask, "quality_reason"] = f"Includes excluded plant reading: {', '.join(sorted(names))}."
    for frame in (grid, plants):
        frame.loc[frame["quality_reason"].ne(""), "mw"] = float("nan")
    excluded = pd.concat(
        [frame.loc[frame["quality_reason"].ne("")] for frame in (grid, plants)],
        ignore_index=True,
    )
    return grid, plants, excluded
