# Monitor Secchia

Sistema intelligente per il monitoraggio della biodiversità osservata nella Cassa di espansione del Secchia.

## Obiettivi
- Raccogliere immagini e suoni da una stazione di monitoraggio (ESP32).
- Identificare le specie tramite API iNaturalist (immagini) e BirdNET (audio).
- Memorizzare le osservazioni in Supabase con metadati (data/ora, station_id, confidence, ecc.).
- Calcolare l'indice di biodiversità (indice di Shannon) e generare alert per specie rare, protette o invasive.
- Visualizzare i dati in una dashboard web (React/Next.js) pubblicata su Vercel.

## Architettura
```
STAZIONE (ESP32) → Backend FastAPI → Supabase → Dashboard
```

- **Stazione**: ESP32 con camera, microfono e sensore PIR, comunica via Wi‑Fi.
- **Backend**: FastAPI, gestisce upload, chiama iNaturalist/BirdNET, salva su Supabase.
- **Database**: Supabase, tabella `osservazioni` (id, species, category, method, media_url, date_time, station_id, confidence, verification_status, source, source_update_date, habitat_zone, coordinates, quality).
- **Dashboard**: React/Next.js, mostra osservazioni, indice, grafici, alert.

## Primo MVP
1. Ricevere file immagine/audio da un client di test.
2. Identificare la specie (iNaturalist / BirdNET).
3. Salvare l'osservazione in Supabase.
4. Visualizzare le osservazioni e l'indice sulla dashboard.

## Prossimi passi
- Configurare il repository GitHub e le credenziali Supabase/Render/Vercel.
- Inizializzare il progetto FastAPI (`backend/`).
- Creare il layout iniziale della dashboard (`frontend/`).
- Preparare dataset demo per la modalità presentazione.
