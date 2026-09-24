import os
import asyncio
import datetime
import random
from db import supabase, save_observation
from alerts import check_and_create_alert

# Specie mock realistiche per zona Secchia (mix di uccelli comuni, rari, protetti)
MOCK_SPECIES_DATA = [
    # Uccelli comuni
    {"species": "Passer domesticus", "category": "bird", "method": "image", "confidence": 0.92, "source": "iNaturalist (mock)", "verification_status": "confirmed"},
    {"species": "Turdus merula", "category": "bird", "method": "image", "confidence": 0.87, "source": "iNaturalist (mock)", "verification_status": "confirmed"},
    {"species": "Parus major", "category": "bird", "method": "image", "confidence": 0.91, "source": "iNaturalist (mock)", "verification_status": "confirmed"},
    {"species": "Erithacus rubecula", "category": "bird", "method": "image", "confidence": 0.85, "source": "iNaturalist (mock)", "verification_status": "pending"},
    {"species": "Fringilla coelebs", "category": "bird", "method": "image", "confidence": 0.89, "source": "iNaturalist (mock)", "verification_status": "confirmed"},
    {"species": "Sylvia atricapilla", "category": "bird", "method": "image", "confidence": 0.83, "source": "iNaturalist (mock)", "verification_status": "pending"},
    # Uccelli da audio
    {"species": "Cuculus canorus", "category": "bird", "method": "audio", "confidence": 0.94, "source": "BirdNET (mock)", "verification_status": "confirmed"},
    {"species": "Upupa epops", "category": "bird", "method": "audio", "confidence": 0.91, "source": "BirdNET (mock)", "verification_status": "pending"},
    {"species": "Luscinia megarhynchos", "category": "bird", "method": "audio", "confidence": 0.89, "source": "BirdNET (mock)", "verification_status": "confirmed"},
    {"species": "Oriolus oriolus", "category": "bird", "method": "audio", "confidence": 0.86, "source": "BirdNET (mock)", "verification_status": "pending"},
    # Specie rara (per alert)
    {"species": "Aquila chrysaetos", "category": "bird", "method": "image", "confidence": 0.78, "source": "iNaturalist (mock)", "verification_status": "pending"},
    # Specie protetta (per alert)
    {"species": "Falco peregrinus", "category": "bird", "method": "image", "confidence": 0.82, "source": "iNaturalist (mock)", "verification_status": "confirmed"},
    # Specie invasiva (per alert)
    {"species": "Psittacula krameri", "category": "bird", "method": "image", "confidence": 0.88, "source": "iNaturalist (mock)", "verification_status": "pending"},
]

STATIONS = ["SECCHIA-01", "SECCHIA-02", "SECCHIA-03", "SECCHIA-04"]

# Placeholder images per media_url
PLACEHOLDER_BASE = "https://via.placeholder.com/400x300/2d6a4f/ffffff?text="

def generate_mock_observations(count=30):
    """Genera osservazioni mock distribuite negli ultimi 3 mesi."""
    observations = []
    base_date = datetime.datetime(2026, 6, 1)  # Inizio giugno 2026

    for i in range(count):
        species_data = random.choice(MOCK_SPECIES_DATA).copy()
        station = random.choice(STATIONS)

        # Distribuisci date negli ultimi 3 mesi (giugno-agosto 2026)
        days_offset = random.randint(0, 90)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        obs_date = base_date + datetime.timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)

        # Genera filename e media_url
        ext = ".jpg" if species_data["method"] == "image" else ".wav"
        filename = f"{species_data['species'].replace(' ', '_').lower()}_{i}{ext}"
        media_url = f"{PLACEHOLDER_BASE}{filename}"

        obs = {
            "species": species_data["species"],
            "category": species_data["category"],
            "method": species_data["method"],
            "media_url": media_url,
            "date_time": obs_date.isoformat() + "Z",
            "station_id": station,
            "confidence": round(species_data["confidence"] + random.uniform(-0.03, 0.03), 2),
            "verification_status": species_data["verification_status"],
            "source": species_data["source"],
            "source_update_date": None,
            "habitat_zone": None,
            "coordinates": None,
            "quality": random.choice(["high", "medium", "low"]),
        }
        observations.append(obs)

    return observations

async def load_demo_data():
    """Carica dati demo in Supabase (versione async)."""
    print("Generazione osservazioni mock...")
    observations = generate_mock_observations(35)

    print(f"Inserimento {len(observations)} osservazioni in Supabase...")
    inserted = 0
    for obs in observations:
        try:
            res = await save_observation(obs)
            if res.data:
                obs_id = res.data[0]["id"]
                # Crea alert se specie speciale
                await check_and_create_alert({**obs, "id": obs_id})
                inserted += 1
        except Exception as e:
            print(f"Errore inserimento {obs['species']}: {e}")

    print(f"Completato! {inserted}/{len(observations)} osservazioni inserite.")

if __name__ == "__main__":
    # Verifica variabili d'ambiente
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("ERRORE: Imposta SUPABASE_URL e SUPABASE_KEY come variabili d'ambiente")
        exit(1)

    asyncio.run(load_demo_data())