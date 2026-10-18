"""test_reports.py - Unit tests for reports.py.
Covers F5 (Work Queue sorting & tie-breaking), F6 (Reports metrics & zero-ticket handling),
and Requirement D (Trustworthy quality insights - Acceptance Criteria 10 and 11).
"""

import unittest
import reports


class TestReportsAndWorkQueue(unittest.TestCase):

    def test_work_queue_sorting_and_tie_breaking(self):
        """Appendix A: Open-ticket queue sorted by priority, then numeric ID (open-only)"""
        tickets_list = [
            {"id": "T005", "priority": "low", "status": "open"},
            {"id": "T003", "priority": "high", "status": "open"},
            {"id": "T007", "priority": "high", "status": "open"},
            {"id": "T001", "priority": "high", "status": "in_progress"},  # in_progress should be excluded!
            {"id": "T002", "priority": "critical", "status": "open"},
            {"id": "T004", "priority": "critical", "status": "resolved"},  # resolved should be excluded!
            {"id": "T006", "priority": "medium", "status": "open"},
        ]

        queue = reports.get_work_queue(tickets_list)

        # Ensure resolved T004 and in_progress T001 are excluded
        queue_ids = [t["id"] for t in queue]
        self.assertNotIn("T004", queue_ids)
        self.assertNotIn("T001", queue_ids)

        # Expected order (open tickets only):
        # 1. T002 (critical)
        # 2. T003 (high, lower numeric ID than T007)
        # 3. T007 (high)
        # 4. T006 (medium)
        # 5. T005 (low)
        expected_ids = ["T002", "T003", "T007", "T006", "T005"]
        self.assertEqual(queue_ids, expected_ids)

    def test_empty_work_queue(self):
        """Empty input, in_progress-only, or resolved-only tickets produces empty work queue without crashing"""
        queue = reports.get_work_queue([])
        self.assertEqual(queue, [])

        resolved_only = [{"id": "T001", "priority": "high", "status": "resolved"}]
        self.assertEqual(reports.get_work_queue(resolved_only), [])

        in_progress_only = [{"id": "T002", "priority": "high", "status": "in_progress"}]
        self.assertEqual(reports.get_work_queue(in_progress_only), [])

    def test_report_zero_tickets_case(self):
        """F6: Zero-tickets case must not crash and returns zero counts"""
        rep = reports.generate_report([])
        self.assertEqual(rep["total"], 0)
        self.assertEqual(rep["by_status"]["open"], 0)
        self.assertEqual(rep["by_status"]["in_progress"], 0)
        self.assertEqual(rep["by_status"]["resolved"], 0)
        self.assertEqual(rep["by_priority"]["critical"], 0)
        self.assertEqual(rep["by_priority"]["high"], 0)
        self.assertEqual(rep["by_priority"]["medium"], 0)
        self.assertEqual(rep["by_priority"]["low"], 0)

    def test_report_aggregated_counts(self):
        """F6: Accurate counts by status and priority"""
        sample_tickets = [
            {"id": "T001", "priority": "critical", "status": "open"},
            {"id": "T002", "priority": "high", "status": "in_progress"},
            {"id": "T003", "priority": "high", "status": "resolved"},
            {"id": "T004", "priority": "low", "status": "resolved"},
        ]
        rep = reports.generate_report(sample_tickets)
        self.assertEqual(rep["total"], 4)
        self.assertEqual(rep["by_status"]["open"], 1)
        self.assertEqual(rep["by_status"]["in_progress"], 1)
        self.assertEqual(rep["by_status"]["resolved"], 2)
        self.assertEqual(rep["by_priority"]["critical"], 1)
        self.assertEqual(rep["by_priority"]["high"], 2)
        self.assertEqual(rep["by_priority"]["medium"], 0)
        self.assertEqual(rep["by_priority"]["low"], 1)

    def test_10_empty_dataset_resolution_percentage_is_zero_not_crash(self):
        """10. Empty report returns 0%, no crash (division-by-zero protection)."""
        rep = reports.generate_report([])
        self.assertEqual(rep["resolution_percentage"], 0.0)
        self.assertEqual(rep["unresolved"], 0)
        self.assertEqual(rep["resolved"], 0)

    def test_resolution_percentage_and_unresolved_count(self):
        """Requirement D: calculates unresolved (open + in_progress), resolved, and percentage."""
        sample_tickets = [
            {"id": "T001", "priority": "critical", "status": "open", "category": "Network"},
            {"id": "T002", "priority": "high", "status": "in_progress", "category": "Hardware"},
            {"id": "T003", "priority": "high", "status": "resolved", "category": "Hardware"},
            {"id": "T004", "priority": "low", "status": "resolved", "category": "Software"},
        ]
        rep = reports.generate_report(sample_tickets)
        self.assertEqual(rep["unresolved"], 2)   # open + in_progress
        self.assertEqual(rep["resolved"], 2)
        self.assertEqual(rep["resolution_percentage"], 50.0)
        self.assertEqual(rep["by_category"]["Hardware"], 2)
        self.assertEqual(rep["by_category"]["Network"], 1)
        self.assertEqual(rep["by_category"]["Software"], 1)

    def test_11_report_counts_agree_with_known_fixture_after_resolve_reopen(self):
        """11. Report counts agree with known fixture after resolve/reopen."""
        fixture = [
            {"id": "T001", "priority": "high", "status": "open", "category": "Network"},
            {"id": "T002", "priority": "medium", "status": "in_progress", "category": "Software"},
        ]
        # Initial: 1 open, 1 in_progress -> unresolved=2, resolved=0, 0.0%
        rep1 = reports.generate_report(fixture)
        self.assertEqual(rep1["unresolved"], 2)
        self.assertEqual(rep1["resolved"], 0)
        self.assertEqual(rep1["resolution_percentage"], 0.0)

        # Resolve T001: 1 in_progress, 1 resolved -> unresolved=1, resolved=1, 50.0%
        fixture[0]["status"] = "resolved"
        rep2 = reports.generate_report(fixture)
        self.assertEqual(rep2["unresolved"], 1)
        self.assertEqual(rep2["resolved"], 1)
        self.assertEqual(rep2["resolution_percentage"], 50.0)

        # Reopen T001: 1 open, 1 in_progress -> unresolved=2, resolved=0, 0.0%
        fixture[0]["status"] = "open"
        rep3 = reports.generate_report(fixture)
        self.assertEqual(rep3["by_status"]["open"], 1)
        self.assertEqual(rep3["by_status"]["resolved"], 0)
        self.assertEqual(rep3["unresolved"], 2)
        self.assertEqual(rep3["resolved"], 0)
        self.assertEqual(rep3["resolution_percentage"], 0.0)

    def test_sort_search_results_orders_by_priority_then_id(self):
        """Requirement D: separate view sorting search results by priority then ID."""
        results = [
            {"id": "T003", "priority": "high", "status": "resolved"},
            {"id": "T001", "priority": "critical", "status": "open"},
            {"id": "T002", "priority": "high", "status": "open"},
        ]
        sorted_results = reports.sort_search_results(results)
        self.assertEqual([t["id"] for t in sorted_results], ["T001", "T002", "T003"])
        # Unlike get_work_queue, a resolved ticket (T003) is allowed to appear in search results
        self.assertIn("T003", [t["id"] for t in sorted_results])


if __name__ == "__main__":
    unittest.main()
