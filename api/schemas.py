from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ---------------- Vehicles ----------------
class VehicleBase(BaseModel):
    name: str
    plate_number: str
    purpose: Optional[str] = None
    profile_picture: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    date_registered: datetime

    class Config:
        from_attributes = True


# ---------------- Logs ----------------
class LogBase(BaseModel):
    plate_number: str
    status: Optional[str] = "unregistered"

class LogCreate(LogBase):
    vehicle_id: Optional[int] = None

class Log(LogBase):
    id: int
    timestamp: datetime
    vehicle_id: Optional[int] = None

    class Config:
        from_attributes = True
