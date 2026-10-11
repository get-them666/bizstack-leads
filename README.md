# bizstack-leads

The shared lead pipeline for the BizStack apps (Broom Service and Buildstack
Construction). Both apps import this package so the lead lifecycle, intake rules
and work queue are defined once instead of copied between two repositories.

## The model

- **One lifecycle** (`lifecycle.STAGES`): `new → contacted → engaged → quoted →
  won | lost`. Business state (a project's own status, whether a deposit was
  paid) is an attribute, not this column.
- **Next action** (`lifecycle.next_action`): every lead is tagged with the one
  thing to do next — `respond`, `follow_up`, `first_touch`, `enrich`, `waiting`,
  `closed` — and when it is due. The UI is organised by this, not by status.
- **One intake** (`intake.intake_lead`): every source (website, finance, radar,
  SAM.gov, permits, skiptrace, inbound email/SMS/voice) goes through the same
  normalise → dedupe → insert-or-merge → recompute path.
- **Review-mode outreach** (`outreach`): compose and stage here; sending is
  delegated to a transport the app injects, so the package holds no credentials
  and stays testable.

## Usage

```python
from bizstack_leads import schema, intake, queue, store, outreach

schema.ensure_schema(db)                       # once, at boot
intake.intake_lead(db, company="broom", source="website", name="Amy", phone="...")

for bucket in queue.buckets(db, company="broom"):
    print(bucket["label"], bucket["count"])
```

## Tests

```sh
createdb bz_leads_test
DATABASE_URL=postgresql://localhost/bz_leads_test python -m unittest discover -s tests -v
```
