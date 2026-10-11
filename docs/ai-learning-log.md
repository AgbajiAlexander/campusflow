## Interaction #3 — Rejecting an AI suggestion to use a list-of-rules engine

**Problem:**
I was writing the priority engine and asked the AI for a cleaner way to
structure the four rules. The AI suggested replacing the if/elif cascade
with a list of `(rule_function, priority)` tuples and iterating through it.

**My initial understanding:**
The AI's suggestion looked elegant — fewer lines of code, and easy to add
new rules later by just appending to a list.

**Prompt to AI:**
"Refactor this priority function to avoid long if/elif chains. Show me a
more scalable approach."

**Useful AI guidance:**
The AI returned this refactor:

```python
def is_critical(urgency, users):
    return urgency == "high" and users >= 10

def is_high(urgency, users):
    return urgency == "high" or users >= 10

def is_medium(urgency, users):
    return urgency == "medium" or users >= 3

PRIORITY_RULES = [
    (is_critical, "critical"),
    (is_high, "high"),
    (is_medium, "medium"),
]

def calculate_priority(urgency, affected_users):
    for rule, priority in PRIORITY_RULES:
        if rule(urgency, affected_users):
            return priority
    return "low"


My independent experiment:
I saved the AI's version in a scratch file and ran my 9 tests against it.
All 9 passed. The behaviour was identical to my if/elif version. But then
I tried to explain the code out loud as if I were in the technical demo.
I could not quickly explain why the rules were stored as tuples of
function references, or why the order inside PRIORITY_RULES mattered.
During the hand-tracing practice I had been doing, the if/elif version
let me read rule 1, then rule 2, then rule 3, in the same order the spec
lists them. The AI's version hides that order inside a list, one level of
indirection away.

Verification source:
I re-read the Python docs on lists and tuple unpacking, and I asked
myself: "Can I explain this code at the whiteboard in 60 seconds?" The
answer was no. I also re-read the spec to confirm that the cascade order
is the core requirement — which meant the code should make that order
visually obvious.

Decision:
Rejected — I kept the explicit if/elif cascade. The AI's version was
technically correct and my 9 tests confirmed it behaved the same, but it
was harder for me to explain and defend under time pressure. The if/elif
version maps one-to-one onto the spec's rule list, which makes it easy to
review, trace, and debug. Learning value: elegance is not the same as
clarity.

Related file/commit:
campusflow/tickets.py — final calculate_priority()
Commit: 104101c

What I can now explain without AI:
AI can suggest clever refactors, but "clever" is not always the right
goal. Code that maps directly onto the requirements — even if more
verbose — is easier to defend, easier to trace, and less likely to hide
bugs. I chose readability instead of cleverness.