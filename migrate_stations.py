import asyncio
from backend.db import supabase
from backend.constants import MOCK_STATIONS

async def migrate():
    print("Starting migration of stations to Supabase...")
    
    # 1. Create table using a RPC or just trying to insert and seeing if it fails.
    # Since we can't easily run DDL via the client without specific setup, 
    # we'll assume the user can run the SQL or we try a simple insert.
    # Actually, I'll provide the SQL for the user and a script to populate.
    # But wait, I can try to execute a raw SQL if there is a function for it.
    # There isn't a standard 'execute_sql' in the client for security reasons.
    
    # I'll create the population script.
    try:
        # Attempt to insert. If it fails because table doesn't exist, we inform the user.
        print("Inserting stations into 'stations' table...")
        # We need to map MOCK_STATIONS to match the expected table columns
        # Expected columns: id (text/uuid), name (text), lat (float), lon (float), shannon (float)
        data_to_insert = []
        for s in MOCK_STATIONS:
            data_to_insert.append({
                "id": s["id"],
                "name": s["name"],
                "lat": s["lat"],
                "lon": s["lon"],
                "shannon": s["shannon"]
            })
        
        res = supabase.table("stations").insert(data_to_insert).execute()
        print("Successfully migrated stations!")
        print(f"Inserted {len(res.data)} stations.")
    except Exception as e:
        print(f"Migration failed: {e}")
        print("\n--- ACTION REQUIRED ---")
        print("Please run the following SQL in your Supabase SQL Editor first:")
        print("CREATE TABLE stations (")
        print("  id TEXT PRIMARY KEY,")
        print("  name TEXT NOT NULL,")
        print("  lat FLOAT8 NOT NULL,")
        print("  lon FLOAT8 NOT NULL,")
        print("  shannon FLOAT8")
        print(");")
        print("------------------------")

if __name__ == "__main__":
    asyncio.run(migrate())
