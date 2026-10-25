#!/bin/bash

# Simple HTTP server launcher for DM Screen
# This avoids cross-origin issues when opening file:// URLs

echo "🎲 Starting DM Screen HTTP Server..."
echo ""
echo "The server will start at: http://localhost:8000"
echo "Open this URL in your browser: http://localhost:8000/5e_artisanal_database/tools/dmscreen/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd ../../../
python3 -m http.server 8000

