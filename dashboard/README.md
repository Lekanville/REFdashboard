# Dashboard App

This is the Streamlit dashboard for the REFdashboard project. It presents the processed research-output dataset, UoA comparisons, trend plots, and prediction outputs for review and analysis.

## Overview

The dashboard is the user-facing application used to inspect research data and predictions by Unit of Assessment (UoA). It authenticates users, filters the dataset, and renders analytical charts using Plotly and Streamlit.

## Main entry points

- `dashboard/app.py` starts the Streamlit application and handles login flow
- `dashboard/code/dashboard.py` renders the dashboard content
- `dashboard/code/authentication.py` contains authentication logic
- `dashboard/code/tools/tools.py` contains UoA filtering helpers

## User workflow

1. A user signs in from the Streamlit sidebar.
2. They select a permitted UoA tab.
3. The dataset is filtered by UoA and either:
   - embedding distance less than 0.7, or
   - minimum embedding distance
4. The dashboard displays:
   - publications over time
   - distance vs prediction plots
   - embeddings comparisons
   - SJR and Altmetric trends
   - top research methods by class
   - prediction export options

## Authentication

The app uses `streamlit_authenticator` and reads configuration values from the project config file located under `dashboard/config.yaml`.

## Running the dashboard

From the project root:

```bash
docker compose up app --build
```

or locally:

```bash
streamlit run app.py
```

with the working directory set to `dashboard/`.

## Notes

- The dashboard depends on the backend data and the MongoDB-backed dataset being available.
- UoA selection is now mapped explicitly to avoid incorrect data assignment by index position.
- Dashboard access is gated by authentication and user permissions from the config file.
