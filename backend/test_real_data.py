import asyncio
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone

from config import config
from db import supabase, save_observation
from pipeline import identify_image, identify_audio, upload_to_storage
from constants import CONFIDENCE_THRESHOLDS
from alerts import check_and_create_alert

async def process_real_file(file_path: Path, method: str, station_id: str):
    print(f"Processing {method}: {file_path.name}...")
    
    try:
        # 1. Identify
        if method == "image":
            result = await identify_image(file_path)
        elif method == "audio":
            result = await identify_audio(file_path)
        else:
            print(f"Unsupported method {method}")
            return None

        # 2. Upload to storage
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        media_url = await upload_to_storage(file_bytes, file_path.name, station_id)

        # 3. Calculate status
        confidence = result.get("confidence", 0.0) if result else 0.0
        species = result.get("species", "Sconosciuta") if result else "Sconosciuta"
        
        if confidence >= CONFIDENCE_THRESHOLDS["auto_confirm"]:
            verification_status = "confirmed"
        elif confidence >= CONFIDENCE_THRESHOLDS["min_acceptable"]:
            verification_status = "pending"
        else:
            verification_status = "excluded"

        # 4. Save observation
        observation = {
            "species": species,
            "method": method,
            "media_url": media_url,
            "station_id": station_id,
            "confidence": confidence,
            "verification_status": verification_status,
            "date_time": datetime.now(timezone.utc).isoformat()
        }

        save_res = await save_observation(observation)
        if save_res and save_res.data and len(save_res.data) > 0:
            obs_data = save_res.data[0]
            obs_id = obs_data.get("id")
            if obs_id:
                await check_and_create_alert({**observation, "id": obs_id})
                print(f"  -> Success: {species} ({confidence}) ID: {obs_id}")
                return obs_id

    except Exception as e:
        print(f"  -> Error processing {file_path.name}: {e}")
    
    return None

async def main():
    # Force DEMO_MODE off for this test to avoid mocks if possible
    # However, if tokens are missing, the pipeline still mocks.
    # We'll just proceed and see what happens.
    
    station_id = "SECCHIA-01"
    
    # Define folders
    # Note: based on ls -R, they are 'Audio' and 'Foto'
    audio_dir = Path("Audio")
    foto_dir = Path("Foto")

    # Process Photos
    if foto_dir.exists():
        print("\n--- Processing Photos ---")
        for file in foto_dir.glob("*"):
            if file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                await process_real_file(file, "image", station_id)

    # Process Audio
    if audio_dir.exists():
        print("\n--- Processing Audio ---")
        for file in audio_dir.glob("*"):
            if file.suffix.lower() in [".mp3", ".wav", ".ogg"]:
                await process_real_file(file, "audio", station_id)

if __name__ == "__main__":
    asyncio.run(main())
