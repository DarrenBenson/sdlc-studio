# Why SDLC Studio

> The short version: disciplined software process has always worked and has almost never
> been sustained, because it spends the expensive currency - engineer attention. Agents move
> that cost into the cheap currency (tokens), and deterministic gates make the discipline
> enforced rather than aspirational. SDLC Studio is that trade, packaged: the proven
> SDLC discipline, run by the agent and policed by the tooling. This document lays out the argument, the
> evidence for it (including the unflattering parts), and the economics - each section
> deeper than the last. Read as far as you need.

## The problem is not knowledge, it is pressure

Every experienced engineering leader knows what good delivery looks like: clear
requirements, acceptance criteria written before code, traceability from intent to
implementation, independent review, a definition of done that means done. Almost no team
sustains it. Under deadline pressure the acceptance criteria thin out, the review becomes a
skim, the spec goes stale the week after it is written, and the test inventory is whatever
survived the sprint. This is not a failing of individuals - it is the predictable economics
of a process whose every step costs scarce human attention.

AI coding made this worse before it made it better. "Vibe coding" - prompt, generate, hope -
produces a demo fast, but the intent lives only in a chat that scrolls away, nothing checks
the result against what was asked, and by release nobody (the model included) can say what
done meant. The industry's first correction, spec-driven development, writes intent down
first - a real step up. But the spec is prose the agent produced and is then *trusted* to
honour, and nothing recomputes whether code and documents still agree ten changes later.
Trust-based process decays under pressure whether the executor is a human or a model.

SDLC Studio's bet is the third step: keep the specs and plans, and add a source of truth the
tooling **recomputes from the files and holds the agent to**. Status is derived from a
census, never asserted. Acceptance criteria carry executable `Verify:` lines that actually
run. A story cannot reach Done while its criteria are red (an operator override exists,
and is recorded - never silent). A review verdict whose reviewer id matches its author id
never clears the Done gate, so nobody signs off their own work. The discipline stops
depending on anyone (carbon or silicon) remembering it under pressure.

## The founding observation, reproduced in agents

The design thesis came from years of building and reforming engineering teams: humans under
pressure skip hygiene, so process survives only when it is infrastructure rather than
virtue. What we did not expect was how literally that observation would transfer.

In our controlled benchmark (below), the arm that had the full pipeline *installed and
available*, with judgement about when to use it, behaved exactly like the plain-AI baseline:
under effort pressure it skipped the process, implemented the ticket text directly, went
green on its own tests - and shipped the same requirements-interaction defect the baseline
shipped. The only arm that caught that defect class was the one where the planning pass was
**mandatory**. Agents, it turns out, are lazy under pressure in precisely the way engineers
are. Which is the whole argument for gates over goodwill, and why SDLC Studio's checks are
deterministic scripts the model cannot skip, not instructions it is asked to follow.

## The evidence

We hold positioning claims to the same standard the tool holds code to, so the evidence
below is labelled by what it is, includes the results that flatter us and the results that
do not, and links to the raw data. (In a category full of framework hype, publishing the
unflattering findings is itself the differentiator.)

### Production field results (operator-reported, uncontrolled)

Reported by the tool's author from his own production deliveries with SDLC Studio - real
scale and stakes, no counterfactual arm, so read these as experience reports rather than
measurements:

- A maintenance deliverable estimated at twelve months - thirty production websites -
  delivered in under seven days, with every action auditable and a full test inventory
  sufficient for CAB sign-off to production deployment.
- Production features estimated at a team of five for twenty weeks, delivered in under a
  week.
- This repository dogfoods the skill on itself: its features are delivered through its
  own pipeline, with the audit trail in the repo to inspect.

The common shape: one planning structure fanned out across many units of work, an audit
trail that a change-approval board would accept, and the elapsed-time compression coming
from agents executing a process that no human team could afford to run at that fidelity.

### Controlled benchmark (small n, adversarially reviewed, raw data published)

We built a measurement harness ([protocol](benchmarks/protocol-v2.md), pre-registered before
the runs so results could not be quietly reshaped) comparing three arms on fixture repos
with **held-back acceptance suites the agent never sees**: plain AI coding with a genuinely
good CLAUDE.md (independently reviewed against straw-manning), the pipeline available with
judgement, and the pipeline with a mandated planning pass. Findings so far, at n=1 per cell
([v1 report](benchmarks/2026-07-08-n1-spike.md),
[v2 report](benchmarks/2026-07-08-v2-respike.md)):

