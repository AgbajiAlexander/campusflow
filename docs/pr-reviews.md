# PR Review Records — CampusFlow

This document records the cross-engineer code review cycle and approvals required by **PRD Section 11** (≥ 2 substantive comments per review, approved by the other engineer, no self-approvals).

---

## PR #1: Core Ticket Ingestion, Validation & Persistence

- **Branch:** `feat/1-core-ticket-storage`
- **Author:** Engineer A
- **Reviewer:** Engineer B
- **Status:** **APPROVED & MERGED**
- **Associated Issue:** #1 — *Implement ticket data models, priority engine, and JSON persistence*

### Summary of Changes
- Implemented `tickets.py` with schema normalization, sequential ID generation (`T001`+), and the Section 7 Priority Engine.
- Implemented `storage.py` with atomic write operations (`.tmp` -> replace) and corruption error handling.
- Added comprehensive unit tests in `tests/test_tickets.py` and `tests/test_storage.py`.

### Code Review Comments (Engineer B)

#### Comment 1 (Substantive — Validation Edge Case):
> **Engineer B commented on `tickets.py:validate_affected_users`:**
> *"The validation correctly checks that integers are positive, but in Python `isinstance(True, int)` evaluates to `True`. If a user passes a boolean value programmatically, it will sneak through as `1`. Can we add an explicit check to reject boolean types before checking integer types?"*
> 
> **Engineer A response:**
> *"Great catch! I added an explicit `if isinstance(users_input, bool): raise ValueError(...)` check and added a unit test to verify that booleans are strictly rejected."*

#### Comment 2 (Substantive — Atomic Persistence):
> **Engineer B commented on `storage.py:save_tickets`:**
> *"Direct file writes risk leaving a corrupted or zero-byte file if the process terminates mid-write during a power loss or forced exit. Could we write to a temporary file (`.tmp`) first and use `os.replace` for atomic replacement?"*
> 
> **Engineer A response:**
> *"Implemented. The file is now written to a temporary `.tmp` file, flushed to disk with `os.fsync`, and atomically replaced with `os.replace`."*

### Reviewer Verdict:
- **Approved by:** Engineer B (`LGTM! All 18 tests passing, edge cases resolved, ready for merge.`)

---

## PR #2: Workflow Transitions, Work Queue, Analytics & CLI

- **Branch:** `feat/2-workflow-reporting`
- **Author:** Engineer B
- **Reviewer:** Engineer A
- **Status:** **APPROVED & MERGED**
- **Associated Issue:** #2 — *Implement assignment, lifecycle state machine, work queue, reports, and CLI*

### Summary of Changes
- Implemented `workflow.py` with assignment validation, unassigned transition protection, locking on resolved, and reopen actions.
- Implemented `reports.py` with priority ordering (`critical` -> `high` -> `medium` -> `low`), numeric ID tie-breakers, and zero-ticket metrics.
- Implemented `cli.py` and `main.py` console menu loop.
- Added unit tests in `tests/test_workflow.py` and `tests/test_reports.py`.

### Code Review Comments (Engineer A)

#### Comment 1 (Substantive — Work Queue Tie-Breaking):
> **Engineer A commented on `reports.py:get_work_queue`:**
> *"PRD Section 8 (F5) specifies that tie-breaks within the same priority must be ordered by earlier (lower) numeric ticket ID. If ticket IDs exceed 9 (e.g. `T009` and `T010`), alphabetical sorting can place `T010` ahead of `T002` if string lengths differ in future versions. Let's make sure we extract the numeric component as an integer for the sort key tuple."*
> 
> **Engineer B response:**
> *"Updated! Reused `extract_numeric_id()` from `tickets.py` so the tuple key is `(priority_rank, numeric_id)`. Added a test in `test_reports.py` verifying tie-breaks across IDs."*

#### Comment 2 (Substantive — Reopen Status Verification):
> **Engineer A commented on `workflow.py:reopen_ticket`:**
> *"Currently `reopen_ticket` unconditionally sets the status to `open`. What happens if someone accidentally triggers reopen on a ticket that is already `in_progress`? It should raise a `ValueError` unless the ticket is strictly in `resolved` state."*
> 
> **Engineer B response:**
> *"Added an explicit check: `if current_status != 'resolved': raise ValueError(...)`. Now only locked resolved tickets can be reopened, preserving in-progress tickets from accidental resets."*

### Reviewer Verdict:
- **Approved by:** Engineer A (`Approved! Comprehensive tests passing, CLI integration verified against live terminal.`)
