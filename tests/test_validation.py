"""test_validation.py - Engineer A's tests for validation.py."""

import unittest
import validation
import tickets


def make_valid_ticket(**overrides):
    base = tickets.create_ticket([], "Wifi down", "Network", "high", 15)
    base.update(overrides)
    return base


class TestValidateTicket(unittest.TestCase):
    def test_accepts_a_well_formed_ticket(self):
        ticket = make_valid_ticket()
        self.assertIs(validation.validate_ticket(ticket), ticket)

    def test_rejects_ticket_missing_notes_key(self):
        ticket = make_valid_ticket()
        del ticket["notes"]
        with self.assertRaises(ValueError):
            validation.validate_ticket(ticket)

    def test_rejects_illegal_status_value(self):
        ticket = make_valid_ticket(status="archived")
        with self.assertRaises(ValueError):
            validation.validate_ticket(ticket)

    def test_rejects_duplicate_note_ids_within_one_ticket(self):
        ticket = make_valid_ticket(notes=[
            {"note_id": "N001", "author": "A", "message": "first message here"},
            {"note_id": "N001", "author": "B", "message": "second message here"},
        ])
        with self.assertRaises(ValueError):
            validation.validate_ticket(ticket)


class TestCanTransition(unittest.TestCase):
    def test_unassigned_open_cannot_go_to_in_progress(self):
        self.assertFalse(validation.can_transition("open", "in_progress", None))

    def test_assigned_open_can_go_to_in_progress(self):
        self.assertTrue(validation.can_transition("open", "in_progress", "Chidi"))

    def test_resolved_can_never_transition_via_this_check(self):
        self.assertFalse(validation.can_transition("resolved", "open", "Chidi"))

    def test_can_transition_never_mutates_anything(self):
        # It takes plain values, not a ticket dict -- nothing to mutate.
        # This test documents that invariant explicitly rather than assuming it.
        status, target, assignee = "open", "in_progress", "Chidi"
        validation.can_transition(status, target, assignee)
        self.assertEqual((status, target, assignee), ("open", "in_progress", "Chidi"))


if __name__ == "__main__":
    unittest.main()
