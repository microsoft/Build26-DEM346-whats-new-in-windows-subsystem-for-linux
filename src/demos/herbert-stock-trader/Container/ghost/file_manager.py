"""File manager — create timestamped report files and eat random ones."""

import os
import random
from datetime import datetime

from config import FILE_MANAGER_DIR


def ensure_directories():
    """Ensure the Documents directory exists."""
    os.makedirs(FILE_MANAGER_DIR, exist_ok=True)


def create_report_file():
    """Create a timestamped report file in Documents. Returns the filepath."""
    ensure_directories()
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"report_{ts}.txt"
    filepath = os.path.join(FILE_MANAGER_DIR, filename)
    with open(filepath, "w") as f:
        f.write(f"Trade Report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 40 + "\n")
        f.write(f"Status: {'COMPLETED' if random.random() > 0.3 else 'PENDING'}\n")
        f.write(f"Trades executed: {random.randint(1, 50)}\n")
        f.write(f"P/L: ${random.uniform(-500, 2000):.2f}\n")
    return filepath


def list_deletable_files():
    """Get a list of files that exist and can be deleted."""
    files = []
    if os.path.exists(FILE_MANAGER_DIR):
        for f in os.listdir(FILE_MANAGER_DIR):
            full = os.path.join(FILE_MANAGER_DIR, f)
            if os.path.isfile(full):
                files.append(full)
    return files


def eat_random_file():
    """Delete a random file from Documents. Returns the filename or None."""
    files = list_deletable_files()
    if not files:
        return None
    filepath = random.choice(files)
    name = os.path.basename(filepath)
    try:
        os.remove(filepath)
        return name
    except OSError:
        return None


def eat_random_file_specific(filepath):
    """Delete a specific file. Returns the filename or None."""
    name = os.path.basename(filepath)
    try:
        os.remove(filepath)
        return name
    except OSError:
        return None


def populate_files():
    """Create a few initial report files so there's something to see."""
    ensure_directories()
    for _ in range(3):
        create_report_file()
