import re

file_path = 'frontend/pages/species-distinct.js'
with open(file_path, 'r') as f:
    content = f.read()

# Target the specific filtering logic
pattern = r'let filteredByCategory =\s+filterCategory === "all"\s+?\s+?\?\s+speciesList\.filter\(s => s\.category === \'protected\' \|\| s\.category === \'invasive\'\)\s+:\s+filterCategory === "normal"\s+?\s+?\?\s+speciesList\.filter\(\(s\) => s\.category === "normal"\)\s+:\s+speciesList\.filter\(\(s\) => s\.category === filterCategory\);'
replacement = 'let filteredByCategory = filterCategory === "all" ? speciesList : speciesList.filter((s) => s.category === filterCategory);'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(new_content)

print("Frontend patched successfully.")
