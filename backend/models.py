from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base

class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    date = Column(DateTime)
    time = Column(String)
    rocket = Column(String, index=True)
    mission = Column(String, index=True)
    rocket_status = Column(String)
    price = Column(Float, nullable=True)
    mission_status = Column(String, index=True)

