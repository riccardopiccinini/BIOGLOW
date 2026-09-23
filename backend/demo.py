import os
from supabase import create_client
import asyncio
import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Mock data for demo mode
MOCK_OBSERVATIONS = [
    {
        "species": "Mocked species A",
        "category": "bird",
        "method": "image",
        "media_url": "mock_a.jpg",
        "date_time": datetime.datetime.utcnow().isoformat(),
        "station_id": "SECCHIA-01",
        "confidence": 0.95,
        "verification_status": "confirmed",
        "source": "iNaturalist",
        "source_update_date": None,
        "habitat_zone": None,
        "coordinates": None,
        "quality": "high",
    },
    {
        "species": "Mocked bird B",
        "category": "bird",
        "method": "audio",
        "media_url": "mock_b.wav",
        "date_time": datetime.datetime.utcnow().isoformat(),
        "station_id": "SECCHIA-01",
        "confidence": 0.88,
        "verification_status": "pending",
        "source": "BirdNET",
        "source_update_date": None,
        "habitat_zone": None,
        "coordinates": None,
        "quality": "medium",
    },
]

def load_demo_data():
    # Insert mock observations (sync version)
    for obs in MOCK_OBSERVATIONS:
        supabase.table("osservazioni").insert(obs).execute()
    print("Demo data loaded.")

if __name__ == "__main__":
    load_demo_data()

