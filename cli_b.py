"""Engineer B's CLI views. Wire these into your existing main menu.

Error convention (agree with Engineer A): A's exceptions subclass ValueError,
and add_note(tickets, ticket_id, author, message) raises on any rejection.
"""
from campusflow.cli_input import prompt_choice, prompt_text
from campusflow.reports import build_report, format_report
from campusflow.search import (VALID_CATEGORIES, VALID_STATUSES, VALID_PRIORITIES,
                               search_tickets, sort_by_priority_then_id)


def format_table(rows):
    if not rows:
        return "No tickets found."
    head = f"{'ID':<6}{'Title':<30}{'Category':<10}{'Priority':<9}{'Status':<12}Assigned"
    body = [f"{r['id']:<6}{str(r['title'])[:28]:<30}{r['category']:<10}{r['priority']:<9}"
            f"{r['status']:<12}{r.get('assigned_to') or '-'}" for r in rows]
    return "\n".join([head, "-" * len(head)] + body)


def search_menu(tickets, input_fn=input, output_fn=print):
    query = input_fn("Title contains (Enter for any): ").strip()
    cat = prompt_choice("Category filter: ", VALID_CATEGORIES, input_fn, output_fn, allow_blank=True)
    st = prompt_choice("Status filter: ", VALID_STATUSES, input_fn, output_fn, allow_blank=True)
    pr = prompt_choice("Priority filter: ", VALID_PRIORITIES, input_fn, output_fn, allow_blank=True)
    results = search_tickets(tickets, query, cat, st, pr)  # read-only
    if prompt_choice("Sort by priority then ID? (y/n): ", ("y", "n"), input_fn, output_fn) == "y":
        results = sort_by_priority_then_id(results)
    output_fn(format_table(results))
    return results


def add_note_menu(tickets, add_note, input_fn=input, output_fn=print, errors=(ValueError,)):
    ticket_id = prompt_text("Ticket ID: ", input_fn, output_fn).upper()
    author = input_fn("Author: ")
    message = input_fn("Note message (5-300 chars): ")
    try:
        note = add_note(tickets, ticket_id, author, message)
    except errors as exc:
        output_fn(f"Could not add note: {exc}")
        return None
    output_fn(f"Added note {note['note_id']} to {ticket_id}.")
    return note


def view_notes_menu(tickets, input_fn=input, output_fn=print):
    ticket_id = prompt_text("Ticket ID: ", input_fn, output_fn).upper()
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if ticket is None:
        output_fn(f"No ticket with ID {ticket_id}.")
        return []
    notes = sorted(ticket.get("notes", []), key=lambda n: n["note_id"])
    if not notes:
        output_fn(f"{ticket_id} has no notes.")
    for n in notes:
        output_fn(f"{n['note_id']} [{n['author']}]: {n['message']}")
    return notes


def report_menu(tickets, output_fn=print):
    output_fn(format_report(build_report(tickets)))