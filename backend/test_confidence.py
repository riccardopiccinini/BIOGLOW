#!/usr/bin/env python3
"""
Test script to verify confidence distribution in extract_species_from_filename
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pipeline import extract_species_from_filename
import random

# Set seed for reproducible results in this test
random.seed(42)

# Test files from the simulate_esp32.py
test_files = [
    "Erithacus_rubecula_with_cocked_head.jpg",
    "1280px-Myocastor_coypus_-_ragondin.jpg", 
    "Ardea_cinerea_EM1A2714_(27349354381).jpg",
    "Portrait_of_a_red_fox_in_Rautas_fjällurskog_(cropped).jpg",
    "1280px-Male_mallard3.jpg",
    "Alcedo_Atthis.jpg"
]

print("Testing confidence distribution for filename-based identification:")
print("=" * 70)
print(f"{'Filename':<50} {'Species':<25} {'Confidence':<12} {'Status'}")
print("-" * 70)

below_85_count = 0
at_or_above_85_count = 0

for filename in test_files:
    species, confidence = extract_species_from_filename(filename)
    if species is None:
        species = "None"
        confidence = 0.0
    
    status = "BELOW 85% (REVIEW)" if confidence < 0.85 else "AT/ABOVE 85% (AUTO)"
    
    if confidence < 0.85:
        below_85_count += 1
    else:
        at_or_above_85_count += 1
        
    print(f"{filename:<50} {species:<25} {confidence:<12.2f} {status}")

print("-" * 70)
print(f"Summary: {below_85_count} below 85% (require admin review), {at_or_above_85_count} at/above 85% (eligible for auto-confirm)")
print("=" * 70)

# Verify we have some of each for testing
if below_85_count > 0 and at_or_above_85_count > 0:
    print("✅ SUCCESS: Mixed confidence distribution achieved!")
    print("   - Some identifications will require admin confirmation (<85%)")
    print("   - Some identifications can be auto-confirmed (≥85%)")
else:
    print("⚠️  WARNING: Not getting mixed distribution. Try running again with different random seed.")
