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

    def test_notes_persist_across_full_lifecycle_and_reloads(self):
        """Integrated test: notes survive save, reload, resolve, reopen, and note counter continues."""
        import os, tempfile, shutil, storage

        temp_dir = tempfile.mkdtemp()
        try:
            store_file = os.path.join(temp_dir, "test_notes_lifecycle.json")
            # 1. Add note and save
            notes.add_note(self.tickets_list, self.ticket["id"], "Mentor A", "Initial diagnostic note")
            storage.save_tickets(self.tickets_list, store_file)

            # 2. Reload and transition to in_progress
            loaded, err = storage.load_tickets(store_file)
            self.assertIsNone(err)
            t = loaded[0]
            workflow.assign_ticket(t, "Engineer A")
            workflow.transition_status(t, "in_progress")
            notes.add_note(loaded, t["id"], "Engineer A", "Replaced cable and rebooted")
            storage.save_tickets(loaded, store_file)

            # 3. Reload and resolve
            loaded2, err2 = storage.load_tickets(store_file)
            self.assertIsNone(err2)
            t2 = loaded2[0]
            workflow.transition_status(t2, "resolved")
            storage.save_tickets(loaded2, store_file)

            # 4. Reload, verify locked notes while resolved
            loaded3, err3 = storage.load_tickets(store_file)
            self.assertIsNone(err3)
            t3 = loaded3[0]
            with self.assertRaises(ValueError):
                notes.add_note(loaded3, t3["id"], "Mentor B", "Should fail on resolved")

            # 5. Reopen, add third note, verify N003
            workflow.reopen_ticket(t3)
            n3 = notes.add_note(loaded3, t3["id"], "Mentor B", "Reopened for verification")
            self.assertEqual(n3["note_id"], "N003")
            self.assertEqual(len(t3["notes"]), 3)
            storage.save_tickets(loaded3, store_file)

            # 6. Final reload verification
            final_loaded, final_err = storage.load_tickets(store_file)
            self.assertIsNone(final_err)
            self.assertEqual(len(final_loaded[0]["notes"]), 3)
            self.assertEqual([n["note_id"] for n in final_loaded[0]["notes"]], ["N001", "N002", "N003"])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


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
