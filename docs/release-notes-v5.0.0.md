# SDLC Studio v5.0.0

**The release where the process stopped being advice and started being a gate.**

v4 gave you a lifecycle an agent could run: requirements, a plan, stories, tests, a review.
v5 is about the difference between a lifecycle that is *described* and one that *refuses*.
Everything below exists because a rule written down and not followed cost this project a
sprint, and the fix was never a longer document. It was a command that says no.

If you read one thing, read [What v5 refuses](#what-v5-refuses).

---

## What v5 is

SDLC Studio is an open [Agent Skill](https://agentskills.io): a plug-in that gives an AI
coding tool a full software development lifecycle. You describe what you want; the agent
writes the requirements, decomposes them, plans a sprint, builds, tests, reviews and closes
out, and every document stays in step with the code that was actually built.

One install works in Claude Code, Cursor, OpenAI Codex, Gemini CLI, opencode and GitHub
Copilot. See the [README](../README.md) to start from scratch.

---

## What v5 refuses

These are the gates that will stop work. They are the release, more than any feature is.

| Gate | What it refuses |
| --- | --- |
| `sprint plan` | a batch holding a unit with no `Affects` or `Points`, or one over the split threshold. An unsized backlog cannot be planned. |
| `transition -> Done` | a story whose executable acceptance criteria have not passed, or that is past the two-role threshold without both halves of its review |
| `transition -> Fixed` | a bug with no parseable verification depth |
| `sprint close` | units that no independent pass covers, and any unanswered item on the sprint checklist |
| `critic record` | a review verdict carrying no brief provenance, unless a recorded decision stands the rule down |
| `critic signoff` | a principal the authoring session controls. The author cannot approve the author, and cannot invent a delegate who can. |
| pre-commit and commit-msg hooks | any guard failure, a multi-id commit subject with no `Refs:` trailer, a collapsed test suite |

Each refusal names the rule it enforces, the line that broke it, and the command that fixes
it. A gate that only says `failed` is a gate people learn to route around.

---

## The four things that changed most

### 1. Review is two roles, and neither can be the author

A review is now an adversarial pass by a context that did not write the code, filing findings
as evidence, plus a reviewer of record who approves. They are never the same party, and the
tooling enforces it rather than asking.

- **Reviewers are briefed by the tool, never by hand.** `critic brief --unit <id> --seat
  engineering|product|qa` carries the seat's charter, the bounded diff scope, the acceptance
  criteria as law, and a claim-inventory pass. A hand-written prompt carries none of those and
  silently swaps a unit review for an unbounded one.
- **A review judges the unit's own diff.** Findings are classified by origin: a regression or
  a newly introduced defect blocks; anything already true of the tree is reported with its id
  and does not hold the gate. This is what made reviews discriminate instead of always failing.
- **The test plan is reviewed before the code is written.** Reviewing a test costs a fraction
  of reviewing an implementation, and it catches a class code review cannot: a criterion that
  is unobservable, or a discriminator that is simply wrong.
- **Review depth follows the unit's risk band**, and the coverage gate reads the tier. A light
  verdict does not cover a unit the band tiers full.

### 2. Evidence, not assertion

The recurring defect in this project was never weak code. It was a test that could not fail
on the thing its criterion claimed.

- **A criterion must name the production change that would redden it** before it is written,
  and grooming refuses one whose mutant cannot be named.
- **Mutation evidence is a lane**, configurable as `report`, `block` or `off`, and it is wired
  rather than described. A repair takes its mutatable surface from the diff, so a
  mis-declared `Affects` cannot open the gate.
- **No two acceptance criteria may share a verifier.** Two criteria pinned by one command are
  one criterion wearing two hats.
- **Vacuous verifiers are refused per runner family**: a selector that resolves to nothing, a
  substring check over source text that a comment would satisfy, an assertion that is monotone
  in the number of things added.

### 3. The gate became cheap enough to leave on

A guard whose cost is paid on every commit gets switched off. So the cost is measured and
budgeted.

- Tests are **selected by what the change can reach** instead of running everything.
- The unit suites are **skipped when the test-relevant surface has not moved** since the last
  green verdict.
- A **full-suite run is confined to boundaries**: push, release, and sprint close.
- The gate **reports its own seconds per lane against a declared budget**, every run.
- `reconcile detect` went from 22.3s to 1.3s by reading the corpus once per run.

### 4. A sprint closes on a derived record, not on memory

- **One compulsory checklist, and it is the sprint report.** Every row is derived from the
  tree where the tree holds the answer, because a checklist that asks an agent to retype
  delivered points gets filled in with what the agent remembers.
- The one row that is a judgement, the stop-ship ruling on each carried finding, is recorded
  as a judgement. An open finding with no ruling reads UNRULED. "We looked and carried it" and
  "nobody looked" must never render the same.
- `sprint close --dry-run` reports every refusal all seven steps would raise, in one pass,
  writing nothing.
- `sprint_report operator-summary` is the page an operator leads from: what shipped and who
  signed it, what was rejected and in what repair state, what is carried, what it cost, and
  the judgements most worth overturning. No channel carries anybody's prose into it.

---

## Also new

- **Guided `init`.** A greenfield project goes from empty directory to a written sprint plan
  without the operator knowing which command comes next. This path is rehearsed on every push
  and release boundary, so it reddens a build rather than rotting quietly.
- **`migrate`, one orchestrator.** Upgrading used to mean knowing to run `project upgrade`,
  `migrate_v3 sizing` and `reconcile`, then reading three reports. `migrate` runs them in
  order and emits one report split into what it upgraded deterministically and what needs a
  human. It never guesses a judgement.
- **Documentation generated from the corpus**: a command catalogue, an index, and reading
  guides, so a page cannot quietly stop describing the tool.
- **Every sprint verb documented as a runnable invocation**, with the verifier derived from
  the parser rather than from a list somebody maintains.
- **Repository audit** (`audit --profile repo`) and stakeholder panels with declared types.
- `autosprint` is now `sprint`. The old name still works.

---

## Upgrading from v4.1

**Your artefacts are safe.** Nothing rewrites your files without asking, sequential ids stay
valid, and every change to your artefacts arrives as an explicit question.

**What is not a drop-in is the gate.** Two things will refuse work on day one:

1. `sprint plan` refuses a backlog that predates the sizing fields. Groom the units you are
   about to plan, or record `sprint.breakdown: judgement` in `sdlc-studio/.config.yaml` as a
   deliberate decision. Omission is not an escape: an absent config blocks.
2. `gate.py` judges every story you have ever written unless you tell it where your history
   starts. Set `conformance: { adopt_after: <last pre-v5 id> }`. Ids at or below it are
   reported exempt and the gate judges forward only.

Both remedies, and the full upgrade sequence, are in
[docs/existing-users.md](existing-users.md). Those steps are executed against a fixture on
every boundary gate run, so if they stop working this project finds out before you do.

---

## Known issues

**v5.0.0 ships with 41 open defects: 40 Medium, 1 Low. Zero Critical, zero High.**

They are listed by id, with their reproductions, in [docs/known-issues.md](known-issues.md),
and each is triaged to v5.1.

This is a deliberate change of bar. The original bar was zero open bugs of any severity. It
was the maximum-rigour answer and it is defensible, but on this backlog's inflow it was not a
reachable one: the review finds roughly as many findings as a run closes, so the set does not
converge on a date. The bar is now zero open High, with everything else disclosed by id.

What that costs you is stated plainly. The residue is internal-consistency work: inert
detectors, verifiers that cannot fail on what they claim, counts that drift. They are real
defects and they are tracked. They are not experiences a consumer of the lifecycle meets.
What it buys you is a release you can read the whole truth about, which is the only kind
worth shipping from a tool that exists to stop people hiding things.

One item is worth naming here rather than leaving in the list. **58 executable acceptance
criteria, of 1,899 across 669 stories already at Done, fail when run.** They are stale
selectors rather than broken features: test methods renamed, test files deleted, the criterion
left pointing at a name that is gone. v5 ships the write-time guard that refuses a new one, and
puts the 35-minute verification lane on a schedule so the count is reported between releases
rather than never. The repairs are a v5.1 sweep with their own review, because a repair that
merely makes a criterion pass is worse than the red it replaced: it turns a visible stale
selector into an invisible vacuous one.

That number is worth distrusting on principle, and this project distrusts it in writing. It
was 106 on 2026-08-07 and 53 on 2026-08-09, and it was wrong in these records every time it
was carried forward instead of re-run. The scheduled lane exists because of that, not in spite
of it, and it reddens in both directions: a count above the baseline is a new dead selector
nobody guarded, and a count below it is a baseline that was never lowered when the criteria
were fixed.

---

## The full record

The per-unit changelog is [CHANGELOG.md](../CHANGELOG.md). It is long, and it is meant to be:
every unit that shipped, with its id, for anyone auditing a specific change. This page is the
part a person deciding whether to upgrade can read.

- [README](../README.md) - installation and quick start
- [docs/existing-users.md](existing-users.md) - the upgrade path in full
- [docs/known-issues.md](known-issues.md) - the 38 disclosed findings
- [docs/INSTALL.md](INSTALL.md) - step-by-step installation
