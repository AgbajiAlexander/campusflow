# Engineering Reflections & Defense Notes — campus-flow-next

This document fulfills the submission requirements of **Section 11 (Individual Engineering Reflections)** and provides preparation notes for the **Live Defense Prompts (Section 09)** and **Engineer Sprint Questions (Section 04)**.

---

## 1. Section 11 Individual Reflections

### Engineer B: Gabriel Oche Adanu (@Aocheg)
- **Role:** Search, Reporting Analytics, Notes CLI & Engineering Understanding Check
- **One Verified Mistake:**
  During initial search exploration, I considered whether combining filters (`category`, `status`, `priority`) using logical `OR` would be more helpful to campus staff by returning broader results. When I created a test with sample tickets, `OR` returned false positives (e.g. resolved tickets when the user explicitly searched for open ones). Furthermore, re-reading Requirement C confirmed that the specification strictly requires: *"Filters must work together: if supplied, ALL must match."* I rejected the `OR` approach and enforced strict logical `AND`.
- **One Learning Gain:**
  Mastered the principle of separating business logic from presentation (I/O). By implementing `search.py`, `reports.py`, and `understanding_check.py` as pure functions without embedded `input()` or `print()` calls, all core functionality could be rigorously tested with automated unittests without relying on complex stdin mocking.
- **One Improvement Received Through Code Review:**
  During PR #6 review, Engineer A pointed out that returning ticket references from `search_tickets()` could allow downstream callers to inadvertently mutate tickets in memory. In response, I implemented `copy.deepcopy()` on all search matches before returning them and added `test_search_does_not_mutate_any_ticket` to permanently protect this invariant.

---

### Engineer A: Alexander Agbaji (@AgbajiAlexander)
- **Role:** Ticket Safety, Validation & Safe Storage
- **One Verified Mistake:**
  Initially considered wrapping JSON loading in a generic exception block that would silently reset the database to an empty list `[]` upon decode failure. When testing with a corrupted JSON file, this wiped out existing records permanently. Replaced this with non-destructive error handling that rejects corrupted files and leaves disk and memory state completely intact.
- **One Learning Gain:**
  Learned the critical value of the *validate-before-mutate* pattern. Rather than streaming or updating records iteratively during file reload, the entire collection is validated first (`_validate_collection`). If even one record has a duplicate ID or invalid fields, the load is rejected atomically and the previous valid memory state remains untouched.
- **One Improvement Received Through Code Review:**
  In the review for PR #4, Engineer B pointed out that tickets created by original CampusFlow (v1) lacked the `"notes"` field and would fail collection validation upon reload. I implemented `_migrate_record()` in `storage.py` to seamlessly initialize `"notes": []` for legacy tickets, ensuring 100% backward compatibility without data loss.

---

## 2. Engineer B Sprint Questions (Section 04)

1. **Why should search not edit the collection?**
   Search is fundamentally an inspection/query operation. If a search function modifies ticket records, caller state becomes unpredictable and bugs can silently corrupt ticket data. Returning deep copies guarantees read-only safety.
2. **When combining filters, should you use AND or OR?**
   Logical `AND`. Requirement C explicitly dictates: *"Filters must work together: if supplied, ALL must match."* Using `AND` allows users to narrow down specific tickets (e.g., open Network issues).
3. **Why does an empty report need special handling?**
   Calculating resolution percentage involves division by total tickets: `(resolved / total) * 100`. When total is 0, direct division raises a `ZeroDivisionError` that crashes the program. The formula must guard: `(resolved / total * 100) if total > 0 else 0.0`.
4. **How does an in_progress ticket affect unresolved count?**
   Unresolved tickets are defined as `open + in_progress`. An `in_progress` ticket is actively being worked on but not yet completed, so it is counted as unresolved until explicitly transitioned to `resolved`.
5. **Why is a resolved ticket forbidden from receiving new notes?**
   A resolved ticket represents a closed incident. Permitting notes on resolved tickets allows undocumented modifications to closed work. To add follow-up notes, staff must explicitly reopen the ticket to maintain auditability.
6. **How do you test CLI behavior without repeatedly typing manually?**
   By decoupling business logic into pure functions that take inputs as parameters and return data structures, and by designing CLI input loops to accept injectable `input_fn` and `output_fn` callables or running scripted tests against the pure functions.
