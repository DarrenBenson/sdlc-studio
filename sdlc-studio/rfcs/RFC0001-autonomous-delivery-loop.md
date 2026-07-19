# RFC-0001: Autonomous Delivery Loop for SDLC Studio

> **Status:** Accepted
> **Priority:** High
> **Author:** Darren Benson
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill (SKILL.md, reference-*, templates/automation, scripts)
> **Related:** reference-project.md, reference-outputs.md, reference-reconcile.md, reference-verify.md, reference-agentic-lessons.md
> **Supersedes / Superseded by:** –

## Summary

Promote the hand-driven "tranche orchestrator" prompt (currently a copied
`coding-prompts-2.txt`, run under Claude Code `/goal`) into a first-class
SDLC Studio capability: a documented **outer control loop** that drives the
existing pipeline (plan → implement → verify → reconcile → review) autonomously
to a Definition of Done, with the three deterministic guardrails the
loop-engineering consensus says the model cannot supply itself – a stall/iteration
cap, a repetition breaker, and an independent completion oracle.

## Context & Problem

SDLC Studio already has the inner machinery a fully agentic loop needs: a
machine-checkable acceptance oracle (`verify_ac.py` + executable AC Verify
lines), drift detection (`reconcile`), wave orchestration
(`epic/project implement --agentic`), and resumable state (`project-state.json`).
What it lacks is the **outer policy layer** that decides when to retry, when to
escalate, when to stop, and how to keep the run honest.

That layer currently lives outside the skill, as a `.txt` prompt the operator
pastes each tranche and then loops with `/goal`. Consequences:

- The loop's guardrails are left to model discretion. The 2026 loop-engineering
  consensus is that an LLM cannot reliably self-judge "am I done" or "am I
  stuck"; these need external, deterministic enforcement (hard iteration cap,
  tool-call repetition detector, domain-aware completion check).
- The decisions ledger lives in context, so compaction across a long `/goal`
  run loses earlier rulings and the agent re-litigates them. Ralph-style loops
  survive precisely because they use the filesystem as memory.
- Completion signals (tests, reconcile, review) are produced by the same agent
  that wants to finish. Under finite evaluation, an optimiser systematically
  under-invests in quality dimensions the oracle does not measure (spec gaming
  as a structural equilibrium, not a bug), so a same-author oracle is gameable.
- The policy is unversioned and unimprovable: fixes to one tranche's prompt do
  not propagate.

The operator has already settled the central design choice in practice: **stop
once after triage for approval, then run autonomously, re-pausing only on a
material issue.** This RFC captures that as the default and fills the gaps.

## Goals / Non-Goals

**Goals**

- Make the outer loop a versioned, improvable skill asset, not a pasted prompt.
- Bake in the three deterministic guardrails (cap, repetition breaker, oracle).
- Persist the decisions ledger to disk so it survives compaction and resume.
- Add an independent verification step that resists spec gaming.
- Keep the operator's chosen autonomy ceiling as the default; make it tunable.
- **Use the SDLC Studio commands end to end** - the loop drives `cr action`
  (decompose every CR into stories under an existing or new epic), then per story
  `code plan` / `code implement` under TDD, `verify`, `reconcile`, `review`. It
  does not bypass the pipeline with bespoke edits.
- TDD and agentic execution are the defaults.
- A **deterministic lifecycle-conformance check** confirms each unit went through
  the required stages (decomposed, AC present, tested under TDD, verified,
  reconciled, reviewed), so "everything was used" is enforced, not assumed.
- Every run ends with a mandatory **closing reconcile + review (the sprint
  review)** - drift fixed and the unified plus CODE review run - regardless of
  `--goal`; this also produces the conformance `reviewed` signal. The retro writes
  durable lessons to `sdlc-studio/retros/` (a general capability, CR0018), read at
  the start of the next sprint - a learning loop.

**Non-Goals**

- Replacing `verify_ac`, `reconcile`, or the wave engine. This wraps them.
- Removing the human triage gate. Phase 2 approval stays mandatory.
- Mandating trunk-based / no-branches workflow for all users (it is one
  supported mode, see D6).
