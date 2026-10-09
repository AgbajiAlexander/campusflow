# PRD — CampusFlow
**Product:** CampusFlow — Campus IT Helpdesk Ticket Manager (CLI)
**Owner:** Alexander Agbaji (@AgbajiAlexander) & Eli Odeh (@eliodeh)
**Sprint:** AI-Native Engineering Sprint, 6 hours, 100 marks
**Status:** Final / Active — Upstream: https://github.com/AgbajiAlexander/CampusFlowTeamG | Fork: https://github.com/eliodeh/CampusFlowTeamG

---

## 1. Problem Statement

Learn2Earn campus staff report technical issues (Wi-Fi outages, broken laptops,
inaccessible dev environments) informally, and reports get lost. There is no system
to record, prioritize, assign, and track the resolution of these issues.

## 2. Goal

Build a working, tested, Python command-line application that lets staff record
support tickets, automatically calculates a priority, allows assignment to a staff
member, tracks a ticket through its lifecycle, surfaces an ordered work queue, reports
on ticket volume, and persists everything to disk between runs.

## 3. Success Metrics (Definition of Done)

- All 7 features (F1–F7) work from a single running CLI menu.
- The four documented priority examples all resolve correctly.
- Invalid input/transitions are rejected without corrupting stored data.
- Data survives an application restart (JSON round-trip), with IDs staying unique.
- ≥ 8 meaningful automated tests pass on `main` (not just on a feature branch).
- Both features were built on separate branches, each reviewed via a real PR with
  ≥ 2 substantive comments, approved by the *other* engineer, and merged — not self-approved.

## 4. Users

- **Campus IT staff (ticket creators / assignees)** — the people who will run this CLI
  day-to-day. Not technical; needs clear menus and clear error messages.
- **Engineer A / Engineer B** — the two fellows, who are also the only "developers"
  of this system.

## 5. Scope

**In scope:** text-based CLI, JSON file persistence, the 7 features below, automated
tests via `unittest`.
**Out of scope:** GUI, web interface, database, external API/AI SDK calls at runtime,
multi-user auth, networked access. Do not spend sprint time on any of these.

## 6. Data Model

### Ticket object

| Field | Type | Notes |
|---|---|---|
| `id` | string | Auto-generated, unique, format `T001`, `T002`, … |
| `title` | string | Required, must not be blank |
| `category` | string | One of: `Network`, `Hardware`, `Software`, `Other` |
| `urgency` | string | One of: `low`, `medium`, `high` |
| `affected_users` | int | Required, positive integer only (not 0, negative, decimal, or text) |
| `priority` | string | Computed — see §7. One of: `critical`, `high`, `medium`, `low` |
| `status` | string | `open` → `in_progress` → `resolved`, with reopen path back to `open` |
| `assigned_to` | string or `None` | Staff member name, or `None` until assigned |

Example:
```json
{
  "id": "T001",
  "title": "Campus Wi-Fi is down",
  "category": "Network",
  "urgency": "high",
  "affected_users": 15,
  "priority": "critical",
  "status": "open",
  "assigned_to": null
}
```

Input normalization: accept reasonable case variations (e.g. `High`, `HIGH`, `high`)
and normalize consistently before storing/comparing. Invalid values must produce a
clear, specific error message, not a silent default or a crash.

## 7. Priority Engine (fixed business logic — not AI-generated, not configurable)

Evaluate in this exact order; apply the **first** matching rule:

1. `urgency == high` AND `affected_users >= 10` → **critical**
2. `urgency == high` OR `affected_users >= 10` → **high**
3. `urgency == medium` OR `affected_users >= 3` → **medium**
4. Otherwise → **low**

This is ordinary Python conditional logic. It must be a pure, independently testable
function (no interactive input inside it).

## 8. Features & Acceptance Criteria

### F1 — Create Ticket
- Collect title, category, urgency, affected_users via CLI prompts.
- Validate every field; reject blank title, invalid category/urgency, non-positive or
  non-integer `affected_users`, with a specific error per field.
- Auto-generate the next sequential unique ID.
- Compute priority via the engine in §7.
- Store the record (default `status = "open"`, `assigned_to = None`).

### F2 — List / View
- List all tickets (summary view: id, title, priority, status).
- View full detail for one ticket by ID; handle unknown ID gracefully.

