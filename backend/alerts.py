import json
import os
from supabase import create_client
from pathlib import Path

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load reference lists (assumes the JSON file is in the docs folder)
REF_PATH = Path(__file__).resolve().parents[1] / "docs" / "species_reference.json"
with open(REF_PATH, "r") as f:
    REFERENCE = json.load(f)

async def check_and_create_alert(observation: dict):
    species = observation.get("species")
    if not species:
        return None
    alert_type = None
    if species in REFERENCE.get("invasive", []):
        alert_type = "invasive"
    elif species in REFERENCE.get("protected", []):
        alert_type = "protected"
    elif species in REFERENCE.get("rare", []):
        alert_type = "rare"
    if alert_type:
        # Insert alert into a separate table (you may need to create it first)
        alert = {
            "species": species,
            "observation_id": observation.get("id"),
            "alert_type": alert_type,
            "status": "pending",
            "created_at": None,
        }
        res = supabase.table("alerts").insert(alert).execute()
        return res
    return None
