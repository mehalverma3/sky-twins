from datetime import date

import pandas as pd
import streamlit as st

from sky import positions, find_aspects

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def sign_of(lon: float) -> str:
    return f"{SIGNS[int(lon // 30)]} {lon % 30:.1f}°"


st.title("Sky Twins")
st.caption(
    "Pick a date and see the sky. Interpretation, not scientific prediction: "
    "astrology has no demonstrated predictive validity."
)

chosen = st.date_input(
    "Date to analyze",
    value=date(2000, 1, 1),
    min_value=date(1900, 1, 1),
    max_value=date(2025, 12, 31),
)

pos = positions(chosen)

st.subheader("Planet positions (noon UTC)")
st.table(pd.DataFrame(
    [(name, sign_of(lon)) for name, lon in pos.items()],
    columns=["Planet", "Position"],
))

st.subheader("Major aspects")
aspects = find_aspects(pos)
if aspects:
    st.table(pd.DataFrame(
        aspects, columns=["Planet A", "Planet B", "Aspect", "Orb (°)"]
    ))
else:
    st.write("No major aspects within orb on this date.")
