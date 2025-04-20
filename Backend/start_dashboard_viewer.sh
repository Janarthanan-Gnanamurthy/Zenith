#!/bin/bash

# Create required directories
mkdir -p dashboards
mkdir -p templates

# Install required packages if not already installed
pip install flask cloudflared

# Add CLOUDFLARE_TUNNEL_HOSTNAME to .env if not exists
if ! grep -q "CLOUDFLARE_TUNNEL_HOSTNAME" .env; then
  echo "CLOUDFLARE_TUNNEL_HOSTNAME=your-tunnel.trycloudflare.com" >> .env
fi

# Start the dashboard viewer in the background
echo "Starting Dashboard Viewer..."
python dashboard_viewer.py &
DASHBOARD_VIEWER_PID=$!

# Wait for the dashboard viewer to start
sleep 2

# Start Cloudflare tunnel in the foreground
echo "Starting Cloudflare Tunnel..."
echo "This will create a public URL for your dashboard viewer"
echo "Press Ctrl+C to stop the tunnel and dashboard viewer"

# Run cloudflared tunnel
cloudflared tunnel --url http://localhost:8050

# This will be executed when the script is interrupted
trap "kill $DASHBOARD_VIEWER_PID; exit" INT TERM EXIT 