"""search.py - Read-only ticket search with combined filtering (Requirement C).

Owned by Engineer B (Milestones B1, B2). Pure function, no input()/print() --
independently testable without typing anything. cli.py's menu collects the
filter values and calls this; this never mutates the tickets list it's given.
"""

from typing import Any, Dict, List, Optional


def search_tickets(
    tickets_list: List[Dict[str, Any]],
    title_query: str = "",
    category: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return tickets matching ALL supplied filters (logical AND).

    - title_query: case-insensitive substring match against the title, using
      casefold() (more aggressive than lower(), correct for caseless text).
      Empty string means "don't filter by title".
    - category / status / priority: exact match once supplied; None or ""
      means "don't filter by that field" -- a ticket doesn't need to match
      a filter that wasn't supplied.
    - Read-only: never modifies any ticket in tickets_list.
    """
    results: List[Dict[str, Any]] = []
    query = (title_query or "").strip().casefold()

    for ticket in tickets_list:
        if not isinstance(ticket, dict):
            continue
        if query and query not in str(ticket.get("title", "")).casefold():
            continue
        if category and ticket.get("category") != category:
            continue
        if status and ticket.get("status") != status:
            continue
        if priority and ticket.get("priority") != priority:
            continue
        results.append(ticket)

    return results
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
