"""cli.py - Text-based user interface for CampusFlow Ticket Manager.
Implements the interactive single menu loop covering F1-F7 and CampusFlow Next requirements.
"""

import sys
from typing import Any, Dict, List
import tickets
import workflow
import storage
import reports
import search
import understanding_check

try:
    import notes
except ImportError:
    notes = None  # type: ignore


def display_menu() -> None:
    print("\n" + "=" * 48)
    print("      CampusFlow — IT Helpdesk Ticket Manager   ")
    print("=" * 48)
    print(" 1. Create Ticket         (F1)")
    print(" 2. List All Tickets      (F2)")
    print(" 3. View Ticket Details   (F2)")
    print(" 4. Assign Ticket         (F3)")
    print(" 5. Change Ticket Status  (F4)")
    print(" 6. Reopen Resolved Ticket(F4)")
    print(" 7. View Work Queue       (F5)")
    print(" 8. View Reports          (F6 + Requirement D)")
    print(" 9. Add Follow-up Note    (Next-B)")
    print("10. View Ticket Notes     (Next-B)")
    print("11. Search Tickets        (Next-C)")
    print("12. Engineering Understanding Check")
    print("13. Exit                  (F7)")
    print("=" * 48)


def print_ticket_summary_table(ticket_list: List[Dict[str, Any]]) -> None:
    if not ticket_list:
        print("No tickets found.")
        return
    print("-" * 65)
    print(f"{'ID':<6} | {'Status':<12} | {'Priority':<10} | {'Title'}")
    print("-" * 65)
    for t in ticket_list:
        tid = t.get("id", "")
        status = t.get("status", "")
        prio = t.get("priority", "")
        title = t.get("title", "")
        if len(title) > 30:
            title = title[:27] + "..."
        print(f"{tid:<6} | {status:<12} | {prio:<10} | {title}")
    print("-" * 65)


def handle_create_ticket(all_tickets: List[Dict[str, Any]], storage_path: str) -> None:
    print("\n--- Create Ticket (F1) ---")
    title = input("Enter ticket title: ").strip()
    if not title:
        print("Error: Ticket title cannot be blank.")
        return

    print("Allowed categories: Network, Hardware, Software, Other")
    category = input("Enter category: ").strip()

    print("Allowed urgencies: low, medium, high")
    urgency = input("Enter urgency: ").strip()

    affected_users_input = input("Enter number of affected users (positive integer): ").strip()

    try:
        new_ticket = tickets.create_ticket(
            all_tickets, title, category, urgency, affected_users_input
        )
        all_tickets.append(new_ticket)
        storage.save_tickets(all_tickets, storage_path)
        print(f"Success! Created ticket {new_ticket['id']} with calculated priority '{new_ticket['priority']}'.")
    except ValueError as err:
        print(f"Validation Error: {err}")


def handle_list_tickets(all_tickets: List[Dict[str, Any]]) -> None:
    print("\n--- All Tickets (F2) ---")
    print_ticket_summary_table(all_tickets)


def handle_view_ticket(all_tickets: List[Dict[str, Any]]) -> None:
    print("\n--- View Ticket Details (F2) ---")
    tid = input("Enter ticket ID (e.g. T001): ").strip()
    ticket = tickets.find_ticket_by_id(all_tickets, tid)
    if not ticket:
        print(f"Error: Ticket with ID '{tid}' not found.")
        return

    print("\n" + "-" * 40)
    print(f"Ticket ID:       {ticket.get('id')}")
    print(f"Title:           {ticket.get('title')}")
    print(f"Category:        {ticket.get('category')}")
    print(f"Urgency:         {ticket.get('urgency')}")
    print(f"Affected Users:  {ticket.get('affected_users')}")
    print(f"Priority:        {ticket.get('priority')}")
    print(f"Status:          {ticket.get('status')}")
    print(f"Assigned To:     {ticket.get('assigned_to') or 'None'}")
    print("-" * 40)


