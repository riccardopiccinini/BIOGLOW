import asyncio
import httpx
import os
from pathlib import Path
from datetime import datetime, timezone

async def send_observation(client, file_path, method, station_id):
    # URL del backend online fornito dall'utente
    url = "https://monitor-secchia-backend.onrender.com/observations"
    
    # Parametri che l'ESP32 manderebbe normalmente
    params = {
        "station_id": station_id,
        "method": method,
        "date_time": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = await client.post(url, params=params, files=files, timeout=60.0)
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ [ESP32 -> Online] Inviato {file_path.name}: {data.get('species')} (Conf: {data.get('confidence')})")
        else:
            print(f"❌ [ESP32 -> Online] Errore invio {file_path.name}: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"⚠️ [ESP32 -> Online] Errore di connessione per {file_path.name}: {e}")

async def main():
    station_id = "SECCHIA-01"
    audio_dir = Path("Audio")
    foto_dir = Path("Foto")
    
    print(f"--- SIMULAZIONE HARDWARE ESP32 [{station_id}] ---")
    print("Invio dati al backend online (https://monitor-secchia-backend.onrender.com)...")
    
    async with httpx.AsyncClient() as client:
        # Processo Foto
        if foto_dir.exists():
            print("\n📸 Invio Foto...")
            for file in foto_dir.glob("*"):
                if file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    await send_observation(client, file, "image", station_id)
        
        # Processo Audio
        if audio_dir.exists():
            print("\n🔊 Invio Audio...")
            for file in audio_dir.glob("*"):
                if file.suffix.lower() in [".mp3", ".wav", ".ogg"]:
                    await send_observation(client, file, "audio", station_id)

    print("\n--- FINE SIMULAZIONE ---")

if __name__ == "__main__":
    asyncio.run(main())
