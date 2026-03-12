import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
from database import get_db, engine, Base
from models import Mission

app = FastAPI()

# Allow Streamlit to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Endpoints ──────────────────────────────────────────────

# 1. Get all missions (with optional filters)
@app.get("/missions")
def get_missions(
    company: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    rocket: Optional[str] = Query(None),
    mission: Optional[str] = Query(None),
    rocket_status: Optional[str] = Query(None),
    mission_status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    time: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Mission)

    if company:
        query = query.filter(Mission.company == company)
    if location:
        query = query.filter(Mission.location == location)
    if rocket:
        query = query.filter(Mission.rocket == rocket)
    if mission:
        query = query.filter(Mission.mission == mission)
    if rocket_status:
        query = query.filter(Mission.rocket_status == rocket_status)
    if mission_status:
        query = query.filter(Mission.mission_status == mission_status)
    if date_from:
        query = query.filter(Mission.date >= datetime.strptime(date_from, "%Y-%m-%d"))
    if date_to:
        query = query.filter(Mission.date <= datetime.strptime(date_to, "%Y-%m-%d"))
    if time:
        query = query.filter(Mission.time == time)
    if price_min is not None:
        query = query.filter(Mission.price >= price_min)
    if price_max is not None:
        query = query.filter(Mission.price <= price_max)

    results = query.all()

    return [
        {
            "Company": r.company,
            "Location": r.location,
            "Date": r.date.isoformat() if r.date else None,
            "Time": r.time,
            "Rocket": r.rocket,
            "Mission": r.mission,
            "RocketStatus": r.rocket_status,
            "Price": r.price,
            "MissionStatus": r.mission_status,
        }
        for r in results
    ]


# 2. Get summary stats
@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Mission).count()
    successful = db.query(Mission).filter(Mission.mission_status == "Success").count()
    failed = db.query(Mission).filter(Mission.mission_status == "Failure").count()
    partial = db.query(Mission).filter(Mission.mission_status == "Partial Failure").count()
    prelaunch = db.query(Mission).filter(Mission.mission_status == "Prelaunch Failure").count()
    success_rate = round(successful / total * 100, 2) if total > 0 else 0

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "partial_failure": partial,
        "prelaunch_failure": prelaunch,
        "success_rate": success_rate
    }


# 3. Get filter options (for dropdowns)
@app.get("/options")
def get_options(db: Session = Depends(get_db)):
    def distinct(col):
        return sorted([
            r[0] for r in db.query(col).distinct().all()
            if r[0] is not None
        ])

    return {
        "companies": distinct(Mission.company),
        "locations": distinct(Mission.location),
        "rockets": distinct(Mission.rocket),
        "missions": distinct(Mission.mission),
        "rocket_statuses": distinct(Mission.rocket_status),
        "mission_statuses": distinct(Mission.mission_status),
    }


# 4. Get price range
@app.get("/price-range")
def get_price_range(db: Session = Depends(get_db)):
    result = db.query(
        func.min(Mission.price),
        func.max(Mission.price)
    ).filter(Mission.price.isnot(None)).first()

    return {
        "min": float(result[0]) if result[0] is not None else 0.0,
        "max": float(result[1]) if result[1] is not None else 0.0
    }