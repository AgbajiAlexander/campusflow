"""test_bug_hunters.py - Section 06's required bug-hunter exercise.

Each engineer devises ONE previously-unlisted edge case for the OTHER
engineer's module. Documented per the brief's format in the docstring of
each test.
"""

import unittest
import tickets
import search
import notes


class TestEngineerA_HuntsEngineerBsModule(unittest.TestCase):
    """
    Bug hunt by: Engineer A, targeting search.py (Engineer B's module)

    Initial state: a ticket created with category 'Network' (search.py's
    filters compare categories with exact string equality, not casefold).
    Input: search_tickets(..., category='network') -- lowercase, as a user
    might reasonably type it.
    Expected result (if this were a real bug): either the ticket is found
    anyway, or the CLI clearly rejects the unnormalized input before ever
    calling search_tickets().
    Actual result: search_tickets() does NOT normalize category -- an exact
    case-sensitive match is required. This is by design (search.py stays a
    pure, simple AND-filter), but it means the CALLER (cli.py's
    handle_search_tickets) is responsible for normalizing category through
    tickets.normalize_category() before calling search -- which it does.
    Any code change made: none needed in search.py; this test exists to make
    that caller-responsibility invariant visible and regression-proof, since
    it would be an easy thing to break while editing cli.py later.
    """
    def test_search_category_filter_is_exact_match_not_case_insensitive(self):
        tickets_list = [tickets.create_ticket([], "Router issue", "Network", "high", 12)]
        self.assertEqual(len(search.search_tickets(tickets_list, category="Network")), 1)
        # Lowercase 'network' does NOT match -- proving search.py expects an
        # already-normalized value, not raw user input.
        self.assertEqual(len(search.search_tickets(tickets_list, category="network")), 0)


class TestEngineerB_HuntsEngineerAsModule(unittest.TestCase):
    """
    Bug hunt by: Engineer B, targeting notes.py (Engineer A's module)

    Initial state: a ticket with no notes yet.
    Input: call notes.next_note_id(ticket) TWICE in a row without actually
    adding a note in between (e.g. the CLI previews the next ID before the
    user finishes typing their message, then the user cancels).
    Expected result: both calls return 'N001' -- previewing the next ID must
    be a read-only operation that doesn't consume anything, the same
    invariant add_note() already protects for rejected notes.
    Actual result: confirmed -- next_note_id() only reads ticket['notes'],
    it never appends or mutates, so calling it any number of times without
    an actual add_note() call is safe and idempotent.
    Any code change made: none needed; this test makes that read-only
    guarantee explicit and regression-proof.
    """
    def test_next_note_id_is_read_only_and_idempotent(self):
        ticket = tickets.create_ticket([], "Printer jam", "Hardware", "low", 1)
        first_preview = notes.next_note_id(ticket)
        second_preview = notes.next_note_id(ticket)
        self.assertEqual(first_preview, "N001")
        self.assertEqual(second_preview, "N001")
        self.assertEqual(ticket["notes"], [])  # still untouched


if __name__ == "__main__":
    unittest.main()


