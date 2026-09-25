"""
Shared constants for the Monitor Secchia Backend
Centralizes configuration to avoid duplication across modules
"""

# Verification status values
VERIFICATION_STATUS = {
    "confirmed": "Confermata",
    "excluded": "Esclusa",
    "pending": "In attesa",
}

# Alert type values
ALERT_TYPES = {
    "protected": "Protetta",
    "invasive": "Invasiva",
    "rare": "Rara",
}

# Observation methods
OBSERVATION_METHODS = {
    "image": "Foto",
    "audio": "Audio",
}

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "auto_confirm": 0.85, # Above this, auto-confirmed
    "min_acceptable": 0.60, # Below this, auto-excluded
}

# Station status thresholds (based on Shannon index)
STATION_STATUS_THRESHOLDS = {
    "alto": 2.0,      # Shannon > 2.0
    "medio": 1.0,     # Shannon 1.0 - 2.0
    "basso": 0.0,     # Shannon < 1.0
}

# Default pagination
DEFAULT_PAGE_LIMIT = 10
MAX_PAGE_LIMIT = 1000

# Default date format
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# Error messages
ERROR_MESSAGES = {
    "station_not_found": "Stazione non trovata",
    "observation_not_found": "Osservazione non trovata",
    "invalid_method": "Metodo non supportato",
    "missing_verification_status": "Solo verification_status può essere aggiornato",
    "save_failed": "Errore nel salvataggio dell'osservazione",
    "db_connection_failed": "Connessione al database fallita",
}
