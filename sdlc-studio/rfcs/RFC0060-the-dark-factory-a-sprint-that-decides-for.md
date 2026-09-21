# RFC-0060: the dark factory: a sprint that decides for itself, and a goal that decides whether it worked

> **Status:** Accepted
> **Decomposed-into:** EP0258, EP0259
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

SDLC Studio should run as a **dark factory**: once a sprint starts, it finishes without a human on
the floor. The human agrees the goal and signs the report. Everything between is the line's own
business.

Two things block that today, and they are the same thing seen twice.

**The goal is a sentence, not a contract.** `--goal-verdict achieved` is a flag the author passes.
It demands a note, and the note is checked for being non-empty, but the verdict itself is asserted
by the party whose work is being judged. The proof is this project's own last run. Its goal was
`the backlog tells the truth: every stalled request and stale finding carries a dated ruling, and
the state that let them accumulate cannot rebuild`. It recorded **achieved**. That run had already
filed BG0722, at High, stating that the guard it built reports zero against the state it cleared -
which is the second clause, unmet, by the run's own evidence. Nothing compared the clause to the
claim, so nothing objected. A goal nothing can falsify is not a goal; it is a title.

The same run found the pattern one level down and filed it as BG0733: a unit's `Verified` line
reading `PARTIAL` is treated exactly like `yes`, so an honest self-report of a miss is laundered
into a green. At every level where this system asks itself how it did, the answer is accepted.

**The line stops for the wrong reasons.** RUN-01M2SPNS and RUN-01M306PY produced **fourteen
operator rulings in one session**, recorded as D0216 through D0229, plus three more on RFC0059.
Reviewed against the standard this RFC proposes, roughly four needed a human - release scope,
destroying four stories, the cost policy. The rest were inside the sprint's own remit and should
never have reached a person: how to slice a sweep, which cluster to rule first, whether to
re-derive a stale ceiling, where a fix belongs. The line stopped seventeen times and about
thirteen of those were the line asking permission to do its job.

The fix is not "ask fewer questions". It is to make explicit what a sprint may decide alone, give
the personas the authority to decide it, and reserve the human for the cases where a machine
genuinely cannot stand in - then hold the goal to a standard where the machine can tell whether it
was met.

## Context & Problem

A dark factory is not a factory without people. It is a factory where the people are not on the
floor. What makes that safe in manufacturing is **jidoka** - autonomation, automation with a human
touch - where a machine that detects an abnormality stops itself, and the andon signal makes the
stoppage visible. Andon is the lantern; jidoka is the discipline of stopping and fixing. The lights
can go out precisely because the line has a reliable way of noticing that something is wrong.

SDLC Studio already has an unusually good andon system. This session is the evidence: a
shell-hazard guard found the residue of a mangled edit inside a bug's prose; `verify-ratchet`
caught four stories sharing one verifier, so a regression in any would have failed all four with
none saying which; `revert-check` flagged a unit as green-after-revert and was right to; the
terminal gate found one added line no verifier executed. The line notices. That half is built.

What is missing is everything about **who answers the andon**. Today the answer is always the same
person, for every class of signal, whether the question is "which of two equivalent orderings
should the sweep use" or "shall I destroy four stories". The system has one escalation path and no
concept of what belongs on it.

Automotive autonomy has the vocabulary this needs. An **Operational Design Domain** is the precise
boundary inside which an automated system is designed to function; leaving the ODD is what triggers
fallback. Level 3 automation requires a fallback-ready human on standby; Level 4 performs its own
fallback within its ODD and needs no standby at all. The ask in this RFC is Level 4 **within a
sprint**: self-contained inside the goal's boundary, with a defined and safe stop when it reaches
the edge.

The 2026 consensus on agent oversight converges on the same shape from a different direction:
escalate on **reversibility, blast radius, data sensitivity and domain** rather than on a single
confidence number; let the reversible majority run with logging and no prompt; separate the
**verdict** an agent may reach from the **action** a human must approve. That separation is already
this project's PREPARE/SEAL split, which is why the split is the right foundation to build on
rather than a thing to redo.

## Goals / Non-Goals

**Goals**

1. A sprint goal that a machine can test, so `achieved` is derived from evidence rather than
   asserted by the author.
2. A written boundary - the sprint's ODD - naming what the line may decide alone.
3. Personas with the authority to decide inside that boundary, and a record of what they decided.
4. A stop rule: the small, named set of conditions that must wake the human, and a safe state to
   stop in when one fires.
5. A report that is worth signing on its own, because the signer was not in the room.

**Non-Goals**

