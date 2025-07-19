import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.generate import GenerativeConfig

from weviate_connect import weaviate_client


load_dotenv()

google_cloud_project_id = os.environ.get("GOOGLE_PROJECT_ID")

gemini_api_key = os.environ.get("GEMINI_API_KEY")

if not google_cloud_project_id:
    raise ValueError(
        "GOOGLE_PROJECT_ID environment variable not set. "
        "Please set it to your Google Cloud Project ID in your .env file."
    )

if not gemini_api_key:
    print("WARNING: GEMINI_API_KEY environment variable not set. "
          "Consolidated summary will not be available. Please set it in your .env file.")

assert weaviate_client.is_ready(), "Weaviate connection failed."

collections_to_search = ["FoodNutrition", "FoodNutrition2", "FoodNutrition3", "FoodNutrition4"]

query_text = input("Enter your search query: ").strip()

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
        
        #all_summaries.append(f"Summary from {collection_name}: {summary}") In Progress

    except weaviate.exceptions.WeaviateQueryError as e:
        error_message = f"Error accessing collection '{collection_name}': {e}"
        print(error_message)
        #all_summaries.append(f"Summary from {collection_name}: {error_message}")
    except Exception as e:
        error_message = f"An unexpected error occurred for collection '{collection_name}': {e}"
        print(error_message)
        #all_summaries.append(f"Summary from {collection_name}: {error_message}") 

