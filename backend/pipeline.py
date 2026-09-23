import os
import httpx
from supabase import create_client
from pathlib import Path

# Load environment variables (FastAPI can use python-dotenv in real setup)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
INATURALIST_TOKEN = os.getenv("INATURALIST_TOKEN")
BIRDNET_API = os.getenv("BIRDNET_API")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def identify_image(file_path: Path):
    # Placeholder: call iNaturalist API
    # Real implementation would POST multipart/form-data with image
    # Here we return a mock result
    return {
        "species": "Mocked species",
        "confidence": 0.85,
        "source": "iNaturalist",
        "source_update_date": None,
    }

async def identify_audio(file_path: Path):
    # Placeholder: call BirdNET API
    return {
        "species": "Mocked bird",
        "confidence": 0.78,
        "source": "BirdNET",
        "source_update_date": None,
    }

async def save_observation(data: dict):
    # Insert into Supabase table "osservazioni"
    response = supabase.table("osservazioni").insert(data).execute()
    return response
