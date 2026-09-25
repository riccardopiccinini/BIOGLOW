# Deployment Guide for Monitor Secchia

## Backend (FastAPI)
1. **Set environment variables** in your deployment environment (Render):
   - `SUPABASE_URL`: Project URL of Supabase.
   - `SUPABASE_KEY`: Anon public key of Supabase.
   - `INATURALIST_TOKEN`: Token for iNaturalist API.
   - `DEMO_MODE`: Set to `true` to force mock results, `false` for real AI identification.
2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Run the app**:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```

## Frontend (Next.js)
1. **Set environment variables** in Vercel:
   - `NEXT_PUBLIC_BACKEND_URL`: URL of the FastAPI service on Render.
2. **Deploy to Vercel**:
   - Connect the GitHub repository.
   - Add the environment variables in the dashboard.
   - Deploy the project.

## Supabase
1. **Project Setup**: Create a project at https://supabase.com.
2. **Database**: Run the SQL schema found in `docs/database_schema.sql` in the Supabase SQL Editor.
3. **Storage**: Create a bucket named `observations` (or as specified in `SUPABASE_STORAGE_BUCKET`) and set it to public.

## ESP32 Station
1. **Tools**: Install Arduino IDE or PlatformIO.
2. **Board**: Add ESP32 board support via Board Manager.
3. **Configuration**: Open `hardware/esp32_sketch.ino`, update Wi-Fi credentials and the backend endpoint URL.
4. **Deployment**: Upload the sketch to the ESP32.
5. **Offline Queue**: Ensure the ESP32 logic implements the `/observations/batch` endpoint to avoid data loss during Wi-Fi outages.

## Demo & Validation
- **Demo Mode**: To ensure a flawless presentation, set `DEMO_MODE=true` on the backend. This bypasses network-dependent AI calls and uses internal mock data.
- **Accuracy Tests**: Run `python backend/test_accuracy.py` to validate the current identification accuracy of the system.

---
**Note**: Use a `.env` file for local development and the platform's dashboard for production credentials.
