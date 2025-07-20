from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from weaviate_client import get_nutrition_info, create_weaviate_client
import json
import os

app = FastAPI()

sample_food = 'banana'

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = create_weaviate_client()
    app.state.weaviate_client = client

    yield

    client.close()

@app.get("/")
def root():
    return {"Hello":"World"}

@app.get("/food")
def get_nutrition():

    try:
        with open("../food_logs.json", "r") as f:
            data = json.load(f)

            final_output = []

            for info in data:
                food = info["food"]
                result = get_nutrition_info(food)
                final_output.append(result)


        return final_output
    except Exception as e:
        return {"error": str(e)}



    






