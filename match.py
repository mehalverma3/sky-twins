from datetime import date
from itertools import combinations

import numpy as np
import pandas as pd

from sky import BODIES, positions

NAMES = list(BODIES)
# Slow planets get more weight: their configurations define an era, while
# the Moon changes ~13 degrees a day and mostly adds noise.
PLANET_WEIGHT = {"Sun": 0.5, "Moon": 0.2, "Mercury": 0.5, "Venus": 0.6,
                 "Mars": 0.8, "Jupiter": 1.0, "Saturn": 1.0,
                 "Uranus": 1.0, "Neptune": 1.0, "Pluto": 1.0}
PAIRS = list(combinations(range(len(NAMES)), 2))
PAIR_I = [i for i, _ in PAIRS]
PAIR_J = [j for _, j in PAIRS]
PAIR_W = np.array([PLANET_WEIGHT[NAMES[i]] * PLANET_WEIGHT[NAMES[j]]
                   for i, j in PAIRS])


def signatures(lons: np.ndarray) -> np.ndarray:
    """(n, 10) longitudes -> (n, 45) pairwise angular separations, 0-180."""
    diff = np.abs(lons[:, PAIR_I] - lons[:, PAIR_J]) % 360
    return np.minimum(diff, 360 - diff)


def similarity(target_sig: np.ndarray, all_sigs: np.ndarray) -> np.ndarray:
    """1.0 = identical sky. Weighted mean difference across planet pairs."""
    d = np.abs(all_sigs - target_sig)
    mean_diff = (d * PAIR_W).sum(axis=1) / PAIR_W.sum()
    return 1 - mean_diff / 180


def find_twins(d: date, k: int = 5, events_per_date: int = 3) -> list[dict]:
    cache = pd.read_csv("sky_cache.csv")
    events = pd.read_csv("events.csv")
    pos = positions(d)
    target = signatures(np.array([[pos[n] for n in NAMES]]))[0]
    cache["score"] = similarity(target, signatures(cache[NAMES].values))
    cache = cache[cache["date"] != d.isoformat()]  # never match a date to itself
    results = []
    for _, row in cache.nlargest(k, "score").iterrows():
        day_events = events[events["date"] == row["date"]].head(events_per_date)
        results.append({
            "date": row["date"],
            "score": round(float(row["score"]), 4),
            "events": day_events[["text", "page_title", "url"]].to_dict("records"),
        })
    return results