- Removing the human. The two touchpoints - agree the goal, sign the report - are the product, not
  a cost to be minimised to zero.
- Autonomy outside a sprint. Planning, release and the backlog's shape stay human-led; this RFC is
  about the span between `sprint plan --write` and `sprint sign`.
- Replacing the gates. The andon system works. This is about who answers it.
- Making the agent more confident. Several decisions this session were improved by being questioned;
  the aim is to route them to a competent answerer, not to skip them.

## Design Options

The four moving parts - the goal, the boundary, the answerer, the stop rule - could each be built
several ways. These options are whole postures, not a menu per part.

### Option A - Trust the agent, drop the prompts

**Approach:** Leave the goal as prose. Instruct the agent to stop asking and decide, escalating only
when it judges a question important. No new machinery.
**Pros:** Zero build cost, available today, would have removed most of the seventeen stops.
**Cons:** The escalation rule lives in a prompt, so it decays under context pressure exactly when it
matters - late in a long run, which is when the hard decisions arrive. Worse, it does nothing for the
goal problem: the run that recorded `achieved` over its own contradicting High finding was not short
of confidence. It had too much. This option makes the confidence problem worse and the stopping
problem better, and the confidence problem is the more expensive one.
**Effort / risk:** Trivial effort, high risk.

### Option B - Human-on-the-loop with a decision queue

**Approach:** Keep every decision, but stop blocking on them. `sprint decision defer` already exists;
make deferral the default, let the run continue on a recorded assumption, and present the queue at
the close for ratification.
**Pros:** Nothing is lost; the human still sees every judgement; the run does not stall.
**Cons:** It moves the seventeen interruptions from the middle of the run to the end of it, which is
the one place this project has decided work must not accumulate - sign-off is meant to be a
signature, not a session. And an assumption ratified after the code is written is not a decision; it
is a formality attached to a fait accompli. This is the shape we have been drifting into, and the
operator's *"the sign should be the last thing needed"* is the objection to it.
**Effort / risk:** Low effort, and it institutionalises the problem.

### Option C - Machine-checkable goal, ODD, persona authority, andon cord

**Approach:** Build all four.

1. **The goal becomes a contract.** A goal is authored as a small set of numbered **clauses**, each
   carrying a **check** - a `Verify:` selector, a tool invocation with an expected verdict, or a
   named artefact predicate (`no open High against EP0257`). `sprint plan --write` refuses a goal
   whose clauses carry no checks, in the same way it already refuses a unit with no `Affects:`.
   `sprint close` **derives** the verdict by running them: every clause green is `achieved`, some
   green is `partial` with the failing clauses named, none is `missed`. The author's note survives as
   commentary. The flag stops being an input and becomes an output.
2. **The ODD is written at plan time.** The plan records what this sprint may decide alone: the
   files it may touch (already `Affects:`), the artefacts it may create, the statuses it may set, the
   budget it may spend, and the decision classes delegated to the bench. Everything outside is an ODD
   exit.
3. **Personas answer inside the ODD.** `persona_resolve.py panel` already picks a competent bench.
   A decision inside the ODD is routed to the seat that owns it, answered, and recorded as a
   **persona ruling** with its seat, its rationale and the alternative it rejected - the same record
   an operator ruling gets today, attributed to the bench instead of the human.
4. **The andon cord is the stop rule.** A named, short list of conditions halts the line and wakes
   the human, keyed on the industry criteria: irreversibility, blast radius outside the ODD, and the
   goal itself becoming unreachable. Everything else the line handles.

**Pros:** It answers the actual ask. The goal becomes something the sprint delivers against rather
than something written on it. The human's two touchpoints become real, because agreeing the goal now
means agreeing the checks that will judge it, and signing the report now means reading something the
signer could not have influenced. It also fixes a defect we can point at: RUN-01M306PY's second
clause had a check available - the guard's own output against the pre-sweep state - and nobody ran it.
**Cons:** Real build cost, four workstreams. Clause-authoring is a new skill and the first sprints
will write weak checks, the same way our first acceptance criteria passed their own mutants. Persona
rulings are only as good as the bench, and a persona that rubber-stamps is worse than an escalation
because it looks like governance.
**Effort / risk:** Roughly 30-40 points across four workstreams; medium risk, with the weak-check
failure mode the one to design against.

### Option D - Full autonomy: agent sets the goal too

**Approach:** Extend Option C so the agent proposes and accepts its own goal from the backlog, and
the human reviews only the report.
**Pros:** One touchpoint instead of two.
**Cons:** Out of scope by the operator's own framing, and wrong on the merits: choosing what to build
next is the decision with the largest blast radius in the system and the one a persona is least able
to stand in for. It is also the touchpoint the operator explicitly kept.
**Effort / risk:** Not recommended at any effort.