def handle_assign_ticket(all_tickets: List[Dict[str, Any]], storage_path: str) -> None:
    print("\n--- Assign Ticket (F3) ---")
    tid = input("Enter ticket ID to assign: ").strip()
    ticket = tickets.find_ticket_by_id(all_tickets, tid)
    if not ticket:
        print(f"Error: Ticket with ID '{tid}' not found.")
        return

    current_assignee = ticket.get("assigned_to") or "Unassigned"
    print(f"Current assignee: {current_assignee}")
    assignee = input("Enter staff member name: ").strip()

    try:
        workflow.assign_ticket(ticket, assignee)
        storage.save_tickets(all_tickets, storage_path)
        print(f"Success! Ticket {ticket['id']} assigned to '{assignee}'.")
    except ValueError as err:
        print(f"Assignment Error: {err}")


def handle_change_status(all_tickets: List[Dict[str, Any]], storage_path: str) -> None:
    print("\n--- Change Ticket Status (F4) ---")
    tid = input("Enter ticket ID: ").strip()
    ticket = tickets.find_ticket_by_id(all_tickets, tid)
    if not ticket:
        print(f"Error: Ticket with ID '{tid}' not found.")
        return

    current = ticket.get("status")
    print(f"Current status: {current}")
    print("Allowed transitions: 'open' -> 'in_progress' -> 'resolved'")
    target = input("Enter target status ('in_progress' or 'resolved'): ").strip()

    try:
        workflow.transition_status(ticket, target)
        storage.save_tickets(all_tickets, storage_path)
        print(f"Success! Ticket {ticket['id']} status changed to '{ticket['status']}'.")
    except ValueError as err:
        print(f"Transition Error: {err}")


def handle_reopen_ticket(all_tickets: List[Dict[str, Any]], storage_path: str) -> None:
    print("\n--- Reopen Ticket (F4) ---")
    tid = input("Enter ticket ID to reopen: ").strip()
    ticket = tickets.find_ticket_by_id(all_tickets, tid)
    if not ticket:
        print(f"Error: Ticket with ID '{tid}' not found.")
        return

    try:
        workflow.reopen_ticket(ticket)
        storage.save_tickets(all_tickets, storage_path)
        print(f"Success! Ticket {ticket['id']} reopened and set back to 'open'.")
    except ValueError as err:
        print(f"Reopen Error: {err}")


def handle_work_queue(all_tickets: List[Dict[str, Any]]) -> None:
    print("\n--- Work Queue (F5 - Unresolved, Priority Order) ---")
    queue = reports.get_work_queue(all_tickets)
    if not queue:
        print("Work queue is empty! No active tickets pending.")
        return
    print_ticket_summary_table(queue)


def handle_reports(all_tickets: List[Dict[str, Any]]) -> None:
    print("\n--- Ticket Volume Reports (F6 + Requirement D) ---")
    rep = reports.generate_report(all_tickets)
    print(f"Total Tickets: {rep['total']}")
    print("\nBreakdown by Status:")
    for status, count in rep["by_status"].items():
        print(f"  - {status:<12}: {count}")
    print("\nBreakdown by Priority:")
    for prio, count in rep["by_priority"].items():
        print(f"  - {prio:<12}: {count}")
    print("\nBreakdown by Category:")
    for cat, count in rep.get("by_category", {}).items():
        print(f"  - {cat:<12}: {count}")
    print(f"\nUnresolved (open + in_progress): {rep.get('unresolved', 0)}")
    print(f"Resolved:                        {rep.get('resolved', 0)}")
    print(f"Resolution rate:                 {rep.get('resolution_percentage', 0.0)}%")


def handle_add_note(all_tickets: List[Dict[str, Any]], storage_path: str) -> None:
    print("\n--- Add Follow-up Note (Next-B) ---")
    if notes is None:
        print("[Notice] The notes module is part of Engineer A's branch and will be active once merged.")
        return

    tid = input("Enter ticket ID: ").strip()
    author = input("Your name: ").strip()
    message = input("Note (5-300 characters): ").strip()

    try:
        note = notes.add_note(all_tickets, tid, author, message)
        storage.save_tickets(all_tickets, storage_path)
        print(f"Success! Added {note['note_id']} to ticket {tid}.")
    except ValueError as err:
        print(f"Note Error: {err}")


