import asyncio
import os
from supabase import create_client
from pathlib import Path

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def run_tests():
    # Simple test: upload a mock image and check insertion
    from ..pipeline import identify_image, save_observation
    # Use a dummy path (no real file needed for placeholder)
    dummy_path = Path("/tmp/dummy.jpg")
    dummy_path.touch()
    result = await identify_image(dummy_path)
    observation = {
        "species": result["species"],
        "category": None,
        "method": "image",
        "media_url": "dummy.jpg",
        "date_time": None,
        "station_id": "SECCHIA-01",
        "confidence": result["confidence"],
        "verification_status": "pending",
        "source": result["source"],
        "source_update_date": result.get("source_update_date"),
        "habitat_zone": None,
        "coordinates": None,
        "quality": None,
    }
    save_res = await save_observation(observation)
    print("Test completed, insert response:", save_res)

if __name__ == "__main__":
    asyncio.run(run_tests())
