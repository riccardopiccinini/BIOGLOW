import httpx
import uuid
import random
import asyncio
import mimetypes
import torch
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
from PIL import Image
import io
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

# --- AUDIO AI SETUP ---
analyzer = None
if BIRDNET_AVAILABLE:
    try:
        analyzer = BirdNETAnalyzer()
    except Exception as e:
        print(f"BirdNET initialization error: {e}")
        BIRDNET_AVAILABLE = False

# --- IMAGE AI SETUP (Local MobileNetV2) ---
# We use a local model because iNaturalist requires an API token we don't have.
# MobileNetV2 is a real AI model trained on ImageNet.
print("Loading Local Image AI (MobileNetV2)...")
try:
    weights = MobileNet_V2_Weights.DEFAULT
    image_model = mobilenet_v2(weights=weights)
    image_model.eval()
    preprocess = weights.transforms()
    # Load ImageNet labels
    # Since we can't easily download the label file on Render, 
    # we use a simplified mapping for the most common project animals
    # in a real scenario, we'd load the full labels.txt
    IMAGE_NET_LABELS = {
        "fox": "Volpe",
        "robin": "Pettirosso",
        "heron": "Airone",
        "mallard": "Germano Reale",
        "kingfisher": "Martin Pescatore",
        "bird": "Uccello",
        "mammal": "Mammifero"
    }
    print("Local Image AI loaded successfully.")
except Exception as e:
    print(f"Local Image AI load error: {e}")
    image_model = None

async def upload_to_storage(file_bytes: bytes, filename: str, station_id: str) -> str:
    ext = Path(filename).suffix.lower()
    file_id = str(uuid.uuid4())
    path = f"stations/{station_id}/{file_id}{ext}"

    if not config.SUPABASE_STORAGE_BUCKET:
        raise Exception("SUPABASE_STORAGE_BUCKET non configurato nel server")

    manual_mimes = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
    }
    
    mime_type = manual_mimes.get(ext)
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"

    try:
        res = supabase.storage.from_(config.SUPABASE_STORAGE_BUCKET).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": mime_type}
        )
        if not res:
            raise Exception("Il server di Storage ha rifiutato l'upload (risposta vuota)")
        return supabase.storage.from_(config.SUPABASE_STORAGE_BUCKET).get_public_url(path)
    except Exception as e:
        print(f"CRITICAL STORAGE ERROR: {e}")
        raise e

async def identify_image(file_path: Path) -> dict:
    if config.DEMO_MODE:
        mock = random.choice(MOCK_SPECIES_IMAGES).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        mock["source"] = "Demo Mode (Mock)"
        return mock

    # 1. Try Local AI first (Token-free)
    if image_model:
        try:
            img = Image.open(file_path).convert('RGB')
            batch = preprocess(img).unsqueeze(0)
            
            with torch.no_grad():
                prediction = image_model(batch).squeeze(0)
                conf = torch.nn.functional.softmax(prediction, dim=0)
                conf_val, class_id = torch.max(conf, 0)
            
            # Convert class_id to a readable name (simplified for demo)
            # In a full setup, we would use weights.meta["categories"]
            category = weights.meta["categories"][class_id.item()]
            
            # Try to map to a project-specific name or just use the category
            species_name = IMAGE_NET_LABELS.get(category.lower(), category.capitalize())
            
            return {
                "species": species_name,
                "confidence": round(conf_val.item(), 2),
                "source": "Local AI (MobileNetV2)"
            }
        except Exception as e:
            print(f"Local AI error: {e}")

    # 2. Fallback to iNaturalist if token is present
    if config.INATURALIST_TOKEN:
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
            print(f"iNaturalist fallback error: {e}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}

async def identify_audio(file_path: Path) -> dict:
    if config.DEMO_MODE:
        mock = random.choice(MOCK_SPECIES_AUDIO).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        mock["source"] = "Demo Mode (Mock)"
        return mock

    if not BIRDNET_AVAILABLE or analyzer is None:
        print("AVVISO: BirdNET non disponibile. Specie impostata a Sconosciuta.")
        return {"species": "Sconosciuta", "confidence": 0.0, "source": "birdnet_unavailable"}

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