def handle_view_notes(all_tickets: List[Dict[str, Any]]) -> None:
    print("\n--- View Ticket Notes (Next-B) ---")
    if notes is None:
        print("[Notice] The notes module is part of Engineer A's branch and will be active once merged.")
        return

    tid = input("Enter ticket ID: ").strip()
    try:
        ticket_notes = notes.view_notes(all_tickets, tid)
    except ValueError as err:
        print(f"Error: {err}")
        return

    if not ticket_notes:
        print(f"Ticket {tid} has no notes yet.")
        return
    for note in ticket_notes:
        print(f"  [{note['note_id']}] {note['author']}: {note['message']}")


def handle_search_tickets(all_tickets: List[Dict[str, Any]]) -> None:
    print("\n--- Search Tickets (read-only) ---")
    title_query = input("Title contains (blank for any): ").strip()

    category = None
    while True:
        cat_in = input("Category filter (Network/Hardware/Software/Other, blank for any): ").strip()
        if not cat_in:
            break
        try:
            category = tickets.normalize_category(cat_in)
            break
        except ValueError as err:
            print(f"Error: {err} Please try again.")

    status = None
    while True:
        status_in = input("Status filter (open/in_progress/resolved, blank for any): ").strip()
        if not status_in:
            break
        cleaned_status = status_in.lower()
        if cleaned_status in tickets.VALID_STATUSES:
            status = cleaned_status
            break
        print(f"Error: invalid status '{status_in}'. Allowed: {', '.join(tickets.VALID_STATUSES)}")

    priority = None
    while True:
        prio_in = input("Priority filter (critical/high/medium/low, blank for any): ").strip()
        if not prio_in:
            break
        cleaned_prio = prio_in.lower()
        if cleaned_prio in tickets.VALID_PRIORITIES:
            priority = cleaned_prio
            break
        print(f"Error: invalid priority '{prio_in}'. Allowed: {', '.join(tickets.VALID_PRIORITIES)}")

    results = search.search_tickets(all_tickets, title_query, category, status, priority)
    if not results:
        print("No matching tickets.")
        return

    print("-" * 75)
    print(f"{'ID':<6} | {'Title':<24} | {'Category':<10} | {'Priority':<9} | {'Status':<12} | Assigned")
    print("-" * 75)
    for t in results:
        print(
            f"{t['id']:<6} | {t['title'][:24]:<24} | {t['category']:<10} | "
            f"{t['priority']:<9} | {t['status']:<12} | {t.get('assigned_to') or 'Unassigned'}"
        )

    sort_view = input("\nAlso show these sorted by priority/ID? (y/n): ").strip().lower()
    if sort_view == "y":
        sorted_results = reports.sort_search_results(results)
        print_ticket_summary_table(sorted_results)


def main_loop(storage_path: str = storage.DEFAULT_STORAGE_PATH) -> None:
    all_tickets, err = storage.load_tickets(storage_path)
    if err:
        print(f"\n[ALERT] {err}")
        print("Existing data was not modified. Starting session with empty memory state.")
    else:
        print(f"\nLoaded {len(all_tickets)} ticket(s) from storage.")

    while True:
        display_menu()
        choice = input("Select an option (1-13): ").strip()
        if choice == "1":
            handle_create_ticket(all_tickets, storage_path)
        elif choice == "2":
            handle_list_tickets(all_tickets)
        elif choice == "3":
            handle_view_ticket(all_tickets)
        elif choice == "4":
            handle_assign_ticket(all_tickets, storage_path)
        elif choice == "5":
            handle_change_status(all_tickets, storage_path)
        elif choice == "6":
            handle_reopen_ticket(all_tickets, storage_path)
        elif choice == "7":
            handle_work_queue(all_tickets)
        elif choice == "8":
            handle_reports(all_tickets)
        elif choice == "9":
            handle_add_note(all_tickets, storage_path)
        elif choice == "10":
            handle_view_notes(all_tickets)
        elif choice == "11":
            handle_search_tickets(all_tickets)
        elif choice == "12":
            understanding_check.run_understanding_check()
        elif choice == "13":
            storage.save_tickets(all_tickets, storage_path)
            print("\nAll data successfully persisted. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 13.")


if __name__ == "__main__":
    main_loop()
