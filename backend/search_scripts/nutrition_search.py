import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.generate import GenerativeConfig
from flask import Flask, request, jsonify
from flask_cors import CORS

from weviate_connect import weaviate_client

load_dotenv() #Load Env Keys

google_cloud_project_id = os.environ.get("GOOGLE_PROJECT_ID")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

if not google_cloud_project_id:
    raise ValueError(
        "GOOGLE_PROJECT_ID environment variable not set. "
    )

if not gemini_api_key:
    print("WARNING: GEMINI_API_KEY environment variable not set. ")

assert weaviate_client.is_ready(), "Weaviate connection failed."

collections_to_search = ["FoodNutrition"] #Define all the collections to search through

def get_nutrition_info(food_item):
    """
    Given a food_item string, search Weaviate and Gemini for nutrition info and return the summary string.
    """
    query_text = f"Provide nutritional info for {food_item}"
    summary = None
    for collection_name in collections_to_search:
        try:
            collection = weaviate_client.collections.get(collection_name)
            response = collection.generate.near_text(
                query=query_text,
                limit=5,
                grouped_task=f"Based ONLY on the provided food nutrition data, answer the query: '{query_text}'. Be concise and directly provide the requested information. If the exact information is not found, state 'I cannot find that specific information in this particular database.' Do NOT ask follow-up questions.",
                generative_provider=GenerativeConfig.google()
            )
            summary = response.generated
            if summary:
                break
        except weaviate.exceptions.WeaviateQueryError as e:
            print(f"Error accessing collection '{collection_name}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred for collection '{collection_name}': {e}")
    return summary or "No nutrition information found."

# --- Flask API for nutrition search ---
app = Flask(__name__)
CORS(app)

@app.route('/api/get-nutrition', methods=['POST'])
def api_get_nutrition():
    data = request.get_json()
    food_item = data.get('food_item')
    if not food_item:
        return jsonify({'status': 'error', 'message': 'No food_item provided'}), 400
    print(f"[nutrition_search] Received request for: {food_item}")
    nutrition_data = get_nutrition_info(food_item)
    print(f"[nutrition_search] Result: {nutrition_data}")
    return jsonify({'status': 'success', 'nutrition_info': nutrition_data})

if __name__ == '__main__':
    print("Nutrition Search API starting on http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)

