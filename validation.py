"""validation.py - Centralized validation helpers (Requirement A).

Owned by Engineer A. These wrap the existing field validators in tickets.py
and add the cross-cutting checks CampusFlow Next needs: a single entry point
for "is this whole ticket dict legal" and a pure, non-mutating check for
"is this status transition legal right now".

Convention: raises ValueError with a specific message, matching tickets.py
and workflow.py. Never mutates its inputs.
"""

from typing import Any, Dict

import tickets

REQUIRED_TICKET_KEYS = (
    "id", "title", "category", "urgency", "affected_users",
    "priority", "status", "assigned_to", "notes",
)


def validate_ticket(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a ticket dict has every required key and each field is legal.

    Used by storage.py when reloading from JSON, and can be reused anywhere
    a full-record sanity check is needed. Returns the same dict unchanged on
    success; raises ValueError naming the first problem found on failure.
    """
    if not isinstance(ticket, dict):
        raise ValueError("Ticket record must be a dictionary.")

    missing = [key for key in REQUIRED_TICKET_KEYS if key not in ticket]
    if missing:
        raise ValueError(f"Ticket {ticket.get('id', '?')} is missing required field(s): {missing}.")

    tickets.validate_title(ticket["title"])
    tickets.normalize_category(ticket["category"])
    tickets.normalize_urgency(ticket["urgency"])
    tickets.validate_affected_users(ticket["affected_users"])

    if ticket["priority"] not in tickets.VALID_PRIORITIES:
        raise ValueError(f"Ticket {ticket['id']} has an illegal priority value: {ticket['priority']!r}.")

    if ticket["status"] not in tickets.VALID_STATUSES:
        raise ValueError(f"Ticket {ticket['id']} has an illegal status value: {ticket['status']!r}.")

    if ticket["assigned_to"] is not None and not isinstance(ticket["assigned_to"], str):
        raise ValueError(f"Ticket {ticket['id']}'s assigned_to must be a string or null.")

    if not isinstance(ticket["notes"], list):
        raise ValueError(f"Ticket {ticket['id']}'s notes field must be a list.")

    seen_note_ids = set()
    for note in ticket["notes"]:
        if not isinstance(note, dict) or not {"note_id", "author", "message"} <= note.keys():
            raise ValueError(f"Ticket {ticket['id']} has a malformed note record: {note!r}.")
        if note["note_id"] in seen_note_ids:
            raise ValueError(f"Ticket {ticket['id']} has a duplicate note_id: {note['note_id']}.")
        seen_note_ids.add(note["note_id"])

    return ticket


def can_transition(current_status: str, target_status: str, assigned_to: Any) -> bool:
    """Pure predicate: would this status change be legal, without mutating anything.

    Mirrors workflow.transition_status()'s rules exactly, but never changes a
    ticket -- useful for the CLI to grey out / warn before even attempting an
    action, and for tests that want to check "is this legal" and "did this
    mutate" as two separate, explicit questions (see Concept 2's check-yourself).
    """
    if current_status == "resolved":
        return False
    if current_status == "open":
        return target_status == "in_progress" and bool(assigned_to)
    if current_status == "in_progress":
        return target_status == "resolved"
    return False
