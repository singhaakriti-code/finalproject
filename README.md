# HardwareRisk

Repository: https://github.com/singhaakriti-code/finalproject

HardwareRisk is a local AI-agent-style diligence app for fictional hardware startups. It ingests a data room, checks evidence and contradictions, and produces a scored risk memo. The data rooms are synthetic; this is decision support, not investment advice.

## Quick start from a fresh clone

The course environment places the real `.env` one directory above the cloned repository. HardwareRisk checks both locations and never requires the real key to be committed.

1. Copy `.env.example` to `.env` (or place `.env` one folder above the repo) and add a course `PORTKEY_API_KEY` or `OPENAI_API_KEY`.
2. Create a Python 3.11+ virtual environment: `python3 -m venv .venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`.
4. Start the app: `streamlit run app.py`.
5. Choose a startup and click **Run risk analysis**.

If using the course key, the app uses `gpt-6-luna` through Portkey. With a personal OpenAI key, set `OPENAI_MODEL` (default `gpt-4o-mini`). If no key is available, the UI reports a clear configuration error.

## Verification and evaluation

- Tests: `pytest -q`
- Live evaluation: `python eval/run_eval.py --mode optimized` or `python eval/run_eval.py --mode baseline`
- Rebuild all measured submission artifacts: `python scripts/run_all.py`
- Submission files: `dist/report.html` and `dist/slides.html`

The included sample data rooms are synthetic. The app is decision support, not investment advice. Never commit `.env`, API keys, `.venv`, or runtime logs.

The app uses local retrieval, validated citations, controlled taxonomy codes, and deterministic scoring. Synthetic data rooms are generated at startup under `data/dataRooms/`.

