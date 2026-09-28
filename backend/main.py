from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Header, Depends, Form, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
import io
import json
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
    station_exists,
    save_observation
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
        return await get_alerts(status)
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

async def run_ai_analysis(observation_id: str, file_path: Path, method: str):
    """Background task to perform AI identification without blocking the HTTP response."""
    try:
        if method == "image":
            result = await identify_image(file_path)
        elif method == "audio":
            result = await identify_audio(file_path)
        else:
            return

        confidence = result.get("confidence", 0.0)
        species = result.get("species", "Sconosciuta")
        
        if confidence >= CONFIDENCE_THRESHOLDS["auto_confirm"]:
            verification_status = "confirmed"
        elif confidence >= CONFIDENCE_THRESHOLDS["min_acceptable"]:
            verification_status = "pending"
        else:
            verification_status = "excluded"

        # Update the observation in DB
        update_data = {
            "species": species,
            "confidence": confidence,
            "verification_status": verification_status
        }
        
        # We use a direct Supabase update since update_observation_status only handles verification_status
        supabase.table("osservazioni").update(update_data).eq("id", observation_id).execute()
        
        # Trigger alert check
        obs = await get_observation_by_id(observation_id)
        if obs:
            await check_and_create_alert({**obs, "confidence": confidence})

        # Clean up temp file
        if file_path.exists():
            file_path.unlink()

    except Exception as e:
        print(f"Background AI Error for obs {observation_id}: {e}")

@app.post("/observations")
async def receive_observation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    method: str = "image",
    station_id: str = Query(...),
    date_time: Optional[str] = None
):
    if not await station_exists(station_id):
        raise HTTPException(status_code=400, detail=f"Stazione {station_id} non valida")

    # 1. Save file to temp path
    tmp_path = Path(f"/tmp/{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    # 2. Upload to permanent storage
    with open(tmp_path, "rb") as f:
        file_bytes = f.read()
        media_url = await upload_to_storage(file_bytes, file.filename, station_id)

    # 3. Save initial observation as "Analyzing..."
    observation = {
        "species": "Analisi in corso...",
        "method": method,
        "media_url": media_url,
        "station_id": station_id,
        "confidence": 0.0,
        "verification_status": "pending",
        "date_time": date_time or datetime.now(timezone.utc).isoformat()
    }

    save_res = await save_observation(observation)
    if not save_res or not save_res.data:
        raise HTTPException(status_code=500, detail="Errore nel salvataggio iniziale dell'osservazione")

    obs_id = save_res.data[0]["id"]

    # 4. Trigger AI analysis in background
    background_tasks.add_task(run_ai_analysis, obs_id, tmp_path, method)

    # 5. Return immediate response to client
    return JSONResponse(content={"observation_id": obs_id, "status": "queued", "species": "Analisi in corso..."})

@app.post("/observations/batch")
async def receive_observations_batch(
    background_tasks: BackgroundTasks,
    station_id: str = Query(...),
    batch_data: str = Form(...)
):
    if not await station_exists(station_id):
        raise HTTPException(status_code=400, detail=f"Stazione {station_id} non valida")

    try:
        observations_list = json.loads(batch_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato batch_data non valido")

    processed_ids = []
    for obs in observations_list:
        try:
            import base64
            content = base64.b64decode(obs.get("content_base64", " ")) if "content_base64" in obs else b"dummy data"
            filename = obs.get("filename", "unknown")
            
            tmp_path = Path(f"/tmp/{filename}")
            with open(tmp_path, "wb") as f:
                f.write(content)

            media_url = await upload_to_storage(content, filename, station_id)

            observation = {
                "species": "Analisi in corso...",
                "method": obs.get("method", "image"),
                "media_url": media_url,
                "station_id": station_id,
                "confidence": 0.0,
                "verification_status": "pending",
                "date_time": obs.get("date_time") or datetime.now(timezone.utc).isoformat()
            }

            save_res = await save_observation(observation)
            if save_res and save_res.data:
                obs_id = save_res.data[0]["id"]
                background_tasks.add_task(run_ai_analysis, obs_id, tmp_path, observation["method"])
                processed_ids.append(obs_id)
        except Exception as e:
            print(f"Batch processing error for {obs.get('filename')}: {e}")

    return JSONResponse(content={"processed": len(processed_ids), "ids": processed_ids})

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
