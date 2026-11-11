# Backend API

This service is the FastAPI backend for the REFdashboard project. It handles data collection, uploads, downloads, startup refresh jobs, and database interactions for the MongoDB instance.

## Overview

The backend exposes REST endpoints under the `/api` prefix and is intended to support the Streamlit dashboard and the data-processing workflow. It also contains scheduled startup tasks that fetch research output metadata and journal metadata from the upstream data source.

## Main entry point

- `backend/main.py` creates the FastAPI application
- `backend/apis/api_base.py` wires route modules into the app
- `backend/apis/v1/route_res_outputs.py` contains the active API routes and startup tasks

## Route summary

### Research output UUID endpoints

- `POST /api/research_uuids`
  - Fetches research output UUIDs for a given school UUID
  - Saves them to the database
  - Returns `1` on success

- `GET /api/research_outputs/{school_uuid}`
  - Fetches research output details for a school
  - Updates the associated detail-check state
  - Returns `1` on success

### Journal and author endpoints

- `GET /api/journal_details/`
  - Fetches journal feature data such as SJR and Altmetric information

- `GET /api/authors_details/`
  - Fetches author metadata for research outputs

### Download endpoints

- `POST /api/download_all_research_data/`
  - Downloads the full processed research data export
  - Requires `X-API-Key` header

- `POST /api/download_new_research_data/`
  - Downloads only newly updated research data
  - Requires `X-API-Key` header

### Upload endpoints

- `POST /api/upload_predictions/`
  - Uploads prediction CSV data
  - Parses and stores prediction results
  - Requires `X-API-Key` header

- `POST /api/upload_ref_embedding_pcas/`
  - Uploads REF embedding PCA data
  - Requires `X-API-Key` header

## Security

Sensitive endpoints are protected by `require_api_key()` in `backend/core/security.py`.

The function enforces:

- a server-side `API_KEY` must exist
- the client must send the correct `X-API-Key` header
- invalid or missing keys return `401 Unauthorized`
- missing server configuration returns `500 Internal Server Error`

## Startup automation

The backend registers startup jobs in `backend/apis/v1/route_res_outputs.py` using a deduplication guard.

These tasks are intended to refresh:

- research output UUIDs
- research output details
- journal details
- author details

They use the `repeat_every` pattern and are designed to re-run on a periodic schedule rather than only once at startup.

## Running the backend

From the project root:

```bash
docker compose up ref_api --build
```

or locally:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

with the working directory set to `backend/`.

## Notes

- The API is meant to be called by the dashboard or an admin user during data refresh/upload workflows.
- API keys are secret and should remain in a local environment file, not in the repository.
- The system assumes configured MongoDB values and the project environment file are present before startup.
