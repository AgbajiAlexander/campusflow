"""tickets.py - Core ticket data structures, validation, and priority engine.
Implements F1 (Create Ticket), F2 (List/View Ticket), and Section 7 Priority Engine.
"""

from typing import Any, Dict, List, Optional

VALID_CATEGORIES = ("Network", "Hardware", "Software", "Other")
VALID_URGENCIES = ("low", "medium", "high")
VALID_PRIORITIES = ("critical", "high", "medium", "low")
VALID_STATUSES = ("open", "in_progress", "resolved")


def normalize_category(category_input: str) -> str:
    """Validate and normalize category to title-case standard value."""
    if not isinstance(category_input, str):
        raise ValueError("Category must be a string.")
    
    cleaned = category_input.strip()
    for valid in VALID_CATEGORIES:
        if cleaned.lower() == valid.lower():
            return valid
    raise ValueError(
        f"Invalid category '{category_input}'. Must be one of: {', '.join(VALID_CATEGORIES)}."
    )


def normalize_urgency(urgency_input: str) -> str:
    """Validate and normalize urgency to lowercase standard value."""
    if not isinstance(urgency_input, str):
        raise ValueError("Urgency must be a string.")
    
    cleaned = urgency_input.strip().lower()
    if cleaned in VALID_URGENCIES:
        return cleaned
    raise ValueError(
        f"Invalid urgency '{urgency_input}'. Must be one of: {', '.join(VALID_URGENCIES)}."
    )


def validate_affected_users(users_input: Any) -> int:
    """Validate that affected_users is a positive integer greater than 0.
    Rejects 0, negative integers, floats/decimals, and non-integer strings.
    """
    if isinstance(users_input, bool):
        raise ValueError("affected_users must be an integer, not a boolean.")
    
    if isinstance(users_input, int):
        val = users_input
    elif isinstance(users_input, str):
        cleaned = users_input.strip()
        if not cleaned.isdigit():
            raise ValueError(
                f"affected_users must be a positive integer, got '{users_input}'."
            )
        val = int(cleaned)
    else:
        raise ValueError(
            f"affected_users must be a positive integer, got '{users_input}'."
        )
    
    if val <= 0:
        raise ValueError(
            f"affected_users must be greater than 0, got {val}."
        )
    return val


def validate_title(title_input: Any) -> str:
    """Validate title is non-blank."""
    if not isinstance(title_input, str):
        raise ValueError("Title must be a text string.")
    cleaned = title_input.strip()
    if not cleaned:
        raise ValueError("Title cannot be blank.")
    return cleaned


def calculate_priority(urgency: str, affected_users: int) -> str:
    """Fixed priority engine per PRD Section 7.
    Evaluates rules strictly in order and returns the first matching priority:
    1. urgency == high AND affected_users >= 10 -> critical
    2. urgency == high OR affected_users >= 10 -> high
    3. urgency == medium OR affected_users >= 3 -> medium
    4. Otherwise -> low
    """
    norm_urgency = normalize_urgency(urgency)
    valid_users = validate_affected_users(affected_users)

    if norm_urgency == "high" and valid_users >= 10:
        return "critical"
    if norm_urgency == "high" or valid_users >= 10:
        return "high"
    if norm_urgency == "medium" or valid_users >= 3:
        return "medium"
    return "low"


def extract_numeric_id(ticket_id: str) -> int:
    """Extract numeric suffix from ID like 'T001' -> 1. Returns 0 if unparseable."""
    if isinstance(ticket_id, str) and ticket_id.startswith("T"):
        suffix = ticket_id[1:]
        if suffix.isdigit():
            return int(suffix)
    return 0


def generate_next_id(existing_tickets: List[Dict[str, Any]]) -> str:
    """Auto-generate the next sequential unique ID in format T001, T002, etc."""
    max_id_num = 0
    for ticket in existing_tickets:
        tid = ticket.get("id", "")
        num = extract_numeric_id(tid)
        if num > max_id_num:
            max_id_num = num
    next_num = max_id_num + 1
    return f"T{next_num:03d}"


def create_ticket(
    existing_tickets: List[Dict[str, Any]],
    title: str,
    category: str,
    urgency: str,
    affected_users: Any
) -> Dict[str, Any]:
    """Create a validated ticket record defaulting to open status and unassigned."""
    clean_title = validate_title(title)
    clean_category = normalize_category(category)
    clean_urgency = normalize_urgency(urgency)
    clean_users = validate_affected_users(affected_users)
    priority = calculate_priority(clean_urgency, clean_users)
    ticket_id = generate_next_id(existing_tickets)

    ticket: Dict[str, Any] = {
        "id": ticket_id,
        "title": clean_title,
        "category": clean_category,
        "urgency": clean_urgency,
        "affected_users": clean_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }
    return ticket


def find_ticket_by_id(
    tickets: List[Dict[str, Any]],
    ticket_id: str
) -> Optional[Dict[str, Any]]:
    """Lookup a ticket by ID (case-insensitive for convenience)."""
    if not isinstance(ticket_id, str):
        return None
    target = ticket_id.strip().upper()
    for t in tickets:
        if t.get("id", "").strip().upper() == target:
            return t
    return None
