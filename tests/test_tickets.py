"""test_tickets.py - Unit tests for tickets.py and priority engine.
Covers F1, F2, Priority rules, and validation edge cases.
"""

import unittest
import tickets


class TestTicketsPriorityAndValidation(unittest.TestCase):

    def test_priority_rule1_high_urgency_large_users(self):
        """Appendix A: High urgency + 12 affected users -> critical"""
        prio = tickets.calculate_priority("high", 12)
        self.assertEqual(prio, "critical")

    def test_priority_rule2_high_urgency_small_users(self):
        """Appendix A: High urgency + 2 affected users -> high"""
        prio = tickets.calculate_priority("high", 2)
        self.assertEqual(prio, "high")

    def test_priority_rule3_low_urgency_moderate_users(self):
        """Appendix A: Low urgency + 4 affected users -> medium"""
        prio = tickets.calculate_priority("low", 4)
        self.assertEqual(prio, "medium")

    def test_priority_rule4_low_urgency_single_user(self):
        """Appendix A: Low urgency + 1 affected user -> low"""
        prio = tickets.calculate_priority("low", 1)
        self.assertEqual(prio, "low")

    def test_priority_medium_urgency(self):
        """Rule 3: medium urgency with 1 user -> medium"""
        prio = tickets.calculate_priority("medium", 1)
        self.assertEqual(prio, "medium")

    def test_priority_case_insensitivity(self):
        """Urgency case variations should be normalized: HIGH -> critical if users >= 10"""
        prio = tickets.calculate_priority("HIGH", 15)
        self.assertEqual(prio, "critical")

    def test_affected_users_zero_rejected(self):
        """Appendix A: affected_users = 0 -> rejected"""
        with self.assertRaises(ValueError):
            tickets.validate_affected_users(0)

    def test_affected_users_negative_rejected(self):
        """Negative affected_users must be rejected"""
        with self.assertRaises(ValueError):
            tickets.validate_affected_users(-5)

    def test_affected_users_invalid_string_rejected(self):
        """Non-numeric strings and floats must be rejected"""
        with self.assertRaises(ValueError):
            tickets.validate_affected_users("ten")
        with self.assertRaises(ValueError):
            tickets.validate_affected_users(3.5)

    def test_blank_title_rejected(self):
        """Blank or whitespace-only title must be rejected"""
        with self.assertRaises(ValueError):
            tickets.validate_title("")
        with self.assertRaises(ValueError):
            tickets.validate_title("   ")

    def test_invalid_category_rejected(self):
        """Invalid category not in allowed set must be rejected"""
        with self.assertRaises(ValueError):
            tickets.normalize_category("Telephony")

    def test_invalid_urgency_rejected(self):
        """Invalid urgency not in ('low', 'medium', 'high') must be rejected"""
        with self.assertRaises(ValueError):
            tickets.normalize_urgency("urgent")

    def test_create_ticket_sequential_id(self):
        """Creating tickets increments ID sequentially starting at T001"""
        all_tickets = []
        t1 = tickets.create_ticket(all_tickets, "Issue 1", "Network", "high", 10)
        self.assertEqual(t1["id"], "T001")
        self.assertEqual(t1["priority"], "critical")
        self.assertEqual(t1["status"], "open")
        self.assertIsNone(t1["assigned_to"])
        all_tickets.append(t1)

        t2 = tickets.create_ticket(all_tickets, "Issue 2", "Hardware", "low", 1)
        self.assertEqual(t2["id"], "T002")
        self.assertEqual(t2["priority"], "low")

    def test_find_ticket_by_id(self):
        """Find ticket by ID works and handles unknown ID gracefully"""
        sample_tickets = [{"id": "T001", "title": "Network down"}]
        found = tickets.find_ticket_by_id(sample_tickets, "T001")
        self.assertIsNotNone(found)
        self.assertEqual(found["title"], "Network down")

        # Unknown ID returns None
        unknown = tickets.find_ticket_by_id(sample_tickets, "T999")
        self.assertIsNone(unknown)


if __name__ == "__main__":
    unittest.main()
