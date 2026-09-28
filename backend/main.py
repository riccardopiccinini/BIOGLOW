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

async def run_full_pipeline_background(file_path: Path, filename: str, method: str, station_id: str, date_time: str):
    """
    ULTRA-FAST BACKGROUND PIPELINE:
    Everything is moved here to ensure the HTTP response is returned instantly.
    """
    try:
        # 1. Upload to storage (Heavy I/O)
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        media_url = await upload_to_storage(file_bytes, filename, station_id)

        # 2. Save initial record (DB I/O)
        observation = {
            "species": "Analisi in corso...",
            "method": method,
            "media_url": media_url,
            "station_id": station_id,
            "confidence": 0.0,
            "verification_status": "pending",
            "date_time": date_time
        }
        
        save_res = await save_observation(observation)
        if not save_res or not save_res.data:
            print(f"Error saving initial observation for {filename}")
            return

        obs_id = save_res.data[0]["id"]

        # 3. Run AI analysis (Heavy CPU/Network)
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

        # 4. Update the observation with results
        update_data = {
            "species": species,
            "confidence": confidence,
            "verification_status": verification_status
        }
        supabase.table("osservazioni").update(update_data).eq("id", obs_id).execute()
        
        # 5. Trigger alert check
        obs = await get_observation_by_id(obs_id)
        if obs:
            await check_and_create_alert({**obs, "confidence": confidence})

    except Exception as e:
        print(f"Full background pipeline error for {filename}: {e}")
    finally:
        # 6. Clean up temp file
        if file_path.exists():
            file_path.unlink()

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

    # ONLY save file to disk and return immediately.
    # NO upload, NO DB save in the request cycle.
    tmp_path = Path(f"/tmp/{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    final_date = date_time or datetime.now(timezone.utc).isoformat()
    
    # Everything happens in background
    background_tasks.add_task(run_full_pipeline_background, tmp_path, file.filename, method, station_id, final_date)

    # Instant response
    return JSONResponse(content={"status": "queued", "message": "File received. Analysis will start in background."})

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

    processed_count = 0
    for obs in observations_list:
        try:
            import base64
            content = base64.b64decode(obs.get("content_base64", " ")) if "content_base64" in obs else b"dummy data"
            filename = obs.get("filename", "unknown")
            
            tmp_path = Path(f"/tmp/{filename}")
            with open(tmp_path, "wb") as f:
                f.write(content)

            final_date = obs.get("date_time") or datetime.now(timezone.utc).isoformat()
            background_tasks.add_task(run_full_pipeline_background, tmp_path, filename, obs.get("method", "image"), station_id, final_date)
            processed_count += 1
        except Exception as e:
            print(f"Batch queuing error for {obs.get('filename')}: {e}")

    return JSONResponse(content={"processed": processed_count, "status": "queued"})

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
