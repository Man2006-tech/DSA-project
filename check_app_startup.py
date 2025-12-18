import subprocess
import time
import urllib.request
import json
import sys

def check_app():
    print("Starting App in background...")
    # Start app
    proc = subprocess.Popen([sys.executable, "Backend/app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    try:
        # Wait for init
        print("Waiting for init (5s)...")
        time.sleep(5)
        
        # Test Search
        print("Testing Search API...")
        try:
            url = "http://127.0.0.1:5000/api/search?q=dengue"
            with urllib.request.urlopen(url) as response:
                status = response.getcode()
                print(f"Status: {status}")
                if status == 200:
                    data = json.loads(response.read().decode())
                    print("Response JSON length:", len(data))
                    print("SUCCESS")
                else:
                    print("FAILURE. Status:", status)
        except urllib.error.HTTPError as e:
            print(f"HTTP Failure: {e.code} - {e.read().decode()}")
        except Exception as e:
            print(f"Request Failed: {e}")
            
    finally:
        print("Killing App...")
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=5)
            print("\nAPP STDOUT:\n", stdout[-2000:])
            print("\nAPP STDERR:\n", stderr[-2000:])
        except:
            proc.kill()

if __name__ == "__main__":
    check_app()
