# SDLC Studio v6 for existing projects

You already run SDLC Studio on a project and want to know what v6 changes, what it removes
from your project and what you must change by hand. This page is the whole answer; the
[README](../README.md) stays focused on newcomers.

**The one-line summary: v6 retires the per-unit review ceremony, and `migrate` removes what your
project kept for it.** Plan review, the test-plan and repair-plan gates, the mutation ledger,
per-unit sign-off and the batch review are gone. One verdict per unit (`critic.py record`) decides
whether a unit was reviewed, and the operator signs the run once with `sprint.py sign`. Your
artefacts are safe: ids stay valid, nothing is renamed, and every judgement is reported to you
rather than made for you. The upgrade steps below are parsed out of this page and executed against
a fixture by the skill's test suite, so if they stop working, a build reddens rather than this
page misleading you.

## Upgrading to v6

### Upgrade steps

Install v6 first (the [README](../README.md) has the command), then run these from the project
root. The scripts live in the skill's `scripts/` directory; `/sdlc-studio migrate` runs the same.

```bash
migrate.py
migrate.py --apply
# add the conformance.adopt_after line migrate named, if it named one
gate.py
```

1. **`migrate`** is a dry run. It prints what it would upgrade deterministically and what needs a
   human, and writes nothing.
2. **`migrate --apply`** writes only the deterministic set, then prints the same needs-a-human
   list.
3. **Work the needs-a-human list.** On a project with history it names the
   `conformance.adopt_after: <id>` line to add under `conformance:` in
   `sdlc-studio/.config.yaml`, listing each unit the conformance lane would fail and what it
   misses, so you can check none of them is recent work before grandfathering it. `migrate` never
   writes that line: the cutoff is a judgement about your history.
4. **`gate.py`** judges the upgraded project (commit the upgrade first: on an uncommitted tree it
   judges only the diff). A lane that fails names its own remedy; an index `migrate` found drifted
   shows as a warning until `reconcile apply` regenerates it.

**On the `6.0.0-rc.1` release candidate?** Reinstall. The candidate's version check reads a
pre-release as equal to its final release, so it never offers you the final. Later releases order
a pre-release below its final, so this happens once. Then run `migrate --apply` again: it restamps
`sdlc-studio/.version` with the version you now run.

### What `migrate --apply` removes and what it leaves to you

It writes only what is deterministic and reversible:

- every retired key in `sdlc-studio/.config.yaml` (named in the table below), with its children,
  keeping every other byte; a comment that explained a removed key stays, and is yours to delete;
- the two retired `[check:]` tags in the Definition of Ready and Done, keeping each criterion as a
  human-judged line;