- A general-purpose multi-agent framework. Scope is SDLC delivery loops.

---

## Design Options

### Option A – Documented policy + parameterised prompt template

**Approach:** Add `reference-autonomous-loop.md` (the policy: ceiling, guardrails,
DoD, escalation rules) and `templates/automation/autonomous-loop-prompt.md` (the
operator's prompt, parameterised with `{{worklist}}`, `{{source_of_truth}}`,
`{{autonomy_ceiling}}`). The operator still drives with `/goal`; guardrails are
instructed, not enforced in code.
**Pros:** Ships immediately; zero code risk; captures the asset and the lessons;
fully tool-portable (no script dependency).
**Cons:** Guardrails remain model-instructed, so the cap/repetition-breaker are
only as reliable as the model's adherence. No hard stop on runaway token burn.
**Effort / risk:** Low / low.

### Option B – Policy + `project implement --autonomous` flag

**Approach:** Encode the outer loop in the skill workflow as a new mode of
`project implement`. The skill runs the cycle: promote/generate upstream
artifacts, run a wave, run `verify_ac` + tests, on failure feed the specific
failures into a bounded repair sub-agent, escalate on stall, run an independent
review, stop at DoD. Decisions ledger written to a file each iteration.
**Pros:** The loop is the skill's behaviour, not a prompt; consistent every run;
the repair/critic sub-agents are structured, not ad hoc.
**Cons:** Larger surface; needs careful resume semantics; more to test.
**Effort / risk:** Medium / medium.

### Option C – Deterministic loop guardrails in scripts (Stop-Hook equivalent)

**Approach:** Move the three mechanisms into Python the model cannot skip: a
completion gate that exits non-zero unless all AC `Verified: yes` + suite green +
`reconcile` clean (the domain-aware check), an iteration/repetition ledger that
quarantines a unit after N same-signature failures, and a token/time budget.
Wire as a Claude Code Stop Hook so the loop physically cannot terminate early or
thrash.
**Pros:** Guardrails are deterministic and audit-logged; matches the
loop-engineering "external mechanisms" requirement exactly; hardest to game.
**Cons:** Couples the skill to a hook/harness feature; most engineering;
portability caveats across tools that lack Stop Hooks.
**Effort / risk:** High / medium.

---

## Recommendation

**Phased: A now, then B, with C's two deterministic mechanisms (stall/quarantine
ledger and the completion gate) grafted in where model discretion proves
unreliable.** A captures the asset and the operator's proven ceiling at near-zero
risk and is independently useful. B makes the loop the skill's own behaviour. C's
determinism is reserved for the two judgements the research says the model should
not own: "am I done" and "am I stuck". Sequencing also lets the operator triage
this RFC through the very loop it describes.

## Open Decisions

