import json
from pathlib import Path
from db import supabase
from config import config
from constants import ALERT_TYPES

# Load reference lists
REF_PATH = Path(__file__).resolve().parents[1] / "docs" / "species_reference.json"
try:
    with open(REF_PATH, "r") as f:
        REFERENCE = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    REFERENCE = {"invasive": [], "protected": [], "rare": []}

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
        alert = {
            "species": species,
            "observation_id": observation.get("id"),
            "alert_type": alert_type,
            "status": "pending",
        }
        res = supabase.table("alerts").insert(alert).execute()
        return res
    return None

async def get_alerts(status_filter=None):
    query = supabase.table("alerts").select("*")
    if status_filter:
        query = query.eq("status", status_filter)

    res = query.execute()
    return res.data if res.data else []