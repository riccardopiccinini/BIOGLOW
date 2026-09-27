import httpx
import uuid
import random
import asyncio
import mimetypes
import google.generativeai as genai
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

# --- GEMINI AI SETUP ---
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

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

    if model:
        try:
            img = Image.open(file_path)
            prompt = "Identify the animal species in this image. Return only the common name in Italian. If you cannot identify the animal or it is not an animal, return 'Sconosciuta'."
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: model.generate_content([prompt, img])
            )
            
            species = response.text.strip()
            return {
                "species": species,
                "confidence": 0.90,
                "source": "Google Gemini"
            }
        except Exception as e:
            print(f"Gemini Image error: {e}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}

async def identify_audio(file_path: Path) -> dict:
    if config.DEMO_MODE:
        mock = random.choice(MOCK_SPECIES_AUDIO).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        mock["source"] = "Demo Mode (Mock)"
        return mock

    if model:
        try:
            loop = asyncio.get_event_loop()
            
            # 1. Upload file
            audio_file = await loop.run_in_executor(
                None, lambda: genai.upload_file(path=str(file_path))
            )
            
            # 2. IMPORTANT: Wait for file to be processed by Gemini
            # Gemini files have states: PROCESSING -> ACTIVE
            while True:
                file_info = await loop.run_in_executor(None, lambda: genai.get_file(audio_file.name))
                if file_info.state.name == 'ACTIVE':
                    break
                if file_info.state.name == 'FAILED':
                    raise Exception("Gemini failed to process the audio file.")
                await asyncio.sleep(2)

            # 3. Enhanced Prompt for better animal recognition
            prompt = (
                "You are an expert biologist. Listen to this audio clip carefully. "
                "Identify the animal species based on its vocalization. "
                "Return ONLY the common name of the species in Italian. "
                "If you are not confident or it is not an animal sound, return 'Sconosciuta'."
            )
            
            response = await loop.run_in_executor(
                None, lambda: model.generate_content([prompt, audio_file])
            )
            
            species = response.text.strip()
            
            # Clean up: delete the uploaded file from Gemini's temporary storage
            await loop.run_in_executor(None, lambda: genai.delete_file(audio_file.name))
            
            return {
                "species": species,
                "confidence": 0.90,
                "source": "Google Gemini"
            }
        except Exception as e:
            print(f"Gemini Audio error: {e}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}
