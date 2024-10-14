import aiohttp
import pandas as pd

from datetime import datetime
from app.v1.models import WeatherData
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
    "latitude": 55.7522,
    "longitude": 37.6175,
    "current": "temperature_2m,wind_speed_10m,wind_direction_10m,pressure_msl,precipitation",
}


async def fetch_weather_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(WEATHER_API_URL, params=PARAMS) as response:
            if response.status == 200:
                data = await response.json()
                return parse_weather_data(data)
            else:
                print(f"Ошибка запроса: {response.status}")
                return None


# Конвертация направления ветра
def get_wind_direction(degree) -> str:
    directions: list[str] = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    index = int((degree + 22.5) / 45) % 8
    return directions[index]


def parse_weather_data(data):
    current_weather = data["current"]
    print(current_weather)
    return {
        "timestamp": datetime.now(),
        "temperature_2m": current_weather["temperature_2m"],
        "wind_speed_10m": current_weather["wind_speed_10m"],
        "wind_direction_10m": get_wind_direction(current_weather["wind_direction_10m"]),
        "pressure_msl": round(current_weather["pressure_msl"] * 0.75006375541921, 2),
        "precipitation": current_weather["precipitation"],
    }


# Сохранение данных в базу данных
async def save_weather_data(db: AsyncSession, weather_data: dict):
    weather_entry = WeatherData(**weather_data)
    db.add(weather_entry)
    await db.commit()
    return weather_entry


# Получение 10 последних записей из базы данных
async def get_weather_data(db: AsyncSession):
    stmt = text(
        """
        SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 10
        """
    )
    query = await db.execute(stmt)
    results = query.fetchall()
    return results


# Получить 10 последних записей о погоде
async def get_ten_last_records(db: AsyncSession):
    stmt = text("SELECT * FROM weather_data ORDER BY id DESC LIMIT 10")
    result = await db.execute(stmt)
    weather_data = result.fetchall()
    return weather_data


# Экспорт в xlsx
def export_to_excel(data, file_path):
    df = pd.DataFrame(
        data,
        columns=[
            "id",
            "timestamp",
            "temperature_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "pressure_msl",
            "precipitation",
        ],
    )

    df.to_excel(file_path, index=False)


async def export_weather_data_to_excel(db: AsyncSession, file_path):
    weather_data = await get_weather_data(db)
    export_to_excel(weather_data, file_path)
