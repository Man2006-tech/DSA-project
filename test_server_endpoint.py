import requests
import sys

try:
    print("Testing server at http://127.0.0.1:5001/api/search?q=dengue")
    response = requests.get("http://127.0.0.1:5001/api/search?q=dengue")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Results found: {len(data)}")
        if data:
            print(f"First result: {data[0]['title']}")
    else:
        print(f"Error Response: {response.text}")
except Exception as e:
    print(f"Method failed: {e}")
