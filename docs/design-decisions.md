# Design Decisions — CampusFlow CLI

## 1. Team Ownership & Role Distribution

In alignment with **PRD Section 11** and the agreed sprint roles:

- **Engineer A: Alexander Agbaji (@AgbajiAlexander) — Upstream / Core Data & Persistence**:
  - **F1 — Create Ticket**: Input validation, ID sequencing (`T001`), and priority evaluation.
  - **F2 — List & View**: Tabular summaries and full record lookups.
  - **F7 — Persistence**: Safe JSON storage, atomic file replacement, and corruption protection.
  - **Branch**: `feat/1-core-ticket-storage`
  - **Repository**: Upstream central repository (`https://github.com/AgbajiAlexander/CampusFlowTeamG.git`).

- **Engineer B: Eli Odeh (@eliodeh) — Fork / Workflow & Analytics**:
  - **F3 — Assign Staff**: Assignee validation and reassignment handling.
  - **F4 — Ticket Lifecycle**: State machine transitions (`open -> in_progress -> resolved`) and resolved-ticket locking / reopening.
  - **F5 — Work Queue**: Filtered active ticket prioritization with numeric ID tie-breakers.
  - **F6 — Analytical Reports**: Summary counts and status/priority aggregations with zero-count safety.
  - **CLI Menu Loop**: Interactive console driver integrating all modules.
  - **Branch**: `feat/2-workflow-reporting`
  - **Repository**: Developer fork (`https://github.com/eliodeh/CampusFlowTeamG.git`).

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
1. `origin`: Upstream repository managed by Engineer A — Alexander Agbaji (`https://github.com/AgbajiAlexander/CampusFlowTeamG.git`).
2. `fork`: Forked repository managed by Engineer B — Eli Odeh (`https://github.com/eliodeh/CampusFlowTeamG.git`).
3. Branches follow the required specification: `<type>/<issue-number>-<short-description>`.
4. Pull Requests require cross-engineer reviews with substantive technical comments prior to merging into `main`.
