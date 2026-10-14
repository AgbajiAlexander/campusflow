"""storage.py - JSON file persistence for CampusFlow tickets.
Implements F7 (Persistence) adhering to PRD Section 8 and Section 10.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import validation

DEFAULT_STORAGE_PATH = os.path.join("data", "tickets.json")


class StorageCorruptedError(Exception):
    """Raised when storage file exists but cannot be parsed as valid JSON."""
    pass


def _migrate_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Small documented migration: tickets saved by the original CampusFlow
    (before CampusFlow Next) have no 'notes' field. Default it to an empty
    list so old, perfectly valid tickets aren't rejected just for predating
    this feature. Nothing else about the record is touched.
    """
    if "notes" not in record:
        record["notes"] = []
    return record


def _validate_collection(data: List[Any], filepath: str) -> Optional[str]:
    """Validate the FULL parsed collection before it's allowed to replace
    anything in memory: structure, required keys, legal field values, ID
    uniqueness, and note shape/uniqueness per ticket (Requirement E).

    Returns None if every record is valid, or an error message describing
    the FIRST problem found. Never raises -- load_tickets() below decides
    what to do with the result, matching the existing (tickets, error)
    convention this module already uses.
    """
    seen_ticket_ids = set()
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            return f"Record #{index} in '{filepath}' is not a ticket object."
        ticket_id = record.get("id")
        if not ticket_id:
            return f"Record #{index} in '{filepath}' is missing an 'id'."
        if ticket_id in seen_ticket_ids:
            return f"Duplicate ticket ID '{ticket_id}' found in '{filepath}'."
        seen_ticket_ids.add(ticket_id)
        try:
            validation.validate_ticket(record)
        except ValueError as exc:
            return f"Invalid record in '{filepath}': {exc}"
    return None


def load_tickets(filepath: str = DEFAULT_STORAGE_PATH) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Load tickets from JSON file.

    Returns:
        (tickets, error_message):
        - If file does not exist: returns ([], None) -> fresh start, no error.
        - If file has valid JSON AND every record passes full validation:
          returns (tickets_list, None).
        - If file is corrupt, malformed, or ANY record is invalid (duplicate
          ID, illegal status/category/urgency, malformed notes, etc.):
          returns ([], error_message). Crucially, this does NOT overwrite or
          wipe the file on disk, and the caller's existing in-memory ticket
          list (if any) is left completely untouched -- see cli.main_loop(),
          which only replaces its working list if error_message is None.
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

            data = [_migrate_record(record) if isinstance(record, dict) else record for record in data]

            validation_error = _validate_collection(data, filepath)
            if validation_error:
                return [], validation_error

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


