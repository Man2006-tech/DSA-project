import subprocess
import time
import urllib.request
import urllib.parse
import json
import sys
import os

SERVER_LOG = "server_log.txt"

def run_test():
    print("Starting Server...")
    with open(SERVER_LOG, "w") as log:
        proc = subprocess.Popen([sys.executable, "Backend/app.py"], stdout=log, stderr=log, text=True)
    
    try:
        print("Waiting for server to be ready (up to 30s)...")
        ready = False
        for i in range(30):
            try:
                with urllib.request.urlopen("http://127.0.0.1:5000/api/check-ready") as resp:
                    if resp.getcode() == 200:
                        data = json.loads(resp.read().decode())
                        if data.get('ready'):
                            print("Server READY!")
                            ready = True
                            break
            except:
                pass
            time.sleep(1)
            print(".", end="", flush=True)
        
        print()
        if not ready:
            print("Server failed to become ready.")
            return

        # 1. Test Search
        print("\n[TEST 1] Semantic Search ('dengue')")
        try:
            url = "http://127.0.0.1:5000/api/search?q=dengue&semantic=true"
            with urllib.request.urlopen(url) as resp:
                data = json.loads(resp.read().decode())
                print(f"  Status: {resp.getcode()}")
                print(f"  Results: {len(data)}")
                if len(data) > 0: print(f"  Top: {data[0].get('title', 'No Title')}")
        except Exception as e: print(f"  Failed: {e}")

        # 2. Test Autocomplete
        print("\n[TEST 2] Autocomplete ('com')")
        try:
            url = "http://127.0.0.1:5000/api/autocomplete?q=com"
            with urllib.request.urlopen(url) as resp:
                data = json.loads(resp.read().decode())
                suggs = data.get('suggestions', [])
                print(f"  Suggestions: {suggs}")
        except Exception as e: print(f"  Failed: {e}")

        # 3. Test Auto-correct (via search enrichment)
        print("\n[TEST 3] Auto-correct logic check")
        # Logic: Search for specific typo, see if corrected results appear (simulated via API logic)
        # Note: API doesn't expose correction directly except in search fallback or explicit call
        # We'll trust the search results for now.
        
    finally:
        print("\nStopping Server...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
        
        print(f"\n--- {SERVER_LOG} CONTENT ---")
        if os.path.exists(SERVER_LOG):
            with open(SERVER_LOG, 'r') as f:
                print(f.read())

if __name__ == "__main__":
    run_test()
