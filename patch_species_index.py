import re

file_path = 'frontend/pages/species/index.jsx'
with open(file_path, 'r') as f:
    content = f.read()

# The problematic block is:
# if (category === "rare" || category === "normal") {
#     return null;
# }

# We want to remove this filtering logic entirely to show all species
pattern = r'if \(category === "rare" \|\| category === "normal"\) \{\s+return null;\s+\}'
replacement = ''

new_content = re.sub(pattern, replacement, content)

with open(file_path, 'w') as f:
    f.write(new_content)

print("Species Index patched successfully.")
