from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid

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

@app.get("/observations/stats")
async def observations_stats():
    from supabase import create_client
    import os
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    total_res = supabase.table("osservazioni").select("id", count="exact").execute()
    total = total_res.count if hasattr(total_res, "count") else 0
    species_res = supabase.table("osservazioni").select("species").execute()
    species_set = set(item["species"] for item in species_res.data if item.get("species"))
    species_count = len(species_set)
    from biodiversity import compute_shannon
    shannon = await compute_shannon()
    return {"total_observations": total, "species_count": species_count, "shannon_index": shannon}

@app.post("/observations")
async def receive_observation(file: UploadFile = File(...), method: str = "image"):
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    from pathlib import Path
    if method == "image":
        result = await identify_image(Path(tmp_path))
    elif method == "audio":
        result = await identify_audio(Path(tmp_path))
    else:
        raise HTTPException(status_code=400, detail="Unsupported method")
    observation = {
        "species": result["species"],
        "category": None,
        "method": method,
        "media_url": f"{file.filename}",
        "date_time": None,
        "station_id": "SECCHIA-01",
        "confidence": result["confidence"],
        "verification_status": "pending",
        "source": result["source"],
        "source_update_date": result.get("source_update_date"),
        "habitat_zone": None,
        "coordinates": None,
        "quality": None,
    }
    save_res = await save_observation(observation)
    from alerts import check_and_create_alert
    await check_and_create_alert({**observation, "id": save_res.data[0]["id"]} if save_res.data else observation)
    return JSONResponse(content={"observation_id": save_res.data[0]["id"] if save_res.data else None, "species": result["species"], "confidence": result["confidence"]})
