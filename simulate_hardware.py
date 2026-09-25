import asyncio
import os
from pathlib import Path
from datetime import datetime, timezone
import random

# Mocking the backend components to avoid network errors in the sandbox
# but keeping the logic identical to the real pipeline
class MockPipeline:
    def __init__(self):
        self.species_map = {
            "coypu": "Myocastor coypus",
            "fox": "Vulpes vulpes",
            "mallard": "Anas platyrhynchos",
            "robin": "Erithacus rubecula",
            "heron": "Ardea cinerea",
            "kingfisher": "Alcedo atthis"
        }

    async def identify(self, file_path, method):
        name = file_path.name.lower()
        for key, species in self.species_map.items():
            if key in name:
                return {"species": species, "confidence": round(random.uniform(0.85, 0.98), 2)}
        return {"species": "Sconosciuta", "confidence": 0.45}

    async def upload(self, file_path):
        # Simulate a public URL
        return f"https://storage.bioglow.local/stations/SECCHIA-01/{file_path.name}"

    async def save_to_db(self, observation):
        # Simulate DB save
        return {"id": str(random.randint(1000, 9999))}

async def run_simulation():
    pipeline = MockPipeline()
    station_id = "SECCHIA-01"
    
    # Folders as defined by user
    audio_dir = Path("Audio")
    foto_dir = Path("Foto")

    print(f"--- AVVIO SIMULAZIONE FOTOTRAPPOLA [{station_id}] ---")
    
    files_to_process = []
    if foto_dir.exists():
        files_to_process.extend([(f, "image") for f in foto_dir.glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png"]])
    if audio_dir.exists():
        files_to_process.extend([(f, "audio") for f in audio_dir.glob("*") if f.suffix.lower() in [".mp3", ".wav", ".ogg"]])

    for file_path, method in files_to_process:
        print(f"\n[Hardware] Rilevato nuovo file: {file_path.name}")
        print(f"[Hardware] Invio a server via protocollo BioGlow...")
        
        # Simulation of the pipeline process
        result = await pipeline.identify(file_path, method)
        url = await pipeline.upload(file_path)
        
        observation = {
            "species": result["species"],
            "method": method,
            "media_url": url,
            "station_id": station_id,
            "confidence": result["confidence"],
            "date_time": datetime.now(timezone.utc).isoformat()
        }
        
        db_res = await pipeline.save_to_db(observation)
        
        print(f"[Server] Identificazione completata: {observation['species']} (Conf: {observation['confidence']})")
        print(f"[Server] File salvato in storage: {url}")
        print(f"[Server] Osservazione registrata nel DB con ID: {db_res['id']}")

    print("\n--- SIMULAZIONE COMPLETATA ---")
    print(f"Totale file processati: {len(files_to_process)}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
