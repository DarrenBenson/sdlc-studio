# Stakeholder Review: EP0287, personas held to a review standard (US1052 to US1057)

> **Date:** 2026-11-20
> **Artefacts:** EP0287 (CR0631), stories US1052 to US1057
> **Mode:** ADVISORY under D0374: a persona verdict informs and holds no gate. The orchestrator ruled as the operator's delegate under D0545, recorded as D0553.
> **Run at:** before any EP0287 story is built, in run twenty's planning
> **Personas:** each consulted in a fresh context, one subagent per persona, adopting its own card, with the objection quota in force

## Verdicts

| Persona | Perspective | Verdict |
| --- | --- | --- |
| Abena Osei | head of engineering in an audited organisation, Primary | Concerns |
| Maya Okafor | solo founder-engineer | Concerns |
| Jonah Reyes | team lead adopting on an inherited codebase, Secondary | Concerns |
| Rowan Achterberg | maintainer of the skill's source repository | Concerns |

All four accepted the direction. None accepted US1055's refusal as written.

## Where they converged, independently

1. **US1055's hard refusal can stop a run with no quick way on.** All four raised it from different goals: Abena and Maya want the refusal to name the one command that clears it; Jonah wants an upgrading repository to adopt the standard without a gate on the day it upgrades; Rowan wants this repository's own cards proven to pass before the refusal can stop its own runs.
2. **The process must stay small.** Abena (End goal 6) and Maya (End goal 5) both warned that an advisory rule repeated on every plan is noise.

## Rulings (D0553)

| Point | Raised by | Ruling |
| --- | --- | --- |
| The refusal names one command to run next | Abena, Maya | Taken: US1055 AC1 |
| This repository's cards pass the standard, held by a test the push gate runs | Rowan | Taken: US1055 AC5 |
| An upgrading project with its own cards gets report mode | Jonah | Taken: new story US1322 (3 points), after US1055 |
| A review row names the person who ran it, not only the seat | Abena | Taken: US1053 AC2 and AC3 (`--run-by`, defaulting to the git user name) |
| The ledger records an assertion, not proof | Jonah | Taken: US1053 note |
| Owed reviews are one count line at plan | Maya | Taken: US1057 AC4; the release cut still names each card |
| The release cut's owed line names its by-day comparison | Rowan | Taken: US1057 AC3 |
| The plan refuses before approval when a blocked card would brief a batch unit | Maya | Declined: report mode for an upgrading project, the remedy line and the plan's blocked line leave a mid-run refusal only for a card edited mid-run |
| The owed list in the cut's report for the change board | Abena | Declined here: the cut's CHANGELOG stays unchanged and the change board reads the evidence pack (CR0704) |
| A stated time bound for `check` | Rowan | Declined: a timing assertion in a test is flaky, and the commit gate already selects tests by change |
| Evidence citing one resolving id is thin | Jonah | Left as written: the rule is reported, not blocking |
