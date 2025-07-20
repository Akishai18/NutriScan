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

collections_to_search = ["FoodNutrition", "FoodNutrition2", "FoodNutrition3", "FoodNutrition4"] #Define all the collections to search through

def search_collections(query_text):
    summaries = []
    for collection_name in collections_to_search:
        print(f"\n--- Searching in collection: {collection_name} ---")
        try:
            collection = weaviate_client.collections.get(collection_name)
            response = collection.generate.near_text(
                query=query_text,
                limit=5,
                grouped_task=f"Based ONLY on the provided food nutrition data, answer the query: '{query_text}'. Be concise and directly provide the requested information. If the exact information is not found, state 'I cannot find that specific information in this particular database.' Do NOT ask follow-up questions.",
                generative_provider=GenerativeConfig.google()
            )
            summary = response.generated
            print(f"\nGenerated summary from {collection_name}:\n{summary}")
            summaries.append({
                'collection': collection_name,
                'summary': summary
            })
        except weaviate.exceptions.WeaviateQueryError as e:
            error_message = f"Error accessing collection '{collection_name}': {e}"
            print(error_message)
            summaries.append({
                'collection': collection_name,
                'summary': error_message
            })
        except Exception as e:
            error_message = f"An unexpected error occurred for collection '{collection_name}': {e}"
            print(error_message)
            summaries.append({
                'collection': collection_name,
                'summary': error_message
            })
    return summaries

# --- Flask API for search ---
app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({'status': 'error', 'message': 'No query provided'}), 400
    print(f"[search] Received query: {query}")
    summaries = search_collections(query)
    print(f"[search] Summaries: {summaries}")
    return jsonify({'status': 'success', 'summaries': summaries})

if __name__ == '__main__':
    print("Search API starting on http://localhost:5002")
    app.run(debug=True, host='0.0.0.0', port=5002)