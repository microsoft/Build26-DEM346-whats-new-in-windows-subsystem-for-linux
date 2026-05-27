"""Actions — xdotool/subprocess wrappers for controlling the desktop."""

import subprocess
import time
import os
import random


def run_cmd(cmd, check=False):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return ""


def move_mouse(x, y):
    """Instantly move mouse to position."""
    run_cmd(f"xdotool mousemove {int(x)} {int(y)}")


def move_mouse_smooth(x, y, steps=30, delay=0.015):
    """Move mouse smoothly to a position with easing."""
    current = run_cmd("xdotool getmouselocation --shell")
    cx, cy = 0, 0
    for line in current.split("\n"):
        if line.startswith("X="):
            cx = int(line.split("=")[1])
        elif line.startswith("Y="):
            cy = int(line.split("=")[1])

    for i in range(1, steps + 1):
        t = i / steps
        # Ease in-out
        t = t * t * (3 - 2 * t)
        nx = cx + (x - cx) * t + random.uniform(-1, 1)
        ny = cy + (y - cy) * t + random.uniform(-1, 1)
        run_cmd(f"xdotool mousemove {int(nx)} {int(ny)}")
        time.sleep(delay)


def click(button=1):
    """Click mouse button."""
    run_cmd(f"xdotool click {button}")


def double_click(button=1):
    """Double-click mouse button."""
    run_cmd(f"xdotool click --repeat 2 --delay 100 {button}")


def right_click():
    """Right-click."""
    click(3)


def type_text(text, delay_ms=50):
    """Type text using xdotool."""
    run_cmd(f"xdotool type --delay {delay_ms} '{text}'")


def press_key(key):
    """Press a key (e.g., 'Return', 'Delete', 'Tab')."""
    run_cmd(f"xdotool key {key}")


def press_keys(*keys):
    """Press a key combination (e.g., 'ctrl+a')."""
    combo = "+".join(keys)
    run_cmd(f"xdotool key {combo}")


def launch_xterm(title, command, geometry="80x24", position=None, font_size=11):
    """Launch a command in an xterm window. Returns the window ID."""
    pos_arg = ""
    if position:
        pos_arg = f"-geometry +{position[0]}+{position[1]}"

    cmd = (
        f'xterm -bg black -fg green -fa "DejaVu Sans Mono" -fs {font_size} '
        f'-T "{title}" -geometry {geometry} {pos_arg} '
        f'-e "bash -c \\"{command}; sleep 9999\\"" &'
    )
    subprocess.Popen(cmd, shell=True, env={**os.environ, "DISPLAY": ":99"})
    time.sleep(0.5)

    # Get the window ID for the new xterm
    wid = run_cmd(f'xdotool search --name "{title}" | tail -1')
    return wid


def open_thunar(directory):
    """Open the Thunar file manager to a specific directory."""
    subprocess.Popen(
        f'thunar "{directory}" &',
        shell=True,
        env={**os.environ, "DISPLAY": ":99"},
    )
    time.sleep(2)
    wid = run_cmd('xdotool search --name "File Manager" | tail -1')
    if not wid:
        wid = run_cmd('xdotool search --class "Thunar" | tail -1')
    return wid


def close_window(window_id=None):
    """Close a window."""
    if window_id:
        run_cmd(f"xdotool windowactivate {window_id}")
        time.sleep(0.2)
    run_cmd("xdotool key alt+F4")


def get_window_geometry(window_id):
    """Get window position and size. Returns (x, y, w, h) or None."""
    if not window_id:
        return None
    output = run_cmd(f"xdotool getwindowgeometry --shell {window_id}")
    info = {}
    for line in output.split("\n"):
        if "=" in line:
            k, v = line.split("=", 1)
            try:
                info[k.strip()] = int(v.strip())
            except ValueError:
                pass

    x = info.get("X")
    y = info.get("Y")
    w = info.get("WIDTH")
    h = info.get("HEIGHT")

    if x is not None and y is not None and w is not None and h is not None:
        return (x, y, w, h)
    return None


def activate_window(window_id):
    """Bring a window to front and focus it."""
    if window_id:
        run_cmd(f"xdotool windowactivate --sync {window_id}")
        time.sleep(0.3)


def list_windows():
    """List all visible windows. Returns list of (id, title)."""
    output = run_cmd("wmctrl -l")
    windows = []
    for line in output.split("\n"):
        if line.strip():
            parts = line.split(None, 3)
            if len(parts) >= 4:
                wid = parts[0]
                title = parts[3]
                windows.append((wid, title))
    return windows


def move_window(window_id, x, y, w=None, h=None):
    """Move (and optionally resize) a window."""
    if not window_id:
        return
    if w and h:
        run_cmd(f"wmctrl -i -r {window_id} -e 0,{x},{y},{w},{h}")
    else:
        run_cmd(f"wmctrl -i -r {window_id} -e 0,{x},{y},-1,-1")


def kill_all_xterms():
    """Kill all xterm windows."""
    run_cmd("pkill -f xterm || true")


def get_mouse_position():
    """Get current mouse position as (x, y)."""
    output = run_cmd("xdotool getmouselocation --shell")
    x, y = 0, 0
    for line in output.split("\n"):
        if line.startswith("X="):
            x = int(line.split("=")[1])
        elif line.startswith("Y="):
            y = int(line.split("=")[1])
    return (x, y)
