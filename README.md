# CampusFlow Next — Campus IT Helpdesk Ticket Manager (CLI)
README.md — Engineer A's Section
Here's a straight, honest README focused on your (Engineer A) contribution. You can either use this as-is or merge it into a shared README with your partner.

Engineer A: Elizabeth Odeh
Engineer B: Agbaji Alexander

# CampusFlow

A Python command-line ticket manager for Learn2Earn campus staff. It records
technical support requests (Wi-Fi outages, faulty laptops, broken dev
environments, inaccessible platforms), calculates priority, assigns
responsibility, and tracks progress.

## Problem

Campus staff report issues informally — through WhatsApp, hallway chats, email —
and those reports get lost. CampusFlow gives every request a tracked record
with a computed priority and a clear owner.

## Team

- **Engineer A** — Ticket creation, input validation, priority engine, tests
- **Engineer B** — Assignment, workflow state machine, work queue, reports,
  JSON persistence, CLI integration

## Requirements

- Python 3.10 or later
- No external dependencies (uses only the standard library)

## Setup

```bash
git clone https://github.com/eliodeh/campusflow.git
cd campusflow

git clone https://github.com/AgbajiAlexander/campusflow.git 



Engineer A — Detailed contribution
I built and tested the ticket creation and priority logic.

Files I own:

campusflow/tickets.py — priority engine, validators, create_ticket(),
generate_next_id()

tests/test_tickets.py — 12 unit tests for the priority engine and input
validation

Key functions:

calculate_priority(urgency, affected_users) — returns
critical / high / medium / low using the four rules above.
Written as a pure function: no I/O, no time, no hidden state.

validate_title(title) — rejects blank or non-string titles.

validate_category(category) — normalizes case, rejects unknown values.

validate_urgency(urgency) — normalizes case, rejects unknown values.

validate_affected_users(users) — requires a positive integer.

generate_next_id(existing_tickets) — produces T001, T002, …

create_ticket(...) — orchestrates the above and returns a complete
ticket dictionary.

Tests I wrote:

Priority rule 1 (high + >= 10 users → critical)

Priority rule 2 (high urgency OR >= 10 users → high)

Priority rule 3 (medium urgency OR >= 3 users → medium)

Priority rule 4 (everything else → low)

Boundary cases at exactly 3 users and exactly 10 users

Case normalization ("NETWORK" → "Network")

Rejection of blank titles

Rejection of non-positive affected_users (zero, negative, non-integer)

Rejection of invalid categories and invalid urgencies

Sequential ID generation starting at T001

Git workflow
This project follows a two-person PR workflow. Every feature was built on
its own branch and merged through a reviewed pull request.

PR #1 — feat/1-ticket-creation: priority engine + 9 tests

PR #2 — feat/2-workflow-reporting: assignment, workflow, queue,
reports, persistence, CLI


AI usage
AI was used to learn concepts, not to write the project. Every AI
suggestion was verified by writing a test or reading the Python
documentation. Details are in docs/ai-learning-log.md.



After Writing It
Save the file

Verify it renders by opening it on GitHub later (after pushing)

Commit it.



What I learned
How ordered if/elif cascades implement business rules — and why the
order matters when Rule 1 is a strict subset of Rule 2.

Why pure functions (no I/O, no time) are easy to test.

The Python AND / OR truth tables and how they show up in real
decision logic.

The professional Git workflow: feature branch → commit → push → PR →
review → merge.
# CampusFlow — Campus IT Helpdesk Ticket Manager (CLI)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-43%20passed-brightgreen.svg)]()
[![Standard Library](https://img.shields.io/badge/dependencies-none%20(stdlib)-orange.svg)](https://docs.python.org/3/library/)

> A dependable, test-driven Python command-line application built for Learn2Earn campus staff to record, prioritize, search, validate, assign, track, and resolve IT support tickets with structured follow-up notes, disk persistence, and trustworthy analytics.

---

## 👥 Team & Sprint Details

- **Product:** CampusFlow Next
- **Sprint:** Guided Reliability, Search & Engineering Quality Sprint
- **Engineering Pair:**
  - **Engineer A:** Alexander Agbaji ([@AgbajiAlexander](https://github.com/AgbajiAlexander)) — Ticket Safety, Validation & Storage
  - **Engineer B:** Gabriel Oche Adanu ([@Aocheg](https://github.com/Aocheg)) — Search, Reporting Analytics, Notes CLI & Engineering Understanding Check *(continuing the project on the team repository originally initiated with Eli Odeh)*
- **Status:** Complete, Tested, and Verified

### Branches & Pull Requests
- **Engineer A Feature Branch:** `feat/21-validation-and-notes` — [PR #4](https://github.com/eliodeh/campusflow-next/pull/4)
- **Engineer B Feature Branch:** `feat/22-search-and-insights`
- **Main Integration Branch:** `main`
- **Primary Remote:** `https://github.com/AgbajiAlexander/campusflow.git`

---

## 🚀 Quick Start & Fresh Clone Setup

