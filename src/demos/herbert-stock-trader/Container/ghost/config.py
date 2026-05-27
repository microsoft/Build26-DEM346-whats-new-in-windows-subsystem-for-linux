"""Ghost configuration — timing, processes, file lists, screen layout."""

# Screen resolution
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_DEPTH = 24

# Ghost movement
GHOST_SPEED = 4            # pixels per frame
GHOST_SIZE = 80            # ghost sprite size in pixels
FRAME_DELAY_MS = 33        # ~30 FPS
MOVE_JITTER = 2            # random pixel offset per frame for organic feel

# State timing (seconds)
ADMIRE_PER_WINDOW = 2.5    # seconds spent looking at each window

# Processes to launch (name, command, xterm_title, font_size)
# font_size=None means use default (11)
# stock_ticker always runs; 2 others are picked from EXTRA_PROCESSES
ALWAYS_ON_PROCESSES = [
    ("stocks", "python3 /opt/ghost/stock_ticker.py", "Stock Trading", None),
]

EXTRA_PROCESSES = [
    ("btop", "btop", "System Monitor", 6),
    ("cmatrix", "cmatrix -b -u 3", "The Matrix", None),
    ("htop", "htop", "Process Manager", None),
    ("pipes", "pipes.sh -t 2 -R -r 4000 -p 5", "Data Pipeline", None),
    ("cbonsai", "cbonsai -l -i -w 5", "Bonsai Growth", None),
]

# Total windows per cycle: len(ALWAYS_ON_PROCESSES) + EXTRA_PER_CYCLE
EXTRA_PER_CYCLE = 2

# xterm geometry and placement — tiled grid, no overlap
# Screen is 1280x720 with ~30px panel at top, so usable area is ~1280x680
# 3 windows tiled: 2 on top row, 1 large on bottom row (or 3 columns)
# Using character geometry (cols x rows) + pixel positions
XTERM_GEOMETRIES = [
    ("75x20", (5, 35)),       # top-left
    ("75x20", (640, 35)),     # top-right
    ("75x18", (5, 385)),      # bottom-left
]

# Legacy — kept for compatibility
XTERM_FONT_SIZE = 12
XTERM_POSITIONS = [pos for _, pos in XTERM_GEOMETRIES]

# File manager target directory — use mounted volume so host can see files
FILE_MANAGER_DIR = "/mnt/herbert/Documents"

# File creation / eating intervals (seconds)
FILE_CREATE_INTERVAL = 10
FILE_EAT_INTERVAL = 7
FILE_EAT_DURATION = 3.0    # how long the eating animation lasts

# Ghost appearance
GHOST_COLOR = "#44FF88"
GHOST_EYE_COLOR = "#FFFFFF"
GHOST_PUPIL_COLOR = "#111111"
GHOST_OPACITY = 0.85
