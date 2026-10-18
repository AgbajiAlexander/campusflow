"""search.py - Read-only ticket search with combined filtering (Requirement C).

Owned by Engineer B (Milestones B1, B2). Pure function, no input()/print() --
independently testable without typing anything. cli.py's menu collects the
filter values and calls this; this never mutates the tickets list it's given.
"""

import copy
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
    - Read-only: never modifies any ticket in tickets_list, and returns deep
      copies so caller cannot mutate stored records through results.
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
        results.append(copy.deepcopy(ticket))

    return results