- the `sdlc-studio/.version` stamp (a project created by v6's `init` already carries one) and a
  container's legacy `Effort` converted to a `Size`.

It reports, and never writes:

- each `AGENTS.md`, `CLAUDE.md`, Definition of Ready or Done line naming a retired key or a
  retired verb, with its line number: edit those by hand;
- the `conformance.adopt_after` cutoff (step 3);
- the frozen review records under `sdlc-studio/reviews/`, reported as history and left as
  written; `sdlc-studio/.local/mutation-runs.json` is read by nothing.

It cannot see your own scripts or CI: search them for each name below. Two defaults also changed:
`review.line_coverage` is `off` (set `report` or `block` to keep measuring) and
`triage.low_consolidation` is `false` (set `true` to keep folding Low findings into one request).
Four gate lanes are gone, `mutation`, `evidence-drift`, `derived-depth` and `close-owed`, and
`gate.py --only` with one of them fails as an unknown check name.

### What replaces each retired name

A retired verb or flag is refused by name (exit 2, the reason printed, nothing written) or fails
as an argparse error; a retired key is ignored where it is still set.

| Retired in v6 | Use instead |
| --- | --- |
| `critic.py signoff`, `critic.py signoff-brief`, `sprint.py close --apply-signoff`, `sprint.py call --apply-signoff`, `sprint.py call --principal`, `persona_resolve.py panel --ceremony signoff` | The operator signs the run once, after the close: `sprint.py sign --report <RPT> --principal <name>`. `refine` and `triage` panels resolve as before |
| `sprint.py close --principal`, `sprint.py close --author` | Pass them to `sprint.py sign`; `close` accepts and ignores them |
| `review.signoff`, `review.two_role_after` (keys), `review.two-role` (`[check:]` id) | The operator signs the run at `sprint.py sign`; `migrate --apply` removes the keys and strips the tag |
| `critic.py evidence`, `critic.py sprint-review`, `sprint.py review-batch` | One delivery verdict per unit: `critic.py record` |
| `critic.py repair` | Answer a REJECT with a round-2 `critic.py record` from the same reviewer, or carry the unit at the review cap |
| `--phase` on `critic.py brief`, `record`, `correct`, `show` or `supersede`; `critic.py record --kind` | Drop the flag: every verdict is a delivery verdict |
| `mutation.py register`, `mutation.py retract`, `mutation.py retractions`, `mutation.py audit`, `mutation.py run --from-plan` | No ledger is kept: measure on demand with `mutation.py run --story <id>` |
| `mutation.py run --unit` | Drop the flag; `run` records a series row, read back with `mutation.py yield --run <id>` |
| `review.mutation_evidence` (key), `repair.mutation-evidence` (`[check:]` id) | No repair-mutation gate: `migrate --apply` removes the key and strips the tag |
| `verify_ac.py testplan` (`derive`, `probe`, `rule`, `withdraw`), `verify_ac.py depth`, `verify_ac.py depth-check`, `plan_review.py`, `repair_plan.py` | Nothing: a unit's criteria and `Verify:` selectors are its plan and its proof, and it reaches Done or Fixed on them |
| `plan_review` (the block), `review.test_plan_after`, `review.plan_falsifiability`, `review.repair_plan_gate`, `review.repair_design_threshold`, `review.require_brief_provenance`, `quality.depth_parity_gate` | Read by nothing: `migrate --apply` removes them |
| `artifact.py new --target`, `artifact.py close --depth`, `transition.py set --depth` | Drop the flag: an acceptance criterion's `Verify:` line is its proof |
| `review.line_coverage_after` | Under `review.line_coverage: block` every unit is judged: set `report` to keep older units moving, or rule the uncovered lines with `verify_ac.py coverage rule`. `migrate --apply` removes the key |
| `sprint.py preflight` | `sprint.py close --dry-run`; the close runs the same pre-flight first |
| `sprint.py plan --goal-review-waived`, `sprint.py plan --override-goal-review` | Drop the flag: a seat's goal verdict is printed as advice and never refuses the plan |
| `gate.py --require-close` | `close_owed.py detect`; `status` still reports an owed close |
| `gate.py --test-relevant` | `gate.py --suite-decision --staged`, or `--changed PATH...` |
| `verify_ac.py lint --ratchet`, `verify_ac.py lint --stamp` | `verify_ac.py lint`, which reports a shared selector and exits 0; no baseline is kept |
| `validate.py warning-ratchet` | `validate.py check`, which prints footprint warnings on open work and exits 0 |
| `persona_resolve.py panel --dry-run` | Drop the flag; it served the sign-off ceremony only |

The full inventory, with what each name did before, is the Breaking section of the first v6
release in [CHANGELOG.md](../CHANGELOG.md).

## What v6 refuses on day one, and how to clear it

| Gate | What it does on an upgraded project | Remedy |
| --- | --- | --- |
| `sprint.breakdown` (default `enforce`) | `sprint plan` refuses any batch holding a unit with no `Affects` or `Points`. A backlog older than both fields fires this on the first plan. | Groom the units you are about to plan (`sprint breakdown --stories Ready --bugs Open` lists them), or record `sprint.breakdown: judgement` in `sdlc-studio/.config.yaml` as a deliberate decision. Omission is not an escape: an absent config blocks. |
| `conformance.adopt_after` (default unset) | Unset judges EVERY story you have ever written, so whenever `gate.py` judges the whole workspace (a clean tree, or `--release`) it fails on history written before the rule existed. | Add the line `migrate` names. Ids at or below it are reported `exempt (pre-adoption)` and the gate judges forward only. |

## A project last upgraded on v4 or earlier

The same two commands, `migrate` then `migrate --apply`, take a project last upgraded on v4.1 or
earlier across in one pass. The path was rehearsed on copies of two real projects, one last on v4.1
(687 stories) and one on v2.4 (593 stories). Every `migrate` run exited 0 in under ten seconds, the
dry run wrote nothing, a second run found nothing left to apply, and the upgrade added no
validation error. The [rehearsal record](upgrade-rehearsal-v6.md) has the figures and findings.

On a `schema_version: 2` project (sequential ids such as `US0001`) `migrate --apply`:

- keeps `schema_version: 2` and every id: it never switches the numbering scheme (see the
  numbering question below, which is your decision);
- stamps `sdlc-studio/.version` from the version it records to the one you run, writing the file
  if the project predates it;
- converts each container's legacy `Effort` or `Points` to a T-shirt `Size` (45 files on the v2.4
  project), leaving the old line in place;
