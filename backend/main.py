from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import io
from pathlib import Path
from datetime import datetime, timezone
from supabase import create_client

# Imports from local modules
from config import config
from db import (
    supabase, 
    get_observations as db_get_observations, 
    get_observation_by_id, 
    update_observation_status, 
    get_stats, 
    get_alerts, 
    get_stations, 
    get_station_detail,
    station_exists
)
from biodiversity import compute_shannon_time_series, compute_shannon_time_series_detail, shannon_index
from alerts import check_and_create_alert
from pipeline import identify_image, identify_audio, upload_to_storage
from constants import CONFIDENCE_THRESHOLDS
from reports import generate_summary_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token di autenticazione mancante o non valido")
    
    token = authorization.split(" ")[1]
    try:
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Utente non autenticato")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Errore di autenticazione: {str(e)}")

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
    if not res:
        return JSONResponse(status_code=500, content={"error": "Impossibile recuperare le statistiche"})
    
    return {
        "total_observations": res.get("total", 0),
        "species_count": res.get("species_count", 0),
        "shannon_index": shannon_index(res.get("observations", []))
    }

@app.get("/observations")
async def get_observations(
    station_id: Optional[str] = None,
    method: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    min_confidence: Optional[float] = None,
    limit: int = 10,
    order: str = "-date_time"
):
    try:
        return await db_get_observations(station_id, method, start, end, min_confidence, limit, order)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "type": type(e).__name__})

@app.get("/observations/shannon-time")
async def get_shannon_time(
    interval: str = "month",
    station_id: Optional[str] = None,
    method: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None
):
  try:
    filters = {"station_id": station_id, "method": method, "start": start, "end": end}
    result = await compute_shannon_time_series(interval=interval, filters=filters)
    return result
  except Exception as e:
    print(f"shannon-time error: {e}")
    return []

@app.get("/observations/shannon-time-detail")
async def get_shannon_time_detail(
    interval: str = "month",
    station_id: Optional[str] = None,
    method: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None
):
  try:
    filters = {"station_id": station_id, "method": method, "start": start, "end": end}
    result = await compute_shannon_time_series_detail(interval=interval, filters=filters)
    return result
  except Exception as e:
    print(f"shannon-time-detail error: {e}")
    return JSONResponse(status_code=500, content={"error": str(e), "type": type(e).__name__})

@app.get("/observations/{id}")
async def get_observation(id: str):
    obs = await get_observation_by_id(id)
    if not obs:
        raise HTTPException(status_code=404, detail="Osservazione non trovata")
    return obs

@app.patch("/observations/{id}")
async def update_observation(id: str, data: dict, user=Depends(verify_token)):
    if "verification_status" not in data:
        raise HTTPException(status_code=400, detail="Solo verification_status può essere aggiornato")

    obs = await update_observation_status(id, data["verification_status"])
    if not obs:
        raise HTTPException(status_code=404, detail="Osservazione non trovata")
    return obs

@app.get("/alerts")
async def get_all_alerts(status: Optional[str] = None):
    try:
        return await get_alerts(status=status)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "type": type(e).__name__})

@app.get("/stations")
async def get_all_stations():
    try:
        return await get_stations()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/stations/{station_id}")
async def get_station(station_id: str):
    detail = await get_station_detail(station_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Stazione non trovata")
    return detail

@app.post("/observations")
async def receive_observation(
    file: UploadFile = File(...),
    method: str = "image",
    station_id: str = Query(...), # Rimosso default, ora obbligatorio per coerenza DB
    date_time: Optional[str] = None
):
    if not await station_exists(station_id):
        raise HTTPException(status_code=400, detail=f"Stazione {station_id} non valida o non censita nel DB")

    tmp_path = Path(f"/tmp/{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    if method == "image":
        result = await identify_image(tmp_path)
    elif method == "audio":
        result = await identify_audio(tmp_path)
    else:
        raise HTTPException(status_code=400, detail="Metodo non supportato")

    with open(tmp_path, "rb") as f:
        media_url = await upload_to_storage(f.read(), file.filename, station_id)

    # Filtri di confidenza dinamici
    confidence = result.get("confidence", 0.0) if result else 0.0
    species = result.get("species", "Sconosciuta") if result else "Sconosciuta"
    
    if confidence >= CONFIDENCE_THRESHOLDS["auto_confirm"]:
        verification_status = "confirmed"
    elif confidence >= CONFIDENCE_THRESHOLDS["min_acceptable"]:
        verification_status = "pending"
    else:
        verification_status = "excluded"

    # Gestione date dinamica (se non fornita, usa l'ora corrente UTC)
    observation = {
        "species": species,
        "method": method,
        "media_url": media_url,
        "station_id": station_id,
        "confidence": confidence,
        "verification_status": verification_status,
        "date_time": date_time or datetime.now(timezone.utc).isoformat()
    }

    from db import save_observation
    save_res = await save_observation(observation)

    if save_res and save_res.data and len(save_res.data) > 0:
        obs_data = save_res.data[0]
        if obs_data:
            obs_id = obs_data.get("id")
            if obs_id:
                await check_and_create_alert({**observation, "id": obs_id})
                return JSONResponse(content={"observation_id": obs_id, "species": species, "confidence": confidence})

    raise HTTPException(status_code=500, detail="Errore nel salvataggio dell'osservazione")

@app.get("/reports/summary")
async def get_summary_report(station_id: Optional[str] = None):
    try:
        pdf_bytes = await generate_summary_pdf(station_id)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=biodiversity_report{'_'+station_id if station_id else ''}.pdf"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
