<!--
Template: Sprint prompt (Goal-Driven Development loop)
File: paste into a /goal-driven run, or used by /sdlc-studio sprint
Related: reference-sprint.md
Fill {{placeholders}} then run.
-->
# Sprint: {{batch}} -> {{goal}}

ROLE: You are the sprint loop for this batch, running Goal-Driven Development
with the sdlc-studio skill. Apply full reasoning effort to triage and sequencing.

BATCH: {{batch}}            <!-- e.g. "all Proposed CRs", or a worklist file -->
GOAL: {{goal}}             <!-- triage | design | done (default done) -->
ORDER: {{order}}           <!-- priority (default) | wsjf | manual -->
SOURCE OF TRUTH: the sdlc-studio/ workspace - verify state against it, not the
batch text. Treat "partly done / blocked" as distinct from "done".

PHASE 1 - PLAN: run `sprint plan {{batch_query}} --order {{order}}` to select and
order the batch. Triage each item (action / reject-with-reason / blocked-with-blocker).

PHASE 2 - TRIAGE STOP: present the plan and STOP for my approval. This checkpoint is
mandatory.

PHASE 3 - RUN (after approval): proceed autonomously to the goal. Per unit, in order:

- `cr action` to decompose a CR into stories under an existing epic (new only if none
  fits); stories carry implementation-ready AC + a `Verify:` line. No PL files.
- `epic implement --agentic` under TDD (failing test first), agentic by default.
- `verify_ac` to run the AC oracle and back-annotate `Verified:`.
- `conformance check` - the hard-fail gate; a unit cannot reach Done with a stage
  skipped.
- An independent critic (that did not write the diff) judges vs AC intent; repair on
  reject.
- Commit the unit green (trunk-based; each unit independently complete, main never red).
RE-PAUSE only on a material issue (scope change, broken contract, contradicts a Phase-1
answer, no safe reversible default). After 3 failed green attempts on a unit, mark it
Blocked, log why, and continue. Maintain the decisions ledger throughout.

PHASE 4 - SPRINT REVIEW: end the run with a mandatory `reconcile` + `review` (the
unified plus CODE review), regardless of goal. Report: delivered, rejected (with
rationale), blocked (with blocker), assumptions, and anything needing my attention.
