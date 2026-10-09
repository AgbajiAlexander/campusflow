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


if __name__ == "__main__":
    unittest.main()
