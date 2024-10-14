from pydantic import BaseModel
from datetime import datetime


class WeatherDataSchema(BaseModel):
    timestamp: datetime
    temperature_2m: float
    wind_speed_10m: float
    wind_direction_10m: str
    pressure_msl: float
    precipitation: float

    class Config:
        orm_mode = True
