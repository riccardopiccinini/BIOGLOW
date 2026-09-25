# BIOGLOW — Monitor Secchia

Sistema intelligente per il monitoraggio della biodiversità osservata nella zona della Cassa di Espansione del Secchia. Il progetto trasforma avvistamenti di animali (immagini e suoni) in dati organizzati per analizzare la diversità biologica di un'area.

## 🏗️ Architettura del Sistema

Il flusso dei dati segue questa catena:
**Stazione (ESP32) → Backend (FastAPI) → AI (iNaturalist/BirdNET) → Database (Supabase) → Dashboard (Next.js)**

### Componenti Tecnici
- **Hardware**: Stazione basata su ESP32 con sensore PIR, camera e microfono.
- **Backend**: FastAPI (Python) ospitato su Render. Gestisce l'identificazione e l'archiviazione.
- **Intelligenza Artificiale**: 
  - **Immagini**: API di iNaturalist per l'identificazione delle specie.
  - **Audio**: BirdNET (implementazione locale) per l'analisi dei canti degli uccelli.
- **Database & Storage**: Supabase per la persistenza dei dati e l'archiviazione dei file multimediali.
- **Dashboard**: Interfaccia in Next.js (Vercel) per la visualizzazione di statistiche, grafici e alert.

## 🚀 Stato di Avanzamento (Settembre 2026)

### ✅ Implementato (Software)
- **Pipeline di Riconoscimento**: Integrazione completa con iNaturalist e BirdNET.
- **Analisi Scientifica**: Calcolo automatico dell'Indice di Biodiversità di Shannon.
- **Sistema di Alert**: Rilevamento automatico di specie rare, protette e invasive tramite liste di riferimento.
- **Dashboard**: Visualizzazione in tempo reale di osservazioni, grafici temporali e mappa stazioni.
- **Reportistica**: Generazione automatica di report riassuntivi in PDF.
- **Robustezza**:
  - **Modalità Demo**: Interruttore per l'uso di dati mock per garantire la stabilità durante le presentazioni.
  - **Logica Offline**: Endpoint `/observations/batch` per l'invio di dati accumulati in coda durante i blackout di rete.
- **Validazione**: Tool di test (`backend/test_accuracy.py`) per calcolare la percentuale di errore dell'AI.

### ⏳ In corso / Da completare (Hardware)
- **Assemblaggio Stazione**: Chiusura del case e cablaggio finale dei componenti.
- **Firmware ESP32**: Sviluppo della logica di acquisizione reale (scatto foto/registrazione audio) e invio file al backend.
- **Test sul campo**: Validazione del sistema in ambiente reale.

## 🛠️ Guida Rapida

### Configurazione Backend
1. Installare le dipendenze: `pip install -r backend/requirements.txt`
2. Configurare le variabili d'ambiente in `.env`:
   - `SUPABASE_URL`, `SUPABASE_KEY`
   - `INATURALIST_TOKEN`
   - `DEMO_MODE=true` (per attivare la modalità dimostrazione)
3. Avviare il server: `uvicorn backend.main:app --reload`

### Configurazione Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## 🧬 Nota Scientifica
Il sistema non misura la biodiversità assoluta della riserva, ma l'**Indice di biodiversità osservata**. Per questo motivo, l'indice di Shannon viene calcolato solo su osservazioni con un livello di *confidence* accettabile, escludendo i dati dubbi per evitare di contaminare le analisi.
