#!/usr/bin/env python3
"""
Test script to verify flexible match confidence range (should all be below 85%)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pipeline import extract_species_from_filename
import random

# Set seed for reproducible results
random.seed(123)

# Filenames that should trigger the flexible match pattern (Genus species with space)
flexible_test_files = [
    "Erithacus rubecula.jpg",
    "Myocastor coypus.png", 
    "Ardea cinerea.jpeg",
    "Vulpes vulpes.tiff",
    "Anas platyrhynchos.bmp",
    "Alcedo atthis.gif"
]

print("Testing flexible match confidence distribution (should ALL be below 85%):")
print("=" * 65)
print(f"{'Filename':<25} {'Species':<25} {'Confidence':<12} {'Status'}")
print("-" * 65)

all_below_85 = True

for filename in flexible_test_files:
    species, confidence = extract_species_from_filename(filename)
    if species is None:
        species = "None"
        confidence = 0.0
    
    status = "BELOW 85% (REVIEW)" if confidence < 0.85 else "AT/ABOVE 85% (AUTO)"
    
    if confidence >= 0.85:
        all_below_85 = False
        
    print(f"{filename:<25} {species:<25} {confidence:<12.2f} {status}")

print("-" * 65)
if all_below_85:
    print("✅ SUCCESS: All flexible matches are below 85% (require admin review)")
    print("   This guarantees test cases for admin confirmation workflow")
else:
    print("❌ ISSUE: Some flexible matches are at/above 85%")
print("=" * 65)