7. **Which change from your partner's PR review improved your work?**
   The suggestion in PR #6 to use `copy.deepcopy()` in `search.py` so that search results are strictly immutable with respect to the source collection.

---

## 3. Engineer A Sprint Questions (Section 04)

1. **What data is validated before any mutation?**
   All ticket fields: `title` (non-blank), `category` (canonical), `urgency` (canonical), `affected_users` (strictly positive int, rejecting bools), `priority` (valid rule output), and `notes` (valid note shape, author, message length 5–300 chars).
2. **What is a ticket invariant?**
   A condition that must always hold true for any ticket throughout its lifecycle (e.g., ticket ID is unique and formatted `T001`+; `affected_users` is an integer > 0; status is one of `open`, `in_progress`, `resolved`; an unassigned ticket cannot be `in_progress`).
3. **Why doesn't a successful print statement prove data integrity?**
   `print()` only confirms that a line of code was reached; it does not verify that the data structure in memory or on disk conforms to schema rules, that types are correct, or that mutations were atomic.
4. **Why do you validate JSON after decoding?**
   `json.load()` only verifies that the file is syntactically valid JSON (valid syntax). It does not know domain invariants—such as whether keys are missing, IDs are duplicated, categories are illegal, or integers are masquerading as booleans.
5. **How do you prevent partial changes if one entry is invalid?**
   By validating all items in a temporary list or collection validator before applying changes to the active in-memory dictionary/list or writing to disk.
6. **How do you test both a thrown error and unchanged state?**
   Record `before = copy.deepcopy(data)`, execute the operation within `with self.assertRaises(ValueError):`, and immediately assert `self.assertEqual(data, before)`.
7. **Which AI recommendation did you accept only after verification?**
   The regex/numeric extraction algorithm for sequential ID calculation (`extract_numeric_id`), which was verified to prevent ID collisions even when earlier tickets are removed or loaded out of order.

---

## 4. Live Defense Preparation Prompts (Section 09)

1. **What important invariant can your function guarantee?**
   - *Engineer B (`search_tickets`):* Search is strictly read-only and will never mutate the underlying ticket collection.
   - *Engineer B (`generate_report`):* Resolution percentage always returns a valid float (`0.0` on empty dataset), never raising `ZeroDivisionError`.
   - *Engineer A (`can_transition` / `validate_ticket`):* An unassigned ticket can never enter `in_progress`, and booleans are strictly rejected for `affected_users`.
2. **Which test failed before you corrected a bug?**
   - *Engineer B:* In `search.py`, German or accented titles failed caseless substring match when using `.lower()`. Once replaced with `.casefold()`, `test_08_search_title_ignores_case_matching_substring` passed.
   - *Engineer A:* In `test_bug_hunter_by_A.py`, unnormalized categories in `search_tickets` required caller-side normalization in `cli.py`.
3. **How does your code avoid modifying state on a rejected action?**
   All validation checks occur BEFORE any mutation of in-memory data structures. If validation fails, `ValueError` is raised immediately, and the dictionary or list remains untouched.
4. **Demonstrate what happens when JSON loads duplicate IDs:**
   `storage.load_tickets()` calls `_validate_collection()`, which detects duplicate IDs and raises `StorageCorruptedError("Duplicate ticket ID found: ...")`. Memory state is not updated.
5. **Why do multiple filters use logical AND?**
   To allow precise filtering. Combining criteria with `AND` ensures that only tickets meeting ALL specified criteria (e.g., Category=Network AND Status=open) are displayed.
6. **How did you check an AI recommendation?**
   By isolating the suggestion in a tiny standalone script, testing with edge-case fixtures, cross-checking against official Python documentation, and verifying compliance with the project specification.
7. **Show your PR and a substantive review you gave your partner:**
   Documented in `docs/pr-reviews.md`: PR #4 (reviewed by Engineer B: Gabriel Oche Adanu) and PR #6 (reviewed by Engineer A: Alexander Agbaji).
8. **If the mentor changes one business rule, identify the function and test to update:**
   - If priority rules change: update `calculate_priority()` in `tickets.py` and `tests/test_tickets.py`.
   - If category choices change: update `VALID_CATEGORIES` in `validation.py` and `tickets.py`, and `tests/test_validation.py`.
   - If note message length changes: update `notes.py:add_note` and `tests/test_notes.py`.
