# AI Learning Log — campus-flow-next Sprint

This log documents prompt-engineering interactions, human verification, and critical review cycles during the development of CampusFlow and campus-flow-next CLI in accordance with **PRD Section 11** and **Section 07 of the CampusFlow Next Sprint Guide** (minimum 2 meaningful learning cycles per engineer, including independent verification and mandatory correction/rejection cycles).

---

## Engineer A: Alexander Agbaji (@AgbajiAlexander) — Ticket Safety, Validation & Storage

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

### Entry A4: Rejecting AI Suggestion to Use a List-of-Rules Engine
- **Context & Goal:** Cleaner structure for the 4 priority rules in `tickets.py`.
- **Initial AI Suggestion:** The AI suggested replacing the if/elif cascade with a list of `(rule_function, priority)` tuples and iterating through it.
- **Tiny Unrelated Experiment:** Saved AI's version in a scratch script and ran 9 unit tests. All passed. However, when trying to explain the code out loud as if in a live technical defense, the indirect list hid the clear sequence order of the specification.
- **Correction Applied (REJECTED):** Kept the explicit if/elif cascade. Elegance is not clarity; code mapping directly onto specification requirements is easier to trace, defend, and audit.
- **Key Takeaway:** Readability and direct alignment with requirements outweigh clever abstraction.

---

## Engineer B: Gabriel Oche Adanu (@Aocheg) — Search, Reporting Analytics, Notes CLI & Engineering Understanding Check

### Entry B1: Case-Insensitive Title Matching (`casefold()` vs `lower()`)
- **Concept Gap:** Determining the most reliable approach for caseless substring search on ticket titles in Python.
- **Exact Question Asked:** `"Compare casefold() and lower() for search; suggest test cases but do not implement my project."`
- **Summary of AI Guidance:** The AI explained that `str.casefold()` is specifically designed for caseless matching per the Unicode standard (Section 3.13 of Unicode), mapping aggressive case variations (such as German 'ß' to 'ss', Greek sigma, etc.) whereas `lower()` only handles standard 1-to-1 ASCII/Unicode lowercase.
- **Tiny Unrelated Experiment:**
  ```python
  text = "Fluß"
  print(text.lower())     # 'fluß'
  print(text.casefold())  # 'fluss'
  assert "fluss" in text.casefold()
  assert "FLUSS".casefold() == "fluss"
  ```
- **Independent Verification Through Tests/Docs:** Consulted Python 3.12 official documentation for `str.casefold()`. Authored `test_08_search_title_ignores_case_matching_substring` in `tests/test_search.py` testing mixed-case and uppercase query matching.
- **Final Engineering Decision:** Used `casefold()` on both the search query and the ticket title string in `search.py` (`query.strip().casefold() in t["title"].casefold()`).
- **Personal Reflection (Section 07 Format):**
  - *What did I believe before?* I believed `.lower()` was completely sufficient for all caseless search requirements in Python.
  - *What did AI explain?* The AI explained that `.lower()` is locale/case-mapping oriented, whereas `casefold()` removes all case distinctions according to the Unicode standard.
  - *Which claim did I test?* I tested caseless matching on strings with non-ASCII casing characters (`"Fluß"` matching `"fluss"`).
  - *What did the test show?* The test confirmed `"fluss" in "Fluß".casefold()` is `True`, whereas `"fluss" in "Fluß".lower()` is `False`.
  - *What did I change in MY code?* In `search.py`, I replaced all `.lower()` calls for title query matching with `.casefold()`.
  - *Which test guards that learning against future regression?* `tests/test_search.py::TestSearchTickets::test_08_search_title_ignores_case_matching_substring`.
  - *Could I explain this choice without AI in the room?* Yes: `casefold()` is Python's standard method for Unicode-compliant caseless comparison, whereas `lower()` only transforms characters to lowercase without handling aggressive Unicode folding.

