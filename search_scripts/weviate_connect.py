import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.init import Auth

# Import Google authentication libraries
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

# Load environment variables from .env file
# This ensures environment variables are available when this module is imported
load_dotenv()

# --- Google Vertex AI Authentication Setup ---

def get_google_credentials() -> Credentials:
    """
    Loads Google service account credentials and refreshes the access token.
    This function expects the GOOGLE_APPLICATION_CREDENTIALS environment variable
    to be set to the path of your service account JSON key file.
    """
    service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not service_account_path:
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS environment variable not set. "
            "Please set it to the path of your Google service account JSON key file."
        )

    # Initialize credentials from the service account file
    credentials = Credentials.from_service_account_file(
        service_account_path,
        scopes=[
            "https://www.googleapis.com/auth/generative-language",
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    )
    
    # Refresh the token. This makes an API call to Google to get a new access token
    # if the current one is expired or close to expiring.
    request = Request()
    credentials.refresh(request)
    return credentials

def re_instantiate_weaviate_client() -> weaviate.WeaviateClient:
    """
    Re-instantiates the Weaviate client with a fresh Vertex AI access token.
    This function should be called periodically in long-running applications
    to ensure the Vertex AI token remains valid. For a single-run script,
    calling it once at the start is sufficient.
    """
    # Retrieve Weaviate URL and API key from environment variables
    weaviate_url = os.environ["WEAVIATE_URL"]
    weaviate_api_key = os.environ["WEAVIATE_API_KEY"]

    # Get the refreshed Google credentials and extract the access token
    credentials = get_google_credentials()
    vertex_ai_token = credentials.token

    # Set the X-Goog-Vertex-Api-Key header with the dynamically obtained token
    headers = {
        "X-Goog-Vertex-Api-Key": vertex_ai_token,
    }

    # Connect to Weaviate Cloud with the updated headers
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(weaviate_api_key),
        headers=headers
    )
    return client

# Instantiate the Weaviate client directly when this module is imported
weaviate_client = re_instantiate_weaviate_client()

