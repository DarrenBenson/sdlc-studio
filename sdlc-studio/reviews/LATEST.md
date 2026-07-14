# Unified Review – 2026-07-14 – the specs have drifted two majors behind the code

> **Review type:** Unified PRD/TRD/TSD/Persona consolidation
> **Reviewer:** sdlc-studio; agent; v1
> **Date:** 2026-07-14
> **Triggered by:** manual `review` run (the sprint-close review is not yet gated - CR0253)
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

The code is in strong shape; the **project spec documents are not**. All three of PRD, TRD and TSD
self-declare **Version 2.0.0** against a **v4.1.0** product, and none reflect the v4 flagship
capabilities: the engagement floor, ULID collision-free identity, the generated team, or the
RFC0032 learning loop. The PRD still uses the retired `autosprint` name; the TRD's ADR log stops
before four architecturally-significant v4 decisions; the TSD does not know the mutation gate. The
personas are alive (Maya and Trevor are consulted in 14 artefacts) but the PRD names neither. A repo
whose whole thesis is spec-code alignment has its own PRD two majors behind - a dogfooding-integrity
gap, filed as **CR0252** (P1, L).

This review itself only happened because it was asked for by hand: **the sprint-close review is not
gated** (reconcile and retro are; review currency is advisory-only), which is why the *previous*
LATEST.md sat claiming "v4.0.0 GA / 4.1.0 READY TO TAG" long after that stopped being true. Filed as
**CR0253** (P1).

```text
══════════════════════════════════════════════════════════
                   DOCUMENT REVIEW SUMMARY
══════════════════════════════════════════════════════════

📋 PRD   v2.0.0   STALE   engagement floor / ULID / team / loop absent;
                          "autosprint" (retired name) still used        -> CR0252
📐 TRD   v2.0.0   STALE   ADR log stops at ADR-003; no ADRs for the
                          four v4 decisions                             -> CR0252
🧪 TSD   v2.0.0   STALE   mutation gate absent from the test strategy    -> CR0252
👥 Persona        MIXED   personas alive (consulted x14) but unnamed in
                          the PRD; index.md miscounted as a persona     -> BG0129
──────────────────────────────────────────────────────────
🔗 CROSS-DOCUMENT CONSISTENCY
   PRD -> code : ✗ the shipped v4 feature set is undocumented
   PRD -> Persona : ✗ Maya Okafor, Trevor Hale defined + consulted, not named in PRD
   Sprint-close contract : ⚠ reconcile ✓ + retro ✓ + review ✗ (ungated - CR0253)
══════════════════════════════════════════════════════════
```

## Per-document verdict

- **PRD** (`prd.md`, v2.0.0, 2026-07-04) - STALE. Feature Inventory and Functional Requirements
  predate v4. No engagement floor, ULID identity, generated team, or learning loop. Uses
  `autosprint` (renamed `sprint` at v4.0). Personas not referenced.
- **TRD** (`trd.md`, v2.0.0, 2026-07-06) - STALE. ADRs 001-003 are sound (progressive-disclosure
  router, JSON-emitting helpers, files-are-truth) but the log stops there; the engagement floor,
  ULID identity, generated team and learning loop are all ADR-worthy and undocumented.
- **TSD** (`tsd.md`, v2.0.0, 2026-06-20) - STALE. Knows the gate and verify_ac; does not cover the
  mutation-check gate.
- **Persona** - MIXED. Two real personas (Maya, Trevor) are load-bearing (consulted in 14
  CRs/stories) but unnamed in the PRD; `personas/amigos/` holds 3 generated seats. `review_prep`
  miscounts `index.md` as a third persona (BG0129).

## Backlog rollup (12 non-terminal)

- **Bugs (5):** BG0125-BG0129 (grep verifier x2, meta_new lock, atomic_write, persona-index filter)
- **CRs (6):** CR0248-CR0253 (archive dedupe, status-vocab, security hardening, verify_ac `--file`
  friction, **CR0252 spec refresh P1**, **CR0253 review-gate P1**)
- **RFC (1):** RFC0033 (reconcile the three-way `audit` overload; Draft, next up for decision)

## Production state

v4.1.0 is released and Latest on GitHub. A release freeze holds until ~2026-07-21; unreleased work
(RFC0032 learning loop, this review's findings) sits on `main` under `[Unreleased]` and is
forward-ported to the installed copy for internal testing only. **No production release this week.**

## For a fresh session

Start here, then read `AGENTS.md` for durable doctrine. The specs (`prd.md`/`trd.md`/`tsd.md`) are
currently NOT a reliable description of the product - trust the CHANGELOG, `reference-*.md`, and the
code until CR0252 lands. The highest-value pending work is CR0252 (refresh the specs) and the two
P1 gaps this review exposed; RFC0033 is the next design decision.
