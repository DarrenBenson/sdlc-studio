# RFC-0032: Close the learning loop: retros and lessons must drive review, audit and the backlog

> **Status:** Accepted
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

SDLC Studio records what it learns and then does not read it back. The registry holds 22
cross-project lessons and the workspace holds 23 retros; the write side is well gated (gate.py
blocks a sprint close without its retro, recomputes the lessons summary rather than trusting it,
and enforces the Review-by horizon). The read side barely exists.

**The cross-project registry has no automatic reader at all.** `sprint plan` does inject a lessons
digest, but `plan_digest` sources the **project tier** (`.local/lessons.md`, 6 entries here) - not
the LL registry. LL0001-LL0022 are reachable only by explicitly running `lessons recall`, which is
prose doctrine, and doctrine gets skipped. That is exactly the failure the project-tier digest was
built to fix; the cross-project tier never got the same treatment.

Nor does anything downstream read them. Review does not. Audit does not. And **no retro finding has
ever become a Bug or a CR** - `file_finding.py` is wired to review and never to retro, so a retro
finding is prose that nothing acts on. The gate checks the retro FILE exists, not that one thing in
it was dispositioned.

## The evidence: one bug class, three repos, already written down

The class is "reported a success it did not achieve" - LL0008, reinforced by LL0009 (silent
misleading failure outranks loud failure of the same scope).

| Repo | Incident | Symptom |
| --- | --- | --- |
| a runtime project | `L-RV-L1-001` | `set -e` under `ssh` did not propagate; **deploy reported success, container still on old code** |
| an infrastructure project | CR-0529 / BG-0384 | truncated secrets file; container ran on in-memory secrets so **nothing looked wrong** until the next deploy crash-looped the primary |
| sdlc-studio | BG0122 (today) | `install.sh` **exited 0, printed nothing, installed nothing** - the README's advertised invocation |

Three repos, one class, and it was in the registry the whole time. Nothing read it back, any of the
three times. The test gap in BG0122 is likewise already written down as LL0020 (a fixture that
supplies the thing under test proves nothing about production).

## The field evidence: teams route around us

An infrastructure project has **zero** sdlc-studio retros and a hand-rolled 750-line `docs/ops-lessons.md`
outside the workspace. Its header records why: the lessons accumulated in the agent's auto-memory
store until they tripped the "Large CLAUDE.md" warning, and had to be **evicted to a document no
tool reads**. Two things follow.

1. **Real lessons are heavier than our registry entries.** They are incident-anchored narrative,
   carry a tickable runbook, cite artefacts (CR/BG/RFC + file:line), and declare their own decay
   ("treat file:line citations as point-in-time").
2. **They are mostly operational** - deploy, incident, DR. Our registry is engineering/process; only
   LL0006 and LL0021 live in that space. The category with the most expensive failures has the
   least support, which is why it was written somewhere else.

A store that grows without bound gets evicted. That is not a hypothetical; it already happened.

### Five repos, surveyed

| Repo | Retros | Lessons store | What the evidence says |
| --- | --- | --- | --- |
| sdlc-studio-lens | **9** (8 carry a `## Lessons` section) | **none at all** - no `.local/lessons.md`, no `LESSONS-SUMMARY.md` | **1** CR/BG id referenced across all 9 retros. The ceremony runs every sprint; the plumbing behind it does not exist. |
| an infrastructure project | 0 | hand-rolled 750-line `docs/ops-lessons.md`, **outside** the workspace | A team that took lessons seriously built its own store because ours had no home for operational/incident lessons. It then outgrew auto-memory and was evicted. |
| a runtime project | 4 | `.local/lessons.md` | `L-RV-L1-001` is LL0008 again: deploy reported success, container still on old code. |
| homelab | 0 | none | No loop at all. |
| sdlc-studio | 23 | 22 LLs + summary | The richest store, and the cross-project tier still has **no automatic reader**. |

The pattern is consistent and it is not a motivation problem. Where the retro template prompts for
lessons, people write them (8 of 9 in lens). They are then not extracted into any store, and they
do not become work. The loop is broken at both ends, in production, today.

