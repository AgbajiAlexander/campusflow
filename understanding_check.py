"""understanding_check.py - The Engineering Understanding Check (Section 05).

Owned by Engineer B (Milestone B5). QUESTIONS is plain data, kept separate from
score_answers() (the scoring logic) and run_understanding_check() (the CLI
loop) -- so the question bank and the scoring can each be tested in
isolation, and so scoring never gets hard-coded into the menu loop.
"""

from typing import Any, Dict, List, Optional

QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "Q1",
        "prompt": "Ticket T001 is open and unassigned. A user tries to move it to in_progress.",
        "options": {
            "A": "Accept",
            "B": "Reject and preserve all data",
            "C": "Resolve it automatically",
            "D": "Remove ticket",
        },
        "correct": "B",
    },
    {
        "id": "Q2",
        "prompt": "The app has zero tickets. What should resolution percentage display?",
        "options": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "correct": "C",
    },
    {
        "id": "Q3",
        "prompt": "Filter title='wifi', category='Network', status='open'. Which records should match?",
        "options": {
            "A": "Any record matching one filter",
            "B": "Only records matching all supplied filters",
            "C": "All network records",
            "D": "All open records",
        },
        "correct": "B",
    },
    {
        "id": "Q4",
        "prompt": "A resolved ticket receives 'Add note'. What should happen?",
        "options": {
            "A": "Append anyway",
            "B": "Delete old notes",
            "C": "Reject until reopened",
            "D": "Change status silently",
        },
        "correct": "C",
    },
    {
        "id": "Q5",
        "prompt": "The JSON file includes two tickets with the same ID. What should load do?",
        "options": {
            "A": "Keep both",
            "B": "Replace memory with duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename IDs silently",
        },
        "correct": "C",
    },
    {
        "id": "Q6",
        "prompt": "A PR changes validation but has no negative-case tests. Best review action?",
        "options": {
            "A": "Approve because it runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "correct": "B",
    },
]


def validate_choice(choice: str) -> Optional[str]:
    """Validate that user choice is one of A, B, C, D (case-insensitive).
    Returns normalized uppercase letter or None if invalid.
    """
    cleaned = (choice or "").strip().upper()
    if cleaned in ("A", "B", "C", "D"):
        return cleaned
    return None


def score_answers(submitted_answers: Dict[str, str]) -> int:
    """Pure scoring function: given {question_id: letter}, return 0-6.

    Deliberately takes a plain dict rather than reading input() itself, so
    tests can call it directly with fixed answers -- including wrong or
    missing ones -- without simulating keystrokes.
    """
    score = 0
    for question in QUESTIONS:
        submitted = submitted_answers.get(question["id"])
        if submitted == question["correct"]:
            score += 1
    return score


def run_understanding_check() -> None:
    """The interactive CLI loop. Invalid letters (anything not A/B/C/D)
    re-prompt instead of being recorded. After scoring, asks for a short
    explanation of at least two answers -- displayed for mentor discussion,
    never auto-graded, since matching a keyword isn't the same as reasoning.
    """
    print("\n--- Engineering Understanding Check ---")
    answers: Dict[str, str] = {}

    for question in QUESTIONS:
        print(f"\n{question['id']}. {question['prompt']}")
        for letter, text in sorted(question["options"].items()):
            print(f"  {letter}) {text}")

        while True:
            choice = input("Your answer (A/B/C/D): ").strip().upper()
            validated = validate_choice(choice)
            if validated:
                answers[question["id"]] = validated
                break
            print("Invalid choice -- please enter A, B, C, or D.")

    score = score_answers(answers)
    print(f"\nScore: {score}/{len(QUESTIONS)}")

    print("\nExplain your answer for at least two questions (for mentor discussion):")
    explained = 0
    while explained < 2:
        qid = input(f"Which question will you explain ({explained + 1}/2)? e.g. Q1: ").strip().upper()
        matching = next((q for q in QUESTIONS if q["id"] == qid), None)
        if matching is None:
            print("Not a valid question ID -- try again.")
            continue
        explanation = input(f"Why is '{matching['correct']}' correct for {qid}? ").strip()
        print(f"  Recorded explanation for {qid}: {explanation}")
        explained += 1
