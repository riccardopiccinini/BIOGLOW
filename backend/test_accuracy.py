import asyncio
import os
from pathlib import Path
from pipeline import identify_image, identify_audio

# Configurazione test: (Percorso file, Specie corretta)
TEST_IMAGES = [
    ("tests/images/passero.jpg", "Passer domesticus"),
    ("tests/images/merlo.jpg", "Turdus merula"),
    # Aggiungere qui gli altri 18 campioni
]

TEST_AUDIO = [
    ("tests/audio/cuculo.wav", "Cuculus canorus"),
    ("tests/audio/upupa.wav", "Upupa epops"),
    # Aggiungere qui gli altri 18 campioni
]

async def run_accuracy_test(test_set, identify_fn, label="Immagini"):
    print(f"\n--- Test Accuratezza {label} ---")
    correct = 0
    total = len(test_set)
    
    if total == 0:
        print("Nessun campione trovato per il test.")
        return 0.0

    for path, expected in test_set:
        full_path = Path(__file__).parent / path
        if not full_path.exists():
            print(f"File mancante: {path}")
            continue
            
        result = await identify_fn(full_path)
        predicted = result.get("species", "Sconosciuta")
        
        is_correct = predicted.lower() == expected.lower()
        if is_correct:
            correct += 1
            
        status = "✅" if is_correct else "❌"
        print(f"{status} File: {path} | Atteso: {expected} | Ricevuto: {predicted} (Conf: {result.get('confidence', 0)})")

    accuracy = (correct / total) * 100
    print(f"\nRisultato finale {label}: {correct}/{total} correct - Accuratezza: {accuracy:.2f}%")
    return accuracy

async def main():
    print("Inizio test di accuratezza BIOGLOW...")
    
    # Crea cartelle di test se non esistono
    (Path(__file__).parent / "tests" / "images").mkdir(parents=True, exist_ok=True)
    (Path(__file__).parent / "tests" / "audio").mkdir(parents=True, exist_ok=True)
    
    img_acc = await run_accuracy_test(TEST_IMAGES, identify_image, "Immagini")
    aud_acc = await run_accuracy_test(TEST_AUDIO, identify_audio, "Audio")
    
    print("\n========================================")
    print(f"ACCURATEZZA TOTALE SISTEMA: {((img_acc + aud_acc) / 2):.2f}%")
    print("========================================\n")

if __name__ == "__main__":
    asyncio.run(main())
