# Deployment Guide for Monitor Secchia

## Backend (FastAPI)
1. **Set environment variables** in your deployment environment (Render, Railway, etc.):
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `INATURALIST_TOKEN`
   - `BIRDNET_API`
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app** (Render will use `uvicorn`):
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
   - Ensure the `$PORT` variable is provided by the platform.

## Frontend (Next.js)
1. **Set environment variables** (optional, for API URL):
   - `NEXT_PUBLIC_BACKEND_URL` – URL of the FastAPI service.
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Deploy to Vercel**:
   - Connect the GitHub repository.
   - In Vercel dashboard, add the `NEXT_PUBLIC_BACKEND_URL` under Environment Variables.
   - Deploy the project.

## Supabase
1. **Create a new project** at https://supabase.com.
2. **Run the SQL schema** located at `docs/database_schema.sql` in the Supabase SQL editor.
3. **Enable `REST` and `Realtime`** if you want live updates on the dashboard.
4. **Copy the `anon` public API key** and the project URL – they will be used as `SUPABASE_KEY` and `SUPABASE_URL`.

## ESP32 Station
1. Install the Arduino IDE or PlatformIO.
2. Add the ESP32 board manager (`https://raw.githubusercontent.com/espressif/arduino-esp32/gh‑pages/package_esp32_index.json`).
3. Open `hardware/esp32_sketch.ino`.
4. Fill in your Wi‑Fi credentials and the backend URL.
5. Compile and upload to the ESP32.

## Demo Mode
- Run the demo script to preload mock data:
  ```bash
  python -m backend.demo
  ```
- The dashboard will now display the pre‑filled observations even without a live ESP32.

## Monitoring & Logs
- Backend logs can be viewed in Render’s dashboard.
- Supabase provides query logs and realtime replication status.
- The ESP32 prints connection status to the serial console.

---
**Note**: Replace placeholder values with your actual credentials before deploying.
