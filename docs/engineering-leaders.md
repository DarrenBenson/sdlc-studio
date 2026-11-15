# SDLC Studio for engineering leaders

This page is for the person who answers for a team's releases at a change approval board. It
says what the record a run leaves behind proves, and who answers for each part of it. Every
claim below links the script, reference section or committed record that enforces it, so you
can check it rather than take it on trust. You do not need to run a command to follow it.

## Change approval

A release goes to the board with its evidence pack, built by one command from committed records
alone. For each change it states what changed, which acceptance criteria passed, who reviewed it
independently, what is known to be wrong, and the accountable person, who is the person that
signed the run's report ([evidence_pack.py](../.claude/skills/sdlc-studio/scripts/evidence_pack.py),
[how the pack is built](../.claude/skills/sdlc-studio/reference-scripts-domain.md#evidence_packpy)).

The pack refuses a report nobody has signed, and it refuses to name an agent as the accountable
person. It reads only what is committed, so an edit nobody has committed cannot change what the
board sees ([evidence_pack.py](../.claude/skills/sdlc-studio/scripts/evidence_pack.py)).

A story reaches Done only through one gate, which refuses it while any of its executable
acceptance criteria is failing or has never run
([transition.py](../.claude/skills/sdlc-studio/scripts/transition.py),
[the Done gate](../.claude/skills/sdlc-studio/reference-scripts-create.md#transitionpy)). An
engineer can override that gate by hand with a flag, but the signature at the end of a run moves
each unit through the same gate and stops at the first one it refuses
([sprint.py](../.claude/skills/sdlc-studio/scripts/sprint.py)).

## Separation of duties: author, reviewer and signer

Each unit of work has three duties, held by three different people or seats, and the record
names each one, so work is never put down to "the agent". The signature refuses a run in which
one of them held two duties on the same unit
([sprint.py](../.claude/skills/sdlc-studio/scripts/sprint.py)).

- **Author.** The seat that builds the unit is recorded on the open run. A review verdict records
  the author beside the reviewer, and the review brief asks for both by name and role
  ([critic.py](../.claude/skills/sdlc-studio/reference-scripts-review.md#criticpy)).
- **Reviewer.** A fresh reviewer who did not write the change is briefed by a script, with the
  unit's acceptance criteria as the contract, and tries to break it
  ([the review brief](../.claude/skills/sdlc-studio/reference-review.md#closing-review-brief)).
  The script writes the verdict to a committed ledger, beside the author's name
  ([a verdict ledger](../sdlc-studio/reviews/critic-verdicts.md)).
- **Signer.** One person signs the whole run once, after reading its report. The signature
  refuses a person who authored or reviewed any unit in the run before it writes anything, and
  stops at a unit that has no approval from a reviewer other than its author
  ([signing a run](../.claude/skills/sdlc-studio/reference-sprint.md#the-loop)).

Before review, the author can be held to a self-check: every claim in the change's own prose
ruled true, false or unverifiable, and its tests mutated to show they fail when they should. This is
configurable. The shipped default reports a missing self-check and lets the review go ahead; a
project that sets it to block refuses the review brief until the self-check is recorded
([the author's self-check](../.claude/skills/sdlc-studio/reference-review.md#author-self-check)).

## The signed report

When a run closes it files one sprint report: a JSON page that is the record, with a readable
copy beside it. It states what shipped, what it cost, whether the estimate held and what is
known to be wrong
([the report of record](../.claude/skills/sdlc-studio/reference-evidence-schema.md#report-of-record)).

The report is the run's one account of what is left. Every open finding raised in the run, and
every unit carried to a later run, is listed as a known issue handed over, so nothing is left
in a separate note
([what the report hands over](../.claude/skills/sdlc-studio/reference-sprint.md#the-handoff-and-the-run-object)).

The signature is over the report's fingerprint, a digest of every figure on the page. Anyone can
recompute it from the page and compare it with the fingerprint the signature names
([how to recompute it](../.claude/skills/sdlc-studio/reference-evidence-schema.md#report-fingerprint)).

Signing refuses a report that is not the run's own, a working tree that has changed since the
close, and a page that no longer matches what its sources produce
([sprint.py](../.claude/skills/sdlc-studio/scripts/sprint.py)).

The run record keeps who signed, when, which report and the fingerprint signed
([the signature fields](../.claude/skills/sdlc-studio/reference-evidence-schema.md#run-record-signature-fields)).
This repository's own runs are signed this way, for example
[a signed report](../sdlc-studio/reports/RPT0031-sprint-report-run-01m7e52t.md) and
[its run record](../sdlc-studio/reports/runs/RUN-01M7E52T.json).

## Cost in dollars a point

The report states a Dollar cost row and a Dollars per point row: the run's estimated cost in US
dollars, and that cost over the story points delivered
([sprint_report.py](../.claude/skills/sdlc-studio/scripts/sprint_report.py),
[how dollars are priced](../.claude/skills/sdlc-studio/reference-sprint.md#dollar-cost)). The
dollar actual prices each model at its own rate from a dated table of list prices, so the actual
for a run that mixes models is never priced at one model's rate. The forecast beside it is priced
at one model's input rate
([the price table](../.claude/skills/sdlc-studio/templates/model-prices.json)). These are
estimates at list price, not an invoice.

Once a project has enough priced runs to set a rate, the plan forecasts a run's dollar cost
before it starts, and the report then states the forecast, the actual and the actual over the forecast. Forecasts are descriptive, not a promise
([forecast and actual](../.claude/skills/sdlc-studio/reference-sprint.md#dollar-cost)).

This repository's own runs show the scale. One signed run delivered 58 points for an estimated
$131.75, which is $2.27 a point
([its report](../sdlc-studio/reports/RPT0031-sprint-report-run-01m7e52t.md)).

The run after it forecast $3.38 a point and came in at $2.35 a point
([its report](../sdlc-studio/reports/RPT0032-sprint-report-run-01m7eyr3.md)).

There is no dollar budget setting. A run is capped by wall-clock minutes and a number of units.
To hold a team to a monthly budget, add up the Dollar cost rows of that month's signed reports
([sprint capacity](../.claude/skills/sdlc-studio/reference-config.md#capacity)).

## Where to read more

- [Why SDLC Studio](why-sdlc-studio.md) sets out the approach.
- [Installing](INSTALL.md) is the one install guide.
