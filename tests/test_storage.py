"""test_storage.py - Unit tests for storage.py persistence.
Covers F7 (Save/Reload, ID continuity, Corrupt file safety, Missing file handling).
"""

import json
import os
import shutil
import tempfile
import unittest
import storage
import tickets


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.test_dir, "data", "test_tickets.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_missing_file_starts_empty_without_error(self):
        """F7: Missing file returns empty list with no error"""
        non_existent = os.path.join(self.test_dir, "does_not_exist.json")
        loaded, err = storage.load_tickets(non_existent)
        self.assertEqual(loaded, [])
        self.assertIsNone(err)

    def test_save_and_reload_preserves_tickets(self):
        """Appendix A: Save/reload preserves existing tickets"""
        sample_tickets = [
            {
                "id": "T001",
                "title": "Main lab router reboot required",
                "category": "Network",
                "urgency": "high",
                "affected_users": 20,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            },
            {
                "id": "T002",
                "title": "Software license expired",
                "category": "Software",
                "urgency": "medium",
                "affected_users": 5,
                "priority": "medium",
                "status": "in_progress",
                "assigned_to": "Engineer A",
            },
        ]
        storage.save_tickets(sample_tickets, self.storage_path)

        loaded, err = storage.load_tickets(self.storage_path)
        self.assertIsNone(err)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["id"], "T001")
        self.assertEqual(loaded[0]["priority"], "critical")
        self.assertEqual(loaded[1]["assigned_to"], "Engineer A")

    def test_id_uniqueness_and_increment_after_reload(self):
        """Appendix A: New ticket after reload does not duplicate an ID"""
        # Save ticket T001 and T002
        initial_tickets = [
            tickets.create_ticket([], "Issue 1", "Hardware", "low", 1),
            tickets.create_ticket([{"id": "T001"}], "Issue 2", "Software", "medium", 3),
        ]
        storage.save_tickets(initial_tickets, self.storage_path)

        # Reload from disk
        reloaded, err = storage.load_tickets(self.storage_path)
        self.assertIsNone(err)
        self.assertEqual(len(reloaded), 2)

        # Create new ticket after reload
        new_ticket = tickets.create_ticket(reloaded, "Issue 3", "Network", "high", 15)
        self.assertEqual(new_ticket["id"], "T003")
        # Ensure ID is strictly unique
        existing_ids = [t["id"] for t in reloaded]
        self.assertNotIn(new_ticket["id"], existing_ids)

    def test_corrupted_json_preserves_file_and_reports_error(self):
        """F7: Corrupt JSON returns error message and does not wipe file"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        corrupt_content = "{ this is invalid json content ]"
        with open(self.storage_path, "w", encoding="utf-8") as f:
            f.write(corrupt_content)

        loaded, err = storage.load_tickets(self.storage_path)
        self.assertEqual(loaded, [])
        self.assertIsNotNone(err)
        self.assertIn("Storage corruption detected", err)

        # Verify the corrupt file was NOT deleted or wiped
        with open(self.storage_path, "r", encoding="utf-8") as f:
            persisted = f.read()
        self.assertEqual(persisted, corrupt_content)

    def test_duplicate_ticket_id_rejected_without_state_loss(self):
        """Requirement E: two tickets sharing an ID must reject the whole load."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        duplicate_data = [
            {
                "id": "T001", "title": "First", "category": "Network", "urgency": "high",
                "affected_users": 5, "priority": "high", "status": "open",
                "assigned_to": None, "notes": [],
            },
            {
                "id": "T001", "title": "Second (duplicate ID)", "category": "Software",
                "urgency": "low", "affected_users": 1, "priority": "low", "status": "open",
                "assigned_to": None, "notes": [],
            },
        ]
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(duplicate_data, f)

        loaded, err = storage.load_tickets(self.storage_path)
        self.assertEqual(loaded, [])
        self.assertIsNotNone(err)
        self.assertIn("Duplicate ticket ID", err)

    def test_notes_and_next_note_id_survive_save_and_reload(self):
        """Required case #12: saving/loading preserves notes and next IDs."""
        import notes as notes_module

        tickets_list = [tickets.create_ticket([], "Wifi down", "Network", "high", 15)]
        notes_module.add_note(tickets_list, tickets_list[0]["id"], "Mentor A", "First note of fair length")
        storage.save_tickets(tickets_list, self.storage_path)

        reloaded, err = storage.load_tickets(self.storage_path)
        self.assertIsNone(err)
        self.assertEqual(len(reloaded[0]["notes"]), 1)
        self.assertEqual(reloaded[0]["notes"][0]["note_id"], "N001")

        # Next note ID after reload must continue from N001, not restart or collide
        second_note = notes_module.add_note(reloaded, reloaded[0]["id"], "Mentor B", "Second note after reload")
        self.assertEqual(second_note["note_id"], "N002")

    def test_old_record_missing_notes_field_is_migrated_not_rejected(self):
        """Backward compatibility: tickets saved by the ORIGINAL CampusFlow
        (pre-Next) have no 'notes' key at all. Loading must migrate them to
        notes=[] rather than rejecting perfectly good old data.
        """
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        old_style_record = [{
            "id": "T001", "title": "Pre-existing ticket", "category": "Network",
            "urgency": "high", "affected_users": 12, "priority": "critical",
            "status": "open", "assigned_to": None,
            # no "notes" key -- this is what v1 saved
        }]
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(old_style_record, f)

        loaded, err = storage.load_tickets(self.storage_path)
        self.assertIsNone(err)
        self.assertEqual(loaded[0]["notes"], [])


if __name__ == "__main__":
    unittest.main()
