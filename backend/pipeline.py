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
    print(f"Gemini API Key found. Initializing model...")
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("WARNING: GEMINI_API_KEY not found in configuration. AI will be unavailable.")
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
            # MODIFIED: More open prompt to encourage a guess instead of 'Sconosciuta'
            prompt = (
                "Analyze this image and identify the animal species. "
                "Provide the most likely common name in Italian. "
                "If you are not 100% sure, give your best guess. "
                "Return ONLY the name of the species."
            )
            
            loop = asyncio.get_event_loop()
            def call_gemini():
                response = model.generate_content([prompt, img])
                if response.candidates and response.candidates[0].content.parts:
                    text = response.text.strip()
                    print(f"Gemini Image Raw Response: {text}")
                    return text
                return "Sconosciuta"

            species = await loop.run_in_executor(None, call_gemini)
            
            if not species or species.lower() == "sconosciuta":
                species = "Specie non identificata"

            return {
                "species": species,
                "confidence": 0.70, # Lowered confidence since it's a guess
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
            
            audio_file = await loop.run_in_executor(
                None, lambda: genai.upload_file(path=str(file_path))
            )
            
            while True:
                file_info = await loop.run_in_executor(None, lambda: genai.get_file(audio_file.name))
                if file_info.state.name == 'ACTIVE':
                    break
                if file_info.state.name == 'FAILED':
                    raise Exception("Gemini failed to process the audio file.")
                await asyncio.sleep(2)

            # MODIFIED: More open prompt for audio
            prompt = (
                "Listen to this audio clip. Identify the animal species based on its vocalization. "
                "Provide the most likely common name in Italian. "
                "Even if you are not certain, give your best guess based on the sound. "
                "Return ONLY the name of the species."
            )
            
            def call_gemini_audio():
                response = model.generate_content([prompt, audio_file])
                if response.candidates and response.candidates[0].content.parts:
                    text = response.text.strip()
                    print(f"Gemini Audio Raw Response: {text}")
                    return text
                return "Sconosciuta"

            species = await loop.run_in_executor(None, call_gemini_audio)
            
            await loop.run_in_executor(None, lambda: genai.delete_file(audio_file.name))
            
            if not species or species.lower() == "sconosciuta":
                species = "Suono non identificato"

            return {
                "species": species,
                "confidence": 0.70,
                "source": "Google Gemini"
            }
        except Exception as e:
            print(f"Gemini Audio error: {e}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}
