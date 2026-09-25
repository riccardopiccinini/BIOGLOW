# 🚀 BIOGLOW Mission Control: Final Checklist

This document is your master guide to moving the project from "code" to "deployed product". Follow these steps in order.

## 1. Cloud Infrastructure (The Brain)
- [ ] **Render Backend**: 
    - Push all changes to GitHub.
    - Go to Render Dashboard $\rightarrow$ Environment Variables.
    - Add/Verify: `SUPABASE_URL`, `SUPABASE_KEY`, `INATURALIST_TOKEN`.
    - Set `DEMO_MODE=false` for real tests, `DEMO_MODE=true` for the final presentation.
- [ ] **Supabase**:
    - Ensure the `observations` and `alerts` tables are created (via `docs/database_schema.sql`).
    - Create a public storage bucket named `observations`.
- [ ] **Vercel Dashboard**:
    - Ensure `NEXT_PUBLIC_BACKEND_URL` points to your Render URL.

## 2. Hardware Deployment (The Eyes)
- [ ] **ESP32 Configuration**:
    - Open `hardware/esp32_sketch.ino`.
    - Enter your Wi-Fi `ssid` and `password`.
    - Set `serverUrl` to your Render URL (ending in `/observations`).
    - Set `stationId` (e.g., `SECCHIA-01`).
- [ ] **Flashing**:
    - Upload the sketch to the ESP32-CAM using Arduino IDE.
    - Test with Serial Monitor to ensure it says "WiFi connected!" and "Camera initialized!".

## 3. Validation & Testing
- [ ] **Accuracy Check**:
    - Put 10-20 real images/audio in `backend/tests/`.
    - Run `python backend/test_accuracy.py`.
    - Note the percentage for the judges.
- [ ] **End-to-End Test**:
    - Trigger the PIR sensor on the hardware.
    - Open the Dashboard $\rightarrow$ Verify the observation appears in real-time.
    - Check the "Alerts" section if you used a rare species.

## 4. Final Presentation Mode
- [ ] **Safety Switch**: 
    - 15 minutes before the demo, set `DEMO_MODE=true` on Render.
    - This ensures that even if the Wi-Fi is slow, the system will react instantly with mock data.
- [ ] **Report Check**:
    - Click "Scarica Report (PDF)" on the dashboard to make sure the PDF is generated correctly for the station.

---
**Emergency Kit**:
- If the backend is slow $\rightarrow$ Check Render logs for "Out of Memory".
- If the ESP32 doesn't send $\rightarrow$ Check if the Wi-Fi signal is strong enough at the site.
- If the Dashboard is empty $\rightarrow$ Check if `NEXT_PUBLIC_BACKEND_URL` is correct.
