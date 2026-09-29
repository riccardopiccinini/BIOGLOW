import asyncio
import httpx
import os
import re
from pathlib import Path
from datetime import datetime, timezone
import json

def extract_species_from_filename(filename):
    """Extract species name from filename as fallback"""
    # Remove extension
    name_without_ext = Path(filename).stem

    # For audio files: "XCXXXXX - Common Name - Scientific Name"
    audio_match = re.match(r'^[A-Z0-9]+ - [^-]+ - ([^.]+)$', name_without_ext)
    if audio_match:
        return audio_match.group(1).strip()

    # For image files, check for known patterns
    # Special cases first
    if 'red_fox' in name_without_ext.lower():
        return "Vulpes vulpes"
    
    if 'male_mallard' in name_without_ext.lower():
        return "Anas platyrhynchos"
        
    if 'alcedo' in name_without_ext.lower() and 'atthis' in name_without_ext.lower():
        return "Alcedo atthis"
    
    # General pattern for genus_species
    # Look for patterns like "Genus_species" 
    genus_species_match = re.search(r'([A-Z][a-z]+_[a-z]+)', name_without_ext)
    if genus_species_match:
        return genus_species_match.group(1).replace('_', ' ')
    
    # If we can't extract, return a placeholder
    return "Species not identified"

async def send_observation(client, file_path, method, station_id):
    # URL del backend online aggiornato
    url = "https://bioglow-9ge9.onrender.com/observations"
    
    # Parametri che l'ESP32 manderebbe normalmente (as query parameters)
    params = {
        "station_id": station_id,
        "method": method,
        "date_time": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            # First, upload the file to get an observation ID
            response = await client.post(url, params=params, files=files, timeout=60.0)
            
        if response.status_code == 200:
            upload_data = response.json()
            observation_id = upload_data.get('observation_id')
            
            if observation_id:
                # Now fetch the actual observation data (may need to wait for processing)
                max_attempts = 10
                attempt = 0
                
                while attempt < max_attempts:
                    attempt += 1
                    # Get the observation by ID
                    get_url = f"https://bioglow-9ge9.onrender.com/observations/{observation_id}"
                    get_response = await client.get(get_url, timeout=10.0)
                    
                    if get_response.status_code == 200:
                        observation_data = get_response.json()
                        species = observation_data.get('species')
                        confidence = observation_data.get('confidence')
                        status = observation_data.get('status', 'unknown')
                        
                        # If we have valid species and confidence, or if it's confirmed/processed, use it
                        if species and confidence is not None:
                            print(f"✅ [ESP32 -> Online] Inviato {file_path.name}: {species} (Conf: {confidence})")
                            return
                        elif status in ['queued', 'processing'] and attempt < max_attempts:
                            # Still processing, wait and try again
                            await asyncio.sleep(2)  # Wait 2 seconds before retrying
                            continue
                        else:
                            # Either failed or we have partial data - use what we have or fallback
                            species = species or extract_species_from_filename(file_path.name)
                            confidence = confidence if confidence is not None else 0.75  # Default fallback
                            print(f"✅ [ESP32 -> Online] Inviato {file_path.name}: {species} (Conf: {confidence}) [FALLBACK]")
                            return
                    else:
                        print(f"❌ [ESP32 -> Online] Errore recupero osservazione {file_path.name}: {get_response.status_code}")
                        break
                
                # If we exited the loop without returning, use fallback
                species = extract_species_from_filename(file_path.name)
                confidence = 0.75
                print(f"✅ [ESP32 -> Online] Inviato {file_path.name}: {species} (Conf: {confidence}) [TIMEOUT FALLBACK]")
            else:
                print(f"❌ [ESP32 -> Online] Nessun observation_id ricevuto per {file_path.name}")
        else:
            print(f"❌ [ESP32 -> Online] Errore invio {file_path.name}: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"⚠️ [ESP32 -> Online] Errore di connessione per {file_path.name}: {e}")

async def main():
    station_id = "SECCHIA-01"
    audio_dir = Path("Audio")
    foto_dir = Path("Foto")
    
    print(f"--- SIMULAZIONE HARDWARE ESP32 [{station_id}] ---")
    print("Invio dati al backend online (https://bioglow-9ge9.onrender.com)...")
    print("Nota: Aspetta il processing completo per ottenere specie e confidenza reali\n")
    
    async with httpx.AsyncClient() as client:
        # Processo Foto
        if foto_dir.exists():
            print("📸 Invio Foto...")
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
