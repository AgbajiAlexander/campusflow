"""test_reports.py - Unit tests for reports.py.
Covers F5 (Work Queue sorting & tie-breaking) and F6 (Reports metrics & zero-ticket handling).
"""

import unittest
import reports


class TestReportsAndWorkQueue(unittest.TestCase):

    def test_work_queue_sorting_and_tie_breaking(self):
        """Appendix A: Open-ticket queue sorted by priority, then numeric ID"""
        tickets_list = [
            {"id": "T005", "priority": "low", "status": "open"},
            {"id": "T003", "priority": "high", "status": "open"},
            {"id": "T001", "priority": "high", "status": "in_progress"},
            {"id": "T002", "priority": "critical", "status": "open"},
            {"id": "T004", "priority": "critical", "status": "resolved"},  # resolved should be excluded!
            {"id": "T006", "priority": "medium", "status": "open"},
        ]

        queue = reports.get_work_queue(tickets_list)

        # Ensure resolved T004 is excluded
        queue_ids = [t["id"] for t in queue]
        self.assertNotIn("T004", queue_ids)

        # Expected order:
        # 1. T002 (critical)
        # 2. T001 (high, lower numeric ID than T003)
        # 3. T003 (high)
        # 4. T006 (medium)
        # 5. T005 (low)
        expected_ids = ["T002", "T001", "T003", "T006", "T005"]
        self.assertEqual(queue_ids, expected_ids)

    def test_empty_work_queue(self):
        """Empty input or only resolved tickets produces empty work queue without crashing"""
        queue = reports.get_work_queue([])
        self.assertEqual(queue, [])

        resolved_only = [{"id": "T001", "priority": "high", "status": "resolved"}]
        self.assertEqual(reports.get_work_queue(resolved_only), [])

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


if __name__ == "__main__":
    unittest.main()
