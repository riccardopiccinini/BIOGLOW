import asyncio
from backend.db import supabase

async def migrate():
    print("Starting migration of stations to Supabase...")
    
    stations_data = [
        {"id": "SECCHIA-01", "name": "Stazione Nord - Riva", "lat": 44.92, "lon": 10.92, "shannon": 2.45},
        {"id": "SECCHIA-02", "name": "Stazione Centro - Bosco", "lat": 44.91, "lon": 10.95, "shannon": 1.80},
        {"id": "SECCHIA-03", "name": "Stazione Sud - Prato", "lat": 44.89, "lon": 10.98, "shannon": 0.70},
        {"id": "SECCHIA-04", "name": "Stazione Est - Argine", "lat": 44.90, "lon": 11.02, "shannon": 1.20},
    ]
    
    try:
        print("Inserting stations into 'stations' table...")
        res = supabase.table("stations").insert(stations_data).execute()
        print("Successfully migrated stations!")
        print(f"Inserted {len(res.data)} stations.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
