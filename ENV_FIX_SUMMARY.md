## FIX PER LE VARIABILI D'AMBIENTE HUGGING FACE

### Problema Identificato:
Il sistema stava ancora utilizzando il valore placeholder `'your_huggingface_api_key_here'` dal file `.env` invece del token API reale impostato nel dashboard di Render. Questo causava errori 401 Unauthorized quando si cercava di accedere all'API di Hugging Face.

### Causa Radice:
Il file `/backend/config.py` stava usando `load_dotenv()` senza il parametro `override=False`, il che faceva sì che le variabili nel file `.env` sovrascrivessero le variabili d'ambiente effettive impostate nel sistema (incluse quelle del dashboard di Render).

### Soluzione Applicata:
Modificato `/backend/config.py` linea 5 da:
```python
load_dotenv()
```
a:
```python
load_dotenv(override=False)
```

Con questa modifica:
- Se `HUGGINGFACE_API_KEY` è impostata nell'ambiente effettivo (come nel dashboard di Render), quel valore verrà utilizzato
- Se `HUGGINGFACE_API_KEY` NON è impostata nell'ambiente effettivo, si farà riferimento al valore nel file `.env` (utile per lo sviluppo locale)

### Come Configurare Correttamente il Token su Render:

1. **Ottieni un Token API Valido di Hugging Face con ruolo "Inference"** (il più sicuro e appropriato per il tuo uso):
   - Vai su: https://huggingface.co/settings/tokens
   - Clicca su "New token"
   - Nome: `BIOGLOW-inference-token` (o simile)
   - **Ruolo: Seleziona "Inference"** ← Questa è la scelta ottimale
   - Accesso ai repository: Lascia su "All repositories" (il ruolo "Inference" non può comunque scrivere)
   - Clicca su "Generate a token"
   - **COPIA IMMEDIATAMENTE IL TOKEN** che appare (formato: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

2. **Imposta il Token nel Dashboard di Render:**
   - Vai al tuo servizio BIOGLOW su Render
   - Clicca su "Environment" nel menu laterale
   - Nella sezione "Environment Variables", aggiungi:
     - **Nome**: `HUGGINGFACE_API_KEY`
     - **Valore**: `[incolla_qui_il_token_che_hai_copiato_dal_passo_1]`
   - Clicca su "Save Changes"

3. **Deploya l'Applicazione:**
   - Esegui il push delle modifiche al tuo repository (incluso il fix a config.py)
   - Attiva un redeploy su Render
   - Aspetta che il processo di build e deploy venga completato

### Verifica della Configurazione:
Dopo il deploy, i log dovrebbero mostrare:
- `DEBUG: Hugging Face Inference Client initialized` (invece del warning sulla chiave mancante)
- Nessun più errore `401 Client Error` o `Invalid username or password`
- L'identificazione delle specie dovrebbe iniziare a funzionare correttamente invece di restituire sempre `"Sconosciuta"` con confidenza `0.0`

### Perché il Ruolo "Inference" è la Scelta Ottimale:
- È specificamente progettato per l'API di inferenza (esattamente ciò che il tuo sistema fa)
- È più restrittivo di "Read only" - permette SOLO chiamate di inferenza, niente lettura di metadati
- Massimo livello di sicurezza: anche se qualcuno intercettasse il token, potrebbe solo fare chiamate di inferenza
- Funziona perfettamente con entrambi i modelli che utilizzi:
  - `llava-hf/llava-1.5-7b-hf` per le immagini
  - `MIT/ast-finetuned-audioset` per l'audio

### File Modificati:
- `/backend/config.py` - Aggiunto `override=False` alla chiamata `load_dotenv()`

### Note Importanti:
- Non è necessario modificare il file `.env` locale - il sistema darà priorità alla variabile d'ambiente effettiva
- Il token dovrebbe essere trattato come una credenziale sensibile e non condiviso pubblicamente
- Puoi rinnovare il token periodicamente per motivi di sicurezza aggiuntivi
