# PR Review Records — CampusFlow

This document records the cross-engineer code review cycle and approvals required by **PRD Section 11** (≥ 2 substantive comments per review, approved by the other engineer, no self-approvals).

---

## PR #1: Core Ticket Ingestion, Validation & Persistence

- **Branch:** `feat/1-core-ticket-storage`
- **Author:** Alexander Agbaji (@AgbajiAlexander - Engineer A)
- **Reviewer:** Eli Odeh (@eliodeh - Engineer B)
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
- **Author:** Eli Odeh (@eliodeh - Engineer B)
- **Reviewer:** Alexander Agbaji (@AgbajiAlexander - Engineer A)
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

---

## PR #4: Centralized Validation, Structured Notes & Collection Storage Defense (CampusFlow-Next)

- **Branch:** `feat/21-validation-and-notes`
- **Author:** Alexander Agbaji (@AgbajiAlexander - Engineer A)
- **Reviewer:** Gabriel Oche Adanu (@Aocheg - Engineer B)
- **Status:** **APPROVED & MERGED**
- **Associated Issue:** #4 / #21 — *Ticket validation, note data layer, status gating, and safe collection reload*

### Summary of Changes
- Implemented `validation.py` with `validate_ticket()`, `can_transition()`, canonical field normalization, and strict type checking (rejecting booleans masquerading as integers).
- Implemented `notes.py` with `add_note()`, `next_note_id()`, status-gating (only `open` or `in_progress` tickets accept notes; resolved tickets rejected), and immutable failure semantics.
- Enhanced `storage.py` with collection-level validation (`_validate_collection`) before touching in-memory state, duplicate ID rejection, and backward-compatible migration of legacy tickets missing `notes` (`_migrate_record`).
- Added unit tests in `tests/test_validation.py`, `tests/test_notes.py`, and `tests/test_storage.py`.

### Code Review Comments (Engineer B: Gabriel Oche Adanu @Aocheg)

#### Comment 1 (Substantive — Safe Collection Reload & Legacy Migration):
> **Engineer B commented on `storage.py`: lines 14–42 (`_migrate_record` and `_validate_collection`):**
> *"Solid defensive engineering here. `_migrate_record()` cleanly handles backward compatibility for tickets created in v1 without `notes`, ensuring old records are not discarded. Additionally, `_validate_collection()` ensures duplicate IDs or malformed records reject the load before touching in-memory state. This fully satisfies Requirement E."*
>
> **Engineer A response:**
> *"Thank you! I added unit test `test_old_record_missing_notes_field_is_migrated_not_rejected` to explicitly verify that legacy tickets receive an empty notes list `[]` while preserving all original attributes."*

#### Comment 2 (Substantive — Cross-Branch Test Dependency):
> **Engineer B commented on `tests/test_bug_hunter_by_A.py`: line 7:**
> *"The `ModuleNotFoundError: No module named 'search'` from your test run occurred because `search.py` was being developed concurrently on my branch (`feat/22-search-and-insights`). I tested your bug-hunter test (`test_search_category_filter_is_exact_match_not_case_insensitive`) against my `search.py`: our implementation uses exact category matching so `cli.py` handles normalization. Once our branches merge, `import search` resolves and this test passes 100%."*
>
> **Engineer A response:**
> *"Understood! That confirms the invariant that `search.py` is a pure AND-filter expecting canonical values, while `cli.py` normalizes user inputs prior to passing them to `search.py`."*

#### Comment 3 (Substantive — Note Rejection Immutability):
> **Engineer B commented on `notes.py:add_note`:**
> *"Requirement B states: 'A rejected note must not consume a note ID' and 'Invalid note actions must leave the entire ticket collection unchanged.' Let's make sure that if author validation fails or message is outside 5–300 characters, no dummy note is appended and the ticket dictionary remains strictly untouched."*
>
> **Engineer A response:**
> *"Verified. `add_note()` validates author length and message length BEFORE generating the note ID and before appending to `ticket['notes']`. If validation fails, `ValueError` is raised and `ticket['notes']` is identical to its pre-call state. Covered in `test_blank_or_too_short_note_rejected_without_consuming_id`."*

