"""storage.py - JSON file persistence for CampusFlow tickets.
Implements F7 (Persistence) adhering to PRD Section 8 and Section 10.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_STORAGE_PATH = os.path.join("data", "tickets.json")


class StorageCorruptedError(Exception):
    """Raised when storage file exists but cannot be parsed as valid JSON."""
    pass


def load_tickets(filepath: str = DEFAULT_STORAGE_PATH) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Load tickets from JSON file.
    
    Returns:
        (tickets, error_message):
        - If file does not exist: returns ([], None) -> fresh start, no error.
        - If file has valid JSON: returns (tickets_list, None).
        - If file is corrupt/malformed: returns ([], error_message).
          Crucially, does NOT overwrite or wipe the corrupt file!
    """
    if not os.path.exists(filepath):
        return [], None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return [], None
            data = json.loads(content)
            if not isinstance(data, list):
                err = f"Storage format error: Root element in '{filepath}' must be a JSON array."
                return [], err
            return data, None
    except json.JSONDecodeError as exc:
        err = f"Storage corruption detected in '{filepath}': {exc}. File retained intact."
        return [], err
    except Exception as exc:
        err = f"Unexpected error reading '{filepath}': {exc}."
        return [], err


def save_tickets(tickets: List[Dict[str, Any]], filepath: str = DEFAULT_STORAGE_PATH) -> None:
    """Save tickets to JSON file atomically to prevent partial writes.
    Creates parent directories if they do not exist.
    """
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    temp_path = f"{filepath}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

    # Atomically replace destination file
    if os.name == "nt" and os.path.exists(filepath):
        os.replace(temp_path, filepath)
    else:
        os.replace(temp_path, filepath)
