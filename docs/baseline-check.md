# CampusFlow Baseline Diagnostic Check
**Date:** October 14, 2026  
**Audited Commit / Version:** CampusFlow v1 (Commit `69357f5`)  
**Engineer:** Engineer B (Gabriel Oche Adanu, @Aocheg)

---

## 1. Baseline Test Execution Command & Results

* **Command Executed:**
  ```bash
  python3 -m unittest discover -s tests -v
  ```
* **Execution Results:**
  ```text
  test_empty_work_queue (test_reports.TestReportsAndWorkQueue.test_empty_work_queue) ... ok
  test_report_aggregated_counts (test_reports.TestReportsAndWorkQueue.test_report_aggregated_counts) ... ok
  test_report_zero_tickets_case (test_reports.TestReportsAndWorkQueue.test_report_zero_tickets_case) ... ok
  test_work_queue_sorting_and_tie_breaking (test_reports.TestReportsAndWorkQueue.test_work_queue_sorting_and_tie_breaking) ... ok
  test_corrupted_json_preserves_file_and_reports_error (test_storage.TestStorage.test_corrupted_json_preserves_file_and_reports_error) ... ok
  test_id_uniqueness_and_increment_after_reload (test_storage.TestStorage.test_id_uniqueness_and_increment_after_reload) ... ok
  test_missing_file_starts_empty_without_error (test_storage.TestStorage.test_missing_file_starts_empty_without_error) ... ok
  test_save_and_reload_preserves_tickets (test_storage.TestStorage.test_save_and_reload_preserves_tickets) ... ok
  test_affected_users_invalid_string_rejected (test_tickets.TestTicketsPriorityAndValidation.test_affected_users_invalid_string_rejected) ... ok
  test_affected_users_negative_rejected (test_tickets.TestTicketsPriorityAndValidation.test_affected_users_negative_rejected) ... ok
  test_affected_users_zero_rejected (test_tickets.TestTicketsPriorityAndValidation.test_affected_users_zero_rejected) ... ok
  test_blank_title_rejected (test_tickets.TestTicketsPriorityAndValidation.test_blank_title_rejected) ... ok
  test_create_ticket_sequential_id (test_tickets.TestTicketsPriorityAndValidation.test_create_ticket_sequential_id) ... ok
  test_find_ticket_by_id (test_tickets.TestTicketsPriorityAndValidation.test_find_ticket_by_id) ... ok
  test_invalid_category_rejected (test_tickets.TestTicketsPriorityAndValidation.test_invalid_category_rejected) ... ok
  test_invalid_urgency_rejected (test_tickets.TestTicketsPriorityAndValidation.test_invalid_urgency_rejected) ... ok
  test_priority_case_insensitivity (test_tickets.TestTicketsPriorityAndValidation.test_priority_case_insensitivity) ... ok
  test_priority_medium_urgency (test_tickets.TestTicketsPriorityAndValidation.test_priority_medium_urgency) ... ok
  test_priority_rule1_high_urgency_large_users (test_tickets.TestTicketsPriorityAndValidation.test_priority_rule1_high_urgency_large_users) ... ok
  test_priority_rule2_high_urgency_small_users (test_tickets.TestTicketsPriorityAndValidation.test_priority_rule2_high_urgency_small_users) ... ok
  test_priority_rule3_low_urgency_moderate_users (test_tickets.TestTicketsPriorityAndValidation.test_priority_rule3_low_urgency_moderate_users) ... ok
  test_priority_rule4_low_urgency_single_user (test_tickets.TestTicketsPriorityAndValidation.test_priority_rule4_low_urgency_single_user) ... ok
  test_assigned_ticket_progresses_open_in_progress_resolved (test_workflow.TestWorkflow.test_assigned_ticket_progresses_open_in_progress_resolved) ... ok
  test_blank_assignee_rejected (test_workflow.TestWorkflow.test_blank_assignee_rejected) ... ok
  test_invalid_transition_open_to_resolved_rejected (test_workflow.TestWorkflow.test_invalid_transition_open_to_resolved_rejected) ... ok
  test_reassignment_allowed (test_workflow.TestWorkflow.test_reassignment_allowed) ... ok
  test_reopen_non_resolved_ticket_rejected (test_workflow.TestWorkflow.test_reopen_non_resolved_ticket_rejected) ... ok
  test_reopen_resolved_ticket_succeeds (test_workflow.TestWorkflow.test_reopen_resolved_ticket_succeeds) ... ok
  test_resolved_ticket_is_locked (test_workflow.TestWorkflow.test_resolved_ticket_is_locked) ... ok
  test_unassigned_ticket_cannot_move_to_in_progress (test_workflow.TestWorkflow.test_unassigned_ticket_cannot_move_to_in_progress) ... ok

  Ran 30 tests in 0.015s
  OK
  ```

All 30 baseline tests pass cleanly without errors.

---

## 2. Three Diagnostic Inputs Tested

### Input 1: Unassigned Ticket Moving to `in_progress`
* **Input:** Call `workflow.transition_status(ticket, "in_progress")` on an unassigned ticket (`assigned_to: None`).
* **Observed Result:** Raises `ValueError: Cannot move unassigned ticket T001 to 'in_progress'`.
* **State Verification:** Ticket status remains `"open"` without modification.
* **Finding:** State machine correctly prevents unassigned progress transitions.

### Input 2: Mutating Assignment on a `resolved` Ticket
* **Input:** Call `workflow.assign_ticket(resolved_ticket, "Staff Member")` on a ticket with `status: "resolved"`.
* **Observed Result:** Mutation was permitted silently in v1!
* **Finding:** Invariant gap identified. Resolved tickets must be locked against assignment changes unless explicitly reopened.

### Input 3: Zero-Tickets Report Division Safety
* **Input:** Call `reports.generate_report([])` with an empty ticket list.
* **Observed Result:** Safely returns report with `total: 0` without `ZeroDivisionError`.
* **Finding:** Basic 0-ticket handling works, but needs extension for Requirement D (category breakdown, unresolved count, and resolution percentage).

---

## 3. Audit Observations & Sprint Action Items

1. **Search & Multi-Filter (Requirement C):**
   * Missing entirely in v1. Users have no way to find tickets by title or combine filters.
   * *Sprint Action:* Build `search.py` with `casefold()` substring search and logical AND filters.
2. **Quality Analytics (Requirement D):**
   * Missing category breakdowns, unresolved vs resolved counts, and resolution percentage.
   * *Sprint Action:* Extend `reports.py` and provide a separate priority-sorted search results view.
3. **Engineering Understanding Check (Section 05):**
   * *Sprint Action:* Implement interactive 6-question quiz in `understanding_check.py` with decoupled scoring logic.
