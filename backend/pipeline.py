import uuid
import random
import asyncio
import mimetypes
from PIL import Image
import io
import re
from pathlib import Path
from typing import Optional, List
from db import supabase
from config import config
from constants import (
    OBSERVATION_METHODS,
    MOCK_SPECIES_IMAGES,
    MOCK_SPECIES_AUDIO
)
from huggingface_hub import InferenceClient

# Hugging Face API Setup
HF_TOKEN = config.HUGGINGFACE_API_KEY
HF_IMAGE_MODEL = "llava-hf/llava-1.5-7b-hf"
HF_AUDIO_MODEL = "MIT/ast-finetuned-audioset-10-10-0.4593"  # Corrected model ID

# Initialize Hugging Face Inference Client with explicit provider
hf_client = None
if HF_TOKEN:
    hf_client = InferenceClient(provider="hf-inference", token=HF_TOKEN)
    print("DEBUG: Hugging Face Inference Client initialized with hf-inference provider")
else:
    print("DEBUG: WARNING: HUGGINGFACE_API_KEY not found in configuration.")

# Mapping from AudioSet labels to scientific names (for alert matching)
# AudioSet uses English common names, our reference uses scientific names
AUDIOSET_TO_SCIENTIFIC = {
    # Birds from reference lists
    "Bird": "Passer domesticus",  # generic fallback
    "Songbird": "Turdus merula",
    "Raptor": "Buteo buteo",
    "Waterbird": "Anas platyrhynchos",
    # Mammals
    "Rodent": "Rattus norvegicus",
    "Canine": "Vulpes vulpes",
    "Feline": "Felis catus",
    "Ungulate": "Sus scrofa",
    # Amphibians
    "Frog": "Rana temporaria",
    # Insects
    "Insect": "Apis mellifera",
    # Reptiles
    "Snake": "Natrix natrix",
}

# Fallback species lists for demo mode
MOCK_SPECIES_IMAGES = [
    {"species": "Erithacus rubecula", "confidence": 0.85},
    {"species": "Myocastor coypus", "confidence": 0.78},
    {"species": "Ardea cinerea", "confidence": 0.92},
    {"species": "Vulpes vulpes", "confidence": 0.88},
    {"species": "Anas platyrhynchos", "confidence": 0.75},
    {"species": "Alcedo atthis", "confidence": 0.90},
]

MOCK_SPECIES_AUDIO = [
    {"species": "Erithacus rubecula", "confidence": 0.82},
    {"species": "Myocastor coypus", "confidence": 0.76},
    {"species": "Ardea cinerea", "confidence": 0.90},
    {"species": "Vulpes vulpes", "confidence": 0.85},
    {"species": "Anas platyrhynchos", "confidence": 0.72},
    {"species": "Alcedo atthis", "confidence": 0.88},
]

def parse_gemini_response(text):
    """
    Parse Gemini response to extract species and confidence.
    Expected format: "Specie: Nome Specie, Confidenza: 0.85"
    """
    try:
        # Look for patterns like "Specie: ..., Confidenza: ..."
        if "Specie:" in text and "Confidenza:" in text:
            species_part = text.split("Specie:")[1].split("Confidenza:")[0].strip()
            confidence_part = text.split("Confidenza:")[1].strip()
            
            # Extract numeric confidence
            import re
            confidence_match = re.search(r'0\.\d+|1\.00?', confidence_part)
            if confidence_match:
                confidence = float(confidence_match.group())
                return species_part, confidence
        
        # Fallback: try to parse as "Species, confidence"
        parts = text.split(',')
        if len(parts) >= 2:
            species = parts[0].strip()
            try:
                confidence = float(parts[1].strip())
                if 0.0 <= confidence <= 1.0:
                    return species, confidence
            except ValueError:
                pass
                
    except Exception:
        pass
    
    return None, None

