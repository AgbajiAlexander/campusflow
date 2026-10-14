## Interaction #3 — Rejecting an AI suggestion to use a list-of-rules engine

**Problem:**
I was writing the priority engine and asked the AI for a cleaner way to
structure the four rules. The AI suggested replacing the if/elif cascade
with a list of `(rule_function, priority)` tuples and iterating through it.

**My initial understanding:**
The AI's suggestion looked elegant — fewer lines of code, and easy to add
new rules later by just appending to a list.

**Prompt to AI:**
"Refactor this priority function to avoid long if/elif chains. Show me a
more scalable approach."

**Useful AI guidance:**
The AI returned this refactor:

```python
def is_critical(urgency, users):
    return urgency == "high" and users >= 10

def is_high(urgency, users):
    return urgency == "high" or users >= 10

def is_medium(urgency, users):
    return urgency == "medium" or users >= 3

PRIORITY_RULES = [
    (is_critical, "critical"),
    (is_high, "high"),
    (is_medium, "medium"),
]

def calculate_priority(urgency, affected_users):
    for rule, priority in PRIORITY_RULES:
        if rule(urgency, affected_users):
            return priority
    return "low"


My independent experiment:
I saved the AI's version in a scratch file and ran my 9 tests against it.
All 9 passed. The behaviour was identical to my if/elif version. But then
I tried to explain the code out loud as if I were in the technical demo.
I could not quickly explain why the rules were stored as tuples of
function references, or why the order inside PRIORITY_RULES mattered.
During the hand-tracing practice I had been doing, the if/elif version
let me read rule 1, then rule 2, then rule 3, in the same order the spec
lists them. The AI's version hides that order inside a list, one level of
indirection away.

Verification source:
I re-read the Python docs on lists and tuple unpacking, and I asked
myself: "Can I explain this code at the whiteboard in 60 seconds?" The
answer was no. I also re-read the spec to confirm that the cascade order
is the core requirement — which meant the code should make that order
visually obvious.

Decision:
Rejected — I kept the explicit if/elif cascade. The AI's version was
technically correct and my 9 tests confirmed it behaved the same, but it
was harder for me to explain and defend under time pressure. The if/elif
version maps one-to-one onto the spec's rule list, which makes it easy to
review, trace, and debug. Learning value: elegance is not the same as
clarity.

Related file/commit:
campusflow/tickets.py — final calculate_priority()
Commit: 104101c

What I can now explain without AI:
AI can suggest clever refactors, but "clever" is not always the right
goal. Code that maps directly onto the requirements — even if more
verbose — is easier to defend, easier to trace, and less likely to hide
bugs. I chose readability instead of cleverness.
# AI Learning Log — CampusFlow Sprint

This log documents prompt-engineering interactions, human verification, and critical review cycles during the development of CampusFlow CLI in accordance with **PRD Section 11** (minimum 3 entries per engineer, with mandatory correction/rejection cycles).

---

## Engineer A: Alexander Agbaji (@AgbajiAlexander) — Core Data, Priority Engine & Persistence

### Entry A1: Priority Engine Rule Hierarchy
- **Context & Goal:** Generate the priority engine algorithm from PRD Section 7.
- **Initial AI Suggestion:** The AI generated a series of independent `if` statements with non-exclusive checks, checking `affected_users >= 10` first before `urgency == 'high'`.
- **Verification & Critical Evaluation:** Testing against the edge case of `urgency == "high"` with `affected_users == 2` would have evaluated incorrectly if rule ordering wasn't strictly sequential. The PRD explicitly specifies:
  1. `urgency == high` AND `affected_users >= 10` -> `critical`
  2. `urgency == high` OR `affected_users >= 10` -> `high`
  3. `urgency == medium` OR `affected_users >= 3` -> `medium`
  4. Otherwise -> `low`
- **Correction Applied (CORRECTED/REFINED):** Rejected the nested independent `if` tree and refactored into a single ordered cascade returning immediately on the first matching condition. Added unit test `test_priority_rule2_high_urgency_small_users` to lock down regression prevention.
- **Key Takeaway:** AI models often simplify compound conditionals into nested structures that subtly alter evaluation precedence. Always cross-verify against truth tables and boundary tests.

### Entry A2: Safe JSON Persistence & File Corruption Defense
- **Context & Goal:** Implement load and save operations in `storage.py` that handle malformed JSON files safely.
- **Initial AI Suggestion:** The AI recommended wrapping `json.load()` in a generic `try...except Exception` block and, upon encountering an error, initializing with an empty array and immediately overwriting `tickets.json` with `[]`.
- **Verification & Critical Evaluation (REJECTED):** This violates PRD Section 8 (F7): *"Malformed/corrupt JSON -> clear error message to the user; do not silently wipe existing data."* Silently overwriting the file with `[]` destroys user data permanently!
- **Correction Applied:** Rejected the silent overwrite. Implemented a non-destructive failure path: when `json.JSONDecodeError` occurs, an error string is returned to inform the user, but the physical file is left untouched on disk. Furthermore, implemented atomic writes using `.tmp` and `os.replace` to prevent mid-write crashes.
- **Key Takeaway:** AI defaults frequently favor "fail-silent convenience" over data durability. Explicit defensive programming requirements must be enforced by the engineer.

### Entry A3: Sequential ID Generation Across Restarts
- **Context & Goal:** Implement ticket ID generation (`T001`, `T002`, etc.) that persists across application restarts.
- **Initial AI Suggestion:** The AI suggested using `f"T{len(tickets) + 1:03d}"`.
- **Verification & Critical Evaluation:** If tickets are ever deleted or loaded out of order, `len(tickets) + 1` produces duplicate IDs (e.g. if `T002` was removed or if records were filtered, a new `T002` would be assigned).
- **Correction Applied (IMPROVED):** Implemented regex/numeric extraction (`extract_numeric_id`) that scans for `max(numeric_ids)` across all existing tickets and increments from the highest observed ID.
- **Key Takeaway:** Never use collection lengths as surrogate sequence generators for persistent entity IDs.

---

## Engineer B: Eli Odeh (@eliodeh) — Workflow, Analytics, Work Queue & CLI

### Entry B1: Workflow Transition Validation & Unassigned Guard
- **Context & Goal:** Implement lifecycle transitions (`open -> in_progress -> resolved`) and locking in `workflow.py`.
- **Initial AI Suggestion:** The AI proposed allowing transitions based solely on input strings without inspecting current ticket attributes.
- **Verification & Critical Evaluation (CORRECTED):** PRD Section 8 (F4) explicitly states: *"An unassigned ticket cannot move to in_progress (must be assigned first)"* and *"A resolved ticket is locked — it can only change again after an explicit reopen action."*
- **Correction Applied:** Added explicit assertion checks:
  1. `if target == "in_progress" and not ticket.get("assigned_to"): raise ValueError(...)`
  2. `if current == "resolved": raise ValueError("Ticket is locked. Reopen required.")`
  3. Created dedicated `reopen_ticket()` function.
- **Key Takeaway:** Workflow state machines require domain invariants that check both current status and related metadata (assignee existence) before permitting transitions.

### Entry B2: Work Queue Ordering and Numeric Tie-Breaking
- **Context & Goal:** Build the F5 Work Queue ordering logic.
- **Initial AI Suggestion:** The AI suggested sorting by `ticket['priority']` alphabetically and then by `ticket['id']` as strings.
- **Verification & Critical Evaluation (CORRECTED):** 
  1. Alphabetical sorting ranks `critical` (c), `high` (h), `low` (l), `medium` (m), which puts `low` before `medium`! The correct priority order is `critical -> high -> medium -> low`.
  2. String sorting of IDs fails when ticket numbers cross digit thresholds (e.g., `'T100' < 'T20'`).
- **Correction Applied:** Defined an explicit priority rank map `{'critical': 0, 'high': 1, 'medium': 2, 'low': 3}` and extracted numeric ID integers for tie-breaking: `sort_key = (rank, extract_numeric_id(t['id']))`.
- **Key Takeaway:** Priority levels must be mapped to discrete monotonic ranks, and IDs must be sorted by integer value rather than lexicographical string comparison.

### Entry B3: Interactive CLI Error Resilience
- **Context & Goal:** Implement `cli.py` menu and input loop without crashing on erroneous user inputs.
- **Initial AI Suggestion:** The AI suggested converting user input directly with `int(input("Affected users: "))` inside the menu loop without error handling.
- **Verification & Critical Evaluation:** Non-integer inputs caused unhandled `ValueError` crashes, terminating the CLI session and dropping unpersisted memory state.
- **Correction Applied (IMPROVED):** Wrapped user prompts in input validation layers and cleanly trapped domain `ValueError` exceptions, presenting clear messages and returning to the menu instead of crashing.
- **Key Takeaway:** CLI applications for non-technical staff must handle invalid input gracefully without crashing.

---

## CampusFlow Next Sprint — Engineer B Learning Cycles (Section 07)
**Engineer B:** Gabriel Oche Adanu (@Aocheg)

### Entry B4: Case-Insensitive Title Matching (`casefold()` vs `lower()`)
- **Concept Gap:** Determining the most reliable approach for caseless substring search on ticket titles in Python.
- **Exact Question Asked:** `"Compare casefold() and lower() for search; suggest test cases but do not implement my project."`
- **Summary of AI Guidance:** The AI explained that `str.casefold()` is specifically designed for caseless matching per the Unicode standard, mapping aggressive case variations (such as German 'ß' to 'ss') whereas `lower()` only handles standard 1-to-1 ASCII/Unicode lowercase.
- **Tiny Unrelated Experiment:**
  ```python
  text = "Fluß"
  print(text.lower())     # 'fluß'
  print(text.casefold())  # 'fluss'
  assert "fluss" in text.casefold()
  ```
- **Independent Verification Through Tests/Docs:** Consulted Python 3.12 documentation for `str.casefold()`. Authored `test_08_search_title_ignores_case_matching_substring` in `tests/test_search.py` testing mixed-case and uppercase query matching.
- **Final Engineering Decision:** Used `casefold()` on both the search query and the ticket title string in `search.py`.
- **Personal Reflection:** Before this cycle, I assumed `.lower()` was sufficient for all text search. The test proved that `casefold()` is standard practice for robust caseless comparisons in Python.

### Entry B5: Multi-Filter Logical Combination (AND vs OR) & Rejected Suggestion
- **Concept Gap:** Designing the composition rules for multi-filter search (`category`, `status`, `priority`) and handling empty inputs.
- **Exact Question Asked:** `"When combining category, status, and priority filters in a ticketing system search view, should filters be combined with OR or AND, and how should empty fields be treated?"`
- **Summary of AI Guidance:** The AI proposed supporting a configurable filter mode defaulting to `OR` so that search returns more results by default.
- **Tiny Unrelated Experiment:** Tested an `OR` vs `AND` sample on 3 tickets:
  * Searching `title='wifi'`, `category='Network'`, `status='open'` with `OR` returned unrelated open tickets (e.g., Python IDE bug) and unrelated network tickets (e.g., resolved router).
  * With `AND`, only tickets satisfying all criteria simultaneously matched.
- **Critique & Rejection of AI Suggestion (Evidence Review):**
  * **REJECTED the AI's proposal to use `OR`**: Requirement C of the project specification explicitly dictates: *"Filters must work together: if supplied, ALL must match. Empty filters mean 'do not filter by that field'."* Using `OR` violates the acceptance contract (Acceptance Criterion 09: *"Combined search filters use AND"*).
- **Final Engineering Decision:** Enforced strict logical `AND` across all non-empty filters. Empty or `None` filters are skipped and do not exclude records.
- **Personal Reflection:** AI suggestions often optimize for broad search retrieval instead of strict business contracts. Validating the AI's suggestion against the project specification prevented an acceptance test failure.

