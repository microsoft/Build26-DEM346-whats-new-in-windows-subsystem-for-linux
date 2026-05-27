"""Desktop Ghost — Main controller.

Ties together the ghost sprite, state machine, and actions to create
an autonomous ghost that haunts a Linux desktop.
"""

import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from config import SCREEN_WIDTH, SCREEN_HEIGHT, GHOST_SIZE, GHOST_COLOR, FRAME_DELAY_MS, FILE_CREATE_INTERVAL
from ghost_sprite import GhostSprite
from state_machine import GhostStateMachine
import file_manager as fm


def wait_for_desktop():
    """Wait until the XFCE desktop is ready."""
    import subprocess

    print("Waiting for desktop to be ready...")
    for attempt in range(60):
        try:
            result = subprocess.run(
                ["xdotool", "search", "--name", "Desktop"],
                capture_output=True, text=True, timeout=5,
                env={**os.environ, "DISPLAY": ":99"},
            )
            if result.stdout.strip():
                print(f"Desktop ready after {attempt + 1} attempts.")
                return True
        except (subprocess.TimeoutExpired, Exception):
            pass
        time.sleep(1)

    print("Desktop detection timed out, proceeding anyway...")
    return True


def main():
    print("=" * 50)
    print("  👻 Desktop Ghost Starting...")
    print("=" * 50)

    os.environ["DISPLAY"] = ":99"

    wait_for_desktop()
    time.sleep(3)

    print("Creating ghost sprite (GTK3+Cairo)...")
    ghost = GhostSprite(
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        size=GHOST_SIZE,
        color=GHOST_COLOR,
    )

    print("Initializing state machine...")
    sm = GhostStateMachine(ghost)

    print("Ghost is now haunting the desktop!")
    print("Open http://localhost:6080/vnc.html in your browser.")

    # Run state machine in a background thread so blocking calls
    # (xdotool, time.sleep) don't freeze the ghost animation.
    def sm_loop():
        while True:
            try:
                sm.update()
            except Exception as e:
                print(f"State machine error: {e}")
            time.sleep(0.05)

    sm_thread = threading.Thread(target=sm_loop, daemon=True)
    sm_thread.start()

    # Background timer: create a report file every FILE_CREATE_INTERVAL seconds
    def create_loop():
        while True:
            time.sleep(FILE_CREATE_INTERVAL)
            try:
                path = fm.create_report_file()
                print(f"📄 Created: {os.path.basename(path)}")
            except Exception as e:
                print(f"File create error: {e}")

    threading.Thread(target=create_loop, daemon=True).start()

    # Ghost animation on the GTK main loop
    last_time = [time.time()]

    def tick():
        now = time.time()
        dt = now - last_time[0]
        last_time[0] = now
        try:
            ghost.update(dt)
        except Exception as e:
            print(f"Animation error: {e}")
        return True  # keep calling

    GLib.timeout_add(FRAME_DELAY_MS, tick)

    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\nGhost has been exorcised! 👻💨")
        ghost.destroy()


if __name__ == "__main__":
    main()
