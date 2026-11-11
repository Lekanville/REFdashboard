# REFdashboard

REFdashboard is a full-stack project for collecting research-output metadata, building REF-style predictions, and visualising them in a Streamlit dashboard.

## Project structure

- `backend/` — FastAPI service for data collection, uploads, downloads, and startup jobs
- `dashboard/` — Streamlit application for analysis and visualisation
- `DB/` — MongoDB data exports and reference collections
- `docker-compose.yml` — local deployment for MongoDB, Mongo Express, the API, and the dashboard

## Required environment variables

Create a local environment file (for example `env` or `.env`) and populate it with the required values before running the app. The project expects variables such as:

- `API_KEY`
- `MONGO_INITDB_ROOT_USERNAME`
- `MONGO_INITDB_ROOT_PASSWORD`
- `PURE_API_KEY`
- `SCOPUS_API_KEY`
- `DB_NAME`
- `ME_CONFIG_BASICAUTH_USERNAME`
- `ME_CONFIG_BASICAUTH_PASSWORD`
- any REF collection names used by the app

Do not commit real secrets. Keep them in a local environment file and ensure the file is excluded from version control.

## Local setup

### 1) Create a Python environment

python -m venv .venv
source .venv/bin/activate

### 2) Install dependencies

pip install -r backend/requirements.txt -r dashboard/requirements.txt

### 3) Run the tests

pytest backend/tests dashboard/tests -q

## Run the app locally with Docker

From the project root:

docker compose up --build

Then open:

- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Mongo Express: http://localhost:8081
- Dashboard: http://localhost:8501

## Expected application flow

1. MongoDB starts and stores REF data collections.
2. The FastAPI backend loads configuration and exposes data collection and upload endpoints.
3. The dashboard reads the processed dataset and presents REF UoA views, metadata, publication trends, and prediction plots.
4. The app can download prediction data and upload new prediction files through the API.

## Notes for handoff

- The API is protected by a server-side API key and validates incoming request headers.
- Startup tasks are deduplicated to reduce repeated scheduler registration.
- UoA selections are resolved explicitly to avoid incorrect data mapping by index position.
- The Compose file should be used for local deployment and is the easiest reproducible setup for reviewers.

