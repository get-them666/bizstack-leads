"""The owner's work queue: leads grouped by what to do next.

This is the view the whole restructure exists to produce. Instead of a flat
table ordered by ``created_at`` that the owner has to triage by hand, it is
grouped into the six :data:`bizstack_leads.lifecycle.ACTION_*` buckets, most
urgent first, each row already carrying its due time.

``respond`` and ``follow_up`` float to the top because a waiting human is the
only thing that gets more expensive with delay.
"""
from __future__ import annotations

from . import lifecycle, store


def buckets(db, company=None, *, q="", limit=500) -> list[dict]:
    """Group open leads by next action.

    Returns ``[{action, label, leads, count}]`` in :data:`ACTION_ORDER`, with
    empty buckets dropped so the page is only as long as the work.
    """
    rows = store.list_leads(db, company, q=q, limit=limit)
    by_action: dict[str, list] = {}
    for row in rows:
        action = row.get("next_action") or lifecycle.ACTION_FIRST_TOUCH
        by_action.setdefault(action, []).append(row)

    out = []
    for action in lifecycle.ACTION_ORDER:
        leads = by_action.get(action) or []
        if not leads:
            continue
        out.append({
            "action": action,
            "label": lifecycle.ACTION_LABELS[action],
            "leads": leads,
            "count": len(leads),
        })
    return out


def counts(db, company=None) -> dict:
    """Action -> count, including zeroes for buckets the owner expects to see."""
    raw = store.queue_counts(db, company)
    return {action: raw.get(action, 0) for action in lifecycle.ACTION_ORDER}


def due_follow_ups(db, company=None, limit=100):
    """Leads whose follow-up is due now -- the input to the outreach sweep."""
    return store.list_leads(db, company, action=lifecycle.ACTION_FOLLOW_UP, limit=limit)


def first_touch_ready(db, company=None, limit=100):
    """Reachable leads nobody has touched yet -- the cold-outreach input."""
    return store.list_leads(db, company, action=lifecycle.ACTION_FIRST_TOUCH, limit=limit)


def needs_contact_info(db, company=None, limit=200):
    """Leads with no phone/email -- the enrichment input (folded-in permits)."""
    return store.list_leads(db, company, action=lifecycle.ACTION_ENRICH, limit=limit)
