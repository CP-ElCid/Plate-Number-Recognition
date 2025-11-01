from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from api.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    plate_number = Column(String, unique=True, index=True, nullable=False)
    purpose = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    date_registered = Column(DateTime, default=datetime.utcnow)

    # Relationship to logs
    logs = relationship("Log", back_populates="vehicle")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="unregistered")
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    # Relationship to vehicle
    vehicle = relationship("Vehicle", back_populates="logs")
