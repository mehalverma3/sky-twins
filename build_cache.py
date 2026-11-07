import pandas as pd
from sky import ts, eph, BODIES


def build():
    df = pd.read_csv("events.csv")
    dates = sorted(df["date"].unique())  # one sky per unique date, not per event
    dt = pd.to_datetime(dates)
    t = ts.utc(dt.year.values, dt.month.values, dt.day.values, 12)
    earth = eph["earth"]
    out = {"date": dates}
    for name, key in BODIES.items():
        lon = earth.at(t).observe(eph[key]).apparent().ecliptic_latlon(epoch="date")[1]
        out[name] = lon.degrees % 360
    pd.DataFrame(out).to_csv("sky_cache.csv", index=False)
    print(f"Cached {len(dates)} unique dates")


if __name__ == "__main__":
    build()