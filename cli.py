"""cli.py - Text-based user interface for CampusFlow Ticket Manager.
Implements the interactive single menu loop covering F1-F7.
"""

import sys
from typing import Any, Dict, List
import tickets
import workflow
import storage
import reports


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
    print(" 8. View Reports          (F6)")
    print(" 9. Exit                  (F7)")
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
    print("\n--- Ticket Volume Reports (F6) ---")
    rep = reports.generate_report(all_tickets)
    print(f"Total Tickets: {rep['total']}")
    print("\nBreakdown by Status:")
    for status, count in rep["by_status"].items():
        print(f"  - {status:<12}: {count}")
    print("\nBreakdown by Priority:")
    for prio, count in rep["by_priority"].items():
        print(f"  - {prio:<12}: {count}")


def main_loop(storage_path: str = storage.DEFAULT_STORAGE_PATH) -> None:
    all_tickets, err = storage.load_tickets(storage_path)
    if err:
        print(f"\n[ALERT] {err}")
        print("Existing data was not modified. Starting session with empty memory state.")
    else:
        print(f"\nLoaded {len(all_tickets)} ticket(s) from storage.")

    while True:
        display_menu()
        choice = input("Select an option (1-9): ").strip()
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
            storage.save_tickets(all_tickets, storage_path)
            print("\nAll data successfully persisted. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")


if __name__ == "__main__":
    main_loop()