---

## Recommendation

**Option C**, built in the order below, with one deliberate sequencing call: **the goal contract
ships before the autonomy**.

The temptation is the reverse - autonomy is the felt pain, and clause-checking is the plumbing. But
an autonomous sprint whose goal cannot be falsified is a line running in the dark with no inspection
at the end, and the dark factory's whole safety argument is that the inspection is real. Ship the
contract first and the worst case is a sprint that still interrupts but can prove what it delivered.
Ship the autonomy first and the worst case is a sprint that decides everything for itself and grades
its own homework - which is, precisely, the state RUN-01M306PY's `achieved` describes.

One further recommendation, cheap and immediate: **make the escalation itself measurable**. Every
ruling - operator or persona - records which it was, and the report prints both counts. The number
this RFC is trying to move is "operator rulings per sprint", currently about fourteen; it cannot be
managed while it is only visible by reading a decisions log after the fact.

## Open Decisions

> Six of seven were ruled by the operator on 2026-09-21 and are recorded in the decisions log.
> D6 remains open and blocks nothing in the first two workstreams.

| # | Decision | Ruling | Recorded |
| --- | --- | --- | --- |
| D1 | What may a goal clause's check be? | All three shapes: a `Verify:` selector, a named tool invocation with an expected verdict, and a persona-judged predicate - the third guarded (see below) | D0230 |
| D2 | Derived verdict versus the author's note | Derived wins; the disagreement is filed as a finding naming both. The close is not refused | D0231 |
| D3 | Is a persona ruling binding? | Binding inside the ODD, advisory at its edge - so a seat can never ratify an ODD exit | D0232 |
| D4 | What is on the andon cord? | Exactly two conditions: an irreversible action (push, tag, release, delete) and an ODD exit | D0233 |
| D5 | Is there an escalation budget? | Not yet. The count is measured and reported every run; the budget is set at the second sprint on that number | D0234 |
| D6 | Who signs when the human is away for days? | Open | - |
| D7 | Do persona rulings need author-independence? | No. The seat, the rationale and the rejected alternative are the audit trail | D0235 |

**The guard on D1.** A persona-judged predicate is the shape closest to today's `--goal-verdict`,
and adopting it without a condition would reproduce the failure with extra steps. So the third shape
carries two obligations the other two do not: the clause must name **at plan time** what would
falsify it, and the ruling must record the alternative it rejected. A persona-judged clause with
neither is a finding, not a check. It earns its place because RUN-01M306PY's second clause - *the
state that let them accumulate cannot rebuild* - has no expressible selector, and that is exactly
the clause that went unchecked.

**What D4 leaves to the line.** A gate refusing, a High finding filed mid-run, a hard design call, a
budget overrun: none of these stop the line. The cord is keyed on reversibility and blast radius, not
on how difficult the decision feels, and PREPARE/SEAL remains the human boundary rather than a second
one being invented beside it.

---

## Architecture Impact

| Layer / System | Impact | Change Type |
| --- | --- | --- |
| `sprint plan` | Accepts and validates goal clauses with checks; refuses a goal with none; records the ODD | Enhancement |
| `sprint.py` run state | New records: goal clauses, per-clause results, ODD, persona rulings, escalation counts | Enhancement |
| `sprint close` (PREPARE) | Runs the clause checks and derives the verdict; `--goal-verdict` becomes an override that must be justified, not the source | Replacement |
| `sprint_report.py` | New sections: goal clauses with per-clause verdict and evidence; operator vs persona ruling counts; ODD exits | Enhancement |
| `persona_resolve.py` / `consult` | New `rule` verb: route a decision to the owning seat, return a recorded ruling | New |
| `sprint decision` | Gains a class (`persona` / `operator`) and an andon-cord test that decides which path a decision takes | Enhancement |
| Gates | The andon cord is a new blocking condition on the run, not on a commit; no per-commit cost | New |
| `critic.py` | `goal_panel` and `judge_defects_against_goal` become reachable from the close rather than only from `close_goal_judgement` | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Clauses are written weakly, so checks pass vacuously | High | High - reproduces today's failure with more ceremony | Apply the existing falsifiability discipline: name the mutant first. A clause whose check cannot fail is refused by the same machinery that refuses a vacuous verifier |
| Personas rubber-stamp, and governance becomes theatre | Medium | High | Every ruling records the rejected alternative; a ruling with none is a finding. D7 may add an independence gate |
| The line runs long without a human and burns the budget on the wrong thing | Medium | Medium | Budget is an ODD dimension and exceeding it is on the andon cord (D4) |
| The andon cord is set too tight and nothing changes | Medium | Low | Measured directly - operator rulings per sprint is the metric, reported every run |
| The andon cord is set too loose and something irreversible happens unattended | Low | High | Irreversibility is the first cord condition; push, tag, release and delete stay human-authorised, which is PREPARE/SEAL's existing line |
| The goal contract makes planning heavier, and goals get vaguer to dodge it | Medium | Medium | The refusal names the missing check and suggests one from the batch's `Verify:` lines, so the cheap path is a real clause rather than a vague goal |
| Derived verdicts are wrong because a check is flaky | Low | Medium | A check that cannot be run is `unknown`, never green; an `unknown` clause degrades the verdict to `partial` and is named in the report |

