
import urllib.request
import os

url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
filename = "cloudflared.exe"

print(f"Downloading {filename} from {url}...")
try:
    urllib.request.urlretrieve(url, filename)
    print("Download complete!")
except Exception as e:
    print(f"Download failed: {e}")
