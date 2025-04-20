@echo off
ECHO Starting Dashboard Viewer Setup...

REM Create required directories
IF NOT EXIST "dashboards" mkdir dashboards
IF NOT EXIST "templates" mkdir templates

REM Install required packages if not already installed
pip install flask

REM Add CLOUDFLARE_TUNNEL_HOSTNAME to .env if not exists
FINDSTR /C:"CLOUDFLARE_TUNNEL_HOSTNAME" .env > nul
IF %ERRORLEVEL% NEQ 0 (
  ECHO CLOUDFLARE_TUNNEL_HOSTNAME=your-tunnel.trycloudflare.com >> .env
)

REM Start the dashboard viewer
ECHO Starting Dashboard Viewer...
START /B python dashboard_viewer.py

REM Wait for the dashboard viewer to start
TIMEOUT /T 2 /NOBREAK > nul

REM Instructions for Cloudflare tunnel
ECHO.
ECHO ============================================================
ECHO Dashboard viewer is running at http://localhost:8050
ECHO.
ECHO To create a public URL with Cloudflare Tunnels, please:
ECHO 1. Install cloudflared from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
ECHO 2. Run this command in a new terminal:
ECHO    cloudflared tunnel --url http://localhost:8050
ECHO 3. Use the URL provided by cloudflared in your .env file
ECHO ============================================================
ECHO.

REM Keep the window open
ECHO Press Ctrl+C to stop the dashboard viewer
PAUSE > nul 