CampusFlow Next runs on **Python 3.10+** and relies **exclusively on the Python standard library** (no external pip dependencies needed).

### 1. Fresh Clone Setup
```bash
git clone https://github.com/AgbajiAlexander/campusflow.git
cd campusflow
```

### 2. Run the Automated Test Suite
Run the full test discovery across all suites:
```bash
python3 -m unittest discover -s tests -v
```

### 3. Launch the Interactive CLI
```bash
# Using main entry point
python3 main.py

# Or directly through cli.py
python3 cli.py
```

---

## 📋 Features Overview

### Original CampusFlow Preserved (F1 – F7)
| Feature | Description | PRD Section | Module |
|---|---|---|---|
| **Create Ticket (F1)** | Interactive ticket creation with validation, sequential `T001` ID generation, and automatic priority calculation. | §8 F1 | `tickets.py` |
| **List & View (F2)** | Tabular overview of all tickets and full-detail single ticket lookup by ID. | §8 F2 | `tickets.py` |
| **Assign Staff (F3)** | Assign or reassign tickets to campus staff members with non-empty validation. | §8 F3 | `workflow.py` |
| **Lifecycle Workflow (F4)** | State machine (`open -> in_progress -> resolved`) with unassigned protection, locking on resolved, and explicit reopening. | §8 F4 | `workflow.py` |
| **Open Work Queue (F5)** | Real-time queue showing only active `open` tickets, ordered by priority rank and numeric ID tie-breakers. | §8 F5 | `reports.py` |
| **Analytical Reports (F6)** | Summary volume metrics, status breakdowns, and priority breakdowns (handles zero tickets safely). | §8 F6 | `reports.py` |
| **Disk Persistence (F7)** | Atomic JSON persistence to `data/tickets.json`, auto-saving on each state change, with corruption protection and ID continuity. | §8 F7 | `storage.py` |

### CampusFlow Next Enhancements
| Feature | Description | Requirement | Module |
|---|---|---|---|
| **Validation & Status Safety** | Centralized record validation (`validate_ticket`) and pure transition checks (`can_transition`). Protects against booleans masquerading as integers. | Req. A | `validation.py` |
| **Structured Follow-up Notes** | Structured notes (`note_id`, `author`, `message`) gated to `open` or `in_progress` status. Preserved through resolve and reopen. | Req. B | `notes.py`, `cli.py` |
| **Multi-Filter Search** | Read-only title search using case-insensitive `casefold()` substring matching combined with `category`, `status`, and `priority` using strict logical AND. | Req. C | `search.py`, `cli.py` |
| **Trustworthy Quality Insights** | Total tickets, counts by category, unresolved count (`open + in_progress`), resolved count, and 0%-safe resolution percentage. Separate priority-sorted search view. | Req. D | `reports.py` |
| **Safe & Reproducible JSON** | Pre-load collection validation, duplicate ID rejection, corruption resistance, ID continuity across restarts, and backward-compatible migration of legacy records missing `notes`. | Req. E | `storage.py` |
| **CLI Understanding Check** | Interactive 6-question multiple-choice quiz covering system invariants with decoupled scoring and explanation capture. | Sec. 05 | `understanding_check.py`, `cli.py` |

---

## 💾 JSON Storage Envelope & Schema (Requirement E)

CampusFlow Next persists tickets as a JSON list in `data/tickets.json` (or any custom path). The collection is fully validated before updating in-memory state.

### Ticket Record Schema
```json
[
  {
    "id": "T001",
    "title": "Wi-Fi access point in Lab 3 disconnected",
    "category": "Network",
    "urgency": "high",
    "affected_users": 15,
    "priority": "critical",
    "status": "open",
    "assigned_to": "Engineer A",
    "notes": [
      {
        "note_id": "N001",
        "author": "Mentor A",
        "message": "Wi-Fi router reboot attempted; checking PoE switch"
      }
    ]
  }
]
```

### Field Definitions & Invariants:
- `id` *(string)*: Unique sequential identifier matching format `T001`, `T002`, etc.
- `title` *(string)*: Non-empty string after trimming whitespace.
- `category` *(string)*: Canonical string; one of `"Network"`, `"Hardware"`, `"Software"`, `"Other"`.
- `urgency` *(string)*: Canonical string; one of `"low"`, `"medium"`, `"high"`.
- `affected_users` *(integer)*: Strictly positive integer (`> 0`). Rejects floats, strings, negative numbers, zero, and booleans (`True`/`False`).
- `priority` *(string)*: Deterministically computed: `"critical"`, `"high"`, `"medium"`, `"low"`.
- `status` *(string)*: One of `"open"`, `"in_progress"`, `"resolved"`.
- `assigned_to` *(string or null)*: Staff label when assigned, or `null` when unassigned.
- `notes` *(list of dictionaries)*: Per-ticket notes ordered by sequential `note_id` (`N001`, `N002`, ...). Each note contains:
  - `note_id`: Unique within the ticket (`N001`+).
  - `author`: Non-empty author label.
  - `message`: Text message strictly between 5 and 300 characters after trimming.

