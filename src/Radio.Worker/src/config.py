import os
from google.cloud import firestore
from google.cloud import storage
import google.genai as genai

# Load and validate configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
TRACK_COUNT = int(os.getenv("TRACK_COUNT", "40"))
MUSIC_MODEL = os.getenv("MUSIC_MODEL", "lyria-3-pro-preview")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-3.1-flash-image")

if not PROJECT_ID:
    raise ValueError("GCP_PROJECT_ID environment variable is not set.")
if not BUCKET_NAME:
    raise ValueError("GCS_BUCKET_NAME environment variable is not set.")

print(f"[Config] Active GCP Project: {PROJECT_ID}")
print(f"[Config] Target GCS Bucket: {BUCKET_NAME}")
print(f"[Config] Daily track generation target: {TRACK_COUNT}")

# Initialize and expose global GCP Clients
db = firestore.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)

def get_ai_client():
    """
    Returns a fresh Google GenAI Client in Vertex AI mode keylessly (ADC).
    Instantiating a new client ensures OAuth2 credentials/access tokens are
    refreshed from the environment/metadata server rather than being cached statically.
    """
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global"
    )
