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

# Mock data fallbacks
MOCK_STATIONS = [
    {
        "id": "SECCHIA-01",
        "name": "Secchia Nord",
        "lat": 44.6472,
        "lon": 10.9258,
        "shannon": 1.45
    },
    {
        "id": "SECCHIA-02",
        "name": "Secchia Centro",
        "lat": 44.6321,
        "lon": 10.9189,
        "shannon": 1.32
    },
    {
        "id": "SECCHIA-03",
        "name": "Secchia Sud",
        "lat": 44.6156,
        "lon": 10.9012,
        "shannon": 1.58
    },
    {
        "id": "SECCHIA-04",
        "name": "Expansione Est",
        "lat": 44.6289,
        "lon": 10.9456,
        "shannon": 1.21
    },
]

# Error messages
ERROR_MESSAGES = {
    "station_not_found": "Stazione non trovata",
    "observation_not_found": "Osservazione non trovata",
    "invalid_method": "Metodo non supportato",
    "missing_verification_status": "Solo verification_status può essere aggiornato",
    "save_failed": "Errore nel salvataggio dell'osservazione",
    "db_connection_failed": "Connessione al database fallita",
}