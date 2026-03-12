# Interactive Space Mission Dashboard

An interactive full-stack dashboard to visualize and analyze historical space mission data from 1957 onwards.

**Author:** Crystal LaMar

---

## Overview

This dashboard allows users to explore space mission data through interactive filters, summary statistics, and visualizations. It is built with a **FastAPI backend**, **SQLite database**, and **Streamlit frontend** — following a standard client-server architecture where the frontend and backend are fully separated.

---

## Technology Stack

**Frontend**
- Python
- Streamlit (dashboard framework)
- Pandas (data manipulation)
- Plotly (interactive visualizations)

**Backend**
- FastAPI (REST API framework)
- SQLAlchemy (database ORM)
- SQLite (database)
- Uvicorn (ASGI server)

---

## Project Structure

```
Interactive-Space-Mission-Dashboard/
├── backend/
│   ├── database.py          # Database connection and session setup
│   ├── models.py            # SQLAlchemy table definitions
│   ├── seed.py              # One-time script to load CSV into database
│   ├── main.py              # FastAPI server and API endpoints
│   └── space_missions.csv   # Source data (used once for seeding)
├── frontend/
│   └── app.py               # Streamlit frontend
├── requirements.txt
└── README.md
```

---

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/crystallamar/Interactive-Space-Mission-Dashboard.git
cd Interactive-Space-Mission-Dashboard
```

### 2. Install dependencies

```bash
pip install streamlit pandas plotly fastapi uvicorn sqlalchemy
```

### 3. Seed the database

This step only needs to be run once. It reads the CSV and loads all mission data into a SQLite database.

```bash
cd backend
python seed.py
```

You should see: `Seeded XXXX missions successfully.`

### 4. Start the backend server

In one terminal, from inside the `backend` folder:

```bash
uvicorn main:app --reload
```

The API will be running at `http://localhost:8000`.

### 5. Start the frontend

In a second terminal, from inside the `frontend` folder:

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

---

## Architecture Overview

This project follows a standard three-layer client-server architecture:

```
Streamlit (frontend)
        ↓  HTTP requests
FastAPI (backend / REST API)
        ↓  SQL queries
SQLite (database)
```

**Why this architecture?**

Previously, the app read directly from a CSV file — meaning all data logic, filtering, and UI were tangled together in a single file. Separating into frontend and backend means:

- Each layer has a single, clear responsibility
- The backend API could serve any frontend (a mobile app, a React app, etc.) without any changes
- The database can be swapped (e.g. to PostgreSQL for production) by changing a single line in `database.py`
- Business logic lives in one place rather than scattered across UI code

---

## API Endpoints

The FastAPI backend exposes the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/missions` | Returns all missions. Accepts optional query parameters for filtering. |
| GET | `/stats` | Returns summary statistics (total, successful, failed, success rate, etc.) |
| GET | `/options` | Returns unique values for all dropdown filters. |
| GET | `/price-range` | Returns the min and max mission price for the price slider. |

**Example filtered request:**
```
GET /missions?company=NASA&mission_status=Success&date_from=1960-01-01&date_to=1970-12-31
```

You can explore all endpoints interactively at `http://localhost:8000/docs` (FastAPI's built-in documentation UI).

---

## Features

### Filters
Users can filter mission data by:
- Company
- Location
- Date Range
- Time
- Rocket
- Mission Name
- Rocket Status
- Price Range
- Mission Status

### Summary Statistics
- Total Missions
- Successful Missions
- Failed Missions
- Partial Failures
- Prelaunch Failures
- Overall Success Rate

### Visualizations
1. **Success Rate by Decade** — a bar chart showing how mission success rates have changed over time, grouped by decade
2. **Top 10 Companies by Mission Count** — a horizontal bar chart comparing relative activity levels across organizations
3. **Most Popular Launch Locations** — a pie chart showing the top 10 launch sites by number of missions

---

## Design Decisions

**SQLite over PostgreSQL**
SQLite was chosen because it requires no separate installation or server process — it runs as a single file. For a dataset of this size (~4,600 rows), it performs well. A production deployment would swap this for PostgreSQL by changing one line in `database.py`.

**SQLAlchemy ORM**
SQLAlchemy allows database queries to be written in Python rather than raw SQL. This makes the code more readable and makes it straightforward to swap the underlying database engine if needed.

**Indexed columns**
Columns that are frequently filtered (`company`, `location`, `rocket`, `mission`, `mission_status`) are indexed in the database. This means SQLite pre-sorts these columns so lookups are faster, which becomes increasingly important as the dataset grows.

**`@st.cache_data` for dropdown options**
The `/options` and `/price-range` endpoints are called once on startup and cached by Streamlit. Since these values don't change between user interactions, caching avoids unnecessary API calls on every filter change.

**Filtering at the database level**
Rather than fetching all rows and filtering in Python (as the original CSV approach did), filters are applied directly in the SQL query. This means only the relevant rows are ever sent over the network, which is more efficient as the dataset scales.

---

## Dataset

`space_missions.csv` contains the following columns:

| Column | Description |
|--------|-------------|
| Company | Organization that conducted the mission |
| Location | Launch site location |
| Date | Launch date (YYYY-MM-DD format) |
| Time | Launch time (HH:MM:SS format) |
| Rocket | Rocket model used |
| Mission | Mission name |
| RocketStatus | Status of the rocket (Active/Retired) |
| Price | Mission cost in millions USD (may be null) |
| MissionStatus | Outcome (Success, Failure, Partial Failure, Prelaunch Failure) |

---

## Available Functions

The following utility functions are available in `app.py`:

| Function | Description |
|----------|-------------|
| `getMissionCountByCompany(companyName)` | Returns total mission count for a given company |
| `getSuccessRate(companyName)` | Returns success rate percentage for a given company |
| `getMissionsByDateRange(startDate, endDate)` | Returns list of mission names within a date range |
| `getTopCompaniesByMissionCount(n)` | Returns top N companies by mission count |
| `getMissionStatusCount()` | Returns count of each mission status type |
| `getMissionsByYear(year)` | Returns number of missions in a given year |
| `getMostUsedRocket()` | Returns the most frequently used rocket |
| `getAverageMissionsPerYear(startYear, endYear)` | Returns average missions per year within a range |

---

## Testing

With `pytest` installed, run:

```bash
pytest test_functions.py -v
```

---

## Future Improvements

**1. Live data via NASA's public API**
The current dataset is static — it was accurate when the CSV was created but never updates. A future improvement would be to integrate NASA's public APIs to automatically fetch new mission data on a schedule. This would involve building an ETL pipeline (Extract, Transform, Load) that periodically pulls data from NASA, transforms it into the existing schema, and loads it into the database — keeping the dashboard current without any manual updates.

**2. User authentication and saved filters**
Currently all users see the same default view. Adding authentication (user accounts, login, JWT tokens) would allow users to save custom filter presets — for example, saving a view for "NASA missions in the 1960s" so they don't have to re-enter filters each session. This would involve adding a `users` table to the database and a login flow to the frontend.

**3. Caching with Redis**
For the current dataset size, querying SQLite on every filter change is fast enough. However, at much larger scale (millions of rows, many concurrent users), the database would become a bottleneck. Adding Redis as a caching layer would mean FastAPI checks Redis first before hitting the database — if the same query was recently made, it returns the cached result instantly. This pattern is standard in production APIs and would significantly improve performance under load.