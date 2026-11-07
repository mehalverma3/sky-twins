from datetime import date

import pandas as pd
import streamlit as st

from match import find_twins
from reading import write_reading
from sky import find_aspects, positions

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def sign_of(lon: float) -> str:
    return f"{SIGNS[int(lon // 30)]} {lon % 30:.1f}°"


@st.cache_data
def cached_twins(d: date):
    return find_twins(d)


st.title("Sky Twins")
st.caption(
    "Find the days in history whose sky looked most like the day you pick. "
    "This is interpretation, not scientific prediction: astrology has no "
    "demonstrated predictive validity."
)

chosen = st.date_input(
    "Date to analyze",
    value=date(2000, 1, 1),
    min_value=date(1900, 1, 1),
    max_value=date(2026, 11, 7),
)

pos = positions(chosen)

with st.expander("Planet positions and aspects on this date"):
    st.table(pd.DataFrame(
        [(n, sign_of(lon)) for n, lon in pos.items()],
        columns=["Planet", "Position"],
    ))
    aspects = find_aspects(pos)
    if aspects:
        st.table(pd.DataFrame(
            aspects, columns=["Planet A", "Planet B", "Aspect", "Orb (°)"]
        ))

st.subheader("Sky twins")
twins = cached_twins(chosen)
for twin in twins:
    st.markdown(f"**{twin['date']}** (similarity {twin['score']})")
    if twin["events"]:
        for ev in twin["events"]:
            link = f" ([source]({ev['url']}))" if isinstance(ev["url"], str) and ev["url"] else ""
            st.write(f"- {ev['text']}{link}")
    else:
        st.write("- No events recorded for this date.")

st.subheader("Reading")
if st.button("Generate reading"):
    with st.spinner("Reading the sky..."):
        st.write(write_reading(chosen.isoformat(), twins))
    st.caption("Every event cited above must come from the matches listed here; "
               "readings that cite anything else are discarded.")

st.divider()
st.caption("Event data from Wikipedia's On This Day (CC BY-SA). Ephemeris: NASA JPL DE421.")