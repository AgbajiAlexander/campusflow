"""Report calculation (pure) and formatting (pure). No input(), no print()."""
from campusflow.search import VALID_CATEGORIES, VALID_STATUSES, VALID_PRIORITIES


def _count(tickets, field, known):
    counts = {k: 0 for k in known}
    for t in tickets:
        value = t.get(field)
        counts[value] = counts.get(value, 0) + 1  # unknown values still counted once
    return counts


def build_report(tickets):
    """Everything is derived from CURRENT ticket data, so reopened tickets
    are counted as open and nothing is double-counted."""
    total = len(tickets)
    by_status = _count(tickets, "status", VALID_STATUSES)
    resolved = by_status["resolved"]
    unresolved = by_status["open"] + by_status["in_progress"]
    return {
        "total": total,
        "by_status": by_status,
        "by_priority": _count(tickets, "priority", VALID_PRIORITIES),
        "by_category": _count(tickets, "category", VALID_CATEGORIES),
        "unresolved": unresolved,
        "resolved": resolved,
        "resolution_percent": round(resolved / total * 100, 2) if total else 0.0,
    }


def format_report(report):
    lines = [f"Total tickets: {report['total']}"]
    for title, key in (("By status", "by_status"), ("By priority", "by_priority"),
                       ("By category", "by_category")):
        lines.append(f"{title}:")
        lines += [f"  {k}: {v}" for k, v in report[key].items()]
    lines += [
        f"Unresolved (open + in_progress): {report['unresolved']}",
        f"Resolved: {report['resolved']}",
        f"Resolution rate: {report['resolution_percent']:.2f}%",
    ]
    if report["total"] == 0:
        lines.append("(No tickets yet.)")
    return "\n".join(lines)