> The unsettled cores. Each must resolve before its dependent workstream is built.
>
> **Resolved on acceptance (2026-06-20) - see the Decision section.**

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Default autonomy ceiling | (a) stop-after-triage then autonomous w/ re-pause **[leaning]** · (b) pause every gate · (c) full overnight, stop only on terminal failure | Operator | Operator call; A leaning matches current practice | Closed: (a) stop once after triage for approval, then run autonomously, re-pausing only on a material issue |
| D2 | Stall-cap aggressiveness + quarantine | N failed green attempts per unit before quarantine (e.g. 3); on stall: re-decompose the story vs. mark Blocked + continue vs. stop the run | Operator + design | Spike on a real tranche; measure thrash vs. abandonment | Closed: quarantine-and-continue at 3 failed green attempts - the unit is marked Blocked and the run carries on (`loop_guard.py`, exit 3) |
| D3 | Independent oracle strength | (a) separate review sub-agent that did not write the diff, judging vs. AC intent **[min]** · (b) + adversarial/mutation checks · (c) + diverse independent verifiers | Design | Threat-model against spec-gaming equilibrium; cost/benefit | Closed: (b) an independent non-author critic judging each diff against AC intent, plus adversarial/mutation checks (`critic.py`) |
| D4 | Decisions ledger form | (a) new artifact type under `sdlc-studio/` (e.g. `decisions/DLNNNN`) · (b) extend `project-state.json` · (c) plain append-only `sdlc-studio/.local/decisions.log` | Design | Pick by need for traceability vs. simplicity; reconcile impact | Closed: (a) a committed, append-only per-tranche ledger at `sdlc-studio/decisions/<tranche>.md` (`ledger.py`) |
| D5 | Where guardrails live | model-instructed (Option A) vs. deterministic script/Stop-Hook (Option C) per guardrail | Design | Decide per guardrail; cap + completion-gate lean deterministic | Closed: per guardrail - iteration cap, repetition-breaker and completion gate are deterministic scripts; autonomy ceiling and escalation stay model-instructed |
| D6 | Commit strategy coupling | autonomous mode assumes trunk-based green-gate vs. honours existing `--commit-strategy` (per-wave/epic/project) | Operator | Operator call; keep trunk-based as one mode, not the only one | Closed: trunk-based green-gate as the operator's default, honouring the existing `--commit-strategy` (per-wave/per-epic/per-project) for other workflows |
| D7 | Are implementation-plan (PL) files required per story? | drop (opt-in `--with-plans` for sequential/audit-sensitive work) | Operator | **Resolved by real-world evidence**: consuming repo B + consuming repo A shipped ~900 Done stories with 3 PL files total (~0.27%) | Resolved |

---

## Architecture Impact

| Layer / System | Impact | Change Type |
| --- | --- | --- |
| `reference-autonomous-loop.md` | New policy reference (ceiling, guardrails, DoD, escalation) | New |
| `templates/automation/` | Parameterised loop prompt template | New |
| `project implement` (reference-project.md) | New `--autonomous` mode wrapping the wave engine | Enhancement |
| Decisions ledger | New persisted artifact or `project-state.json` extension | New / Enhancement |
| `reconcile` / review | Independent (non-author) critic pass added to the cycle | Enhancement |
| `scripts/` | Optional completion-gate + stall/quarantine ledger helper | New (Option C) |
| SKILL.md / help | Router + help entries for the new mode | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Spec gaming – loop satisfies literal AC, neglects unmeasured quality | High | High | Independent non-author critic (D3); keep AC quality gates; diverse oracles |
| Runaway token/time burn on an unreachable DoD | Medium | High | Hard iteration cap + budget; quarantine-and-continue converts "stuck" to "Blocked" terminal state (D2) |
| Decisions lost to context compaction on long runs | High | Medium | Persist ledger to disk every iteration (D4) |
| Trunk-based green-gate serialises parallel sub-agents into a bottleneck | Medium | Medium | Integrate-and-test between commits; or honour per-wave strategy (D6) |
| Stale source-of-truth (worklist vs reality, cross-repo IDs) | Medium | Medium | Mandatory `git fetch` + `reconcile --remote` at loop start (the stale-checkout lesson) |
| Guardrails ignored because model-instructed only | Medium | High | Move cap + completion-gate to deterministic script/Stop-Hook (Option C, D5) |

---

## Persona Consultation

> Consulted 2026-06-20 (RV0001 action U1). Positions are inferred from
> `sdlc-studio/personas.md` against this design and fold into the Open Decisions.

**Orchestrator / Operator (primary).** Endorses the default autonomy ceiling
(D1a: stop after triage, then autonomous with re-pause) - it matches the proven
`coding-prompts-2.txt` practice. On D2 favours quarantine-and-continue over
stop-the-run, so an overnight tranche never wakes them to a fully blocked repo,
but insists a quarantined unit surfaces as **Blocked** in `status`, never
silently dropped. Wants `reconcile --verify` kept as the release gate so the
loop's "Done" still means tests passed.

