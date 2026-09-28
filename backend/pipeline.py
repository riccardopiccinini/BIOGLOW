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
    print(f"DEBUG: Gemini API Key found. Initializing model...")
    genai.configure(api_key=config.GEMINI_API_KEY)
    # UPDATED: Using the latest Gemini 3.8 Flash for superior animal recognition
    model = genai.GenerativeModel('gemini-3.8-flash')
else:
    print("DEBUG: WARNING: GEMINI_API_KEY not found in configuration.")
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
    print(f"DEBUG: Starting image identification for {file_path.name}")
    if config.DEMO_MODE:
        mock = random.choice(MOCK_SPECIES_IMAGES).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        mock["source"] = "Demo Mode (Mock)"
        return mock

    if model:
        try:
            img = Image.open(file_path)
            prompt = (
                "You are an expert wildlife biologist. "
                "1. Describe the animal features you see in the image. "
                "2. Based on these features, identify the most likely species. "
                "3. Provide the final answer as: 'Specie: [Common Name in Italian]'. "
                "If it's not an animal, return 'Specie: Sconosciuta'."
            )
            
            loop = asyncio.get_event_loop()
            def call_gemini():
                print("DEBUG: Sending image to Gemini 3.8 Flash...")
                response = model.generate_content([prompt, img])
                if response.candidates and response.candidates[0].content.parts:
                    text = response.text.strip()
                    print(f"DEBUG: Gemini Image Raw Response: {text}")
                    
                    if "Specie:" in text:
                        species = text.split("Specie:")[-1].strip()
                    else:
                        species = text.split("\n")[-1].strip()
                    return species
                return "Sconosciuta"

            species = await loop.run_in_executor(None, call_gemini)
            
            if not species or species.lower() == "sconosciuta":
                species = "Specie non identificata"

            return {
                "species": species,
                "confidence": 0.70,
                "source": "Google Gemini 3.8"
            }
        except Exception as e:
            print(f"DEBUG: Gemini Image error: {str(e)}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}

async def identify_audio(file_path: Path) -> dict:
    print(f"DEBUG: Starting audio identification for {file_path.name}")
    if config.DEMO_MODE:
        mock = random.choice(MOCK_SPECIES_AUDIO).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        mock["source"] = "Demo Mode (Mock)"
        return mock

    if model:
        try:
            loop = asyncio.get_event_loop()
            
            print("DEBUG: Uploading audio to Gemini...")
            audio_file = await loop.run_in_executor(
                None, lambda: genai.upload_file(path=str(file_path))
            )
            
            while True:
                file_info = await loop.run_in_executor(None, lambda: genai.get_file(audio_file.name))
                if file_info.state.name == 'ACTIVE':
                    print("DEBUG: Audio file is now ACTIVE.")
                    break
                if file_info.state.name == 'FAILED':
                    raise Exception("Gemini failed to process the audio file.")
                print("DEBUG: Waiting for audio to be processed...")
                await asyncio.sleep(2)

            prompt = (
                "You are an expert bioacoustician. "
                "1. Describe the characteristics of the sound (pitch, rhythm, pattern). "
                "2. Identify the animal species based on these vocalizations. "
                "3. Provide the final answer as: 'Specie: [Common Name in Italian]'. "
                "If it's not an animal sound, return 'Specie: Sconosciuta'."
            )
            
            def call_gemini_audio():
                print("DEBUG: Sending audio prompt to Gemini 3.8 Flash...")
                response = model.generate_content([prompt, audio_file])
                if response.candidates and response.candidates[0].content.parts:
                    text = response.text.strip()
                    print(f"DEBUG: Gemini Audio Raw Response: {text}")
                    
                    if "Specie:" in text:
                        species = text.split("Specie:")[-1].strip()
                    else:
                        species = text.split("\n")[-1].strip()
                    return species
                return "Sconosciuta"

            species = await loop.run_in_executor(None, call_gemini_audio)
            
            await loop.run_in_executor(None, lambda: genai.delete_file(audio_file.name))
            
            if not species or species.lower() == "sconosciuta":
                species = "Suono non identificato"

            return {
                "species": species,
                "confidence": 0.70,
                "source": "Google Gemini 3.8"
            }
        except Exception as e:
            print(f"DEBUG: Gemini Audio error: {str(e)}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}
