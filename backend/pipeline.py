import httpx
import uuid
import random
import asyncio
import mimetypes
import google.generativeai as genai
from PIL import Image
import io
import re
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

def parse_gemini_response(text):
    """
    Extracts species and confidence from Gemini's response.
    Expected format: 'Specie: [Name], Confidenza: [0.0-1.0]'
    """
    species = "Sconosciuta"
    confidence = 0.0
    
    # Look for 'Specie: ...'
    species_match = re.search(r"Specie:\s*([^,\n\.]+)", text)
    if species_match:
        species = species_match.group(1).strip()
    
    # Look for 'Confidenza: ...'
    conf_match = re.search(r"Confidenza:\s*([0-9.]+)", text)
    if conf_match:
        try:
            confidence = float(conf_match.group(1))
        except ValueError:
            confidence = 0.0
            
    return species, confidence

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
                "1. Describe the animal features you see. "
                "2. Identify the most likely species. "
                "3. Provide the final answer in this exact format: 'Specie: [Common Name in Italian], Confidenza: [0.0-1.0]'. "
                "The confidence should represent your certainty. "
                "If it's not an animal, return 'Specie: Sconosciuta, Confidenza: 0.0'."
            )
            
            loop = asyncio.get_event_loop()
            
            # Retry logic for 429 (Quota Exceeded)
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    def call_gemini():
                        print(f"DEBUG: Sending image to Gemini (Attempt {attempt+1})...")
                        response = model.generate_content([prompt, img])
                        if response.candidates and response.candidates[0].content.parts:
                            return response.text.strip()
                        return "Sconosciuta"

                    text = await loop.run_in_executor(None, call_gemini)
                    print(f"DEBUG: Gemini Image Raw Response: {text}")
                    species, confidence = parse_gemini_response(text)
                    
                    if not species or species.lower() == "sconosciuta":
                        species = "Specie non identificata"

                    return {
                        "species": species,
                        "confidence": confidence,
                        "source": "Google Gemini 3.8"
                    }
                except Exception as e:
                    if "429" in str(e):
                        wait_time = (attempt + 1) * 10
                        print(f"DEBUG: Quota exceeded. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise e
            
            raise Exception("Max retries reached for Gemini API")
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
            
            # Upload file
            audio_file = await loop.run_in_executor(
                None, lambda: genai.upload_file(path=str(file_path))
            )
            
            # Wait for processing
            while True:
                file_info = await loop.run_in_executor(None, lambda: genai.get_file(audio_file.name))
                if file_info.state.name == 'ACTIVE':
                    break
                if file_info.state.name == 'FAILED':
                    raise Exception("Gemini failed to process the audio file.")
                await asyncio.sleep(2)

            prompt = (
                "You are an expert bioacoustician. "
                "1. Describe the characteristics of the sound. "
                "2. Identify the animal species based on these vocalizations. "
                "3. Provide the final answer in this exact format: 'Specie: [Common Name in Italian], Confidenza: [0.0-1.0]'. "
                "The confidence should represent your certainty. "
                "If it's not an animal sound, return 'Specie: Sconosciuta, Confidenza: 0.0'."
            )
            
            # Retry logic for 429
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    def call_gemini_audio():
                        print(f"DEBUG: Sending audio prompt to Gemini (Attempt {attempt+1})...")
                        response = model.generate_content([prompt, audio_file])
                        if response.candidates and response.candidates[0].content.parts:
                            return response.text.strip()
                        return "Sconosciuta"

                    text = await loop.run_in_executor(None, call_gemini_audio)
                    print(f"DEBUG: Gemini Audio Raw Response: {text}")
                    species, confidence = parse_gemini_response(text)
                    
                    await loop.run_in_executor(None, lambda: genai.delete_file(audio_file.name))
                    
                    if not species or species.lower() == "sconosciuta":
                        species = "Suono non identificato"

                    return {
                        "species": species,
                        "confidence": confidence,
                        "source": "Google Gemini 3.8"
                    }
                except Exception as e:
                    if "429" in str(e):
                        wait_time = (attempt + 1) * 10
                        print(f"DEBUG: Quota exceeded. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise e
            
            raise Exception("Max retries reached for Gemini API")
        except Exception as e:
            print(f"DEBUG: Gemini Audio error: {str(e)}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}
