"""test_search.py - Engineer B's tests for search.py.
Covers Requirement C, Acceptance Criteria 08 and 09.
"""

import unittest
import search
import tickets


def sample_tickets():
    t1 = tickets.create_ticket([], "Campus WiFi is down", "Network", "high", 15)
    t2 = tickets.create_ticket([t1], "Lab wifi router noisy", "Network", "low", 1)
    t3 = tickets.create_ticket([t1, t2], "Printer out of toner", "Hardware", "low", 1)
    t2["status"] = "resolved"
    return [t1, t2, t3]


class TestSearchTickets(unittest.TestCase):
    def test_08_search_title_ignores_case_matching_substring(self):
        """08. Search title ignores case, matching substring."""
        data = sample_tickets()
        # 'wifi' should match both WiFi tickets regardless of case
        results = search.search_tickets(data, title_query="wifi")
        self.assertEqual({t["title"] for t in results}, {"Campus WiFi is down", "Lab wifi router noisy"})

        # Uppercase search 'ROUTER' matches 'Lab wifi router noisy'
        results_upper = search.search_tickets(data, title_query="ROUTER")
        self.assertEqual([t["title"] for t in results_upper], ["Lab wifi router noisy"])

        # No match returns empty list
        self.assertEqual(search.search_tickets(data, title_query="projector"), [])

    def test_09_combined_search_filters_use_and(self):
        """09. Combined search filters use AND (all supplied non-empty filters must match)."""
        data = sample_tickets()
        # title 'wifi' + category 'Network' + status 'open'
        # t2 is 'resolved' so even though it matches title+category, status excludes it
        results = search.search_tickets(data, title_query="wifi", category="Network", status="open")
        self.assertEqual([t["title"] for t in results], ["Campus WiFi is down"])

        # Restricting by priority that doesn't match eliminates it
        results_mismatch = search.search_tickets(
            data, title_query="wifi", category="Network", status="open", priority="low"
        )
        self.assertEqual(results_mismatch, [])

    def test_empty_filters_mean_no_filtering_on_that_field(self):
        """Omitted or empty filters do not filter out tickets."""
        data = sample_tickets()
        results = search.search_tickets(data)  # no filters at all
        self.assertEqual(len(results), 3)

        results_empty_str = search.search_tickets(data, title_query="", category=None, status="")
        self.assertEqual(len(results_empty_str), 3)

    def test_search_does_not_mutate_any_ticket(self):
        """Search is read-only and never mutates in-memory data."""
        data = sample_tickets()
        snapshot = [dict(t) for t in data]
        search.search_tickets(data, title_query="wifi", category="Network")
        self.assertEqual(data, snapshot)


if __name__ == "__main__":
    unittest.main()
