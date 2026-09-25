import requests
import os
import sys
from pathlib import Path

# --- CONFIGURAZIONE CLOUD ---
# Sostituisci con l'URL reale del tuo backend su Render (es. https://bioglow-backend.onrender.com)
BACKEND_URL = "https://your-backend-url.onrender.com/observations"
STATION_ID = "SECCHIA-VIRTUAL-01"

def send_observation(file_path, method="image"):
    if not os.path.exists(file_path):
        print(f"❌ File non trovato: {file_path}")
        return

    print(f"🚀 Invio {method} al Cloud (Render) da {file_path}...")
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
        params = {
            'station_id': STATION_ID,
            'method': method
        }
        
        try:
            # Invio diretto al server Render, niente localhost
            response = requests.post(BACKEND_URL, params=params, files=files)
            if response.status_code == 200:
                res_data = response.json()
                print(f"✅ Successo Cloud! Specie: {res_data.get('species')} | Confidenza: {res_data.get('confidence')}")
            else:
                print(f"❌ Errore Server Render {response.status_code}: {response.text}")
        except Exception as e:
            print(f"💥 Errore di connessione al Cloud: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Utilizzo: python simulate_station.py [image|audio] [percorso_file]")
        sys.exit(1)

    method = sys.argv[1]
    file_path = sys.argv[2]
    send_observation(file_path, method)
