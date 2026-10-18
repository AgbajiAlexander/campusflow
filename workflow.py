"""workflow.py - Ticket lifecycle transitions and staff assignment.
Implements F3 (Assign) and F4 (Workflow) per PRD Section 8.
"""

from typing import Any, Dict


def assign_ticket(ticket: Dict[str, Any], assignee_name: str) -> Dict[str, Any]:
    """Assign or reassign a ticket to a staff member.
    Rejects empty or whitespace-only staff names.
    Locks resolved tickets: a resolved ticket cannot be assigned or reassigned unless reopened.
    """
    if not isinstance(ticket, dict):
        raise ValueError("Invalid ticket record.")
    if ticket.get("status") == "resolved":
        raise ValueError(
            f"Cannot assign ticket {ticket.get('id', '')} because it is resolved (locked). "
            "Reopen the ticket first before changing assignment."
        )
    if not isinstance(assignee_name, str) or not assignee_name.strip():
        raise ValueError("Assignee name cannot be blank.")
    
    ticket["assigned_to"] = assignee_name.strip()
    return ticket


def transition_status(ticket: Dict[str, Any], new_status: str) -> Dict[str, Any]:
    """Transition ticket status following the strict state machine:
    open -> in_progress -> resolved
    
    Rules:
    - An unassigned ticket CANNOT move to in_progress (must be assigned first).
    - A resolved ticket is locked and cannot transition via this function (must use reopen_ticket).
    - Any invalid transition attempt is rejected with a clear descriptive error.
    - Stored data remains completely unchanged upon rejection.
    """
    if not isinstance(ticket, dict):
        raise ValueError("Invalid ticket record.")
    
    current_status = ticket.get("status", "open")
    target_status = new_status.strip().lower()

    if current_status == "resolved":
        raise ValueError(
            f"Ticket {ticket.get('id', '')} is resolved (locked). Use the explicit 'reopen' action to move it back to open."
        )

    if current_status == "open":
        if target_status == "in_progress":
            if not ticket.get("assigned_to"):
                raise ValueError(
                    f"Cannot move unassigned ticket {ticket.get('id', '')} to 'in_progress'. "
                    "A staff member must be assigned before starting progress."
                )
            ticket["status"] = "in_progress"
            return ticket
        else:
            raise ValueError(
                f"Invalid transition from 'open' to '{target_status}'. "
                "From 'open', a ticket can only transition to 'in_progress'."
            )

    if current_status == "in_progress":
        if target_status == "resolved":
            ticket["status"] = "resolved"
            return ticket
        else:
            raise ValueError(
                f"Invalid transition from 'in_progress' to '{target_status}'. "
                "From 'in_progress', a ticket can only transition to 'resolved'."
            )

    raise ValueError(f"Unknown current status '{current_status}'.")


def reopen_ticket(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """Reopen a ticket, transitioning it back to 'open'.
    Only resolved tickets can be reopened.
    """
    if not isinstance(ticket, dict):
        raise ValueError("Invalid ticket record.")
    
    current_status = ticket.get("status", "")
    if current_status != "resolved":
        raise ValueError(
            f"Ticket {ticket.get('id', '')} is currently '{current_status}'. "
            "Only tickets with 'resolved' status can be reopened."
        )
    
    ticket["status"] = "open"
    return ticket
