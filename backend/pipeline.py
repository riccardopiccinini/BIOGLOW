import httpx
import uuid
import random
import asyncio
from pathlib import Path
from db import supabase
from config import config
from constants import OBSERVATION_METHODS

try:
    from birdnetlib import BirdNETAnalyzer
    BIRDNET_AVAILABLE = True
except ImportError:
    BIRDNET_AVAILABLE = False

# Global analyzer instance
analyzer = None
if BIRDNET_AVAILABLE:
    try:
        # Inizia l'analyzer (scarica i modelli se non presenti)
        analyzer = BirdNETAnalyzer()
    except Exception as e:
        print(f"BirdNET initialization error: {e}")
        BIRDNET_AVAILABLE = False

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
    """Identifies a species from an image using iNaturalist API."""
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
    """Identifies a species from audio using local BirdNET analyzer."""
    if not BIRDNET_AVAILABLE or analyzer is None:
        # Fallback a specie mock se la libreria non è installata o non initialize
        mock = random.choice(MOCK_SPECIES_AUDIO).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        return mock

    try:
        # Eseguiamo l'analisi in un thread separato per non bloccare l'event loop di FastAPI
        loop = asyncio.get_event_loop()
        predictions = await loop.run_in_executor(
            None, analyzer.analyze, str(file_path)
        )

        if predictions and len(predictions) > 0:
            # Prendiamo la previsione con confidenza più alta
            best = max(predictions, key=lambda x: x.get("confidence", 0))
            return {
                "species": best.get("common_name") or best.get("scientific_name", "Sconosciuta"),
                "confidence": best.get("confidence", 0.0),
                "source": "BirdNET (Local)"
            }
    except Exception as e:
        print(f"Local BirdNET error: {e}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}
