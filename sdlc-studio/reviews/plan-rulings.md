# Plan Rulings

> Append-only. A criterion the plan probe classified as a finding, and the
> recorded decision to plan over it anyway. The digest covers the criterion's
> TITLE and its `Verify:` SELECTOR together, so a ruling stops applying the
> moment either changes - a pin that outlives the criterion it excused is a
> pin nobody decided to give.
> A withdrawal MARKS its row rather than deleting it: what was decided stays
> visible beside the decision to undo it.

| Unit | Criterion | Digest | Reason | Author | Date |
| --- | --- | --- | --- | --- | --- |
| US0626 | AC7 | 0fb1781d4569 | WITHDRAWN: AC7 now names its own test through the shared predicate; the ruled control borrowed US0299's verifier under a different spelling, which the duplicate-verifier lint cannot see (L-0407) - a goal-review QA finding (was: a deliberate regression control: stop's pending-decision exit must keep working when the shared predicate lands (D0196a), so this criterion is green before the change by design and fails if the predicate counts a parked unit as unanswered) | sprint planning 2026-09-15; agent; v1 | 2026-09-15 |
