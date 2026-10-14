"""Read-only search and ordering helpers (Engineer B).

Contract: functions here NEVER mutate the tickets passed in. Search returns
deep copies so display code cannot accidentally edit stored records.
"""
import copy
import re

VALID_CATEGORIES = ("Network", "Hardware", "Software", "Other")
VALID_STATUSES = ("open", "in_progress", "resolved")
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
VALID_PRIORITIES = tuple(PRIORITY_ORDER)


def ticket_number(ticket_id):
    """'T10' -> 10. Numeric tie-breaker so T2 sorts before T10."""
    match = re.search(r"\d+", str(ticket_id))
    return int(match.group()) if match else float("inf")


def _norm(text):
    return str(text).strip().casefold()


def search_tickets(tickets, query="", category="", status="", priority=""):
    """Title substring (casefold) AND every supplied filter. Empty = skip."""
    for value, allowed, label in (
        (category, VALID_CATEGORIES, "category"),
        (status, VALID_STATUSES, "status"),
        (priority, VALID_PRIORITIES, "priority"),
    ):
        if value and _norm(value) not in {_norm(a) for a in allowed}:
            raise ValueError(f"Invalid {label} filter: {value!r}")

    q, cat, st, pr = _norm(query), _norm(category), _norm(status), _norm(priority)
    matches = []
    for t in tickets:
        if q and q not in _norm(t.get("title", "")):
            continue
        if cat and _norm(t.get("category", "")) != cat:
            continue
        if st and _norm(t.get("status", "")) != st:
            continue
        if pr and _norm(t.get("priority", "")) != pr:
            continue
        matches.append(copy.deepcopy(t))
    return matches


def sort_by_priority_then_id(tickets):
    """Separate optional view: critical > high > medium > low, then numeric ID."""
    return sorted(
        tickets,
        key=lambda t: (PRIORITY_ORDER.get(t.get("priority"), 99), ticket_number(t.get("id"))),
    )