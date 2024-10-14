from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime

Base = declarative_base()

class WeatherData(Base):
    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    temperature_2m = Column(Float) # Температура в цельсиях
    wind_speed_10m = Column(Float) # скорость ветра в км/ч
    wind_direction_10m = Column(String) # Направление ветра
    pressure_msl = Column(Float) # Давление в мм рт. ст.
    precipitation = Column(Float) # Количество осадков в мм