### F3 — Assign
- Assign a ticket to a non-empty staff name.
- Reject assignment to an unknown ticket ID.
- Reassignment (changing an existing assignee) should be allowed.

### F4 — Workflow
- Valid transitions: `open → in_progress → resolved`.
- An **unassigned** ticket cannot move to `in_progress` (must be assigned first).
- A `resolved` ticket is locked — it can only change again after an explicit **reopen**
  action, which sets it back to `open`.
- Any other transition attempt is rejected with a clear message; stored data is
  unchanged on rejection.

### F5 — Work Queue
- Show only open, unresolved tickets (i.e., not `resolved`).
- Sort order: `critical → high → medium → low`.
- Tie-break within the same priority by the earlier (lower) numeric ticket ID.

### F6 — Reports
- Total ticket count.
- Breakdown by `status`.
- Breakdown by `priority`.
- Must handle the zero-tickets case without crashing (show zero counts, not an error).

### F7 — Persistence
- Save all tickets to a JSON file after changes (or on exit — decide and document).
- Reload on startup.
- Missing file → start fresh with an empty ticket list (not an error).
- Malformed/corrupt JSON → clear error message to the user; **do not silently wipe**
  existing data.
- IDs must remain unique and continue incrementing correctly after a reload.

## 9. CLI

Single menu loop, text-only, options for each feature plus **Exit**. No GUI/web work.

## 10. Non-Functional Requirements

- Python standard library only (`unittest`, `json`); no external frameworks, DB, or
  API keys required to run the app.
- ≥ 8 meaningful automated tests: cover normal cases, invalid input, boundary values,
  and persistence (see Appendix A for the required scenario list).
- Clean separation of concerns suggested: `tickets.py` (create/validate/priority),
  `workflow.py` (status transitions), `storage.py` (load/save JSON), `reports.py`
  (queue/report views) — see the Fellows' Guide §2.3 for the suggested layout.
- Runtime files (`data/tickets.json`) and local dev files excluded from Git via
  `.gitignore`.

## 11. Process Requirements (also graded)

- Two Git branches, one per engineer, named `<type>/<issue-number>-<short-description>`.
- A GitHub Issue per major work area with acceptance criteria.
- One PR per engineer, reviewed by the other with ≥ 2 substantive comments, approved
  by the reviewer (never self-approved), merged into `main`.
- `docs/design-decisions.md` recording agreed interfaces/ownership.
- `docs/ai-learning-log.md` with ≥ 3 logged AI interactions per fellow, including at
  least one where an AI suggestion was corrected, improved, or rejected after
  verification.

## 12. Milestones (mapped to the 6-hour sprint)

| Time | Milestone |
|---|---|
| 00:00–00:20 | Repo created, both collaborators set up, `.gitignore` in place |
| 00:20–00:50 | Issues filed, ownership split, `design-decisions.md` drafted |
| 00:50–01:30 | Initial AI learning-loop entries (2 per fellow) |
| 01:30–03:55 | Feature branches implemented + tested, commits pushed |
| 03:55–05:00 | PRs opened, cross-reviewed, corrections applied |
| 05:00–05:40 | Merged to `main`, integration-tested, README/docs finalized |
| 05:40–06:00 | Live demo + technical defence |

## 13. Risks

| Risk | Mitigation |
|---|---|
| Second branch goes stale after first merge | Merge `main` into the remaining branch, resolve conflicts, rerun tests before final PR approval |
| Priority rule order misapplied | Write the 4 documented examples as tests *first*, before building other features |
| JSON corruption wipes data | Wrap load in a try/except that reports the error instead of overwriting the file |
| One partner does most of the work | Explicit per-feature ownership (§2.1 of Fellows' Guide) + independent PR authorship requirement |

## 14. Appendix A — Required Test Scenarios (minimum set)

- High urgency + 12 affected users → `critical`
- High urgency + 2 affected users → `high`
- Low urgency + 4 affected users → `medium`
- Low urgency + 1 affected user → `low`
- `affected_users = 0` → rejected
- Unassigned ticket cannot move to `in_progress`
- Assigned ticket progresses `open → in_progress → resolved`
- Open-ticket queue sorted by priority, then numeric ID
- Save/reload preserves existing tickets
- New ticket after reload does not duplicate an ID

Recommended extra cases: empty report, unknown ticket ID, blank title, invalid
urgency, invalid transition, reopening, corrupted JSON, queue ties.
