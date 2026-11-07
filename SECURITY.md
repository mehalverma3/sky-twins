# Security

- **Secrets:** API key lives only in environment variables / Streamlit Secrets. Never committed; `.gitignore` covers `.env` and `.streamlit/secrets.toml`. Git history checked for key patterns.
- **Input validation:** dates are parsed strictly (`parse_date`) and restricted to 1900-2025; invalid input stops the page with a clear error (tested in `test_inputs.py`).
- **Prompt integrity:** the LLM prompt is built only from retrieved dataset rows, never from free-text user input.
- **Output grounding:** every citation in a generated reading must match an event we retrieved; otherwise the reading is discarded (tested in `test_reading.py`).
- **Cost abuse:** readings run only on button click; API errors fail gracefully without exposing details.
- **Dependencies:** pinned in `requirements.txt`; secret scanning enabled on the repo.
- **Known gaps:** no rate limiting on the public app; shared hackathon API key may be revoked after the event.