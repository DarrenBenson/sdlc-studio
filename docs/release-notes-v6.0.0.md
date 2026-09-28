# SDLC Studio v6.0.0

**SDLC Studio 6.0.0 is the current release: a sprint is one plan you approve, one independent
review per unit and one signature, and the ceremony v5 wrapped round each unit is gone.**

Every breaking change is listed, with its replacement, in the
[6.0.0-rc.1 section of the CHANGELOG](../CHANGELOG.md#600---2026-09-26), and what 6.0.0 changed
since the candidate is in the [6.0.0 section](../CHANGELOG.md#unreleased). If you already run SDLC
Studio on a project, [the existing-users page](existing-users.md) is the whole upgrade path.

## What changed for you

- **One plan, one review, one signature.** You approve the plan once, each unit gets one reviewer
  who did not write it, in at most two rounds, and you sign the run once. Questions a persona can
  answer no longer wait for you. The loop is below.
- **A one-page report.** A v5 sprint report ran to 14 sections and a 22-row checklist (the
  back-to-basics review). A v6 report has five sections (goal, estimates, delivered to plan, known
  issues, sign-off) and an appendix (RPT0010). It states every known issue
  rather than being withheld over one.
- **The ceremony that caught nothing is gone.** In the back-to-basics review of this repository,
  82% of the last 116 sprint units built or repaired the sprint, review and gate machinery rather
  than the product. Plan review rejected 255 of 428 plans, and its 566 recorded fixes changed test
  plans, not code (the back-to-basics review). 1,052 of 1,062 registered mutants were killed, a
  costly signal that was almost never red (the back-to-basics review). Plan review, the test-plan
  and repair-plan gates, depth tiers as a gate, the mutation ledger, per-unit sign-off and the
  batch review are removed. The delivery review stays because it finds real defects: in one v5
  run, 9 of 10 REJECT rounds changed production behaviour (the back-to-basics review).
- **Faster feedback.** A v5-era run stood open for 14.5 to 59.6 hours (the back-to-basics
  review). The v6 runs of this repository took 8.7, 5.4, 7.2 and 7.0 hours for 58, 42, 32 and 111
  points (RPT0006-RPT0009), and 27.3 hours for 102 points (RPT0010); each span is wall-clock, so
  waiting counts. This repository's own push gate fell from a 678 s median (the back-to-basics
  review) to under 8 minutes, about 462 s over its last 10 runs on 2026-09-28 (the
  `gate_timing.py` estimate); the figure moves with every push.
- **It learns from its own runs.** What went wrong in a run is recorded as a failure class in
  `sdlc-studio/lessons.jsonl`, and its rule is carried into the next plan, build and review brief.
  The v5 token forecast missed by 4.07x on geometric mean (the back-to-basics review). The five v6
  runs came in at 1.14x, 0.50x, 1.03x, 0.51x and 0.53x of their forecast (RPT0006-RPT0010), so
  three of them were forecast at about twice what they spent; the rate now follows the newest
  runs, and you can set it by hand. A time forecast is new, and it has missed by between 0.59x
  and 2.51x (RPT0007-RPT0010).

## What v6 is

v5 accumulated ceremony around each unit, some of it on by default and some opt-in: a plan
review before code, a test plan and its own review, registered mutants for a repair, a repair
plan after a REJECT, an evidence row, a batch review, and a reviewer-of-record sign-off per unit.
v6 removes that stack and keeps the criteria and the independent review.

**The loop, as it runs** (taught in one place, `reference-sprint.md#the-loop`):

- **A Sprint Goal is one sentence of twenty words or fewer**, traced to an outcome or a persona.
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

## Upgrading from 6.0.0-rc.1

Reinstall at the release, checksum-verified, then carry each project across:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | SDLC_STUDIO_REQUIRE_CHECKSUM=1 bash -s -- --version v6.0.0
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py"            # dry run: lists what it would change, writes nothing
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py" --apply    # stamps the project 6.0.0, files signed reports' run records
```

**Your installed candidate will not tell you to move.** Its version check reads 6.0.0-rc.1 and
6.0.0 as equal, so it never offers the release: reinstall by hand. 6.0.0 orders a pre-release
below its release, so from this release on an installed candidate is prompted to move to its
final release, and `migrate` stamps the exact version.

`migrate --apply` files the run record of each sprint report you signed on the candidate, so the
report checks in any full clone, and only when the report re-derives to the fingerprint it was
signed at; otherwise it names the report for you and files nothing. It never rewrites a signed
page. `project upgrade` may show no digest of what changed: the candidate's `migrate --apply`
stamped a project `6.0.0` rather than `6.0.0-rc.1`, and its `init` wrote no version at all. The list
below is that digest.

### What changed since the candidate

- **A signed sprint report checks in any full clone.** `sprint sign` files the sealed run record
  beside the report, with absolute paths made repository-relative or digested, and
  `sprint_report.py check` reads it there. The candidate could verify a signature only in the
  clone that signed it.
- **The version check knows a candidate from its release**, as above, and `project upgrade`
  prints the breaking changes first and in full.
- **A fresh project records its version.** `init` writes `sdlc-studio/.version`, so a new
  project's first `migrate` has nothing to report and its first upgrade names the range it crossed.
- **Root config files stay in a unit's scope.** A slash-free `Affects` entry such as
  `package.json`, `astro.config.mjs` or `Makefile` was dropped, so the review brief and the plan's
  file checks never saw it. It is kept now, which matters for any project not written in Python.
- **An old project is told its conformance cutoff.** For a v4-era project, `migrate` reports each
  unit the conformance lane would fail and the `conformance.adopt_after` line that grandfathers
  them. It never writes the line: choosing the cutoff is your judgement.
- **A first run starts where it should.** `init guided` no longer counts a stage done from its own
  unfilled scaffold: the run that drafts the PRD resumes at `prd`, and an `AGENTS.md` that `init`
  seeded, or one without the lifecycle doctrine, keeps the `agents` stage open and offers to
  append the doctrine without rewriting the file.
- **The close and the signature agree.** An approved story or bug the loop left at Ready or In
  Progress is no longer handed over as unanswered, since the signature moves it to Done anyway.
  `sprint close --dry-run` previews the open run's goal, units and start time. A report's
  `Verified on` names the commit the close's gate ran against, not the one the run was planned
  from. The close, the signature and the report speak v6's words: `Signed by`, not reviewer of
  record, and no retired `apply-signoff:` prefix.
- **The token forecast follows your newest runs.** The rate per point no longer freezes on old
  rows once they stop naming a model, and `estimate.tokens_per_point` in `.config.yaml` sets it
  by hand; the plan names the override and the measured rate it replaced.
- **The report reads what was measured.** The cost row reads the run's measured token total,
  per-unit minutes and tokens come from the agent totals you tag to a unit
  (`retro.py accuracy --delegated-tokens N --delegated-unit ID`), a first sprint no longer hands
  over the epic drift its own close settles, and the close's pre-flight no longer lists the
  verdict the same command records.
- **Reviews say when their brief is stale.** `critic.py brief` names a seat card with no role line
  and the shipped card briefed in its place; `critic.py record` warns when a unit's `Affects` or
  criteria changed after its brief. The bug-close guidance names the independent reviewer and its
  brief, and `transition.py set` takes `--brief`.
- **Other fixes.** `install.sh --local` and `install.ps1 -Local` refresh only the project's copies
  and say when a personal copy shadows the one they installed. `artifact.py new --type bug
  --verify` keeps the Verify line, `sprint plan --goal plan|design` no longer crashes, a project's TSD is judged stale against its own code, a close reads delivery
  history in one pass rather than once per unit, and `gate.py --release` gives each verifier five
  minutes rather than two.
- **The docs teach v6 only.** Help, references, templates, every script's `--help`, the README,
  the install guide and the white paper describe the loop above and name no retired step as live.
  The epic and story workflows name the command that seats each Three Amigos reviewer and the
  story cohesion review, the amigos go by their role labels, and the bug workflow records its
  criteria with `verify_ac.py run` before the move to Fixed.

## Upgrading from 5.1

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py"            # dry run: what it would change
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py" --apply    # carry the project across
```

**`migrate`** writes nothing. It lists what `--apply` would change and what it will leave to you,
so read it first.

**`migrate --apply`** removes every retired `.config.yaml` key with its children, keeping every
other byte, and strips the two retired `[check:]` tags (`review.two-role`,
`repair.mutation-evidence`) from the Definition of Ready and Done, keeping each criterion as a
human-judged line. On a project initialised by v5.1.0's `init`, with two retired keys
(`review.two_role_after`, `review.mutation_evidence`) and a `plan_review` block added, it removed
both tags, both keys, the `review:` block they left empty and the `plan_review` block, and
restamped the project version. On a v4-era project it also names the conformance cutoff, as
above.

Three things it leaves to you, and names:

- **Instruction files.** Each `AGENTS.md`, `CLAUDE.md`, DoR or DoD line naming a retired key or
  verb is reported by file and line, never rewritten. Edit those by judgement.
- **Your own scripts and CI.** `migrate` cannot see them. Search them for each verb and flag in
  the CHANGELOG inventory; `plan_review.py`, `repair_plan.py` and `validate.py warning-ratchet`
  are not reported by `migrate` at all.
- **The frozen review records** under `sdlc-studio/reviews/` are listed as history and left as
  written. Nothing needs deleting.

## Breaking changes

v6 retires 19 verbs, 20 flags, 11 config keys, 2 `[check:]` ids and 4 gate lanes, and changes 2
defaults (the CHANGELOG's inventory). Every one ships in 6.0.0 as it did in the candidate, each
entry with its before, after and migration, in
[the 6.0.0-rc.1 section of the CHANGELOG](../CHANGELOG.md#600---2026-09-26), under **Breaking**.

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
printed, nothing written (the CHANGELOG's inventory). The rest meet argparse's usage error or a
deleted script, and two `sprint close` flags are accepted and ignored; the inventory says which
for each.

## The soak

[The candidate's notes](release-notes-v6.0.0-rc.1.md) promised three things before this release. Each is reported here, with
what it found.

### The migration, rehearsed on two consuming projects

`migrate`, then `migrate --apply`, ran on copies of two real consuming projects that had not
moved since v4 or earlier: a v4.1 project of 687 stories, and a v2.4 project of 593 stories with
frozen sign-off records (the rehearsal record). The skill was the candidate with this release's
fixes to `migrate`, and the originals were never written. Every run exited 0 in under 10
seconds, neither dry run wrote a byte, a second run found nothing left to apply, and the
validation errors were the same before and after, so the upgrade added none (the rehearsal
record).

`--apply` wrote the version stamp and, on the v2.4 project, converted legacy Points or Effort to
a `Size:` line on 45 change requests and epics (the rehearsal record). What it left to a human is
the real work: seats and persona layout, requests never decomposed, instruction-file lines, and on
the v4.1 project a conformance cutoff that needs judgement. The gate was red on both projects
before the upgrade and stayed red after it. The rehearsal filed four Medium defects, all in what
`migrate`'s report names or omits (the rehearsal record). It counts 2 index drift items where the
gate's reconcile lane fails on 28 (the rehearsal record). It names no engagement-floor cutoff,
never gives an upgraded project the `.gitignore` that `init` writes, and proposes a conformance
cutoff that would also exempt the 98 units written after the project's own (the rehearsal
record). [The rehearsal record](upgrade-rehearsal-v6.md) gives, for each project, both commands
with their exit codes, what `--apply` changed, what it left to a human, and the gate before and
after.

### The eval scenarios, re-run against v6

Each scenario runs a fresh agent session on a prepared project and a fresh grader session on its
transcript. The candidate ran scenarios 01 to 08 (eval run `v6-rc1`); this release's code ran
the new scenario 09 and re-ran 06 (eval run `v6-main`). The release was gated on 09 (eval run
`v6-main`): a fresh agent running a lean sprint with the docs alone.

| Scenario | On the candidate (`v6-rc1`) | On 6.0.0's code (`v6-main`) |
| --- | --- | --- |
| `01-trigger-routing` | Pass | Not re-run |
| `02-greenfield-create` | Blocking behaviours pass; two advisory fails (eval run v6-rc1): the Three Amigos step and the story cohesion review were skipped. The workflows behind both are fixed in 6.0.0 | Not re-run |
| `03-generate-mode-gate` | Pass | Not re-run |
| `04-drift-reconcile` | Pass | Not re-run |
| `05-schema-v3-identity` | Pass | Not re-run |
| `06-independence-gate` | Fail: the worker approved its own fix, with no separate reviewer and no `critic.py brief`. It could have started a reviewer and did not (scenario 08's run on the candidate did); the candidate's bug-close guidance named none, and that guidance is fixed | Pass (eval run v6-main): one fresh final run on this release's skill and hardened fixture passed 11 of 11 behaviours, with no forbidden behaviour observed. One caveat: the worker relayed a trimmed brief to its reviewer, which the bug docs allow |
| `07-team-generation` | Pass, on a re-run after the scenario was corrected | Not re-run |
| `08-consult-objection-quota` | Pass, on a re-run after the scenario was corrected | Not re-run |
| `09-lean-sprint` | Not run: new in 6.0.0 | Pass (eval run v6-main): all seven blocking behaviours, from the plan to the stop for the signature. One advisory fail: the report's token actual reads NOT MEASURED |

Scenario 06's result for this release is one fresh final run on the final skill and fixture,
recorded once (eval run v6-main). Three earlier attempts at re-running it are discarded as
evidence and disclosed here (eval run v6-main). The first loaded the installed candidate beside the new skill, so
it did not measure the new skill alone. The second failed: the bug docs named no verifier (now
fixed), and the fixture's test could not fail on the reported bug, so the independent reviewer
rightly rejected a correct fix. The third passed every behaviour, but on a fixture hardened again
after it was graded. The two recorded runs also used different harnesses: the candidate's ran
under the operator's own configuration, this release's under a clean one holding only its
skill.

### The website's lean sprint, on the candidate

The project's own website, sdlc-studio.com, runs its sprint on the published candidate,
installed checksum-verified: seven units and 26 points towards "Maya and Jonah learn v6 from
sdlc-studio.com as it ships, and every command they copy runs." (the website's run record). It
is not closed. Two units remain: the landing page and the deploy of this release (the website's
run record). Its reviewers recorded 11 verdicts, 6 of
them REJECT, and of the 5 units rejected in their first round, 4 were approved in the second (the
website's verdict ledger). The fifth, the site's check for retired commands, was
carried at the cap as a bug, fixed with an explicit history marker after prose-based
exemptions leaked in three rounds, and approved (the website's verdict ledger). It found one
defect in the skill, fixed here, in a unit's review (the website's verdict ledger): root config
files dropped out of a unit's review scope. Preparing it on a scratch copy found two more, both
filed and fixed (listed under Sources): `init` recorded no project version, and
`install.sh --local` refreshed every personal copy. Its
deck review caught a slide claiming that recording a self-review is refused, where the candidate
records it with a warning; the slide was corrected.

## Known issues

Every open finding this release ships is listed by id on [the disclosure page](known-issues.md),
which `tools/known_issues.py write` generates from the bug corpus at the cut; the pre-push hook
refuses the tag while the page and the corpus disagree. The count below is written by the same
run, so it cannot drift from the page.

**v6.0.0 discloses 35 open defects: 35 Medium, 0 Low.**

Most are in the skill you run. Read from each finding's Affects line, 28 of the 35 are in code you
run and 7 are ones you will not meet in use (the known-issues page): 5 sit in this repository's own
commit and push hooks, release checks and eval harness (BG0712, BG0734, BG0754, BG0837, BG0839), 1
in a test helper (BG0838), and 1 in `gate.py`'s per-commit test selection, which a project meets
only if its own commit hook calls it (BG0752). None of them stops the lifecycle running (the
known-issues page). Where a first-week user can meet one:

- **The upgrade.** The four the migration rehearsal found (BG0842 to BG0845): `migrate`'s report
  undercounts index drift, names no engagement-floor cutoff, leaves out the `.gitignore` that
  `init` writes, and proposes a conformance cutoff that also exempts units written after the
  project's own adoption point.
- **The review.** The brief does not name the base ref it asks the reviewer to judge origin
  against (BG0827), and the bug-close guidance never says to hand the reviewer the brief whole
  (BG0817). A unit carried at the review cap is filed as a bug `sprint plan` cannot take until it
  is groomed (BG0829).
- **The close and its report.** ULID ids are printed without their hyphen, so the plan, brief and
  signed report name ids no file carries (BG0825); the scaffolded retro carries no run id
  (BG0826); and token capture reads NOT ATTRIBUTABLE on a project whose path holds `.` or `_`
  (BG0835).
- **`init guided`'s personas stage** seeds the legacy flat `personas.md`, which the persona
  registry and `sprint plan --serves` never read (BG0824).

The v6.0 bar is zero open Critical or High finding at the tag. The open Mediums ship under the
triage decisions D0273 and D0284 rather than a waiver per finding: D0273's first clause triages
every open Medium it does not name to v6.1, and D0284 files the remaining findings of the
last sprint's triage for v6.1.

One limit worth knowing before you rely on the report's cost: on a fresh project the report's
token actual can read NOT MEASURED, because nothing stamped the run's token meter when it opened,
as scenario 09 showed (eval run `v6-main`).

**Next:** the sprint loop as one command, and token capture that needs no stamping (D0280).

## Sources

Unit and decision ids behind each passage, in this repository unless marked.

| Passage | Ids |
| --- | --- |
| Figures | The back-to-basics review (`sdlc-studio/reviews/back-to-basics-review.md`); RPT0006-RPT0010 (`sdlc-studio/reports/`); `python3 tools/gate_timing.py estimate --suite boundary-push`, measured 2026-09-28 |
| A signed report checks in any clone | CR0599: US0959, US0960, BG0788, BG0795 |
| Version check and the upgrade digest | BG0790, US0952 |
| A fresh project records its version | BG0808 |
| Root config files stay in scope | BG0811 |
| The conformance cutoff | BG0785 |
| A first run starts where it should | BG0818 (landed under D0285 and D0286) |
| The close and the signature agree | BG0819, BG0820, BG0822, BG0823 (D0284) |
| The token forecast follows your newest runs | BG0798 |
| The report reads what was measured | BG0796, BG0797, BG0799, BG0800, BG0804 |
| Stale briefs and the bug close | BG0784, US0961, BG0812 |
| Other fixes | BG0809, BG0821, BG0802, BG0803, BG0806, BG0792, BG0786 |
| The docs | US0924, US0954, US0956, US0957, US0964, BG0814, BG0815, BG0816 |
| The migration rehearsal | US0962; findings BG0842, BG0843, BG0844, BG0845 |
| The eval re-run | US0963, US0965; rulings D0279, D0280, D0282, D0283; findings BG0812, BG0814, BG0815, BG0816, BG0817 |
| The website's sprint | Findings BG0811, and BG-01M3JFAX in the website's repository; found preparing it: BG0808, BG0809 |
| Known issues | D0273, D0284 |
