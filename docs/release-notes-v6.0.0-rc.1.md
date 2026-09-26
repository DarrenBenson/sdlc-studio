# SDLC Studio v6.0.0-rc.1

**The lean loop: one verdict ledger decides whether a unit was reviewed, and one signature seals
the run.** This is a release candidate. v5.1.0 remains the current stable release until the
soak described below ends and 6.0.0 is cut.

## What v6 is

v5 accumulated ceremony around each unit, some of it on by default and some opt-in: a plan
review before code, a test plan and its own review, registered mutants for a repair, a repair
plan after a REJECT, an evidence row, a batch review, and a reviewer-of-record sign-off per unit.
By September 2026, 82% of this repository's sprint units served its own machinery rather than
the product. v6 removes that stack and keeps the criteria and the independent review.

**The loop, as it runs:**

- **A Sprint Goal is one sentence of 20 words or fewer**, traced to an outcome or a persona.
  `sprint.py plan` orders and sizes the batch, and the operator approves the plan once. A seat's
  read of the goal is printed as advice; it no longer stops the plan.
- **Each unit is built against its acceptance criteria and reviewed by one reviewer, in at most
  two rounds.** The brief comes from `critic.py brief`, never a hand-written prompt. Round two
  re-checks the fixes. A unit still rejected at the cap is carried: its findings are filed as a
  bug, the unit leaves the batch, and it is delivered again in a later run.
- **One verdict ledger.** `critic.py record` writes the per-unit delivery verdict, and every
  reader (conformance, the close, the sign, the report, escalation) decides from it. The
  evidence, repair, sign-off and plan-review ledgers are frozen history: read by nothing, except
  that rows dated before the retirement in the repair and batch-review records still count.
- **Persona rulings.** A question in a seat's lens is ruled by that seat and recorded with
  `decisions.py rule`, so the run does not wait on it.
- **One signature.** `sprint.py close` runs the close in one pass and files a one-page sprint
  report that states every known issue rather than being withheld over one. `sprint.py sign`
  seals that report once, and refuses a principal who authored or reviewed a unit in it.
- **A unit closes on its criteria.** A story reaches Done, and a bug Fixed, when its executable
  criteria pass and its review approves. No test plan, depth tier, plan review or mutation
  ledger is asked for. `mutation.py run` still measures a suite on demand, and line coverage
  runs only when a project opts in.

What went wrong in a run is recorded as a failure class in `sdlc-studio/lessons.jsonl`, and its
rule is carried into the next plan, build and review.

## Breaking changes

v6 retires 19 verbs, 20 flags, 11 config keys, 2 `[check:]` ids and 4 gate lanes, and changes 2
defaults. The full inventory, each entry with its before, after and migration, is in
[the 6.0.0 section of the CHANGELOG](../CHANGELOG.md#600---2026-09-26), under **Breaking**.

The ones most likely to meet you:

- **`critic.py signoff` and `signoff-brief` are refused.** Sign the run once with
  `sprint.py sign --report <RPT> --principal <name>`. `sprint close --apply-signoff` is refused
  the same way.
- **`critic.py evidence`, `critic.py sprint-review` and `sprint.py review-batch` are refused.**
  Record a per-unit delivery verdict with `critic.py record`.
- **`mutation.py register`, `retract`, `retractions` and `audit` are refused.** No per-target
  ledger is kept; `mutation.py run --story <id>` measures on demand.
- **`plan_review.py` and `repair_plan.py` are deleted**, and `verify_ac.py testplan` and `depth`
  are refused. A unit's criteria and `Verify:` selectors are its plan.
- **`review.line_coverage` now defaults to `off`**, and `triage.low_consolidation` to `false`:
  a Low finding mints its own bug. Set either back if you relied on it.

Most retired verbs and flags are refused by name: exit 2, the reason and its replacement
printed, nothing written. The rest meet argparse's usage error or a deleted script, and two
`sprint close` flags are accepted and ignored; the inventory says which for each.

## Upgrading from v5.1

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py"            # dry run: what it would change
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py" --apply    # carry the project across
```

`migrate --apply` removes every retired `.config.yaml` key with its children, keeping every other
byte, and strips the two retired `[check:]` tags (`review.two-role`,
`repair.mutation-evidence`) from the Definition of Ready and Done, keeping each criterion as a
human-judged line. On a project initialised by v5.1.0's `init`, with two retired keys
(`review.two_role_after`, `review.mutation_evidence`) and a `plan_review` block added, it removed
both tags, both keys, the `review:` block they left empty and the `plan_review` block, and
restamped the project version.

Three things it leaves to you, and names:

- **Instruction files.** Each `AGENTS.md`, `CLAUDE.md`, DoR or DoD line naming a retired key or
  verb is reported by file and line, never rewritten. Edit those by judgement.
- **Your own scripts and CI.** `migrate` cannot see them. Search them for each verb and flag in
  the CHANGELOG inventory; `plan_review.py`, `repair_plan.py` and `validate.py warning-ratchet`
  are not reported by `migrate` at all.
- **The frozen review records** under `sdlc-studio/reviews/` are listed as history and left as
  written. Nothing needs deleting.

## Known issues

Every open finding this release ships is listed by id on [the disclosure page](known-issues.md),
which `tools/known_issues.py write` generates from the bug corpus at the cut; the pre-push hook
refuses the tag while the page and the corpus disagree. The count below is written by the same
run, so it cannot drift from the page.

**v6.0.0-rc.1 discloses 27 open defects: 27 Medium, 0 Low.**

The v6.0 bar is zero open Critical or High finding at the tag. The open Mediums ship under the
triage decision D0273 rather than a waiver per finding: it names most of them individually,
and its first clause triages every other open Medium to v6.1. D0277 records why BG0788 ships
open.

Three limits worth knowing before you rely on the signature, the commit hook and the updater:

- **A signed report can be verified only in the clone that signed it.** The signature record
  lives in the gitignored `sdlc-studio/.local/`; CR0599 moves it into a tracked file.
- **A commit touching a widely imported script runs over its 90-second budget** (BG0754). The
  hook warns and never refuses; the full suite at push is unchanged.
- **An installed candidate is not prompted to move to 6.0.0** (BG0790): the version check reads
  `6.0.0-rc.1` and `6.0.0` as equal. Reinstall with `--version v6.0.0` when it is cut; BG0790 is
  fixed before that cut.

## This is a release candidate

Sprint 6 is the soak. This repository runs that sprint on the candidate, and 6.0.0 is cut only
after it closes, from a fully green release gate. Before the final tag:

- the skill documentation stops naming retired verbs, and this repository runs on the shipped
  defaults (EP0266);
- the migration is rehearsed on two real consuming projects, with the record linked from the
  6.0.0 notes;
- the eval scenarios are re-run against v6 behaviour;
- any finding the soak raises at Critical or High is fixed first.

To try the candidate now, pin it:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | SDLC_STUDIO_REQUIRE_CHECKSUM=1 bash -s -- --version v6.0.0-rc.1
```

## What is in it

Composed at the cut from `changelog.d/` by `release_cut.py changelog-cut`: 152 fragments, one
per delivered unit, now the [6.0.0 section of the CHANGELOG](../CHANGELOG.md#600---2026-09-26).
