"""test_workflow.py - Unit tests for workflow.py.
Covers F3 (Assign), F4 (Lifecycle transitions, locks, and reopen).
"""

import unittest
import workflow


class TestWorkflow(unittest.TestCase):

    def setUp(self):
        self.ticket = {
            "id": "T001",
            "title": "Broken HDMI cable in Room 101",
            "category": "Hardware",
            "urgency": "medium",
            "affected_users": 5,
            "priority": "medium",
            "status": "open",
            "assigned_to": None,
        }

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        """Appendix A: Unassigned ticket cannot move to in_progress"""
        with self.assertRaises(ValueError) as ctx:
            workflow.transition_status(self.ticket, "in_progress")
        self.assertIn("Cannot move unassigned ticket", str(ctx.exception))
        # Ensure status was not altered
        self.assertEqual(self.ticket["status"], "open")

    def test_assigned_ticket_progresses_open_in_progress_resolved(self):
        """Appendix A: Assigned ticket progresses open -> in_progress -> resolved"""
        # Assign staff
        workflow.assign_ticket(self.ticket, "Alice")
        self.assertEqual(self.ticket["assigned_to"], "Alice")

        # Step 1: open -> in_progress
        workflow.transition_status(self.ticket, "in_progress")
        self.assertEqual(self.ticket["status"], "in_progress")

        # Step 2: in_progress -> resolved
        workflow.transition_status(self.ticket, "resolved")
        self.assertEqual(self.ticket["status"], "resolved")

    def test_reassignment_allowed(self):
        """F3: Reassignment of an existing assignee is allowed"""
        workflow.assign_ticket(self.ticket, "Alice")
        workflow.assign_ticket(self.ticket, "Bob")
        self.assertEqual(self.ticket["assigned_to"], "Bob")

    def test_blank_assignee_rejected(self):
        """Blank or whitespace-only assignee name is rejected"""
        with self.assertRaises(ValueError):
            workflow.assign_ticket(self.ticket, "")
        with self.assertRaises(ValueError):
            workflow.assign_ticket(self.ticket, "   ")

    def test_invalid_transition_open_to_resolved_rejected(self):
        """Cannot skip in_progress state directly to resolved"""
        workflow.assign_ticket(self.ticket, "Alice")
        with self.assertRaises(ValueError):
            workflow.transition_status(self.ticket, "resolved")
        self.assertEqual(self.ticket["status"], "open")

    def test_resolved_ticket_is_locked(self):
        """Resolved tickets cannot be changed via normal transition"""
        workflow.assign_ticket(self.ticket, "Alice")
        workflow.transition_status(self.ticket, "in_progress")
        workflow.transition_status(self.ticket, "resolved")

        with self.assertRaises(ValueError) as ctx:
            workflow.transition_status(self.ticket, "in_progress")
        self.assertIn("locked", str(ctx.exception))

    def test_reopen_resolved_ticket_succeeds(self):
        """Explicit reopen action sets resolved ticket back to open"""
        workflow.assign_ticket(self.ticket, "Alice")
        workflow.transition_status(self.ticket, "in_progress")
        workflow.transition_status(self.ticket, "resolved")

        workflow.reopen_ticket(self.ticket)
        self.assertEqual(self.ticket["status"], "open")

    def test_assign_resolved_ticket_rejected(self):
        """Resolved tickets cannot be assigned or reassigned unless reopened."""
        workflow.assign_ticket(self.ticket, "Alice")
        workflow.transition_status(self.ticket, "in_progress")
        workflow.transition_status(self.ticket, "resolved")

        with self.assertRaises(ValueError) as ctx:
            workflow.assign_ticket(self.ticket, "Bob")
        self.assertIn("resolved", str(ctx.exception).lower())
        # Ensure assignee remains unchanged
        self.assertEqual(self.ticket["assigned_to"], "Alice")


if __name__ == "__main__":
    unittest.main()
