import os

search_path = r"d:\Third Semester\DSA\Project\Search-Engine"
target = "dataset.jsonl"

print(f"Searching for {target} in {search_path}...")
found = False
for root, dirs, files in os.walk(search_path):
    if target in files:
        print(f"FOUND: {os.path.join(root, target)}")
        found = True

if not found:
    print("Not found.")
