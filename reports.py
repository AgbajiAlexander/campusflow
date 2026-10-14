"""reports.py - Work queue ordering and analytical reporting.
Implements F5 (Work Queue) and F6 (Reports) per PRD Section 8,
extended for Requirement D (Trustworthy quality insights).
"""

from typing import Any, Dict, List
from tickets import extract_numeric_id

PRIORITY_RANKS = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def get_work_queue(tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return active (unresolved) tickets ordered by priority and numeric ID.
    
    Sorting rules:
    - Exclude tickets with status 'resolved'.
    - Priority rank: critical (highest) -> high -> medium -> low.
    - Tie-breaker: earlier (lower) numeric ticket ID (e.g., T001 before T002).
    """
    unresolved = [t for t in tickets if t.get("status") != "resolved"]

    def sort_key(ticket: Dict[str, Any]):
        prio = ticket.get("priority", "low").strip().lower()
        rank = PRIORITY_RANKS.get(prio, 99)
        num_id = extract_numeric_id(ticket.get("id", ""))
        return (rank, num_id)

    return sorted(unresolved, key=sort_key)


def generate_report(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary metrics and breakdowns by status, priority, and category.
    Safely handles the zero-tickets case without errors or division by zero.
    """
    total = len(tickets)
    
    status_counts = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
    }
    
    priority_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for t in tickets:
        status = t.get("status", "").strip().lower()
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = status_counts.get(status, 0) + 1

        priority = t.get("priority", "").strip().lower()
        if priority in priority_counts:
            priority_counts[priority] += 1
        else:
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

    by_category: Dict[str, int] = {}
    for t in tickets:
        category = t.get("category", "Other")
        by_category[category] = by_category.get(category, 0) + 1

    unresolved = status_counts.get("open", 0) + status_counts.get("in_progress", 0)
    resolved = status_counts.get("resolved", 0)
    resolution_percentage = (resolved / total * 100) if total > 0 else 0.0

    return {
        "total": total,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "by_category": by_category,
        "unresolved": unresolved,
        "resolved": resolved,
        "resolution_percentage": round(resolution_percentage, 1),
    }


def sort_search_results(matching_tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Requirement D's separate optional view: sort SEARCH results by
    priority then ticket ID -- same ordering rule as the work queue, but
    deliberately a different function over a different input (search
    results, which may include resolved tickets), so it never silently
    replaces or is confused with get_work_queue(), which must stay
    OPEN-tickets-only and untouched.
    """
    def sort_key(ticket: Dict[str, Any]):
        prio = ticket.get("priority", "low").strip().lower()
        rank = PRIORITY_RANKS.get(prio, 99)
        num_id = extract_numeric_id(ticket.get("id", ""))
        return (rank, num_id)

    return sorted(matching_tickets, key=sort_key)