### Backward Compatibility & Migration
Tickets generated by original CampusFlow (v1) lacked the `"notes"` field. On load, `storage.load_tickets()` automatically migrates legacy records by initializing `"notes": []` without rejecting or discarding existing data.

---

## 🧠 Priority Engine Logic (§7)

Ticket priority is evaluated deterministically in strict sequential order:
1. `urgency == "high"` **AND** `affected_users >= 10` $\rightarrow$ **`critical`**
2. `urgency == "high"` **OR** `affected_users >= 10` $\rightarrow$ **`high`**
3. `urgency == "medium"` **OR** `affected_users >= 3` $\rightarrow$ **`medium`**
4. Otherwise $\rightarrow$ **`low`**

---

## 📂 Project Directory Structure

```text
campusflow/
├── cli.py                     # Interactive menu covering F1-F7 and Next-B, C, D, Understanding Check
├── main.py                    # Root CLI entry point
├── tickets.py                 # Core schema validation, sequential ID generator, Priority Engine
├── workflow.py                # State transitions, unassigned gate, lock on resolved, reopening
├── validation.py              # Centralized record validation and transition predicates (Req. A)
├── notes.py                   # Structured follow-up notes data layer and ID generator (Req. B)
├── search.py                  # Read-only multi-filter search with casefold substring matching (Req. C)
├── reports.py                 # Quality analytics, Work Queue, and search sorting view (Req. D)
├── storage.py                 # Safe JSON loader/saver with atomic replacement and collection validation (Req. E)
├── understanding_check.py     # Interactive 6-question quiz and scoring engine (Section 05)
├── tests/                     # Automated unittest suite
│   ├── __init__.py
│   ├── test_tickets.py        # Priority engine and field validation tests
│   ├── test_workflow.py       # State machine, unassigned protection, and reopen tests
│   ├── test_storage.py        # Atomic persistence, reload continuity, and corruption safety
│   ├── test_reports.py        # Queue ordering, tie-breaking, category metrics, zero-safe division
│   ├── test_search.py         # Case-insensitive search, combined AND filtering, immutability
│   ├── test_understanding.py  # Quiz input rejection, scoring logic, question bank isolation
│   ├── test_validation.py     # Centralized ticket and transition validation tests
│   ├── test_notes.py          # Structured note creation, resolved ticket rejection, ID continuity
│   └── test_bug_hunters.py    # Cross-engineer bug hunter edge case tests
├── docs/                      # Sprint governance and engineering logs
│   ├── baseline-check.md      # Section 02 diagnostic baseline results and action items
│   ├── ai-learning-log.md     # Documented AI learning cycles with verified corrections
│   ├── design-decisions.md    # Architecture and module ownership decisions
│   └── pr-reviews.md          # Multi-engineer code review records and approvals
├── data/                      # Local runtime data directory (ignored by git)
│   └── tickets.json           # Runtime storage file
├── .gitignore                 # Standard exclusions (runtime data, caches, IDE files)
└── README.md                  # Project documentation
```

---

## 🧪 Automated Test Suite (Section 06)

The test suite covers all required acceptance cases and runs cleanly from a fresh clone:

```bash
python3 -m unittest discover -s tests -v
```

### Required Acceptance Cases Verified:
- **01. Original priority calculation:** Strict rule precedence respected.
- **02. Unassigned open $\rightarrow$ in_progress:** Rejected with unchanged data.
- **03. Resolved assignment mutation:** Rejected on locked tickets.
- **04. Invalid affected_users:** Rejects `0`, negative numbers, floats, and booleans masquerading as integers.
- **05. Valid note added:** Generates sequential `N001` note ID.
- **06. Blank/short note rejected:** Does not consume note ID.
- **07. Note on resolved ticket rejected:** Note accepted only after explicit reopen.
- **08. Search title ignores case:** Substring matching using `casefold()`.
- **09. Combined search filters:** Strict logical `AND` across all supplied filters.
- **10. Empty report division safety:** Returns `0%` resolution percentage without crash.
- **11. Report counts consistency:** Matches known fixtures across resolve and reopen cycles.
- **12. Save/load continuity:** Preserves ticket fields, notes, and sequential note IDs.
- **13. Corrupt/duplicate JSON rejected:** Safely rejected without memory loss.
- **14. CLI Understanding Check:** Rejects invalid choices and scores accurately.
- **Extra Bug-Hunter Tests:** Cross-module edge cases in `tests/test_bug_hunters.py`.
---

## 🌿 Git Multi-Branch Workflow & Remotes

### Remote Repositories
```bash
# Upstream repository (Engineer A - eliodeh)
git remote add origin https://github.com/eliodeh/CampusFlow.git

# Fork repository (Engineer B - AgbajiAlexander)
git remote add fork https://github.com/AgbajiAlexander/CampusFlow.git
```

### Feature Branches
- **Engineer A:** `feat/1-core-ticket-storage`
- **Engineer B:** `feat/2-workflow-reporting`
- **Integration Branch:** `main`

Good Collaboration
