import urllib.request
import urllib.error

def probe(url):
    print(f"Probing {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            print(f"  [OK] Status: {response.status}")
            print(f"  Content: {response.read().decode()[:100]}...")
    except urllib.error.HTTPError as e:
        print(f"  [ERR] HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"  [ERR] Connection failed: {e}")

probe("http://127.0.0.1:5001/")
probe("http://127.0.0.1:5001/api/check-ready")
probe("http://127.0.0.1:5001/api/debug")
