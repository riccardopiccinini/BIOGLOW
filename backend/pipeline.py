import httpx
import uuid
from pathlib import Path
from .db import supabase, config

async def upload_to_storage(file_bytes: bytes, filename: str, station_id: str) -> str:
    """Uploads a file to Supabase Storage and returns the public URL."""
    ext = Path(filename).suffix
    file_id = str(uuid.uuid4())
    path = f"stations/{station_id}/{file_id}{ext}"
    
    # Upload file to the 'observations' bucket
    res = supabase.storage.from_(config.SUPABASE_STORAGE_BUCKET).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": "application/octet-stream"}
    )
    
    if not res:
        raise Exception("Failed to upload file to Supabase Storage")
        
    return supabase.storage.from_(config.SUPABASE_STORAGE_BUCKET).get_public_url(path)

async def identify_image(file_path: Path) -> dict:
    """Identifies a species from an image using iNaturalist CV API."""
    if not config.INATURALIST_TOKEN:
        return {"species": "Sconosciuta", "confidence": 0.0, "source": "error: no token"}
        
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        async with httpx.AsyncClient() as client:
            # iNaturalist CV API requires multipart upload
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
            
            # Best match is usually the first in the results list
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
    """Identifies a species from audio using BirdNET-Analyzer API."""
    if not config.BIRDNET_API_URL:
        return {"species": "Sconosciuta", "confidence": 0.0, "source": "error: no URL"}
        
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        async with httpx.AsyncClient() as client:
            files = {'file': (file_path.name, file_data)}
            # Add API key if configured
            params = {}
            if config.BIRDNET_API_KEY:
                params["api_key"] = config.BIRDNET_API_KEY
                
            resp = await client.post(
                config.BIRDNET_API_URL,
                files=files,
                params=params,
                timeout=60.0
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Assuming BirdNET returns a list of predictions
            if data and "predictions" in data and len(data["predictions"]) > 0:
                best = data["predictions"][0]
                return {
                    "species": best.get("common_name") or best.get("scientific_name", "Sconosciuta"),
                    "confidence": best.get("confidence", 0.0),
                    "source": "BirdNET"
                }
    except Exception as e:
        print(f"BirdNET error: {e}")
        
    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}
