import os

file_path = r"d:\Third Semester\DSA\Project\Search-Engine\DATA\PMC000xxxxxx\PMC176545.txt"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read(1000) # Read first 1000 chars
        print(f"Content of {file_path}:")
        print(content)
except Exception as e:
    print(f"Error reading file: {e}")
