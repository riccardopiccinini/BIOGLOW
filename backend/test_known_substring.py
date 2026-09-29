#!/usr/bin/env python3
"""
Test script to verify known species substring matches can be both below and above 85%
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pipeline import extract_species_from_filename
import random

# Set seed for reproducible results
random.seed(456)

# Filenames that should trigger known species substring matches
known_substring_test_files = [
    "snapshot_Erithacus_rubecula_2026.jpg",
    "photo of Myocastor coypus in wetland.png", 
    "Ardea cinerea closeup.jpeg",
    "Vulpes vulpes running through forest.tiff",
    "Anas platyrhynchos flock.bmp",
    "rare Alcedo atthis sighting.gif",
    "ERITHACUS RUBECULA variant.JPG",  # uppercase version
    "myocastor_coypus_alternate.png"   # with underscore
]

print("Testing known species substring matches (should be mixed below/above 85%):")
print("=" * 70)
print(f"{'Filename':<35} {'Species':<25} {'Confidence':<12} {'Status'}")
print("-" * 70)

below_85_count = 0
at_or_above_85_count = 0

for filename in known_substring_test_files:
    species, confidence = extract_species_from_filename(filename)
    if species is None:
        species = "None"
        confidence = 0.0
    
    status = "BELOW 85% (REVIEW)" if confidence < 0.85 else "AT/ABOVE 85% (AUTO)"
    
    if confidence < 0.85:
        below_85_count += 1
    else:
        at_or_above_85_count += 1
        
    print(f"{filename:<35} {species:<25} {confidence:<12.2f} {status}")

print("-" * 70)
print(f"Summary: {below_85_count} below 85% (require admin review), {at_or_above_85_count} at/above 85% (eligible for auto-confirm)")
if below_85_count > 0 and at_or_above_85_count > 0:
    print("✅ SUCCESS: Mixed confidence distribution achieved for substring matches!")
else:
    print("⚠️  Note: May need different random seed to see both ranges")
print("=" * 70)
