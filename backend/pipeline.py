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
from typing import Optional
from db import supabase
from config import config
from constants import (
    OBSERVATION_METHODS,
    MOCK_SPECIES_IMAGES,
    MOCK_SPECIES_AUDIO
)

# --- AI SETUP ---
if config.GEMINI_API_KEY:
    print(f"DEBUG: Gemini API Key found. Initializing model...")
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3.8-flash')
else:
    print("DEBUG: WARNING: GEMINI_API_KEY not found in configuration.")
    model = None

# Hugging Face API Setup
HF_TOKEN = config.HUGGINGFACE_API_KEY
HF_IMAGE_MODEL = "llava-hf/llava-1.5-7b-hf"
HF_AUDIO_MODEL = "MIT/ast-finetuned-audioset"

async def call_hf_api(model_id: str, data: bytes, prompt: Optional[str] = None):
    """Generic helper to call Hugging Face Inference API with retries for DNS/network errors"""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{model_id}",
                    headers=headers,
                    content=data,
                    timeout=30.0
                )
                if response.status_code != 200:
                    # Special case: model is loading
                    if response.status_code == 503:
                        print(f"DEBUG: HF Model {model_id} is loading... retrying...")
                        await asyncio.sleep(5)
                        continue
                    raise Exception(f"HF API Error: {response.status_code} - {response.text}")
                return response.json()
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"DEBUG: HF API Network error: {e}. Retrying in {wait_time}s... (Attempt {attempt+1})")
                await asyncio.sleep(wait_time)
            else:
                print(f"DEBUG: HF API failed after {max_retries} attempts: {e}")
                raise e

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

    # Retry logic for storage timeouts
    max_retries = 3
    for attempt in range(max_retries):
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
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"DEBUG: Storage upload timeout/error. Retrying in {wait_time}s... (Attempt {attempt+1})")
                await asyncio.sleep(wait_time)
            else:
                print(f"CRITICAL STORAGE ERROR after {max_retries} attempts: {e}")
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

    # Use Hugging Face (LLaVA) as Primary
    if HF_TOKEN:
        try:
            with open(file_path, "rb") as f:
                img_bytes = f.read()

            print(f"DEBUG: Calling Hugging Face LLaVA for {file_path.name}...")
            result = await call_hf_api(HF_IMAGE_MODEL, img_bytes, "Identify the animal in this image in Italian. Format: Specie: [Name], Confidenza: [0.0-1.0]")

            if isinstance(result, list) and len(result) > 0:
                text = result[0].get("generated_text", "Sconosciuta")
                species, confidence = parse_gemini_response(text)
                return {"species": species, "confidence": confidence, "source": "Hugging Face LLaVA"}
        except Exception as e:
            print(f"DEBUG: Hugging Face Image error: {e}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}

async def identify_audio(file_path: Path) -> dict:
    print(f"DEBUG: Starting audio identification for {file_path.name}")
    if config.DEMO_MODE:
        mock = random.choice(MOCK_SPECIES_AUDIO).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        mock["source"] = "Demo Mode (Mock)"
        return mock

    # Use Hugging Face (AST) as Primary
    if HF_TOKEN:
        try:
            with open(file_path, "rb") as f:
                audio_bytes = f.read()

            print(f"DEBUG: Calling Hugging Face AST for {file_path.name}...")
            result = await call_hf_api(HF_AUDIO_MODEL, audio_bytes)

            if isinstance(result, list) and len(result) > 0:
                top_match = max(result, key=lambda x: x.get("score", 0))
                return {
                    "species": top_match.get("label", "Sconosciuta"),
                    "confidence": round(top_match.get("score", 0.0), 2),
                    "source": "Hugging Face AST"
                }
        except Exception as e:
            print(f"DEBUG: Hugging Face Audio error: {e}")

    return {"species": "Sconosciuta", "confidence": 0.0, "source": "error"}
