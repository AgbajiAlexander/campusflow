import copy, os, tempfile, unittest
from campusflow.search import search_tickets, sort_by_priority_then_id, ticket_number
from campusflow.reports import build_report, format_report
from campusflow.question_bank import QUESTIONS
from campusflow.understanding_check import score_answers, run_check
from campusflow import cli_b


def T(i, title, cat="Network", status="open", pr="medium", notes=None):
    return {"id": i, "title": title, "category": cat, "urgency": "low", "affected_users": 1,
            "priority": pr, "status": status, "assigned_to": "Sam", "notes": notes or []}


def fixture():
    return [T("T001", "WiFi down in Lab", "Network", "open", "high"),
            T("T002", "wi-fi slow", "Network", "resolved", "low"),
            T("T010", "Laptop battery", "Hardware", "open", "critical"),
            T("T003", "WIFI printer", "Hardware", "open", "high")]


def feeder(items):
    it = iter(items)
    return lambda prompt="": next(it)


class SearchTests(unittest.TestCase):
    def test_title_ignores_case_and_matches_substring(self):
        ids = [t["id"] for t in search_tickets(fixture(), "WI-FI")]
        self.assertEqual(ids, ["T002"])
        self.assertEqual({t["id"] for t in search_tickets(fixture(), "wifi")}, {"T001", "T003"})

    def test_combined_filters_use_and(self):
        ids = [t["id"] for t in search_tickets(fixture(), "wifi", "network", "open")]
        self.assertEqual(ids, ["T001"])

    def test_empty_filters_return_everything(self):
        self.assertEqual(len(search_tickets(fixture())), 4)

    def test_search_is_read_only(self):
        data = fixture(); before = copy.deepcopy(data)
        results = search_tickets(data, "wifi")
        results[0]["title"] = "MUTATED"
        self.assertEqual(data, before)

    def test_invalid_filter_rejected(self):
        with self.assertRaises(ValueError):
            search_tickets(fixture(), category="Banana")

    def test_priority_sort_uses_numeric_ids(self):
        data = [T("T10", "a", pr="high"), T("T2", "b", pr="high"), T("T5", "c", pr="critical")]
        self.assertEqual([t["id"] for t in sort_by_priority_then_id(data)], ["T5", "T2", "T10"])
        self.assertEqual(ticket_number("T10"), 10)


class ReportTests(unittest.TestCase):
    def test_empty_report_is_zero_percent(self):
        r = build_report([])
        self.assertEqual((r["total"], r["resolution_percent"], r["unresolved"]), (0, 0.0, 0))
        self.assertIn("0.00%", format_report(r))

    def test_counts_match_fixture_and_never_double_count(self):
        r = build_report(fixture())
        self.assertEqual(r["by_status"], {"open": 3, "in_progress": 0, "resolved": 1})
        self.assertEqual(sum(r["by_status"].values()), r["total"])
        self.assertEqual(sum(r["by_priority"].values()), r["total"])
        self.assertEqual(sum(r["by_category"].values()), r["total"])
        self.assertEqual(r["resolution_percent"], 25.0)

    def test_reopened_ticket_counts_as_open_and_in_progress_is_unresolved(self):
        data = fixture()
        data[1]["status"] = "open"          # reopened
        data[0]["status"] = "in_progress"
        r = build_report(data)
        self.assertEqual(r["resolved"], 0)
        self.assertEqual(r["unresolved"], 4)


class UnderstandingCheckTests(unittest.TestCase):
    def test_scoring_is_pure_and_correct(self):
        perfect = [q["answer"] for q in QUESTIONS]
        self.assertEqual(score_answers(QUESTIONS, perfect), 6)
        self.assertEqual(score_answers(QUESTIONS, ["A"] * 6), 0)

    def test_invalid_answer_retries_and_score_uses_submitted_answers(self):
        answers = [q["answer"] for q in QUESTIONS]
        script = ["Z", answers[0], "I picked B because the ticket is unassigned.",
                  "x", "", answers[1], "Division by zero must be guarded."]
        script += answers[2:]
        out = []
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "notes.txt")
            result = run_check(QUESTIONS, feeder(script), out.append, notes_path=path, learner="B")
            self.assertEqual(result["score"], 6)
            self.assertEqual(len(result["explanations"]), 2)
            with open(path) as f:
                self.assertIn("score 6/6", f.read())
        self.assertTrue(any("Invalid choice" in line for line in out))

    def test_wrong_answers_lower_score(self):
        wrong = ["A", "A", "A", "A", "A", "A"]
        script = []
        for i, a in enumerate(wrong):
            script.append(a)
            if i < 2:
                script.append("a reasonable explanation here")
        self.assertEqual(run_check(QUESTIONS, feeder(script), lambda s: None)["score"], 0)


class CliTests(unittest.TestCase):
    def test_search_menu_reprompts_on_invalid_filter_and_is_read_only(self):
        data = fixture(); before = copy.deepcopy(data)
        out = []
        script = ["wifi", "banana", "network", "open", "", "n"]
        results = cli_b.search_menu(data, feeder(script), out.append)
        self.assertEqual([t["id"] for t in results], ["T001"])
        self.assertTrue(any("Invalid choice" in o for o in out))
        self.assertEqual(data, before)

    def test_add_note_menu_shows_friendly_error(self):
        def fake_add(tickets, tid, author, msg):
            raise ValueError("Cannot add notes to a resolved ticket.")
        out = []
        r = cli_b.add_note_menu(fixture(), fake_add, feeder(["t002", "Sam", "hello there"]), out.append)
        self.assertIsNone(r)
        self.assertIn("Could not add note: Cannot add notes", out[0])

    def test_view_notes_in_id_order_and_missing_ticket(self):
        notes = [{"note_id": "N002", "author": "B", "message": "second"},
                 {"note_id": "N001", "author": "A", "message": "first"}]
        data = [T("T001", "x", notes=notes)]
        out = []
        cli_b.view_notes_menu(data, feeder(["t001"]), out.append)
        self.assertTrue(out[0].startswith("N001"))
        out2 = []
        cli_b.view_notes_menu(data, feeder(["T999"]), out2.append)
        self.assertIn("No ticket", out2[0])


if __name__ == "__main__":
    unittest.main()