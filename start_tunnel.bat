@echo off
echo Starting Cloudflare Tunnel for Veridia Search Engine...
echo.
echo Tunneling http://localhost:5001
echo.
echo ========================================================
echo  LOOK FOR THE URL BELOW (It will look like https://....trycloudflare.com)
echo ========================================================
echo.
cloudflared.exe tunnel --url http://localhost:5001
pause