**Consuming-project Developer.** Flags D5 as the adoption risk: Option C (a
Claude Code Stop-Hook) couples the loop to one harness and breaks
tool-neutrality. Wants Option A (documented policy + portable prompt) to stay a
fully functional path under any `AGENTS.md`-compatible tool, with deterministic
guardrails offered as an enhancement, not a precondition. No new third-party
dependency for the ledger (D4) - plain files over anything needing a service.

**AI Agent Executing the Skill.** Strongly supports D4 (persist the decisions
ledger to disk): re-reading a file after a context reset is exactly how it
recovers orientation today via `reviews/LATEST.md`; an in-context ledger is lost
to compaction. Wants the completion oracle unambiguous (D3) and the stall signal
explicit (D2) so it is never left guessing whether to retry or escalate, and
prefers guardrails that return structured JSON like the other helpers.

**Skill Maintainer.** Cautions on Options B and C (D5): every line of loop logic
is new test surface, and the markdown command behaviours are already the main
untested gap (per the TSD). Wants the deterministic guardrails delivered as a
unit-tested `scripts/` helper, not model-instructed prose, precisely so they are
verifiable - and the new mode to keep `SKILL.md` lean (delegating to
`reference-autonomous-loop.md`) within the `check_budgets.py` line budgets.

**Outcome.** The four converge on the phased recommendation: keep the portable
Option A path, persist the ledger to disk, make guardrails verifiable scripts not
prose, and default to quarantine-and-continue with a visible Blocked state. These
are recorded as the leaning options in D1-D5.

---

## Phased Plan / Workstreams

> Each workstream becomes a CR referencing this RFC once accepted.

| WS | Workstream | Repo | Becomes | Depends on |
| --- | --- | --- | --- | --- |
| WS1 | `reference-autonomous-loop.md` policy doc (ceiling, guardrails, DoD, escalation) | sdlc-studio | CR (TBD) | D1, D2 |
| WS2 | Parameterised loop prompt template + SKILL.md/help wiring | sdlc-studio | CR (TBD) | WS1 |
| WS3 | Stall-cap + quarantine semantics (deterministic ledger) | sdlc-studio | CR (TBD) | D2, D5 |
| WS4 | Independent (non-author) critic pass wired into verify/reconcile | sdlc-studio | CR (TBD) | D3 |
| WS5 | Persisted decisions ledger (artifact + schema + reconcile awareness) | sdlc-studio | CR (TBD) | D4 |
| WS6 | `project implement --autonomous` mode wiring the above | sdlc-studio | CR (TBD) | WS1-WS5 |
| WS7 | Lifecycle-conformance check (deterministic): per CR/tranche, assert it was decomposed into stories with AC, implemented under TDD (test precedes/accompanies impl), verified (`verify_ac`), reconciled clean, and reviewed; flag any skipped stage | sdlc-studio | CR (TBD) | D7 |

---

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** Accepted (2026-06-20).

**Resolved decisions:**

- **D1 Autonomy ceiling:** stop once after triage for approval, then run
  autonomously, re-pausing only on a material issue (scope change, broken
  contract, no safe reversible default). Matches the proven `coding-prompts-2.txt`.
- **D2 Stall handling:** quarantine-and-continue. After 3 failed green attempts a
  unit is marked **Blocked**, logged, and skipped; the run continues and the
  blocked unit surfaces in `status`.
- **D3 Verify strength:** an independent non-author critic judges each unit's diff
  against AC intent, plus adversarial/mutation checks (does the test fail if the
  behaviour breaks).
- **D4 Decisions ledger:** a committed, append-only per-tranche ledger - traceable
  and survives context compaction.
- **D5 Guardrails:** the iteration cap, repetition-breaker and completion-gate are
  deterministic scripts the model cannot skip; the autonomy ceiling and escalation
  policy stay model-instructed.
- **D6 Commit strategy:** trunk-based green-gate by default (the operator's
  workflow); honours `--commit-strategy` for others.

