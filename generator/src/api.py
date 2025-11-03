import json
import logging
from datetime import datetime
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from __init__ import SCHEDULE_FILENAME
from models import GeneticConfigModel, APIMessageModel, APIResponseModel
from main import (
    set_population_size, set_generations, set_elitism_rate, 
    set_survival_rate, get_current_config, create_schedule_task, load_schedule_from_json, schedule_to_dict
)


app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/create_schedule", response_model=APIMessageModel)
async def get_schedule(background_tasks: BackgroundTasks):
    background_tasks.add_task(create_schedule_task)
    return {"message": "Расписание создается."}


@app.get("/visualize_schedule", response_model=APIResponseModel)
async def visualize_schedule_route():
    try:
        with open(SCHEDULE_FILENAME, encoding="utf-8") as f:
            raw_data = json.load(f)
        
        if not raw_data.get("schedule"):
            return JSONResponse(
                content={"message": "Не удалось загрузить расписание. Сначала вызовите /create_schedule"},
                status_code=404
            )
        
        return APIResponseModel(
            schedule={
                "metadata": raw_data.get("metadata", {}),
                "schedule": raw_data.get("schedule", {})
            }
        )

    except FileNotFoundError:
        return JSONResponse(
            content={"message": "Файл расписания не найден. Сначала вызовите /create_schedule"},
            status_code=404
        )
    except Exception as e:
        logger.error(f"Ошибка при визуализации расписания: {str(e)}")
        return JSONResponse(
            content={"message": f"Внутренняя ошибка сервера: {str(e)}"},
            status_code=500
        )
@app.post("/config/genetic", response_model=APIMessageModel)
async def update_genetic_config(config: GeneticConfigModel):
    try:
        if config.population_size is not None:
            set_population_size(config.population_size)
        if config.generations is not None:
            set_generations(config.generations)
        if config.elitism_rate is not None:
            set_elitism_rate(config.elitism_rate)
        if config.survival_rate is not None:
            set_survival_rate(config.survival_rate)
        
        return {"message": "Конфигурация генетического алгоритма успешно обновлена"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при обновлении конфигурации: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/config/genetic", response_model=GeneticConfigModel)
async def get_genetic_config():
    try:
        config = get_current_config()
        return GeneticConfigModel(**config)
    except Exception as e:
        logger.error(f"Ошибка при получении конфигурации: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")