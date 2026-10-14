"""Engineering Understanding Check: scoring is separate from the menu loop."""
from datetime import datetime
from campusflow.cli_input import prompt_choice, prompt_text
from campusflow.question_bank import QUESTIONS

LETTERS = ("A", "B", "C", "D")


def score_answers(questions, answers):
    """Pure scoring: 1 point per exact match against the submitted answers."""
    return sum(1 for q, a in zip(questions, answers) if a == q["answer"])


def save_explanations(path, learner, score, total, explanations):
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"--- {learner} | {datetime.now():%Y-%m-%d %H:%M} | score {score}/{total} ---\n")
        for e in explanations:
            f.write(f"{e['question_id']} (answered {e['answer']}): {e['explanation']}\n")


def run_check(questions=QUESTIONS, input_fn=input, output_fn=print,
              explain_count=2, notes_path=None, learner="learner"):
    answers, explanations = [], []
    for q in questions:
        output_fn(f"\n{q['id']}. {q['prompt']}")
        for letter in LETTERS:
            output_fn(f"  {letter}) {q['options'][letter]}")
        choice = prompt_choice("Your answer (A/B/C/D): ", LETTERS, input_fn, output_fn)
        answers.append(choice)  # first submitted choice is final
        output_fn("Correct!" if choice == q["answer"]
                  else f"Not quite. Correct: {q['answer']}. {q['explanation']}")
        if len(explanations) < explain_count:
            text = prompt_text("Explain your answer in a sentence or two: ",
                               input_fn, output_fn, min_len=10)
            explanations.append({"question_id": q["id"], "answer": choice, "explanation": text})
    score = score_answers(questions, answers)
    output_fn(f"\nFinal score: {score}/{len(questions)}")
    if notes_path:
        save_explanations(notes_path, learner, score, len(questions), explanations)
    return {"score": score, "answers": answers, "explanations": explanations}