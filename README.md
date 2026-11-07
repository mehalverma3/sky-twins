# Sky Twins

Pick a date from 1900 to 2050. Sky Twins computes the planetary configuration for that day, finds the days in history whose skies looked most similar, and surfaces what happened on them.

*Live app:* [Sky Twins App](https://sky-twins-5hat5mtdavknsars7oqgrs.streamlit.app/)

## The Honest Framing

This is an analog-day pattern finder, not a scientific predictor. Astrology has no demonstrated predictive validity. Matches show similar sky geometry, not causation, and any reading is an interpretation built strictly from the retrieved events. 

Future dates are supported, but future readings cannot be checked against what actually happens—they show which historical days the sky resembles, not a forecast.

## How It Works

1. **Sky Engine** (`sky.py`): Calculates planet positions from NASA JPL's DE421 ephemeris via `skyfield`, along with major aspects and retrograde statuses.
2. **Matching Engine** (`match.py`): Compares pairwise angular separations between planets on the target date against historical dates in the event dataset, weighted by planet speed.
3. **Grounded Reading** (`reading.py`): An LLM generates a short synthesis using *only* the retrieved events. Each claim must cite an event tag (e.g., `[E1]`), and any reading citing external information is automatically discarded.

## Run It Locally

```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY="..."   # or ANTHROPIC_API_KEY
export LLM_MODEL="..."           # your configured model name
streamlit run streamlit_app.py
