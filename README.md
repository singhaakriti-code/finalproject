# HardwareRisk

HardwareRisk is a local AI-agent-style diligence app for fictional hardware startups. It ingests a data room, checks evidence and contradictions, and produces a scored risk memo. The data rooms are synthetic; this is decision support, not investment advice.

1. Copy `.env.example` to `.env` (or place `.env` one folder above the repo) and add a course `PORTKEY_API_KEY` or `OPENAI_API_KEY`.
2. Create a Python 3.11 virtual environment and run `pip install -r requirements.txt`.
3. Run `streamlit run app.py`, choose a startup, and click **Run risk analysis**.
4. Run tests with `pytest -q`.

The app uses local retrieval, validated citations, controlled taxonomy codes, and deterministic scoring. Synthetic data rooms are generated at startup under `data/dataRooms/`.

