from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from pathlib import Path
from supabase import create_client

# Imports from local modules
from biodiversity import compute_shannon, compute_shannon_time_series, shannon_index
from alerts import check_and_create_alert, get_alerts

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/observations/stats")
async def observations_stats(
    station_id: Optional[str] = None,
    method: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None
):
    # Build query for total and species count
    query = supabase.table("osservazioni").select("id", count="exact")
    if station_id: query = query.eq("station_id", station_id)
    if method: query = query.eq("method", method)
    if start: query = query.gte("date_time", start)
    if end: query = query.lte("date_time", end)
    
    res = query.execute()
    total = res.count if hasattr(res, "count") else 0
    
    # Species count
    species_query = supabase.table("osservazioni").select("species")
    if station_id: species_query = species_query.eq("station_id", station_id)
    if method: species_query = species_query.eq("method", method)
    if start: species_query = species_query.gte("date_time", start)
    if end: species_query = species_query.lte("date_time", end)
    
    species_res = species_query.execute()
    species_set = set(item["species"] for item in species_res.data if item.get("species")) if species_res.data else set()
    species_count = len(species_set)
    
    # Shannon index for the filtered set
    obs_for_shannon = species_res.data if species_res.data else []
    shannon_val = shannon_index(obs_for_shannon)
    
    return {
        "total_observations": total, 
        "species_count": species_count, 
        "shannon_index": shannon_val
    }

@app.get("/observations")
async def get_observations(
    station_id: Optional[str] = None,
    method: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 10,
    order: str = "-date_time"
):
    query = supabase.table("osservazioni").select("*")
    
    if station_id: query = query.eq("station_id", station_id)
    if method: query = query.eq("method", method)
    if start: query = query.gte("date_time", start)
    if end: query = query.lte("date_time", end)
    
    # Ordering
    if order.startswith("-"):
        col = order[1:]
        query = query.order(col, ascending=False)
    else:
        query = query.order(order, ascending=True)
        
    query = query.limit(limit)
    res = query.execute()
    return res.data if res.data else []

@app.get("/observations/{id}")
async def get_observation(id: str):
    res = supabase.table("osservazioni").select("*").eq("id", id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Osservazione non trovata")
    return res.data

@app.patch("/observations/{id}")
async def update_observation(id: str, data: dict):
    if "verification_status" not in data:
        raise HTTPException(status_code=400, detail="Solo verification_status può essere aggiornato")
    
    res = supabase.table("osservazioni").update(data).eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Osservazione non trovata")
    return res.data[0]

@app.get("/observations/shannon-time")
async def get_shannon_time(
    interval: str = "month", 
    station_id: Optional[str] = None, 
    method: Optional[str] = None, 
    start: Optional[str] = None, 
    end: Optional[str] = None
):
    filters = {"station_id": station_id, "method": method, "start": start, "end": end}
    return await compute_shannon_time_series(interval=interval, filters=filters)

@app.get("/alerts")
async def get_all_alerts(status: Optional[str] = None):
    return await get_alerts(status_filter=status)

@app.post("/observations")
async def receive_observation(file: UploadFile = File(...), method: str = "image"):
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    from pipeline import identify_image, identify_audio, save_observation
    from pathlib import Path
    file_path = Path(tmp_path)
    
    if method == "image":
        result = await identify_image(file_path)
    elif method == "audio":
        result = await identify_audio(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported method")
        
    observation = {
        "species": result["species"],
        "method": method,
        "media_url": f"{file.filename}",
        "station_id": "SECCHIA-01", 
        "confidence": result["confidence"],
        "verification_status": "pending",
    }
    
    save_res = await save_observation(observation)
    if save_res.data:
        obs_id = save_res.data[0]["id"]
        await check_and_create_alert({**observation, "id": obs_id})
        return JSONResponse(content={"observation_id": obs_id, "species": result["species"], "confidence": result["confidence"]})
    
    raise HTTPException(status_code=500, detail="Errore nel salvataggio dell'osservazione")
