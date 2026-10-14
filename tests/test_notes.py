"""test_notes.py - Engineer A's tests for notes.py."""

import unittest
import tickets
import workflow
import notes


class TestAddNote(unittest.TestCase):
    def setUp(self):
        self.tickets_list = []
        self.ticket = tickets.create_ticket(self.tickets_list, "Wifi down", "Network", "high", 15)
        self.tickets_list.append(self.ticket)

    def test_valid_note_gets_sequential_ids(self):
        n1 = notes.add_note(self.tickets_list, self.ticket["id"], "Mentor A", "Wifi router reboot attempted")
        n2 = notes.add_note(self.tickets_list, self.ticket["id"], "Mentor B", "Investigating switch ports")
        self.assertEqual(n1["note_id"], "N001")
        self.assertEqual(n2["note_id"], "N002")

    def test_too_short_message_rejected_and_id_not_consumed(self):
        with self.assertRaises(ValueError):
            notes.add_note(self.tickets_list, self.ticket["id"], "Mentor A", "hi")
        # Rejected note must not consume an ID -- next real note should still be N001
        note = notes.add_note(self.tickets_list, self.ticket["id"], "Mentor A", "Now a long enough message")
        self.assertEqual(note["note_id"], "N001")

    def test_blank_author_rejected(self):
        with self.assertRaises(ValueError):
            notes.add_note(self.tickets_list, self.ticket["id"], "   ", "A perfectly fine length message")

    def test_note_on_resolved_ticket_rejected_then_accepted_after_reopen(self):
        workflow.assign_ticket(self.ticket, "Chidi")
        workflow.transition_status(self.ticket, "in_progress")
        workflow.transition_status(self.ticket, "resolved")

        with self.assertRaises(ValueError):
            notes.add_note(self.tickets_list, self.ticket["id"], "Mentor A", "Trying to note a resolved ticket")

        workflow.reopen_ticket(self.ticket)
        note = notes.add_note(self.tickets_list, self.ticket["id"], "Mentor A", "Now allowed after reopening")
        self.assertEqual(note["note_id"], "N001")

    def test_notes_survive_resolve_and_reopen(self):
        notes.add_note(self.tickets_list, self.ticket["id"], "Mentor A", "Wifi router reboot attempted")
        workflow.assign_ticket(self.ticket, "Chidi")
        workflow.transition_status(self.ticket, "in_progress")
        workflow.transition_status(self.ticket, "resolved")
        workflow.reopen_ticket(self.ticket)
        self.assertEqual(len(self.ticket["notes"]), 1)
        self.assertEqual(self.ticket["notes"][0]["note_id"], "N001")


class TestViewNotes(unittest.TestCase):
    def test_notes_returned_in_id_order(self):
        tickets_list = []
        ticket = tickets.create_ticket(tickets_list, "Printer jam", "Hardware", "low", 1)
        tickets_list.append(ticket)
        notes.add_note(tickets_list, ticket["id"], "A", "First note of reasonable length")
        notes.add_note(tickets_list, ticket["id"], "B", "Second note of reasonable length")

        result = notes.view_notes(tickets_list, ticket["id"])
        self.assertEqual([n["note_id"] for n in result], ["N001", "N002"])

    def test_unknown_ticket_raises(self):
        with self.assertRaises(ValueError):
            notes.view_notes([], "T999")


if __name__ == "__main__":
    unittest.main()