---

## Phased Plan / Workstreams

| WS | Workstream | Repo | Becomes | Depends on |
| --- | --- | --- | --- | --- |
| WS1 | Goal as contract: clause authoring, plan-time refusal, close-time derivation, report section | sdlc-studio | CR (TBD) | - |
| WS2 | The ODD: recorded at plan time, checked at decision time, exits reported | sdlc-studio | CR (TBD) | WS1 |
| WS3 | Persona authority: `rule` verb, recorded rulings, ruling-vs-escalation classification and counts | sdlc-studio | CR (TBD) | WS2 |
| WS4 | The andon cord: the stop conditions, the safe-stop state, the escalation budget | sdlc-studio | CR (TBD) | WS2, WS3 |

WS1 is the one that must ship first and the one that carries value alone: a sprint that still asks
fourteen questions but proves its goal is strictly better than today. WS3 and WS4 are the pair that
actually turns the lights off, and neither is safe without WS1's inspection at the end.

**Sequencing against current work (D0236).** D0228 committed the next run to the five open High
findings - BG0715, BG0719, BG0722, BG0730, BG0733 - four of which are the close and the report being
honest about themselves. That is WS1's foundation by another name, so the next run takes both rather
than fixing the honesty defects through code WS1 would then rewrite. WS2 joins it under one
condition: it must have a consumer on the day it lands. Plan-time refusal therefore also rejects a
goal clause that reaches outside the declared ODD, so the boundary is load-bearing immediately
instead of lying dormant until WS3 arrives to read it.

That makes the next run the largest this project has planned. The mitigation is that the surface is
narrow even where the point count is not - `sprint.py`, `sprint_report.py`, the close and the plan -
and four of the five bugs are already changes to the code WS1 extends.

---

## Decision

**Outcome:** Accepted - Option C, four workstreams, six of seven open decisions ruled (D0230-D0235).

**Rationale:** The two measurements this RFC rests on are the project's own: a goal recorded
`achieved` over a High finding that contradicts it, and fourteen operator rulings in a single
session of which about four needed a human. Neither is fixed by asking the agent to try harder.
The sequencing stands as recommended - the goal contract ships before the autonomy - because an
unattended line with no real inspection at the end is the failure this RFC is named after.

**Spawned CRs:** TBD - refined alongside the five open Highs under D0236.

---

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| Bug | BG0722 | The unruled lens catches the request nobody closed, not the one everybody abandoned | Open | The evidence that a goal verdict goes unchecked |
| Bug | BG0733 | A Verified line reading PARTIAL is treated exactly like yes | Open | A self-reported miss laundered green - WS1's problem in miniature |
| Bug | BG0719 | The report does not disclose the waivers that permitted the seal | Open | The signer's inspection surface is incomplete |
| Bug | BG0715 | The close attributes findings by the last word of a prose stamp | Open | WS1 foundation |
| Bug | BG0730 | A stop-ship ruling is never re-derived against its finding's status | Open | WS4 foundation - a stop condition that cannot clear |
| Decision | D0213 | No unit is terminal until SEAL | Accepted | The verdict-vs-action separation this RFC builds on |
| Decision | D0228 | The next run takes the five open Highs | Accepted | Sequencing constraint on WS1 |
| Story | US0832 | The PREPARE/SEAL split | Done | The existing human-approval boundary |
| Report | RPT0003 | Sprint report, RUN-01M306PY | Signed | The run whose `achieved` this RFC disputes |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | agent | Drafted: problem, four options, Option C recommended, 7 open decisions, 4 workstreams |
| 2026-09-21 | operator | Accepted. D1-D5 and D7 ruled (D0230-D0235); D6 left open. WS1+WS2 folded into the five-Highs run (D0236) |
