"""State machine for the ghost's behavior cycle.

Launch all windows + Thunar instantly on startup, then float between windows.
Every FILE_EAT_INTERVAL seconds the ghost flies to the file manager, selects
the target file in Thunar, eats it with a 3-second animation, then resumes.
"""

import time
import random
import os

from config import (
    ALWAYS_ON_PROCESSES,
    EXTRA_PROCESSES,
    EXTRA_PER_CYCLE,
    XTERM_GEOMETRIES,
    ADMIRE_PER_WINDOW,
    FILE_MANAGER_DIR,
    FILE_EAT_INTERVAL,
    FILE_EAT_DURATION,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
import actions
import file_manager as fm


class State:
    LAUNCHING = "LAUNCHING_PROCESSES"
    FLOATING = "FLOATING"
    MOVE_TO_EAT = "MOVE_TO_EAT"
    EATING = "EATING"
    POST_EAT = "POST_EAT"
    SCOLDED = "SCOLDED"


SIGNAL_FILE = "/tmp/go_back_to_work"


class GhostStateMachine:
    """Controls the ghost's behavior cycle."""

    def __init__(self, ghost_sprite):
        self.ghost = ghost_sprite
        self.state = State.LAUNCHING
        self.state_start = time.time()
        self.launched_windows = []  # (window_id, title)
        self.thunar_wid = None
        self._float_index = -1
        self._last_eat_time = time.time()
        self._eat_filepath = None

        # Seed a few initial report files
        fm.populate_files()

        # Clear stale signal file on startup
        self._clear_signal()

        # Pick processes (launched once, kept open forever)
        extras = list(EXTRA_PROCESSES)
        random.shuffle(extras)
        self._processes_to_launch = list(ALWAYS_ON_PROCESSES) + extras[:EXTRA_PER_CYCLE]

    def _elapsed(self):
        return time.time() - self.state_start

    def _enter_state(self, new_state):
        self.state = new_state
        self.state_start = time.time()

    def _check_scold_signal(self):
        """Check if the go_back_to_work signal was recently sent."""
        try:
            if os.path.exists(SIGNAL_FILE):
                with open(SIGNAL_FILE, "r") as f:
                    ts = float(f.read().strip())
                # Only honor signals less than 5 seconds old
                if time.time() - ts < 5.0:
                    self._clear_signal()
                    return True
                # Stale signal, clean it up
                self._clear_signal()
        except (ValueError, OSError):
            self._clear_signal()
        return False

    def _clear_signal(self):
        """Remove the signal file."""
        try:
            if os.path.exists(SIGNAL_FILE):
                os.remove(SIGNAL_FILE)
        except OSError:
            pass

    def _get_window_top_right(self, window_id):
        geom = actions.get_window_geometry(window_id)
        if geom:
            x, y, w, h = geom
            return (x + w + 10, y - 10)
        return None

    def update(self):
        if self.state == State.LAUNCHING:
            self._update_launching()
        elif self.state == State.FLOATING:
            self._update_floating()
        elif self.state == State.MOVE_TO_EAT:
            self._update_move_to_eat()
        elif self.state == State.EATING:
            self._update_eating()
        elif self.state == State.POST_EAT:
            self._update_post_eat()
        elif self.state == State.SCOLDED:
            self._update_scolded()

    # ---- Launch everything instantly ----

    def _update_launching(self):
        self.ghost.set_expression("normal")

        # Launch all xterm windows at once
        for i, proc in enumerate(self._processes_to_launch):
            name, cmd, title = proc[0], proc[1], proc[2]
            font_size = proc[3] if len(proc) > 3 and proc[3] else 11

            if i < len(XTERM_GEOMETRIES):
                geom_str, pos = XTERM_GEOMETRIES[i]
            else:
                geom_str, pos = "75x20", (100, 100)

            wid = actions.launch_xterm(title, cmd, geometry=geom_str, position=pos, font_size=font_size)
            if wid:
                self.launched_windows.append((wid, title))
                tile_w = 630
                tile_h = 340 if pos[1] < 200 else 310
                actions.move_window(wid, pos[0], pos[1], tile_w, tile_h)

        # Open Thunar immediately
        fm.ensure_directories()
        self.thunar_wid = actions.open_thunar(FILE_MANAGER_DIR)
        if self.thunar_wid:
            actions.move_window(self.thunar_wid, 640, 385, 630, 310)

        self._last_eat_time = time.time()
        self._enter_state(State.FLOATING)

    # ---- Float between windows, periodically eat a file ----

    def _update_floating(self):
        self.ghost.set_expression("normal")

        # Check if it's time to eat
        if time.time() - self._last_eat_time >= FILE_EAT_INTERVAL:
            files = fm.list_deletable_files()
            if files:
                self._eat_filepath = random.choice(files)
                self.ghost.set_expression("mischievous")
                self._enter_state(State.MOVE_TO_EAT)
                return
            self._last_eat_time = time.time()

        # Float between xterm windows
        if self.launched_windows:
            idx = int(self._elapsed() / ADMIRE_PER_WINDOW) % len(self.launched_windows)
            if idx != self._float_index:
                self._float_index = idx
                wid, _ = self.launched_windows[idx]
                tr = self._get_window_top_right(wid)
                if tr:
                    self.ghost.set_target(tr[0], tr[1])

    # ---- Fly to Thunar, select file, then eat it ----

    def _update_move_to_eat(self):
        # Check if scolded before eating
        if self._check_scold_signal():
            self._enter_scolded()
            return

        if self._elapsed() < 0.1:
            # First frame: activate Thunar, select the target file via xdotool type-ahead
            if self.thunar_wid:
                actions.activate_window(self.thunar_wid)
                # Thunar supports type-ahead search: typing the filename selects it
                if self._eat_filepath:
                    basename = os.path.basename(self._eat_filepath)
                    actions.type_text(basename, delay_ms=20)

            # Move ghost toward the Thunar window center
            if self.thunar_wid:
                fm_geom = actions.get_window_geometry(self.thunar_wid)
                if fm_geom:
                    fm_x, fm_y, fm_w, fm_h = fm_geom
                    self.ghost.set_target(fm_x + fm_w // 2, fm_y + fm_h // 2)
            return

        # Wait for ghost to arrive, then start eating animation
        if self._elapsed() > 1.5:
            self.ghost.start_eating(FILE_EAT_DURATION)
            self._enter_state(State.EATING)

    def _update_eating(self):
        if not self.ghost.is_eating():
            # Eating animation finished — actually delete the file
            if self._eat_filepath:
                name = fm.eat_random_file_specific(self._eat_filepath)
                if name:
                    print(f"👻 Ate: {name}")
                self._eat_filepath = None

            # Refresh Thunar so the deleted file disappears
            if self.thunar_wid:
                actions.activate_window(self.thunar_wid)
                actions.press_key("F5")
                time.sleep(0.3)

            self._enter_state(State.POST_EAT)

    def _update_post_eat(self):
        if self._elapsed() > 0.5:
            self._last_eat_time = time.time()
            self._float_index = -1
            self._enter_state(State.FLOATING)

    # ---- Scolded: look sad, then fly back to work ----

    def _enter_scolded(self):
        """Transition to the scolded state — cancel eating intent."""
        self._eat_filepath = None
        self._last_eat_time = time.time()
        self._float_index = -1
        self.ghost.set_expression("sad")
        print("👻 Herbert was scolded! Going back to work...")
        self._enter_state(State.SCOLDED)

    def _update_scolded(self):
        # Show sad face for 2 seconds, then fly back to first window
        if self._elapsed() > 2.0:
            if self.launched_windows:
                wid, _ = self.launched_windows[0]
                tr = self._get_window_top_right(wid)
                if tr:
                    self.ghost.set_target(tr[0], tr[1])
            self.ghost.set_expression("normal")
            self._enter_state(State.FLOATING)
