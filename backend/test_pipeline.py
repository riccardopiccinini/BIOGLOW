import asyncio
import os
from pathlib import Path
from pipeline import identify_image, identify_audio, upload_to_storage
from config import config
from db import supabase

async def test_pipeline():
    print("🚀 Starting BIOGLOW Pipeline End-to-End Test...")

    # 1. Test iNaturalist (Images)
    print("\n--- Testing iNaturalist (Images) ---")
    # Use a dummy file for testing logic
    img_path = Path("test_image.jpg")
    img_path.write_bytes(b"fake image data")
    try:
        res_img = await identify_image(img_path)
        print(f"Image Result: {res_img}")
    except Exception as e:
        print(f"Image Identification failed: {e}")
    finally:
        img_path.unlink()

    # 2. Test BirdNET (Audio)
    print("\n--- Testing BirdNET (Audio) ---")
    audio_path = Path("test_audio.wav")
    audio_path.write_bytes(b"fake audio data")
    try:
        res_audio = await identify_audio(audio_path)
        print(f"Audio Result: {res_audio}")
    except Exception as e:
        print(f"Audio Identification failed: {e}")
    finally:
        audio_path.unlink()

    # 3. Test Supabase Storage
    print("\n--- Testing Supabase Storage ---")
    try:
        url = await upload_to_storage(b"fake file content", "test_file.txt", "ST01")
        print(f"Storage Result URL: {url}")
    except Exception as e:
        print(f"Storage upload failed: {e}")

    print("\n✅ Pipeline test completed.")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
