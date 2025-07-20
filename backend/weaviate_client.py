import weaviate
from weaviate.classes.init import Auth
import os
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_KEY = os.getenv("WEAVIATE_API_KEY") 

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=Auth.api_key(WEAVIATE_KEY),
)

# sample_food = 'banana'

def create_weaviate_client():
    return client

def get_nutrition_info(food_name: str):
    nutrition = client.collections.get("FoodNutrition")

    response = nutrition.query.near_text(query=food_name,limit=1,return_properties=["name", "calories", "carbohydrate", "fat", "protein"])

    if response.objects:
        result = response.objects[0].properties
        return dict(result)
    return None

# def close_database():
#     client.close()


# print(get_nutrition_info(sample_food))

# for obj in response.objects:
#     print(json.dumps(obj.properties, indent=2))

    

