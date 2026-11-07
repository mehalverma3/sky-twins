# SPEC: Sky Twins (working name)

**One-liner:** Pick any date from 1900 to 2025. Sky Twins computes the planetary configuration that day, finds the historical dates whose skies looked most similar, and writes a reading grounded only in what actually happened on those dates.

## Problem and User
People curious about astrology get generic horoscopes with no evidence behind them. This tool shows the *reasoning*: here are the days in history with the closest sky, and here’s what happened on them. It’s built for astrology-curious people who want a “why” and for anyone who enjoys the intersection of data and symbolism.

## Honest Framing (Shown in the App and Demo)
This is an *analog-day explorer*, not a scientific predictor. Astrology has no demonstrated predictive validity, and the event set is small and curated. The reading is interpretation, clearly labeled as such.

## Three Must-Haves
1. **Sky engine:** For any date, compute the 10 main planets’ positions and the major aspects (conjunction, sextile, square, trine, opposition) with orbs.
2. **Analog matching:** Rank historical events by sky similarity to the chosen date and return the top 5.
3. **Grounded reading:** An LLM writes a short reading using *only* the matched events, citing each one. No invented history.

## Not Building
Birth charts, houses, rising signs, minor aspects, user accounts, dates before 1900 or after 2025, a full historical database, and any claim of predictive accuracy.

## Architecture
* **Python + Streamlit** for the UI.
* **skyfield** with the JPL DE421 ephemeris (covers 1900–2050) for planet positions.
* **Event data:** A curated CSV of about 300–800 events (date, title, description, category), hand-checked.
* **Similarity score:** For each pair of planets, compare angular separation on the target date and the candidate date, then take a weighted average of the differences. Fast-moving planets (Moon, Mercury, Venus) get lower weight so slow-planet years don’t dominate.
* **LLM:** Anthropic API. The prompt contains only the retrieved events and instructs the model to cite them and add nothing else.

## Testing
* Sun’s ecliptic longitude on 2000-01-01 is about 280.4°.
* A date matched against itself scores a perfect 1.0.
* Angle math handles wraparound at 360°.
* Every event cited in a reading must appear in the retrieved list (automated check).
* Empty and invalid date inputs fail gracefully.

## Security
API key in an environment variable or Streamlit secrets and never committed, `.gitignore` set up before the first push, GitHub secret scanning on, date input validated, and the LLM prompt built from retrieved data only.

## Delivery
GitHub Actions runs `pytest` on every push, and the app is deployed on Streamlit Community Cloud.

## Known Limitations (for the Demo)
Small event set with selection bias toward famous events, similarity weights are my judgment rather than validated, matches don’t imply causation, and astrology isn’t predictive.

## Process (the Reusable Part)
A `DECISIONS.md` log (one line per choice, with the reason) and an `AI_LOG.md` noting where AI output was wrong and how I caught it. Both feed the demo.

## Schedule (ET)
| Time | Goal |
| --- | --- |
| 10:20–10:50 | Repo, `.gitignore`, README stub, `SPEC.md`, API key, install libraries |
| 10:50–11:50 | Sky engine plus first tests |
| 11:50–12:30 | Minimal Streamlit page showing transits, *deployed (Checkpoint 1)* |
| 12:30–1:30 | Event dataset |
| 1:30–2:30 | Matching *(Checkpoint 2)* |
| 2:30–3:15 | LLM reading *(Checkpoint 3)* |
| 3:15–3:45 | CI workflow, security pass, error handling |
| 3:45–4:15 | README, limitations, logs cleanup |
| 4:15–4:45 | Record demo (3 min max), fill in Devpost, *submit by 4:45* |
