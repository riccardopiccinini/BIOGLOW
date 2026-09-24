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
        
    if order.startswith("-"):
        col = order[1:]
        query = query.order(col, ascending=False)
    else:
        query = query.order(order, ascending=True)
        
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