### Entry B2: Multi-Filter Logical Combination (AND vs OR) & Rejected Suggestion
- **Concept Gap:** Designing composition rules for multi-filter search (`category`, `status`, `priority`) and handling empty inputs.
- **Exact Question Asked:** `"When combining category, status, and priority filters in a ticketing system search view, should filters be combined with OR or AND, and how should empty fields be treated?"`
- **Summary of AI Guidance:** The AI proposed supporting a configurable filter mode defaulting to `OR` so that search returns more results by default for end users.
- **Tiny Unrelated Experiment:** Tested an `OR` vs `AND` sample on 3 tickets:
  - Ticket 1: `title='Wi-Fi router'`, `category='Network'`, `status='open'`
  - Ticket 2: `title='Python IDE'`, `category='Software'`, `status='open'`
  - Ticket 3: `title='Network cabling'`, `category='Network'`, `status='resolved'`
  - Searching `title='wifi'`, `category='Network'`, `status='open'`:
    - With `OR`: Returns all 3 tickets (Ticket 2 matches `status='open'`, Ticket 3 matches `category='Network'`).
    - With `AND`: Returns strictly Ticket 1.
- **Critique & Rejection of AI Suggestion (Evidence Review):**
  - **REJECTED the AI's proposal to use `OR`**: Requirement C of the project specification explicitly dictates: *"Filters must work together: if supplied, ALL must match. Empty filters mean 'do not filter by that field'."* Using `OR` violates the acceptance contract (Acceptance Criterion 09: *"Combined search filters use AND"*).
- **Final Engineering Decision:** Enforced strict logical `AND` across all non-empty filters in `search.py`. Empty, whitespace, or `None` filters are skipped and do not exclude records.
- **Personal Reflection (Section 07 Format):**
  - *What did I believe before?* I wondered whether users would prefer broader search results via `OR` matching.
  - *What did AI explain?* The AI suggested making `OR` the default to maximize recall.
  - *Which claim did I test?* I tested filtering precision with sample tickets matching partial criteria.
  - *What did the test show?* `OR` returned false positives (e.g. resolved tickets when the user explicitly filtered for `open`).
  - *What did I change in MY code?* In `search.py`, I implemented sequential filtering where each supplied criteria narrows the matching list (`if cat and t["category"] != cat: continue`).
  - *Which test guards that learning against future regression?* `tests/test_search.py::TestSearchTickets::test_09_combined_search_filters_use_and`.
  - *Could I explain this choice without AI in the room?* Yes: Campus support staff searching for specific active issues require strict narrowing (intersection / AND) so they do not receive hundreds of irrelevant resolved or cross-department tickets.

### Entry B3: Division-by-Zero Safety in Analytics Reports
- **Concept Gap:** Ensuring reports handle an empty ticket database safely without crashes.
- **Exact Question Asked:** `"How should an empty dataset resolution percentage be handled in pure calculation functions?"`
- **Summary of AI Guidance:** The AI suggested using `try...except ZeroDivisionError` around `resolved / total * 100` and returning `0.0`.
- **Tiny Unrelated Experiment:**
  ```python
  total = 0
  resolved = 0
  # Guard approach
  pct = (resolved / total * 100) if total > 0 else 0.0
  assert pct == 0.0
  ```
- **Independent Verification Through Tests/Docs:** Authored `test_10_empty_dataset_resolution_percentage_is_zero_not_crash` in `tests/test_reports.py`.
- **Final Engineering Decision:** Used an explicit defensive ternary guard `(resolved / total * 100) if total > 0 else 0.0` rather than exception-driven control flow, adhering to pure function design.
- **Personal Reflection (Section 07 Format):**
  - *What did I believe before?* I considered letting `ZeroDivisionError` be caught in the CLI presentation layer.
  - *What did AI explain?* The AI pointed out that business logic functions should guarantee valid return shapes and invariants regardless of input size.
  - *Which claim did I test?* Tested passing `[]` to `generate_report()`.
  - *What did the test show?* The pure guard returned valid numeric `0.0` and zeroed breakdown dictionaries without throwing.
  - *What did I change in MY code?* Guarded the percentage calculation in `reports.py` and rounded to 1 decimal place.
  - *Which test guards that learning against future regression?* `tests/test_reports.py::TestReportsAndWorkQueue::test_10_empty_dataset_resolution_percentage_is_zero_not_crash`.
  - *Could I explain this choice without AI in the room?* Yes: Business logic functions should uphold contracts that never raise runtime exceptions on legitimate boundary domain inputs like empty collections.
