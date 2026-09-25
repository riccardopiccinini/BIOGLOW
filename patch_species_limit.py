import re

file_path = 'frontend/pages/species/index.jsx'
with open(file_path, 'r') as f:
    content = f.read()

# Update the SWR call to include a higher limit
pattern = r'useSWR\("/observations", jsonFetcher\)'
replacement = 'useSWR("/observations?limit=1000", jsonFetcher)'

new_content = re.sub(pattern, replacement, content)

with open(file_path, 'w') as f:
    f.write(new_content)

print("Species limit patched successfully.")
