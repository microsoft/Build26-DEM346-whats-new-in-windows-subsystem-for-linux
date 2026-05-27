#!/bin/bash
set -e

echo "=========================================="
echo "  👻 Desktop Ghost Container Starting"
echo "=========================================="

# Configuration
export DISPLAY=:99
SCREEN_RES="1280x720x24"
VNC_PORT=5900
NOVNC_PORT=6080

# Start WebSocket relay server (always-on, used by stock_ticker and future commands)
echo "[0/8] Starting WebSocket server on port 8765..."
mkfifo /tmp/ws_server.fifo
cd /opt/ghost
python3 ws_server.py &
WS_PID=$!
sleep 1

# Start D-Bus
echo "[1/8] Starting D-Bus..."
mkdir -p /run/dbus
dbus-daemon --system --fork 2>/dev/null || true
eval $(dbus-launch --sh-syntax)

# Start Xvfb (virtual framebuffer)
echo "[2/8] Starting Xvfb on display ${DISPLAY}..."
Xvfb ${DISPLAY} -screen 0 ${SCREEN_RES} -ac +extension GLX +render -noreset &
sleep 2

# Start XFCE4 desktop
echo "[3/8] Starting XFCE4 desktop..."
startxfce4 &
sleep 4

# Set wallpaper if it exists
if [ -f /usr/share/backgrounds/ghost-wallpaper.png ]; then
    xfconf-query --channel xfce4-desktop \
        --property /backdrop/screen0/monitorscreen/workspace0/last-image \
        --set /usr/share/backgrounds/ghost-wallpaper.png --create --type string 2>/dev/null || true
fi

# Start compositor for RGBA transparency support
echo "[4/8] Starting compositor..."
xcompmgr -c -l0 -t0 -r0 -o.00 &
sleep 1

# Start x11vnc
echo "[5/8] Starting VNC server on port ${VNC_PORT}..."
x11vnc -display ${DISPLAY} -forever -shared -rfbport ${VNC_PORT} -nopw -xkb -q &
sleep 1

# Start noVNC
echo "[6/8] Starting noVNC on port ${NOVNC_PORT}..."
# Find noVNC installation
NOVNC_DIR=""
for dir in /usr/share/novnc /usr/share/novnc/utils /opt/novnc; do
    if [ -d "$dir" ]; then
        NOVNC_DIR="$dir"
        break
    fi
done

if [ -n "$NOVNC_DIR" ]; then
    # Use websockify to bridge noVNC to VNC
    websockify --web=${NOVNC_DIR} ${NOVNC_PORT} localhost:${VNC_PORT} &
else
    echo "WARNING: noVNC directory not found, trying websockify standalone..."
    websockify ${NOVNC_PORT} localhost:${VNC_PORT} &
fi
sleep 2

# Populate fake files and launch ghost
echo "[7/8] Populating fake files..."
cd /opt/ghost
python3 -c "import file_manager; file_manager.populate_files()" 2>/dev/null || true

echo "[8/8] Launching the Ghost..."
export NO_AT_BRIDGE=1
python3 ghost.py &
GHOST_PID=$!

echo ""
echo "=========================================="
echo "  👻 Desktop Ghost is LIVE!"
echo ""
echo "  Open http://localhost:${NOVNC_PORT}/vnc.html in your browser"
echo "  (click 'Connect' if prompted)"
echo "=========================================="
echo ""

# Keep container running and forward signals
trap "kill $GHOST_PID $WS_PID 2>/dev/null; exit 0" SIGTERM SIGINT

# Wait for ghost process, restart if it crashes
while true; do
    wait $GHOST_PID 2>/dev/null || true
    echo "Ghost process ended, restarting in 3s..."
    sleep 3
    cd /opt/ghost
    python3 ghost.py &
    GHOST_PID=$!
done
