import traceback
from collections import defaultdict
from datetime import datetime, timedelta
from supabase import create_client
from config import config
from biodiversity import shannon_index

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

async def get_observations(station_id=None, method=None, start=None, end=None, min_confidence=None, limit=10, order="-date_time"):
    query = supabase.table("osservazioni").select("*")

    if station_id:
        query = query.eq("station_id", station_id)
    if method:
        query = query.eq("method", method)
    if start:
        query = query.gte("date_time", start)
    if end:
        query = query.lte("date_time", end)
    if min_confidence is not None:
        query = query.gte("confidence", min_confidence)

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
    if res.data and len(res.data) > 0:
        return res.data[0]
    return {"id": obs_id, "verification_status": status, "updated": True}

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
        "observations": data
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
    """Recupera la lista delle stazioni e il numero di osservazioni per ciascuna."""
    try:
        # Log per debug
        print("DEBUG: Fetching stations from Supabase...")
        res_stations = supabase.table("stations").select("*").execute()
        
        if not res_stations.data:
            print("DEBUG: No stations found in table.")
            return []
            
        stations = res_stations.data
        print(f"DEBUG: Found {len(stations)} stations.")
        
        for s in stations:
            try:
                res_obs = supabase.table("osservazioni").select("id", count="exact").eq("station_id", s["id"]).execute()
                s["obs_count"] = res_obs.count if hasattr(res_obs, "count") else 0
            except Exception as e_obs:
                print(f"DEBUG: Error counting obs for station {s.get('id')}: {e_obs}")
                s["obs_count"] = 0
            
        return stations
    except Exception as e:
        print(f"CRITICAL ERROR in get_stations: {traceback.format_exc()}")
        # Ritorna None invece di [] per permettere al main di lanciare un 500 esplicito se vogliamo
        raise e

async def get_station_detail(station_id: str):
    res_station = supabase.table("stations").select("*").eq("id", station_id).single().execute()
    station_info = res_station.data
    if not station_info:
        return None

    stats = await get_stats(station_id=station_id)
    total_obs = stats["total"]
    species_count = stats["species_count"]
    shannon_global = 0.0
    if total_obs > 0:
        shannon_global = shannon_index(stats["observations"])

    latest_obs = await get_observations(station_id=station_id, limit=5, order="-date_time")

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

async def station_exists(station_id: str) -> bool:
    res = supabase.table("stations").select("id").eq("id", station_id).execute()
    return len(res.data) > 0 if res.data else False
