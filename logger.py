import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, "logs")


def trigger_log_save():
    """Record a scrape trigger as a timestamped file in logs/. Returns the file path."""
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.datetime.now()
    # No ':' in the name so it is also a valid filename on Windows.
    filepath = os.path.join(log_dir, f"{now:%Y-%m-%d_%H-%M-%S-%f}.txt")
    with open(filepath, "w") as f:
        f.write(f"Scrape triggered at {now.isoformat()}\n")
    return filepath