This is the inspect-and-adapt cycle retrospectives exist to create. We built inspect and skipped
adapt, and it has to hold for every consuming project, not just this repo.

## Design Options

- **Advisory recall: review and audit load bug-class lessons as lenses; findings are the agent's to weigh. Cheap, no new gate, but a lens that can be ignored tends to be.**
- **Gated disposition: every retro finding must be filed as a Bug/CR or explicitly declined with a reason, enforced by a new gate leg. Teeth, matching the repo's fail-loud doctrine, but it can block a close on judgement calls.**
- **Both, staged: recall first (read side, no teeth), disposition second (write side, with teeth) once the recall lens has proved its worth in practice.**

## Recommendation

Both: recall on the read side, disposition on the write side, with a live ranked summary as the
artefact that carries it. Decided below.

## Measured cost

Injecting the whole registry is cheap, which removes the premise behind most of the budget debate.

| Form | Tokens | Use |
| --- | --- | --- |
| 22 lessons, id + title (the form the plan already prints) | ~930 | injected at every read point |
| full recall digest (JSON, with tags) | ~1,955 | machine consumers |
| 22 lesson bodies in full | ~7,210 | never inject wholesale; pull on demand (~330 each) |

## Open Decisions

| # | Decision | Resolution | Status |
| --- | --- | --- | --- |
| D1 | Does the retro-finding disposition gate **block** a sprint close, or only warn? | **Block - but "declined, with a reason" counts as dispositioned.** The gate demands a recorded decision per finding, not a filed artefact. Declining is one keystroke and is equally green, so honesty costs exactly what noise costs and there is nothing to game. Untouched prose blocks. | Decided |
| D2 | Does recall inject the **`bug-class`** subset (12) or the **full set** (22)? | **Full set, compact.** At ~930 tokens the budget argument evaporates. A tag filter would silently exempt the process and deploy lessons (LL0004, LL0006, LL0021) from ever being seen - LL0013 in miniature: an enumeration exempts what it forgot. | Decided |
| D3 | What is the **budget**, and what happens when the registry outgrows it? | **One line per lesson injected; bodies pulled on demand.** Raise `PLAN_DIGEST_MAX` 20 -> 50. The tail stays **loud** (it already prints `+N more`, and the list is newest-first so the cap drops the oldest, not the recent). JSON stays uncapped. Unbounded growth is handled by decay (D6), not by silent truncation. | Decided |
| D4 | How does a **consuming project with an empty registry** bootstrap? | **It inherits the skill-tier registry as its day-one lens** - that is what "cross-project" means. A new project gets LL0008/LL0009/LL0020 from minute one; its own project-tier lessons accumulate on top and are promoted when they generalise. The loop stays silent when it has nothing to add, so it never reads as ceremony. | Decided |
| D5 | Is the loop **doctrine or opt-in**? | **Doctrine, with a config opt-out, and it goes in the benchmark.** Mirrors the engagement floor: mandated because judgement-gated process was *measured* to be skipped. The same claim here must be verified, not assumed - the claims register cuts both ways. | Decided |
| D6 | Is the summary a flat log, or **live and ranked**? | **Live and ranked.** A flat append-only log is what grew until an infrastructure project had to evict it. The summary ranks by **recurrence** (LL0008 has bitten 3x across 3 repos - it should have been top of the list before anyone touched `install.sh`), **recency**, and **structural-fix demotion** (once a guard makes the class impossible, the lesson stops shouting). The `Review-by` horizon already exists and is unused for ranking. Regenerated, never trusted - as the summary gate already does. | Decided |

## Consequences

- Operational/incident lessons need a home in the registry, or teams will keep writing
  `ops-lessons.md` outside it. The heavier shape real lessons take (narrative + runbook + artefact
  citations + declared decay) should inform the template.
- Ranking makes the summary a **live instrument** rather than a diary: what is biting us most,
  right now, in front of the agent at the moment it can act.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
