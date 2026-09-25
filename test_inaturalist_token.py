import urllib.request
import urllib.parse
import os

def get_token_from_env():
    """Cerca il .env nella cartella corrente o in /backend/."""
    paths_to_check = [".env", "backend/.env"]
    
    for path in paths_to_check:
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    for line in f:
                        if line.startswith("INATURALIST_TOKEN="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception as e:
            print(f"Errore lettura {path}: {e}")
    return None

def verify_token():
    token = get_token_from_env()
    
    if not token:
        print("❌ Errore: INATURALIST_TOKEN non trovato in .env né in backend/.env")
        return

    print(f"Verifica token: {token[:10]}...{token[-10:]}")
    
    url = "https://api.inaturalist.org/v1/computervision/score_image"
    
    # Aggiungiamo un User-Agent per evitare che il server ci blocchi come "bot"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    # Creiamo un corpo multipart minimo per simulare l'invio di un'immagine
    boundary = "boundary123"
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"image\"; filename=\"test.jpg\"\r\n"
        f"Content-Type: image/jpeg\r\n\r\n"
        f"fake-image-data\r\n"
        f"--{boundary}--\r\n"
    ).encode('utf-8')
    
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    headers["Content-Length"] = str(len(body))
    
    try:
        print("Invio richiesta di test a iNaturalist (simulando browser)...")
        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            code = response.getcode()
            if code == 200:
                print("✅ TOKEN VALIDO: L'API ha risposto correttamente.")
            else:
                print(f"❓ Risposta inaspettata: {code}")
                
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("❌ TOKEN NON VALIDO: L'API ha restituito 401 Unauthorized.")
        elif e.code == 403:
            print("❌ ACCESSO NEGATO: Il token non ha i permessi (403 Forbidden).")
        elif e.code == 400:
            print("✅ TOKEN VALIDO: L'API ha rifiutato il contenuto (400) ma l'autenticazione è passata!")
        else:
            print(f"❓ Errore HTTP: {e.code}")
            
    except Exception as e:
        print(f"💥 Errore di connessione: {e}")

if __name__ == "__main__":
    verify_token()