**Rationale:** keep the proven manual loop's ergonomics, but move the three
judgements the model cannot own - am-I-done, am-I-stuck, is-this-gamed - onto
deterministic scripts and an independent critic. Phased delivery: Option A (policy
doc + prompt template) ships first for tool-neutrality, then the deterministic
guardrails (D5) and the critic (D3).

**Spawned CRs:** the six workstreams (WS1-WS6 in the Phased Plan) remain tracked
in this RFC and are spawned/actioned as each phase begins (WS1+WS2 first). The RFC
stays the living design home they reference.

**Process conformance (added 2026-06-20):** the loop must use the skill's own
commands throughout - a CR is always decomposed via `cr action` into stories under
an epic, TDD and agentic execution are the defaults, and a new deterministic
**lifecycle-conformance check** (WS7) gates each unit so no stage is silently
skipped. It joins the cap / repetition-breaker / completion-oracle as the fourth
deterministic guardrail. Whether PL plan files stay required is tracked as D7
(leaning: optional in agentic mode, since the agent prompt serves as the plan).

**Conformance + decomposition decisions (2026-06-20):** the lifecycle-conformance
check (WS7) **hard-fails** a unit on any skipped required stage - it cannot reach
Done until the gap is closed. TDD is checked as **test-exists-and-maps-to-story**
(deterministic; not git-ordering). `cr action` places stories in the
**best-matching existing epic, creating a new epic only when none fits**. D7
(whether PL plan files stay required) is **deferred pending a plan-value review** (does a capable model actually need
them, or are they a human or audit artifact, not a model crutch?). The conformance check does not demand a PL in agentic mode.

**D7 resolved (2026-06-20):** drop PL files in the autonomous loop; expose an
opt-in `--with-plans` for sequential or audit-sensitive work. Evidence: two real
SDLC Studio deliveries (consuming repo B, consuming repo A) shipped ~900 Done stories with
**3 PL files between them (~0.27%)** under full TDD/verify/review discipline - so
plans add no value in practice for a capable model. The edge-case discovery a PL
used to force is relocated to the **story Ready criteria** (already mandated), so
nothing is lost; the conformance check enforces it at the story level.

---

## Delivery status

**Phase 1 delivered (2026-06-20).** The command is `autosprint <batch> --goal
triage|design|done [--order priority|wsjf|manual]`, implementing **Goal-Driven
Development** (TDD -> BDD -> Eval-Driven -> Goal-Driven). Shipped, each TDD'd and
dogfooded: `conformance.py` (WS7 hard-fail gate), `autosprint.py plan` (WS2
batch/order), `reference-autosprint.md` + `help/autosprint.md` + the prompt
template + SKILL routing, and the sprint-retro closing gate (CR0018). A measured
run delivered CR0002 end to end (decompose -> TDD -> verify -> critic) for ~164K
tokens, critic-approved - evidence the design works.

**Phase 2 delivered (2026-06-20, CR0020).** The remaining deterministic guardrails
and the persisted ledger now ship, each TDD'd and critic-approved, driven by
autosprint over itself: `ledger.py` (D4/WS5 - committed append-only per-tranche
decisions ledger), `loop_guard.py` (D5/D2/WS3 - iteration cap, repetition-breaker,
completion oracle; quarantine = Blocked-and-continue, exit 3), and the documented
`--autonomous` mode (WS6) tying them plus the independent critic (D3/WS4) and the
unconditional closing reconcile + review. The conformance check gated the delivery
(11/11 conformant) - the loop self-hosting. WS1/WS2 ship as `reference-autosprint.md`.

---

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| Reference | – | reference-project.md (project implement) | Live | extends |
| Reference | – | reference-verify.md (verify_ac oracle) | Live | depends on |
| Reference | – | reference-agentic-lessons.md | Live | informs |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | RFC drafted |
| 2026-06-20 | Darren Benson | Persona consultation added (RV0001 action U1) |
| 2026-06-20 | Autosprint (CR0020) | Phase 2 delivered: ledger, loop guardrails, --autonomous wiring |
| 2026-07-19 | sdlc-studio | Decision rows closed with what shipped |