- **On small, well-specified tasks the pipeline adds nothing** - the baseline matched it.
  The tool's own scale-to-size doctrine says the same; run `profile: lite` there.
- **On a multi-file task whose existing spec silently interacted with the ticket, both
  unstructured arms shipped the same defect** (a quiet-hours rule the ticket never
  mentioned) and declared done on 16-17 green self-written tests. The held-back suite
  caught both.
- **The mandated-planning arm was the only arm with zero defect escapes**: forced to write
  acceptance criteria from the spec before code, it pinned the interacting requirements and
  its implementation passed the full hidden suite.
- **Auditability is measurable - and it graded us honestly.** An independent auditor agent
  answering maintainer questions from the finished workspace alone (with cited evidence
  mechanically validated - a cited test must fail against a seeded mutant to count) scored
  the harder fixture: mandated-planning arm 1.0, plain-AI baseline 0.8, and the
  judgement-scaled pipeline arm **last** at 0.6 - the arm that skipped its own process left
  the worst evidence trail. On the easier fixture all arms scored 1.0. Nothing in the
  scoring rewards the tool's own artifacts; the baseline could have scored 1.0 with good
  tests and docs.
- Honest caveats: n=1 per cell; fixtures were authored in-ecosystem (independently
  fairness-reviewed, and everything needed to pass is present in each visible workspace);
  planning-versus-review contributions are not yet disentangled. The pre-registered N=5 run
  will tighten or kill these findings, and we will publish it either way.

## The economics

Tokens are the wrong denominator; engineer time and defect cost are the right ones. Three
facts to price honestly:

1. **Per single ticket, the full pipeline costs more tokens** - 2.1 to 3.1 times the
   baseline in the n=1 calibration runs. If your unit of work is one small, well-specified change,
   that overhead buys little (see the lite profile).
2. **The overhead amortises with fan-out.** One planning structure driving many units is
   where the field results live: the pipeline's fixed costs (spec extraction, planning,
   gates) spread across every unit delivered under them, while the per-unit defect
   protection repeats.
3. **Model-tier routing attacks the variable cost.** The pipeline estimates each unit's
   difficulty from deterministic signals (blast-radius complexity, churn risk, scope,
   novelty, spec size) and recommends a model tier from a map you declare - trivial work
   runs on your cheapest model, hard work on your strongest, and the independent critic is
   never a smaller model than the author. In its first measured outing the router sent a
   trivial change to the smallest tier at a quarter of the reference cost, correctly, while
   a genuinely medium task stayed on the mid tier.

Against those costs, the comparison that matters: a defect that reaches production - or an
audit you cannot pass - is priced in engineer-days and trust, not tokens. The benchmark's
one measured escape-prevention was a bug both unstructured runs shipped confidently.

## Built for teams - human and agentic

The direction of travel is trunk-based delivery by small human teams directing larger
agentic ones, and the foundations for that are shipped: distributed artifact identity
(ULIDs, so concurrent agents in parallel worktrees never fight over sequential numbers, with
friendly aliases for humans), atomic index writes with advisory locking, typed authorship
(`raised_by`/`triaged_by`) with a separation-of-duties lint, and evidence-as-schema so
"proof" has a checkable shape. All of it is opt-in today (`schema_version: 3`) and becomes
the default in v4 once it has been proven in anger - the same publish-when-earned rule this
document follows.

## What we are still proving

- The pre-registered N=5 benchmark run (error bars instead of direction).
- Whether the value is *having* good acceptance criteria or *mechanically enforcing* them -
  a planned arm with ticket-grade ACs but no gates.
- Fan-out economics as a measurement rather than a field report.

## Try it in ten minutes

- **On an existing repo, zero setup:** `/sdlc-studio review generate` - a three-leg review
  of your actual codebase, findings filed as bugs and change requests, remediation-only on
  anything sensitive.
- **On a small project without the ceremony:** set `profile: lite` and the pipeline
  collapses to PRD, story, implement - promotable to the full discipline later.
- **From an idea:** "start a new project", answer the interview, and watch the spec, plan,
  code, tests and proof arrive as reviewable files.

The [README](../README.md) has the full quick start.
