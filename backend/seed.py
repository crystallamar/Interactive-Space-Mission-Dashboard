import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from database import engine, SessionLocal, Base
from models import Mission

def seed():
    # Create the table if it doesn't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if already seeded
    existing = db.query(Mission).first()
    if existing:
        print("Database already seeded. Skipping.")
        db.close()
        return

    # Read the CSV
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "space_missions.csv"))
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    # Load each row into the database
    missions = []
    for _, row in df.iterrows():
        mission = Mission(
            company=row["Company"] if pd.notna(row["Company"]) else None,
            location=row["Location"] if pd.notna(row["Location"]) else None,
            date=row["Date"] if pd.notna(row["Date"]) else None,
            time=row["Time"] if pd.notna(row["Time"]) else None,
            rocket=row["Rocket"] if pd.notna(row["Rocket"]) else None,
            mission=row["Mission"] if pd.notna(row["Mission"]) else None,
            rocket_status=row["RocketStatus"] if pd.notna(row["RocketStatus"]) else None,
            price=row["Price"] if pd.notna(row["Price"]) else None,
            mission_status=row["MissionStatus"] if pd.notna(row["MissionStatus"]) else None,
        )
        missions.append(mission)

    db.add_all(missions)
    db.commit()
    db.close()
    print(f"Seeded {len(missions)} missions successfully.")

if __name__ == "__main__":
    seed()