async def identify_image(file_path: Path) -> dict:
    print(f"DEBUG: Starting image identification for {file_path.name}")
    
    if config.DEMO_MODE:
        mock = random.choice(MOCK_SPECIES_IMAGES).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        mock["source"] = "Demo Mode (Mock)"
        return mock

    # Use Hugging Face (LLaVA) as Primary
    if hf_client:
        try:
            with open(file_path, "rb") as f:
                img_bytes = f.read()

            print(f"DEBUG: Calling Hugging Face LLaVA for {file_path.name}...")
            
            # Use chat.completions.create with proper image encoding for LLaVA
            # Encode image to base64
            import base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # Prepare messages for chat completion
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is the scientific name of the animal in the image? Give the scientific name and a confidence score between 0 and 1, separated by a comma. For example: 'Erithacus rubecula, 0.85'"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ]
            
            result = hf_client.chat.completions.create(
                messages=messages,
                model=HF_IMAGE_MODEL,
                max_tokens=50
            )
            
            # Extract the generated text
            if hasattr(result, 'choices') and len(result.choices) > 0:
                text = result.choices[0].message.content.strip()
                print(f"DEBUG: HF LLaVA raw response: '{text}'")
                
                # Try to parse the text as "Genus species, confidence"
                parts = text.split(',')
                if len(parts) >= 2:
                    species_candidate = parts[0].strip()
                    try:
                        confidence_candidate = float(parts[1].strip())
                        # Validate confidence is between 0 and 1
                        if 0.0 <= confidence_candidate <= 1.0:
                            species = species_candidate
                            confidence = round(confidence_candidate, 2)
                            return {
                                "species": species,
                                "confidence": confidence,
                                "source": "Hugging Face LLaVA"
                            }
                    except ValueError:
                        pass
                
                # If parsing failed, try to extract scientific name using regex
                # Look for patterns like "Genus species" or "Genus_species"
                import re
                # Pattern for genus species (two words, first capitalized, second lowercase)
                genus_species_pattern = r'\b([A-Z][a-z]+)\s+([a-z]+)\b'
                matches = re.findall(genus_species_pattern, text)
                if matches:
                    # Take the first match that looks like a plausible species
                    for genus, species in matches:
                        candidate = f"{genus} {species}"
                        # Basic validation: common genus/species combinations
                        if len(candidate) > 5:  # reasonable length
                            return {
                                "species": candidate,
                                "confidence": 0.75,  # moderate confidence for regex extraction
                                "source": "Hugging Face LLaVA (regex fallback)"
                            }
                
                # Last resort: return the raw text as species with low confidence
                return {
                    "species": text[:100],  # limit length
                    "confidence": 0.3,
                    "source": "Hugging Face LLaVA (raw response)"
                }
            else:
                print("DEBUG: HF LLaVA returned empty result")
                
        except Exception as e:
            print(f"DEBUG: Hugging Face Image error: {e}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")

    # Fallback to Demo Mode if HF fails
    print("DEBUG: Falling back to Demo Mode for image identification")
    mock = random.choice(MOCK_SPECIES_IMAGES).copy()
    mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
    mock["source"] = "Demo Mode (HF Fallback)"
    return mock

async def identify_audio(file_path: Path) -> dict:
    print(f"DEBUG: Starting audio identification for {file_path.name}")
    
    if config.DEMO_MODE:
        mock = random.choice(MOCK_SPECIES_AUDIO).copy()
        mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
        mock["source"] = "Demo Mode (Mock)"
        return mock

    # Use Hugging Face (AST) as Primary
    if hf_client:
        try:
            with open(file_path, "rb") as f:
                audio_bytes = f.read()

            print(f"DEBUG: Calling Hugging Face AST for {file_path.name}...")
            result = hf_client.audio_classification(
                audio_bytes,
                model=HF_AUDIO_MODEL
            )
            # result is a list of dicts with 'label' and 'score'
            if isinstance(result, list) and len(result) > 0:
                top_match = max(result, key=lambda x: x.get("score", 0))
                audioset_label = top_match.get("label", "Unknown")
                confidence = round(top_match.get("score", 0.0), 2)

                # Map AudioSet label to scientific name if possible
                scientific_name = AUDIOSET_TO_SCIENTIFIC.get(audioset_label, audioset_label)

                return {
                    "species": scientific_name,
                    "confidence": confidence,
                    "source": "Hugging Face AST"
                }
            else:
                print("DEBUG: HF AST returned empty result")
                
        except Exception as e:
            print(f"DEBUG: Hugging Face Audio error: {e}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")

    # Fallback to Demo Mode if HF fails
    print("DEBUG: Falling back to Demo Mode for audio identification")
    mock = random.choice(MOCK_SPECIES_AUDIO).copy()
    mock["confidence"] = round(mock["confidence"] + random.uniform(-0.05, 0.05), 2)
    mock["source"] = "Demo Mode (HF Fallback)"
    return mock
