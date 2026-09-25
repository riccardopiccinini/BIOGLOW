import httpx
import uuid
import random
import asyncio
from pathlib import Path
from db import supabase
from config import config
from constants import (
    OBSERVATION_METHODS, 
    MOCK_SPECIES_IMAGES, 
    MOCK_SPECIES_AUDIO
)

try:
    from birdnetlib import BirdNETAnalyzer
    BIRDNET_AVAILABLE = True
except ImportError:
    BIRDNET_AVAILABLE = False

# Global analyzer instance
analyzer = None
if BIRDNET_AVAILABLE:
    try:
        analyzer = BirdNETAnalyzer()
    except Exception as e:
        print(f"BirdNET initialization error: {e}")
        BIRDNET_AVAILABLE = False

async def upload_to_storage(file_bytes: bytes, filename: str, station_id: str) -> str:
    ext = Path(filename).suffix
    file_id = str(uuid.uuid4())
    path = f"stations/{station_id}/{file_id}{ext}"

    if not config.SUPABASE_STORAGE_BUCKET:
        return f"https://via.placeholder.com/400x300/2d6a4f/ffffff?text={filename}"

    try:
        res = supabase.storage.from_(config.SUPABASE_STORAGE_BUCKET).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": "application/octet-stream"}
        )
        if not res:
            raise Exception("Failed to upload file to Supabase Storage")
        return supabase.storage.from_(config.SUPABASE_STORAGE_BUCKET).get_public_url(path)
    except Exception as e:
        print(f"Storage upload error (mock fallback): {e}")
        return f"https://via.placeholder.com/400x300/2d6a4f/ffffff?text={filename}"

async def identify_image(file_path: Path) -> dict:
    if not config.INATURALIST_TOKEN:
        mock = random.choice(MOCK_SPECIES_IMAGES).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        return mock

    try:
        with open(file_path, "rb") as f:
            file_data = f.read()

        async with httpx.AsyncClient() as client:
            files = {'image': (file_path.name, file_data)}
            headers = {"Authorization": f"Bearer {config.INATURALIST_TOKEN}"}
            resp = await client.post(
                "https://api.inaturalist.org/v1/computervision/score_image",
                files=files,
                headers=headers,
                timeout=30.0
            )
            resp.raise_for_status()
            data = resp.json()

            if data and len(data) > 0:
                best_match = data[0]
                return {
                    "species": best_match.get("name", "Sconosciuta"),
                    "confidence": best_match.get("score", 0.0),
                    "source": "iNaturalist"
                }
    except Exception as e:
        print(f"iNaturalist error: {e}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}

async def identify_audio(file_path: Path) -> dict:
    if not BIRDNET_AVAILABLE or analyzer is None:
        mock = random.choice(MOCK_SPECIES_AUDIO).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        return mock

    try:
        loop = asyncio.get_event_loop()
        predictions = await loop.run_in_executor(
            None, analyzer.analyze, str(file_path)
        )

        if predictions and len(predictions) > 0:
            best = max(predictions, key=lambda x: x.get("confidence", 0))
            return {
                "species": best.get("common_name") or best.get("scientific_name", "Sconosciuta"),
                "confidence": best.get("confidence", 0.0),
                "source": "BirdNET (Local)"
            }
    except Exception as e:
        print(f"Local BirdNET error: {e}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}
