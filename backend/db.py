import math
import traceback
from collections import defaultdict
from datetime import datetime, timedelta
from supabase import create_client
from config import config

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

async def get_observations(station_id=None, method=None, start=None, end=None, limit=10, order="-date_time"):
    query = supabase.table("osservazioni").select("*")

    if station_id:
        query = query.eq("station_id", station_id)
    if method:
        query = query.eq("method", method)
    if start:
        query = query.gte("date_time", start)
    if end:
        query = query.lte("date_time", end)

    # Supabase postgrest-py usa desc=True/False invece di ascending
    if order.startswith("-"):
        col = order[1:]
        query = query.order(col, desc=True)
    else:
        query = query.order(order, desc=False)

    query = query.limit(limit)
    res = query.execute()
    return res.data if res.data else []

async def get_observation_by_id(obs_id: str):
    res = supabase.table("osservazioni").select("*").eq("id", obs_id).single().execute()
    return res.data if res.data else None

async def update_observation_status(obs_id: str, status: str):
    res = supabase.table("osservazioni").update({"verification_status": status}).eq("id", obs_id).execute()
    return res.data[0] if res.data else None

async def get_stats(station_id=None, method=None, start=None, end=None):
    query = supabase.table("osservazioni").select("id, species", count="exact")
    if station_id: query = query.eq("station_id", station_id)
    if method: query = query.eq("method", method)
    if start: query = query.gte("date_time", start)
    if end: query = query.lte("date_time", end)

    res = query.execute()
    total = res.count if hasattr(res, "count") else 0

    data = res.data if res.data else []
    species_set = set(item["species"] for item in data if item.get("species"))
    species_count = len(species_set)

    return {
        "total": total,
        "species_count": species_count,
        "observations": data # returned for shannon index calculation
    }

async def get_alerts(status=None):
    query = supabase.table("alerts").select("*")
    if status:
        query = query.eq("status", status)
    res = query.execute()
    return res.data if res.data else []

async def save_observation(observation: dict):
    res = supabase.table("osservazioni").insert(observation).execute()
    return res


async def get_stations():
    """Restituisce lista stazioni con coordinate per la mappa.
    Per ora ritorna dati mock, in futuro si può creare tabella stations."""
    # Stazioni mock per area Secchia
    stations = [
        {
            "id": "SECCHIA-01",
            "name": "Secchia Nord",
            "lat": 44.6472,
            "lon": 10.9258,
            "shannon": 1.45
        },
        {
            "id": "SECCHIA-02",
            "name": "Secchia Centro",
            "lat": 44.6321,
            "lon": 10.9189,
            "shannon": 1.32
        },
        {
            "id": "SECCHIA-03",
            "name": "Secchia Sud",
            "lat": 44.6156,
            "lon": 10.9012,
            "shannon": 1.58
        },
        {
            "id": "SECCHIA-04",
            "name": "Expansione Est",
            "lat": 44.6289,
            "lon": 10.9456,
            "shannon": 1.21
        },
    ]
    return stations


async def get_station_detail(station_id: str):
    """Restituisce dettagli di una stazione: info base, stats, specie osservate, ultime osservazioni."""
    # Ottenere info stazione dalla lista mock (o da tabella se esistente)
    stations = await get_stations()
    station_info = next((s for s in stations if s["id"] == station_id), None)
    if not station_info:
        return None

    # Stats globali per quella stazione (tutto il periodo)
    stats = await get_stats(station_id=station_id)
    total_obs = stats["total"]
    species_set = set(item["species"] for item in stats["observations"] if item.get("species"))
    species_count = len(species_set)
    shannon_global = 0.0
    if total_obs > 0:
        # Calcola Shannon usando le osservazioni della stazione
        shannon_global = shannon_index(stats["observations"])

    # Ultime 5 osservazioni per quella stazione
    latest_obs = await get_observations(station_id=station_id, limit=5, order="-date_time")

    # Specie osservate (lista di specie con conteggio)
    # Possiamo riutilizzare stats["observations"] per conteggio
    species_counts = {}
    for obs in stats["observations"]:
        sp = obs.get("species")
        if sp:
            species_counts[sp] = species_counts.get(sp, 0) + 1
    species_list = [{"species": sp, "count": cnt} for sp, cnt in species_counts.items()]

    return {
        "station": station_info,
        "stats": {
            "total_observations": total_obs,
            "species_count": species_count,
            "shannon_index": shannon_global
        },
        "species": species_list,
        "latest_observations": latest_obs
    }


def shannon_index(observations):
    total = len(observations)
    if total == 0:
        return 0.0

    counts = {}
    for obs in observations:
        sp = obs.get('species')
        if sp:
            counts[sp] = counts.get(sp, 0) + 1

    h = 0.0
    for cnt in counts.values():
        p = cnt / total
        h -= p * math.log(p)
    return h