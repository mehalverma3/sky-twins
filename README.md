# Sky Twins

Pick a date from 1900 to 2050. Sky Twins computes the planetary configuration for that day, finds the dates in history whose skies looked most similar, and shows what happened on them.

**Live app:** [your Streamlit link]

## The honest framing
This is an analog-day explorer, not a scientific predictor. Astrology has no demonstrated predictive validity. Matches show similar sky geometry, not causation, and any reading is interpretation built only from the matched events.
Dates after today are supported, but future readings cannot be checked against what actually happens. They show which historical days the sky resembles, and they are not forecasts.

## Who it's for
Astrology-curious people who want to see the reasoning behind a reading, and anyone interested in where data and symbolism meet.

## How it works
1. **Sky engine** (`sky.py`): planet positions from NASA JPL's DE421 ephemeris via skyfield, plus major aspects.
2. **Matching** (`match.py`): compares the pairwise angular separations between planets on the chosen date against every date in the event dataset, weighted by planet speed.
3. **Reading** (`reading.py`): an LLM writes a short reading using only the retrieved events. Each claim must cite an event tag, and readings citing anything else are discarded.

## Run it locally
pip install -r requirements.txt
export ANTHROPIC_API_KEY="..."   # key for your LLM provider
export LLM_MODEL="..."           # model name
streamlit run streamlit_app.py

The app works without a key; only the reading button needs one.

## Rebuild the data
python fetch_events.py   # Wikipedia On This Day -> events.csv
python build_cache.py    # sky_cache.csv

## Tests
python -m pytest
Covers ephemeris accuracy, angle wraparound, matching math, date validation, dataset sanity, and citation grounding. CI runs them on every push (GitHub Actions).

## Process
See DECISIONS.md, AI_LOG.md, and SECURITY.md.

## Known limitations
- Event data comes from Wikipedia editors, so it skews toward wars, disasters, politics, and Western history.
- Similarity weights are my judgment, not validated.
- Readings depend on a third-party model and may be unavailable.
- Dates limited to 1900-2025 (ephemeris and data coverage).

## Credits
Event text from Wikipedia's On This Day (CC BY-SA 4.0). Planetary data: NASA JPL DE421 via skyfield.