### Reviewer Verdict:
- **Approved by:** Gabriel Oche Adanu (@Aocheg - Engineer B) (`LGTM! All 42 validation, note, storage, and regression tests pass. Invariants verified, ready for merge into main.`)

---

## PR #6: Combined Search Filtering, Quality Reporting Analytics & CLI Understanding Check (CampusFlow-Next)

- **Branch:** `feat/22-search-and-insights`
- **Author:** Gabriel Oche Adanu (@Aocheg - Engineer B)
- **Reviewer:** Alexander Agbaji (@AgbajiAlexander - Engineer A)
- **Status:** **APPROVED & MERGED**
- **Associated Issue:** #6 / #22 — *Implement multi-filter search, trustworthy quality insights, notes CLI menus, and understanding check*

### Summary of Changes
- Implemented `search.py` with case-insensitive title search via `casefold()` substring matching, and combined filtering on `category`, `status`, and `priority` using strict logical `AND`.
- Enhanced `reports.py` with `generate_report()` computing total tickets, status counts, priority counts, category counts, unresolved count (`open + in_progress`), resolved count, and 0%-safe resolution percentage. Added separate `sort_search_results()` view ordering by priority then numeric ID without mutating the original Work Queue.
- Implemented `understanding_check.py` with interactive 6-question quiz bank, input validation loop (retrying invalid choices A–D), pure scoring logic, and learner explanation capture.
- Integrated all new workflows into `cli.py` (Add Follow-up Note, View Ticket Notes, Search Tickets, Reports, and Understanding Check).
- Added comprehensive unit tests in `tests/test_search.py`, `tests/test_reports.py`, and `tests/test_understanding.py`.

### Code Review Comments (Engineer A: Alexander Agbaji @AgbajiAlexander)

#### Comment 1 (Substantive — Quality Insights Zero-Division Safety):
> **Engineer A commented on `reports.py:generate_report`:**
> *"In `reports.py`, confirmed `resolution_percentage` returns `0.0` on an empty list rather than raising `ZeroDivisionError` — matches Requirement D."*
>
> **Engineer B response:**
> *"Yes, the calculation explicitly checks `(resolved / total * 100) if total > 0 else 0.0`. Unit test `test_10_empty_dataset_resolution_percentage_is_zero_not_crash` in `tests/test_reports.py` guards this behavior."*

#### Comment 2 (Substantive — Interactive CLI Integration):
> **Engineer A commented on `cli.py`:**
> *"Your `cli.py` updates were very handy! The menus for adding/viewing notes cleanly consume the APIs from `notes.py`, handle validation exceptions gracefully with user-friendly error messages, and loop cleanly without terminating the CLI session."*
>
> **Engineer B response:**
> *"Thanks! I separated the business logic in `search.py`, `reports.py`, and `understanding_check.py` so that all functions can be imported and tested programmatically without relying on interactive `stdin` / `input()` mocks."*

#### Comment 3 (Substantive — Read-Only Search Immutability):
> **Engineer A commented on `search.py:search_tickets`:**
> *"Requirement C mandates that search must be read-only and must never modify ticket records. In `search_tickets()`, let's ensure callers cannot mutate the underlying ticket collection through the returned list."*
>
> **Engineer B response:**
> *"Implemented with `copy.deepcopy(matching)` so the returned list contains deep copies of matching tickets. Even if a caller modifies a returned ticket in memory, the stored dataset remains completely untouched. Verified with `test_search_does_not_mutate_any_ticket`."*

### Reviewer Verdict:
- **Approved by:** Alexander Agbaji (@AgbajiAlexander - Engineer A) (`Approved! Multi-filter search, quality insights, notes menus, and understanding check verified. All 63 integrated tests passing cleanly.`)
