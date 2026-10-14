"""notes.py - Structured follow-up notes on tickets (Requirement B).

Owned by Engineer A. Business/data layer only -- no input()/print() here,
so it's independently testable. Engineer B's CLI menus in cli.py call
add_note() and view_notes() and handle the printing.
"""

from typing import Any, Dict, List

import tickets

MIN_MESSAGE_LENGTH = 5
MAX_MESSAGE_LENGTH = 300
NOTE_ALLOWED_STATUSES = ("open", "in_progress")


def extract_note_numeric_id(note_id: str) -> int:
    """'N007' -> 7. Returns 0 if unparseable, same pattern as tickets.extract_numeric_id."""
    if isinstance(note_id, str) and note_id.startswith("N"):
        suffix = note_id[1:]
        if suffix.isdigit():
            return int(suffix)
    return 0


def next_note_id(ticket: Dict[str, Any]) -> str:
    """Next sequential note ID for THIS ticket, from the highest existing N00x.

    Deliberately scoped per-ticket (not global) and derived from the max
    existing ID rather than len(notes), for the same reason
    tickets.generate_next_id() doesn't use len(tickets): a rejected note
    must not consume an ID, and this stays correct even if notes are ever
    filtered/reordered in memory.
    """
    notes = ticket.get("notes", [])
    highest = 0
    for note in notes:
        num = extract_note_numeric_id(note.get("note_id", ""))
        if num > highest:
            highest = num
    return f"N{highest + 1:03d}"


def add_note(tickets_list: List[Dict[str, Any]], ticket_id: str, author: str, message: str) -> Dict[str, Any]:
    """Add a validated follow-up note to a ticket. Returns the new note dict.

    Rules (Requirement B):
    - Ticket must exist.
    - Ticket status must be 'open' or 'in_progress' (resolved tickets reject
      notes until explicitly reopened through workflow.reopen_ticket()).
    - author must be non-blank after stripping.
    - message must be 5-300 characters after stripping.
    - A rejected note must NOT consume a note_id -- next_note_id() is only
      called after every check above has passed, so a failed validation
      never advances the counter.
    """
    ticket = tickets.find_ticket_by_id(tickets_list, ticket_id)
    if ticket is None:
        raise ValueError(f"Ticket with ID '{ticket_id}' not found.")

    if ticket.get("status") not in NOTE_ALLOWED_STATUSES:
        raise ValueError(
            f"Ticket {ticket['id']} is '{ticket.get('status')}'; notes can only be added "
            "while a ticket is 'open' or 'in_progress'. Reopen it first if it's resolved."
        )

    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author cannot be blank.")

    if not isinstance(message, str):
        raise ValueError("Note message must be text.")
    clean_message = message.strip()
    if not (MIN_MESSAGE_LENGTH <= len(clean_message) <= MAX_MESSAGE_LENGTH):
        raise ValueError(
            f"Note message must be between {MIN_MESSAGE_LENGTH} and {MAX_MESSAGE_LENGTH} "
            f"characters after trimming (got {len(clean_message)})."
        )

    note = {
        "note_id": next_note_id(ticket),
        "author": author.strip(),
        "message": clean_message,
    }
    ticket.setdefault("notes", []).append(note)
    return note


def view_notes(tickets_list: List[Dict[str, Any]], ticket_id: str) -> List[Dict[str, Any]]:
    """Return all notes for a ticket, in ID order. Read-only; raises if ticket unknown."""
    ticket = tickets.find_ticket_by_id(tickets_list, ticket_id)
    if ticket is None:
        raise ValueError(f"Ticket with ID '{ticket_id}' not found.")
    return sorted(ticket.get("notes", []), key=lambda n: extract_note_numeric_id(n.get("note_id", "")))

