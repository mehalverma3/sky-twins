import calendar
from datetime import date

import streamlit as st

import ui
from inputs import parse_date
from match import find_twins
from reading import write_reading
from sky import find_aspects, is_retrograde, positions

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
MONTHS = list(calendar.month_name)[1:]


def sign_of(lon: float) -> str:
    return f"{SIGNS[int(lon // 30)]} {lon % 30:.1f}°"


@st.cache_data(show_spinner=False)
def cached_twins(d: date):
    return find_twins(d)


st.set_page_config(page_title="Sky Twins", page_icon="✦", layout="centered")
st.markdown(ui.CSS, unsafe_allow_html=True)

st.markdown('<span class="sky-badge">Celestial harmonics active</span>', unsafe_allow_html=True)
st.title("Sky Twins")
st.caption(
    "Find the days in history whose sky looked most like the day you pick. "
    "Interpretation, not scientific prediction: astrology has no demonstrated predictive validity."
)

st.session_state.setdefault("target", date(2000, 1, 1))

YEARS = list(range(2050, 1899, -1))

st.markdown("##### Observation date")
c_month, c_day, c_year = st.columns(3)
with c_month:
    month_name = st.selectbox("Month", MONTHS, index=0)
with c_year:
    year = st.selectbox("Year", YEARS, index=YEARS.index(2000))
month_num = MONTHS.index(month_name) + 1
with c_day:
    day = st.selectbox("Day", list(range(1, calendar.monthrange(year, month_num)[1] + 1)), index=0)

if st.button("Run analysis", type="primary", use_container_width=True):
    chosen = parse_date(f"{year:04d}-{month_num:02d}-{day:02d}")
    if chosen is None:
        st.error("Please choose a valid date between 1900 and 2025.")
    else:
        st.session_state["target"] = chosen

target = st.session_state["target"]

st.markdown('### Celestial core &nbsp; <span class="sky-badge">Live ephemeris</span>',
            unsafe_allow_html=True)
st.caption(f"Sky on {target.isoformat()} at noon UTC")
pos = positions(target)
st.markdown(
    ui.planet_rows([(n, sign_of(lon), is_retrograde(n, target)) for n, lon in pos.items()]),
    unsafe_allow_html=True,
)

st.markdown("### Major aspects")
st.markdown(ui.aspect_rows(find_aspects(pos)), unsafe_allow_html=True)

twins = cached_twins(target)
st.markdown(f'### Historical echoes &nbsp; <span class="sky-badge">{len(twins)} found</span>',
            unsafe_allow_html=True)
for twin in twins:
    st.markdown(ui.echo_card(twin), unsafe_allow_html=True)

st.markdown("### Reading")
reading_key = f"reading_{target.isoformat()}"
if st.button("Generate reading"):
    with st.spinner("Reading the sky..."):
        st.session_state[reading_key] = write_reading(target.isoformat(), twins)
if reading_key in st.session_state:
    st.write(st.session_state[reading_key])
    st.caption("Readings may only cite the events listed above; anything else is discarded.")
from reading import get_setting
st.caption(f"debug: key length {len(get_setting('ANTHROPIC_API_KEY'))}, model length {len(get_setting('LLM_MODEL'))}")

st.divider()
st.caption("Event data from Wikipedia's On This Day (CC BY-SA). Ephemeris: NASA JPL DE421.")