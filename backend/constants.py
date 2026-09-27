from enum import Enum

class ObservationMethod(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"

CONFIDENCE_THRESHOLDS = {
    "auto_confirm": 0.80,
    "min_acceptable": 0.50,
}

# Configurazione Alert per il backend (necessaria per alerts.py)
ALERT_TYPES = {
    "protected": {"label": "Protetta"},
    "invasive": {"label": "Invasiva"},
    "rare": {"label": "Rara"},
}

# Mock species for fallback/testing (comuni in zona Secchia)
MOCK_SPECIES_IMAGES = [
    {"species": "Passer domesticus", "confidence": 0.92, "source": "Gemini (mock)"},
    {"species": "Turdus merula", "confidence": 0.87, "source": "Gemini (mock)"},
    {"species": "Parus major", "confidence": 0.91, "source": "Gemini (mock)"},
    {"species": "Erithacus rubecula", "confidence": 0.85, "source": "Gemini (mock)"},
    {"species": "Fringilla coelebs", "confidence": 0.89, "source": "Gemini (mock)"},
    {"species": "Sylvia atricapilla", "confidence": 0.83, "source": "Gemini (mock)"},
    {"species": "Phylloscopus collybita", "confidence": 0.88, "source": "Gemini (mock)"},
    {"species": "Motacilla alba", "confidence": 0.90, "source": "Gemini (mock)"},
]

MOCK_SPECIES_AUDIO = [
    {"species": "Cuculus canorus", "confidence": 0.94, "source": "Gemini (mock)"},
    {"species": "Upupa epops", "confidence": 0.91, "source": "Gemini (mock)"},
    {"species": "Luscinia megarhynchos", "confidence": 0.89, "source": "Gemini (mock)"},
    {"species": "Oriolus oriolus", "confidence": 0.86, "source": "Gemini (mock)"},
    {"species": "Corvus corax", "confidence": 0.93, "source": "Gemini (mock)"},
    {"species": "Picus viridis", "confidence": 0.88, "source": "Gemini (mock)"},
    {"species": "Dendrocopos major", "confidence": 0.90, "source": "Gemini (mock)"},
    {"species": "Strix aluco", "confidence": 0.87, "source": "Gemini (mock)"},
]

OBSERVATION_METHODS = {
    "image": "Foto",
    "audio": "Audio"
}
