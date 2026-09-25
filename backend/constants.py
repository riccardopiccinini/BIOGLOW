from enum import Enum

class ObservationMethod(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"

CONFIDENCE_THRESHOLDS = {
    "auto_confirm": 0.90,
    "min_acceptable": 0.70,
}

# Mock species for fallback/testing (comuni in zona Secchia)
MOCK_SPECIES_IMAGES = [
    {"species": "Passer domesticus", "confidence": 0.92, "source": "iNaturalist (mock)"},
    {"species": "Turdus merula", "confidence": 0.87, "source": "iNaturalist (mock)"},
    {"species": "Parus major", "confidence": 0.91, "source": "iNaturalist (mock)"},
    {"species": "Erithacus rubecula", "confidence": 0.85, "source": "iNaturalist (mock)"},
    {"species": "Fringilla coelebs", "confidence": 0.89, "source": "iNaturalist (mock)"},
    {"species": "Sylvia atricapilla", "confidence": 0.83, "source": "iNaturalist (mock)"},
    {"species": "Phylloscopus collybita", "confidence": 0.88, "source": "iNaturalist (mock)"},
    {"species": "Motacilla alba", "confidence": 0.90, "source": "iNaturalist (mock)"},
]

MOCK_SPECIES_AUDIO = [
    {"species": "Cuculus canorus", "confidence": 0.94, "source": "BirdNET (mock)"},
    {"species": "Upupa epops", "confidence": 0.91, "source": "BirdNET (mock)"},
    {"species": "Luscinia megarhynchos", "confidence": 0.89, "source": "BirdNET (mock)"},
    {"species": "Oriolus oriolus", "confidence": 0.86, "source": "BirdNET (mock)"},
    {"species": "Corvus corax", "confidence": 0.93, "source": "BirdNET (mock)"},
    {"species": "Picus viridis", "confidence": 0.88, "source": "BirdNET (mock)"},
    {"species": "Dendrocopos major", "confidence": 0.90, "source": "BirdNET (mock)"},
    {"species": "Strix aluco", "confidence": 0.87, "source": "BirdNET (mock)"},
]

OBSERVATION_METHODS = {
    "image": "Foto",
    "audio": "Audio"
}