- removes any retired key or tag, as above.

What it leaves to you, each with the command it prints:

- **the `conformance.adopt_after` cutoff.** Older Done stories carry no recorded evidence the
  lane reads, so it fails them until you grandfather them; `migrate` names the line and each unit
  with what it misses. Check the list before you accept it: on the v4.1 project the proposed
  cutoff also covered units reviewed under the old ledger shape (BG0845).
- **index drift**: review it with `/sdlc-studio reconcile`, and `reconcile apply` regenerates the
  indexes. The report counts only part of what the gate's reconcile lane reads (BG0842).
- **a request accepted but never decomposed**: `refine apply --request <id> ...`, printed per
  request.
- **persona layout**: uncovered seat roles (`persona generate --team` grows seats from your
  project, or `migrate --apply --with-default-amigos` installs the shipped defaults), an index
  naming the old persona categories, and nested persona folders.
- **`AGENTS.md` and `CLAUDE.md` hygiene**: each finding against `templates/agent-instructions.md`
  (refresh from it, keeping your project's own sections), and any line naming a retired key or
  verb.
- **validate errors** the project already carried (136 and 562 on the two projects); the upgrade
  adds none.
- **a delivery unit sized only in `Effort`**: set its `Points` by judgement; there is no honest
  map from one to the other.

Two things the report does not name: units below the engagement floor, which surface only at the
gate (BG0843), and the `sdlc-studio/.gitignore` that `init` writes, which an upgraded project
never gets, so a gate run leaves its runtime state in `git status` (BG0844). Commit the upgrade,
then run `gate.py` on the clean tree, where it judges the whole workspace. Then
`sprint.breakdown` (above) refuses a plan until the units in it carry `Affects` and `Points`.

## The numbering question - three answers, all supported

When you run `project upgrade` on a v3-or-earlier project, it asks you explicitly how
to handle identity. There is no default that rewrites anything:

1. **Migrate everything** (`migrate_v3 apply --confirm`) - every artifact gets a ULID;
   old sequential ids are kept as aliases, so links and tickets keep resolving.
2. **Adopt forward-only** (`migrate_v3 adopt --confirm`) - the recommended path for a
   living project. Existing ids stay exactly as they are (still valid in tickets, chat,
   and docs); only NEW artifacts mint ULIDs. The two eras coexist by design and nothing
   is renamed.
3. **Stay sequential** - decline, and the project keeps sequential numbering entirely.
   You can revisit at any later upgrade.

Both migration commands refuse to run without `--confirm`, and refuse to touch a
directory that is not an sdlc-studio workspace. If your clones disagree (one machine
upgraded, another not), `reconcile` raises an era-divergence advisory rather than
letting two writers mint in different modes silently.

`project upgrade` without `--apply` is a report: it lists what would change (including
a `team-offer` entry and any legacy amigo cards that would migrate to `seats/`) and
applies nothing. The installer also refuses to downgrade a newer installed copy unless
you pass `--allow-downgrade`.

## Meeting the generated team on an existing project

`persona generate --team` is offered, never run for you. On a brownfield project it
works from the repo map alone (no PRD needed), asks at most four multi-choice
questions, and **never overwrites a card you authored or edited** - authored and
generated cards are discriminated by a provenance stamp plus a content hash, so your
edit promotes a card to authored and re-runs propose diffs instead of clobbering.
Generated cards stay labelled provisional-unverified until you review and accept them
(`persona review`); `status` counts the unreviewed ones so the label cannot silently
linger.

## Developing or testing the skill itself

- **Try a local working tree** without touching your global install:
  `./install.sh --from <dir> --target claude` installs from a directory instead of the
  frozen release, under the same identity and downgrade guards.
- **Check what changed since your version:** `project upgrade` reports the capability
  delta; [CHANGELOG.md](../CHANGELOG.md) carries the full history.
- **Run the repo's own gate** before contributing: `npm run lint` and `npm test`, or
  the plain Python/bash equivalents listed in [AGENTS.md](../AGENTS.md) - the
  pre-commit hook (`bash tools/enable-hooks.sh`) runs all of it on every commit.

## If something refuses you

- `autosprint` is still an alias of `sprint`.
- Default amigo cards are not auto-installed at upgrade; the generated team is offered first,
  existing cards are never deleted, and legacy `personas/amigos/` cards move to
  `personas/seats/` without overwriting a seat that already exists.
- New projects default to `schema_version: 3` (ULIDs); an existing project is never switched
  for you.
- If v6 refuses you something this page does not prepare you for, that is a bug - please file
  it.
