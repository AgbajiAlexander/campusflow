README.md — Engineer A's Section
Here's a straight, honest README focused on your (Engineer A) contribution. You can either use this as-is or merge it into a shared README with your partner.

Engineer A: Elizabeth Odeh
Engineer B: Agbaji Alexander

# CampusFlow

A Python command-line ticket manager for Learn2Earn campus staff. It records
technical support requests (Wi-Fi outages, faulty laptops, broken dev
environments, inaccessible platforms), calculates priority, assigns
responsibility, and tracks progress.

## Problem

Campus staff report issues informally — through WhatsApp, hallway chats, email —
and those reports get lost. CampusFlow gives every request a tracked record
with a computed priority and a clear owner.

## Team

- **Engineer A** — Ticket creation, input validation, priority engine, tests
- **Engineer B** — Assignment, workflow state machine, work queue, reports,
  JSON persistence, CLI integration

## Requirements

- Python 3.10 or later
- No external dependencies (uses only the standard library)

## Setup

```bash
git clone https://github.com/eliodeh/campusflow.git
cd campusflow

git clone https://github.com/AgbajiAlexander/campusflow.git 



Engineer A — Detailed contribution
I built and tested the ticket creation and priority logic.

Files I own:

campusflow/tickets.py — priority engine, validators, create_ticket(),
generate_next_id()

tests/test_tickets.py — 12 unit tests for the priority engine and input
validation

Key functions:

calculate_priority(urgency, affected_users) — returns
critical / high / medium / low using the four rules above.
Written as a pure function: no I/O, no time, no hidden state.

validate_title(title) — rejects blank or non-string titles.

validate_category(category) — normalizes case, rejects unknown values.

validate_urgency(urgency) — normalizes case, rejects unknown values.

validate_affected_users(users) — requires a positive integer.

generate_next_id(existing_tickets) — produces T001, T002, …

create_ticket(...) — orchestrates the above and returns a complete
ticket dictionary.

Tests I wrote:

Priority rule 1 (high + >= 10 users → critical)

Priority rule 2 (high urgency OR >= 10 users → high)

Priority rule 3 (medium urgency OR >= 3 users → medium)

Priority rule 4 (everything else → low)

Boundary cases at exactly 3 users and exactly 10 users

Case normalization ("NETWORK" → "Network")

Rejection of blank titles

Rejection of non-positive affected_users (zero, negative, non-integer)

Rejection of invalid categories and invalid urgencies

Sequential ID generation starting at T001

Git workflow
This project follows a two-person PR workflow. Every feature was built on
its own branch and merged through a reviewed pull request.

PR #1 — feat/1-ticket-creation: priority engine + 9 tests

PR #2 — feat/2-workflow-reporting: assignment, workflow, queue,
reports, persistence, CLI


AI usage
AI was used to learn concepts, not to write the project. Every AI
suggestion was verified by writing a test or reading the Python
documentation. Details are in docs/ai-learning-log.md.



After Writing It
Save the file

Verify it renders by opening it on GitHub later (after pushing)

Commit it.



What I learned
How ordered if/elif cascades implement business rules — and why the
order matters when Rule 1 is a strict subset of Rule 2.

Why pure functions (no I/O, no time) are easy to test.

The Python AND / OR truth tables and how they show up in real
decision logic.

The professional Git workflow: feature branch → commit → push → PR →
review → merge.