from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from pathlib import Path
from supabase import create_client

# Imports from local modules
from config import config
from db import supabase, get_observations as db_get_observations, get_observation_by_id, update_observation_status, get_stats, get_alerts, get_stations
from biodiversity import compute_shannon_time_series, shannon_index
from alerts import check_and_create_alert
from pipeline import identify_image, identify_audio, upload_to_storage

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/health")
async def health():
    try:
        supabase.table("osservazioni").select("id", count="exact").limit(1).execute()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "db": f"disconnected: {str(e)}"}
        )

@app.get("/observations/stats")
async def observations_stats(
    station_id: Optional[str] = None,
    method: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None
):
    res = await get_stats(station_id, method, start, end)
    return {
        "total_observations": res["total"], 
        "species_count": res["species_count"], 
        "shannon_index": shannon_index(res["observations"])
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
    return await db_get_observations(station_id, method, start, end, limit, order)

@app.get("/observations/{id}")
async def get_observation(id: str):
    obs = await get_observation_by_id(id)
    if not obs:
        raise HTTPException(status_code=404, detail="Osservazione non trovata")
    return obs

@app.patch("/observations/{id}")
async def update_observation(id: str, data: dict):
    if "verification_status" not in data:
        raise HTTPException(status_code=400, detail="Solo verification_status può essere aggiornato")
    
    obs = await update_observation_status(id, data["verification_status"])
    if not obs:
        raise HTTPException(status_code=404, detail="Osservazione non trovata")
    return obs

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

@app.get("/stations")
async def get_all_stations():
    """Restituisce lista stazioni con coordinate per la mappa."""
    return await get_stations()

@app.post("/observations")
async def receive_observation(
    file: UploadFile = File(...), 
    method: str = "image", 
    station_id: str = "SECCHIA-01"
):
    tmp_path = Path(f"/tmp/{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
        
    if method == "image":
        result = await identify_image(tmp_path)
    elif method == "audio":
        result = await identify_audio(tmp_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported method")
        
    # Upload to Supabase Storage
    with open(tmp_path, "rb") as f:
        media_url = await upload_to_storage(f.read(), file.filename, station_id)
        
    observation = {
        "species": result["species"],
        "method": method,
        "media_url": media_url,
        "station_id": station_id,
        "confidence": result["confidence"],
        "verification_status": "pending",
        "date_time": "2026-09-23T12:00:00Z" # Simplified, should be current time
    }
    
    from db import save_observation
    save_res = await save_observation(observation)
    
    if save_res.data:
        obs_id = save_res.data[0]["id"]
        await check_and_create_alert({**observation, "id": obs_id})
        return JSONResponse(content={"observation_id": obs_id, "species": result["species"], "confidence": result["confidence"]})
    
    raise HTTPException(status_code=500, detail="Errore nel salvataggio dell'osservazione")
