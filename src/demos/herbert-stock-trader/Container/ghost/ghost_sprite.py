"""Ghost sprite — GTK3+Cairo overlay with true RGBA transparency."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import cairo
import math
import time
import random


class GhostSprite:
    """A floating ghost overlay with per-pixel transparency via Cairo."""

    def __init__(self, screen_width, screen_height, size=80, color="#44FF88"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size = size

        # Parse hex color
        self.ghost_rgb = (
            int(color[1:3], 16) / 255.0,
            int(color[3:5], 16) / 255.0,
            int(color[5:7], 16) / 255.0,
        )

        # Position state
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.target_x = self.x
        self.target_y = self.y

        # Animation state
        self._bob_phase = random.uniform(0, math.pi * 2)
        self._wiggle_until = 0
        self._look_dir = 0
        self._blink_until = 0
        self._expression = "normal"
        self._eating_until = 0
        self._eating_phase = 0.0

        # Window dimensions
        self.win_size = size + 60
        self.win_height = self.win_size + 30

        # Create GTK window
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title("DesktopGhostOverlay")
        self.window.set_decorated(False)
        self.window.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.window.set_keep_above(True)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_accept_focus(False)
        self.window.set_resizable(False)

        # Enable RGBA visual for transparency
        screen = self.window.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.window.set_visual(visual)
        self.window.set_app_paintable(True)

        self.window.set_size_request(self.win_size, self.win_height)
        self.window.set_default_size(self.win_size, self.win_height)

        self.window.connect('draw', self._on_draw)
        self.window.connect('realize', self._on_realize)

        self.window.show_all()
        self._update_window_position()

    def _on_realize(self, widget):
        """Make the window click-through after it's realized."""
        try:
            region = cairo.Region()
            self.window.input_shape_combine_region(region)
        except Exception:
            pass

    def _update_window_position(self):
        wx = int(self.x - self.win_size // 2)
        wy = int(self.y - self.win_size // 2 - 10)
        self.window.move(wx, wy)

    def _on_draw(self, widget, cr):
        """Draw the ghost with Cairo — transparent background."""
        # Clear with full transparency
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        s = self.size
        cx = self.win_size / 2.0
        cy = self.win_size / 2.0

        bob = math.sin(self._bob_phase) * 4
        wiggle = 0
        if time.time() < self._wiggle_until:
            wiggle = math.sin(time.time() * 15) * 8

        cy_adj = cy + bob
        cx_adj = cx + wiggle
        half = s / 2.0

        # --- Ghost body ---
        r, g, b = self.ghost_rgb
        cr.set_source_rgba(r, g, b, 0.92)

        # Top dome (semicircle)
        cr.arc(cx_adj, cy_adj - half * 0.1, half, math.pi, 0)

        # Right side down
        right_x = cx_adj + half
        left_x = cx_adj - half
        bottom_y = cy_adj + half * 0.7
        cr.line_to(right_x, bottom_y)

        # Wavy bottom
        wave_count = 4
        wave_amp = s * 0.09
        wave_phase = time.time() * 3
        steps = wave_count * 6
        for i in range(steps + 1):
            frac = i / steps
            wx = right_x - frac * (right_x - left_x)
            wy = bottom_y + math.sin(wave_phase + frac * wave_count * math.pi * 2) * wave_amp
            cr.line_to(wx, wy)

        # Left side back up to dome
        cr.line_to(left_x, cy_adj - half * 0.1)
        cr.close_path()
        cr.fill()

        # --- Eyes ---
        eye_y = cy_adj - s * 0.08
        eye_sep = s * 0.22
        eye_w = s * 0.13
        eye_h = s * 0.17
        is_blinking = time.time() < self._blink_until
        is_eating = time.time() < self._eating_until

        for side in [-1, 1]:
            ex = cx_adj + side * eye_sep
            if is_blinking:
                cr.set_source_rgba(1, 1, 1, 1)
                cr.set_line_width(2)
                cr.move_to(ex - eye_w, eye_y)
                cr.line_to(ex + eye_w, eye_y)
                cr.stroke()
            else:
                # Eye white (ellipse)
                cr.set_source_rgba(1, 1, 1, 1)
                cr.save()
                cr.translate(ex, eye_y)
                cr.scale(eye_w, eye_h)
                cr.arc(0, 0, 1, 0, 2 * math.pi)
                cr.restore()
                cr.fill()

                # Pupil
                pupil_off = self._look_dir * eye_w * 0.35
                pupil_r = eye_w * (0.6 if self._expression in ("mischievous", "eating") else 0.5)
                cr.set_source_rgba(0.07, 0.07, 0.07, 1)
                cr.arc(ex + pupil_off, eye_y, pupil_r, 0, 2 * math.pi)
                cr.fill()

        # --- Mouth ---
        mouth_y = cy_adj + s * 0.14
        if is_eating:
            chomp = abs(math.sin(self._eating_phase * 8)) * s * 0.2
            cr.set_source_rgba(0.08, 0.08, 0.08, 1)
            cr.save()
            cr.translate(cx_adj, mouth_y)
            cr.scale(s * 0.16, max(chomp * 0.6, 2))
            cr.arc(0, 0, 1, 0, 2 * math.pi)
            cr.restore()
            cr.fill()
            # Crumbs
            if chomp > s * 0.06:
                cr.set_source_rgba(0.65, 0.65, 0.65, 0.7)
                for _ in range(4):
                    crumb_x = cx_adj + random.uniform(-s * 0.35, s * 0.35)
                    crumb_y = mouth_y + random.uniform(s * 0.05, s * 0.25)
                    crumb_s = random.uniform(2, 5)
                    cr.rectangle(crumb_x, crumb_y, crumb_s, crumb_s)
                    cr.fill()
        elif self._expression == "mischievous":
            cr.set_source_rgba(0.08, 0.08, 0.08, 1)
            cr.arc(cx_adj, mouth_y, s * 0.12, 0.15, math.pi - 0.15)
            cr.fill()
        elif self._expression == "surprised":
            cr.set_source_rgba(0.08, 0.08, 0.08, 1)
            cr.arc(cx_adj, mouth_y, s * 0.06, 0, 2 * math.pi)
            cr.fill()
        elif self._expression == "sad":
            # Frown — upside-down arc
            cr.set_source_rgba(0.13, 0.33, 0.53, 1)
            cr.set_line_width(2.5)
            cr.arc(cx_adj, mouth_y + s * 0.08, s * 0.1, math.pi + 0.3, 2 * math.pi - 0.3)
            cr.stroke()
            # Tear drops under each eye
            tear_y = eye_y + s * 0.22
            cr.set_source_rgba(0.4, 0.6, 1.0, 0.7)
            for side in [-1, 1]:
                tx = cx_adj + side * eye_sep
                cr.arc(tx, tear_y, s * 0.04, 0, 2 * math.pi)
                cr.fill()
        else:
            cr.set_source_rgba(0.13, 0.53, 0.33, 1)
            cr.set_line_width(2)
            cr.arc(cx_adj, mouth_y - s * 0.02, s * 0.1, 0.3, math.pi - 0.3)
            cr.stroke()

    # --- Public API ---

    def set_target(self, x, y):
        self.target_x = max(self.size, min(x, self.screen_width - self.size))
        self.target_y = max(self.size, min(y, self.screen_height - self.size))

    def set_expression(self, expr):
        """'normal', 'mischievous', 'surprised', 'eating', 'sad'"""
        self._expression = expr

    def start_wiggle(self, duration=2.0):
        self._wiggle_until = time.time() + duration

    def start_eating(self, duration=1.8):
        self._eating_until = time.time() + duration
        self._eating_phase = 0.0
        self._expression = "eating"

    def is_eating(self):
        return time.time() < self._eating_until

    def blink(self):
        self._blink_until = time.time() + 0.15

    def update(self, dt):
        """Update position, animation, and redraw."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 2:
            ease = min(1.0, 4.0 * dt)
            self.x += dx * ease
            self.y += dy * ease
            self._look_dir = (1 if dx > 0 else -1) if abs(dx) > 5 else 0
        else:
            self._look_dir = 0

        self.x += random.uniform(-0.5, 0.5)
        self.y += random.uniform(-0.5, 0.5)
        self._bob_phase += dt * 2.5

        if time.time() < self._eating_until:
            self._eating_phase += dt
        elif self._expression == "eating":
            self._expression = "mischievous"

        if random.random() < dt * 0.3 and not self.is_eating():
            self.blink()

        self._update_window_position()
        self.window.queue_draw()

    def is_near_target(self, threshold=30):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        return math.sqrt(dx * dx + dy * dy) < threshold

    def destroy(self):
        self.window.destroy()
