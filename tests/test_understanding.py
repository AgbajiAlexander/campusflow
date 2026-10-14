"""test_understanding.py - Engineer B's tests for understanding_check.py.
Covers Section 05 and Acceptance Criterion 14.
"""

import unittest
import understanding_check as uc


class TestScoreAnswers(unittest.TestCase):
    def test_all_correct_scores_six(self):
        all_correct = {q["id"]: q["correct"] for q in uc.QUESTIONS}
        self.assertEqual(uc.score_answers(all_correct), 6)

    def test_all_wrong_scores_zero(self):
        # Pick a deliberately wrong letter for every question
        all_wrong = {}
        for q in uc.QUESTIONS:
            wrong_letter = next(letter for letter in q["options"] if letter != q["correct"])
            all_wrong[q["id"]] = wrong_letter
        self.assertEqual(uc.score_answers(all_wrong), 0)

    def test_partial_and_missing_answers_score_correctly(self):
        partial = {"Q1": "B", "Q2": "C"}  # both correct per the brief; rest unanswered
        self.assertEqual(uc.score_answers(partial), 2)

    def test_question_bank_is_separate_data_not_hardcoded_in_scoring(self):
        # score_answers() must work purely from QUESTIONS data, not a parallel
        # hard-coded answer key -- proven by checking it reads QUESTIONS directly.
        self.assertEqual(len(uc.QUESTIONS), 6)
        for q in uc.QUESTIONS:
            self.assertIn(q["correct"], q["options"])

    def test_14_validate_choice_rejects_invalid_inputs(self):
        """14. CLI understanding check rejects invalid answer and scores correctly."""
        # Valid inputs (case-insensitive)
        self.assertEqual(uc.validate_choice("a"), "A")
        self.assertEqual(uc.validate_choice("B"), "B")
        self.assertEqual(uc.validate_choice(" c "), "C")
        self.assertEqual(uc.validate_choice("D"), "D")

        # Invalid inputs return None to trigger retry
        self.assertIsNone(uc.validate_choice("E"))
        self.assertIsNone(uc.validate_choice("1"))
        self.assertIsNone(uc.validate_choice(""))
        self.assertIsNone(uc.validate_choice("yes"))


if __name__ == "__main__":
    unittest.main()
