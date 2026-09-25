import httpx
import uuid
import random
from pathlib import Path
from db import supabase
from config import config
from constants import OBSERVATION_METHODS

# Specie mock per test (comuni in zona Secchia)
MOCK_SPECIES_IMAGES = [
    {"species": "Passer domesticus", "confidence": 0.92, "source": "iNaturalist (mock)"},
    {"species": "Turdus merula", "confidence": 0.87, "source": "iNaturalist (mock)"},
    {"species": "Parus major", "confidence": 0.91, "source": "iNaturalist (mock)"},
    {"species": "Erithacus rubecula", "confidence": 0.85, "source": "iNaturalist (mock)"},
    {"species": "Fringilla coelebs", "confidence": 0.89, "source": "iNaturalist (mock)"},
    {"species": "Sylvia atricapilla", "confidence": 0.83, "source": "iNaturalist (mock)"},
    {"species": "Phylloscopus collybita", "confidence": 0.88, "source": "iNaturalist (mock)"},
    {"species": "Motacilla alba", "confidence": 0.90, "source": "iNaturalist (mock)"},
]

MOCK_SPECIES_AUDIO = [
    {"species": "Cuculus canorus", "confidence": 0.94, "source": "BirdNET (mock)"},
    {"species": "Upupa epops", "confidence": 0.91, "source": "BirdNET (mock)"},
    {"species": "Luscinia megarhynchos", "confidence": 0.89, "source": "BirdNET (mock)"},
    {"species": "Oriolus oriolus", "confidence": 0.86, "source": "BirdNET (mock)"},
    {"species": "Corvus corax", "confidence": 0.93, "source": "BirdNET (mock)"},
    {"species": "Picus viridis", "confidence": 0.88, "source": "BirdNET (mock)"},
    {"species": "Dendrocopos major", "confidence": 0.90, "source": "BirdNET (mock)"},
    {"species": "Strix aluco", "confidence": 0.87, "source": "BirdNET (mock)"},
]

async def upload_to_storage(file_bytes: bytes, filename: str, station_id: str) -> str:
    """Uploads a file to Supabase Storage and returns the public URL.
    In modalità mock, restituisce un URL placeholder."""
    ext = Path(filename).suffix
    file_id = str(uuid.uuid4())
    path = f"stations/{station_id}/{file_id}{ext}"

    # Se non c'è bucket configurato o siamo in mock, ritorna URL placeholder
    if not config.SUPABASE_STORAGE_BUCKET:
        return f"https://via.placeholder.com/400x300/2d6a4f/ffffff?text={filename}"

    try:
        # Upload file to the 'observations' bucket
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
    """Identifies a species from an image.
    Se INATURALIST_TOKEN non configurato, restituisce specie mock casuale."""
    if not config.INATURALIST_TOKEN:
        # Modalità mock: specie casuale con confidenza alta
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
    """Identifies a species from audio.
    Se BIRDNET_API_URL non configurato, restituisce specie mock casuale."""
    if not config.BIRDNET_API_URL:
        # Modalità mock: specie casuale con confidenza alta
        mock = random.choice(MOCK_SPECIES_AUDIO).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        return mock

    try:
        with open(file_path, "rb") as f:
            file_data = f.read()

        async with httpx.AsyncClient() as client:
            files = {'file': (file_path.name, file_data)}
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