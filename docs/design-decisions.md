# Design Decisions — CampusFlow & CampusFlow-Next CLI

## 1. Team Ownership & Role Distribution

### Original CampusFlow (v1 Foundation)
- **Engineer A:** Alexander Agbaji (@AgbajiAlexander) — Upstream / Core Data & Persistence (`tickets.py`, `storage.py`, `feat/1-core-ticket-storage`, PR #1)
- **Engineer B:** Eli Odeh (@eliodeh) — Initial Workflow & Analytics (`workflow.py`, `reports.py`, `cli.py`, `feat/2-workflow-reporting`, PR #2)

### CampusFlow-Next (Quality, Search & Reliability Sprint)
- **Engineer A: Alexander Agbaji (@AgbajiAlexander) — Ticket Safety, Validation & Storage**:
  - **Requirement A — Validation & Lifecycle Safety**: Centralized validation helper `validate_ticket()`, transition predicate `can_transition()`, canonical field normalization, and strict type verification rejecting booleans masquerading as integers.
  - **Requirement B — Notes Business Layer**: Structured note schema, `add_note()`, `next_note_id()`, status-gating (only `open` or `in_progress` accept notes; `resolved` rejected), and immutable failure semantics.
  - **Requirement E — Safe JSON Persistence**: Collection-level validation (`_validate_collection()`) prior to memory replacement, duplicate ID rejection, corruption resistance, and legacy migration (`_migrate_record()`).
  - **Branch:** `feat/21-validation-and-notes` — PR #4
  - **Test Suites:** `tests/test_validation.py`, `tests/test_notes.py`, `tests/test_storage.py`, `tests/test_bug_hunter_by_A.py`

- **Engineer B: Gabriel Oche Adanu (@Aocheg) — Search, Reporting Analytics, Notes CLI & Engineering Understanding Check**:
  - **Requirement C — Multi-Filter Search**: Read-only title search using Unicode-standard `casefold()` substring matching combined with `category`, `status`, and `priority` using strict logical `AND`. Non-mutating with `copy.deepcopy()`.
  - **Requirement D — Trustworthy Quality Insights**: Enhanced analytical reports computing total tickets, status breakdown, priority breakdown, category breakdown, unresolved count (`open + in_progress`), resolved count, and 0%-safe resolution percentage. Separate optional view `sort_search_results()` ordering by priority then numeric ID without modifying the original Work Queue.
  - **Requirement B & CLI Integration**: Console menus for 'Add Follow-up Note', 'View Ticket Notes', 'Search Tickets', 'Reports', and input/retry loops with friendly feedback.
  - **Section 05 — Engineering Understanding Check**: Interactive 6-question quiz bank, input validation loop (retrying invalid choices A–D), pure scoring logic decoupled from question bank, and learner explanation capture.
  - **Branch:** `feat/22-search-and-insights` — PR #6
  - **Test Suites:** `tests/test_search.py`, `tests/test_reports.py`, `tests/test_understanding.py`, and `TestEngineerB_HuntsEngineerAsModule` in `tests/test_bug_hunter_by_A.py`

---

## 2. Architecture & Modular Separation of Concerns

The application adheres to clean separation of concerns without external third-party dependencies (Python standard library only):

```
CampusFlowTeamG/
├── tickets.py          # Data validation, normalization, ID sequencing, Priority Engine
├── storage.py          # JSON read/write, atomic replacement, corruption handling
├── workflow.py         # Assignment logic, state transitions, locking, reopening
├── reports.py          # Work queue filtering/sorting, volume reports
├── cli.py              # Interactive console interface and input loop
├── main.py             # Application entrypoint
├── tests/              # Modular unittest test suites (30 tests)
│   ├── test_tickets.py
│   ├── test_workflow.py
│   ├── test_storage.py
│   └── test_reports.py
├── docs/               # Sprint governance, AI learning logs, and PR reviews
│   ├── design-decisions.md
│   ├── ai-learning-log.md
│   └── pr-reviews.md
├── data/               # Local runtime data directory (ignored in git)
└── PRD.md              # Product Requirement Document
```

---

## 3. Data Model & Input Normalization Decisions

1. **Identifier Format (`id`)**:
   - Sequential format `T001`, `T002`, `T003`...
   - Extracted numerically on reload so subsequent ticket creations never collide, even after deleting or modifying previous tickets.

2. **Case Normalization**:
   - `category`: Accepted case-insensitively and stored strictly normalized as `Network`, `Hardware`, `Software`, or `Other`.
   - `urgency`: Accepted case-insensitively and stored normalized as lowercase (`low`, `medium`, `high`).
   - `status`: Normalizes to lowercase (`open`, `in_progress`, `resolved`).
   - `affected_users`: Must strictly be a positive integer > 0. Floating-point numbers, negative numbers, 0, and non-numeric text are explicitly rejected with distinct error messages.

3. **Pure Priority Engine**:
   - `calculate_priority(urgency, affected_users)` is implemented as a pure function without I/O or global state, allowing 100% deterministic unit testing against PRD Section 7 rules.

---

## 4. Lifecycle & State Machine Security

- **Unassigned Gate**: A ticket with `assigned_to = None` CANNOT move to `in_progress`.
- **Lock on Resolved**: Once a ticket reaches `resolved`, it cannot directly transition to any other status.
- **Explicit Reopen**: A resolved ticket can only be modified if explicitly reopened via `reopen_ticket`, resetting its status to `open`.
- **Atomic Operations**: Any invalid transition raises a `ValueError` without mutating stored ticket attributes.

---

## 5. Storage & Persistence Reliability

- **Persistence Timing**: In addition to saving upon clean exit, CampusFlow automatically persists tickets immediately after every state mutation (create, assign, transition, reopen). This eliminates data loss in unexpected terminal disconnections.
- **Corrupt Storage Defense**: If `data/tickets.json` contains malformed or corrupted JSON, `storage.load_tickets` returns a descriptive error message and an empty in-memory list **without** truncating or overwriting the damaged file on disk.
- **Atomic Writes**: Saves write first to a `.tmp` file and perform an atomic filesystem replacement (`os.replace`) to prevent corrupted half-written files during sudden process termination.

---

## 6. GitHub Multi-Repo Collaboration Workflow

To reflect the team's two-repository setup:
1. `origin`: Repository managed by Engineer A (Alexander Agbaji) and Engineer B (Gabriel Oche Adanu): `https://github.com/AgbajiAlexander/campusflow.git`.
2. `upstream/fork context`: Project originally initiated with Eli Odeh (`https://github.com/eliodeh/campusflow-next.git`), now independently continued as `campus-flow-next` on Alexander Agbaji's repository.
3. Branches follow the required specification: `<type>/<issue-number>-<short-description>`.
4. Pull Requests require cross-engineer reviews with substantive technical comments prior to merging into `main`.

---

## 7. campus-flow-next Architectural & Invariant Decisions

### 7.1 Centralized Validation & Transition Predicates (Requirement A)
- **Centralized Helper**: `validation.validate_ticket()` enforces schema rules in a single location, verifying mandatory keys, non-empty titles after stripping, canonical categories (`Network`, `Hardware`, `Software`, `Other`), canonical urgencies (`low`, `medium`, `high`), positive non-zero integers for `affected_users`, and legal statuses.
- **Boolean Guard**: `isinstance(True, int)` is true in Python. Validation explicitly checks `if isinstance(users, bool): raise ValueError(...)` before verifying numeric bounds.
- **Pure Transition Invariants**: `validation.can_transition(ticket, target_status)` operates as a pure predicate without side effects. An unassigned ticket (`assigned_to is None`) cannot transition to `in_progress`. A resolved ticket cannot transition via normal progression.

### 7.2 Structured Follow-up Notes (Requirement B)
- **Schema & Identification**: Each note is stored as `{"note_id": "N001", "author": str, "message": str}` under the ticket's `"notes"` list.
- **Status Gating**: `notes.add_note()` allows note appending only when status is `open` or `in_progress`. Resolved tickets strictly reject new notes until explicitly reopened. Existing notes are preserved across status changes.
- **ID Continuity & Immutability**: `next_note_id()` inspects existing notes to determine the next sequential ID (`N001`, `N002`, ...). If validation fails on author or message length (5–300 chars), the function raises `ValueError` before generating or consuming a note ID, leaving the ticket collection untouched.

### 7.3 Multi-Filter Search Architecture (Requirement C)
- **Read-Only Guarantee**: `search.search_tickets()` returns deep copies (`copy.deepcopy`) of matching records, ensuring callers cannot mutate repository memory.
- **Unicode Caseless Matching**: Title search utilizes `casefold()` on both query and title strings, providing reliable caseless matching for Unicode strings.
- **Logical AND Combination**: Category, status, and priority filters are combined using strict logical `AND`. A ticket must satisfy all supplied filters to match. Empty or omitted filters are ignored.

### 7.4 Trustworthy Quality Insights (Requirement D)
- **Zero-Safe Metrics**: `reports.generate_report()` derives metrics dynamically from current ticket states. Resolution percentage is calculated as `(resolved / total * 100) if total > 0 else 0.0`, preventing `ZeroDivisionError` on empty datasets.
- **Unresolved Derivation**: Unresolved tickets are strictly calculated as `open + in_progress`. Reopened tickets are counted as `open`, eliminating double-counting.
- **Separation of Work Queue and Search View**: The original Open Work Queue (`get_work_queue()`) remains strictly filtered to `open` tickets only. A separate function `sort_search_results()` sorts general search results by priority rank and numeric ID without altering work queue behavior.

### 7.5 Pre-Load Collection Validation & Legacy Migration (Requirement E)
- **Parse-Before-Mutate**: `storage.load_tickets()` decodes JSON, validates the entire collection structure and duplicate ID uniqueness, and rejects the load if any record is invalid. In-memory state remains untouched upon rejection.
- **Backward-Compatible Migration**: Records created in v1 without the `"notes"` key are automatically migrated by `_migrate_record()` to include `"notes": []`, preserving backward compatibility.

### 7.6 Engineering Understanding Check (Section 05)
- **Decoupled Scoring Engine**: `understanding_check.score_answers()` is a pure function that evaluates submitted choices against the answer key without relying on I/O or CLI interactions.
- **Robust Input Validation**: The interactive CLI loop accepts only choices `A`, `B`, `C`, or `D` (case-insensitive), re-prompting on invalid inputs without incrementing the score or aborting the session.
- **Self-Explanation Capture**: Learners provide explanations for at least two questions for live mentor defense and inspection.

