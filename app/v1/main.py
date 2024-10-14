import os
import asyncio

from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.v1.database import get_db, AsyncSessionLocal
from app.v1.services import (
    fetch_weather_data,
    save_weather_data,
    export_weather_data_to_excel,
    get_ten_last_records,
)
from app.v1.schemas import WeatherDataSchema

app = FastAPI()


@app.get("/weather/", response_model=WeatherDataSchema)
async def get_weather_data(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
    Получить данные о погоде от API и записать в базу данных
    """
    weather_data = await fetch_weather_data()
    if weather_data:
        background_tasks.add_task(save_weather_data, db, weather_data)
        return weather_data
    return {"error": "Ошибка при запросе данных погоды"}


@app.get("/weather/top/", response_model=List[WeatherDataSchema])
async def get_weather_data(db: AsyncSession = Depends(get_db)):
    """
    Получить 10 последних данных о погоде от API
    """
    return await get_ten_last_records(db)


@app.post("/export/")
async def export_data(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
    Экспорт данных в фоновом режиме
    """
    file_name = f"weather_data_{datetime.now().strftime("%d-%m-%Y %H-%M-%S")}.xlsx"
    file_path = os.path.join(os.getcwd(), "public" , file_name)

    background_tasks.add_task(export_weather_data_to_excel, db, file_path)

    return {"message": f"Export started. File will be saved as {file_name}"}


async def scheduled_weather_updates():
    while True:
        weather_data = await fetch_weather_data()
        if weather_data:
            async with AsyncSessionLocal() as db:
                await save_weather_data(db, weather_data)
        await asyncio.sleep(180)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(scheduled_weather_updates())
