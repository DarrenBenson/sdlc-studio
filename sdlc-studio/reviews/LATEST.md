# Unified Review - 2026-07-16 (close) - the un-skippable sprint close-down (RFC0042 -> EP0046)

> **Review type:** Sprint-close review (required by the `--require-review` gate)
> **Reviewer:** sdlc-studio; agent; v1 (delivery critiqued independently by the Dani Okafor engineering seat)
> **Date:** 2026-07-16
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**4/4 delivered (18 points).** RFC0042 built and Accepted (by derivation): the sprint close-down is
now **mechanically detectable and enforceable**, not doctrine an agent has to remember. `close_owed.py`
answers "is a close owed right now?" deterministically - a delivery unit terminal since a one-time
grandfather **baseline** (the SET of ids terminal at adoption) with no retro's `Batch` naming it. It
surfaces three ways: a soft `advisory:` on `status`/`hint` (**US0164**), a blocking
`gate --require-close` lane for push/release (**US0165**, bound-only), and an optional
`hooks/close_guard.py` Stop hook that reminds the agent before a turn ends (**US0166**, default-allow,
never a hard-lock). The detector (**US0163**) caught its own sprint - EP0046 + US0163-0166 showed as
owing a close until this retro named them. Full suite 2492, tools 183, 0 drift, style clean.

## What went well

- **The feature caught its own close.** A live end-to-end proof: the four Done stories + their epic
  registered as an owed close, cleared only by RETRO0039 naming them.
- **The bound-lane invariants kept the design honest.** An early attempt to make `close-owed` a
  warn-by-default gate check tripped two existing invariant tests (a bound lane must not sit in the
  plain gate; must block on crash). They were right - the soft nudge belongs on status/hint, the gate
  carries only the blocking lane.

## What the independent review caught

- **A real BLOCKER in the baseline model.** The first cut baselined a per-prefix **highest id**, which
  silently grandfathered a lower-id unit that was in flight at adoption and closed later - the exact
  false "none owed" this sprint exists to kill - and broke entirely on non-numeric v3/ULID ids. Fixed
  at root: baseline the **set** of terminal ids. Two regression tests lock it (in-flight-lower-id +
  ULID). Re-review APPROVE. Plus four MINOR/NIT (an un-nudged unbaselined prerequisite; two tests that
  passed by avoiding their own claim; a title over-claim) - all fixed.

## Backlog rollup (non-terminal)

- **RFC0043** (DoR/DoD as editable per-project artefacts) - filed, Accepted-pending; this sprint
  delivered the sprint-DoD's **close clause** it depends on. XL, decompose next.
- Buildable-now discovery backlog: RFC0035/0036/0037, CR0264/0273, RFC0039 close-out. Release-gated
  (5.0.0, after the freeze): RFC0040, CR0254/0255/0256, CR0272 retire/promote half.

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. Additive.

## For a fresh session

Start here, then `AGENTS.md`. The close-down is now enforceable: `close_owed.py baseline` once at
adoption, then `close_owed.py detect` / `gate --require-close` / the `status` advisory tell you when a
close is owed. A sprint is complete only when the close gate is green and shown, never at "deployed".
