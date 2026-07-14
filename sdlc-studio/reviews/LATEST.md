# Unified Review – 2026-07-14 (close) – internal-hardening sprint COMPLETE, and the first velocity data

> **Review type:** Sprint-close review (required by the `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1
> **Date:** 2026-07-14
> **Triggered by:** the sprint close - review currency is now a hard gate
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

The internal-hardening sprint is **complete - all 6 units**, every one delivered by an instrumented
subagent and verified independently before commit. The review's findings are cleared: the `verify_ac`
grep verb, the persona-index miscount, the retro disposition order, the `meta_new` allocation lock,
the duplicated archive writer, the triplicated status vocabulary, and six non-atomic index writes.
The P1 review gate (CR0253) shipped and immediately proved itself by flagging its own sprint's stale
anchor.

**And the project has velocity data for the first time.** The token supplier (CR0258's hard half)
works: a subagent's reported usage now lands in telemetry. Six units measured:

| unit | tools | wall | ACTUAL | estimate | over |
| --- | --- | --- | --- | --- | --- |
| CR0250 | 11 | 80s | 46,359 | 50,000 | 1.1x |
| BG0126 | 14 | 272s | 46,792 | 245,000 | 5.2x |
| BG0130 | 15 | 189s | 42,687 | 125,000 | 2.9x |
| BG0127 | 27 | 347s | 65,625 | 310,000 | 4.7x |
| CR0249 | 28 | 475s | 98,513 | 245,000 | 2.5x |
| CR0248 | 39 | 485s | 84,302 | 310,000 | 3.7x |
| **TOTAL** | | **31 min** | **384,278** | **1,285,000** | **3.3x** |

**The estimator over-estimates 3.3x.** It is near-exact (1.1x) on the one unit with complexity 0 and
over by 2.5x-5.2x on every unit touching a complex file - so the `complexity x 5,000` term is the
error source, and the 50k base is about right for the fixed cost. **Cognitive complexity of the FILE
is a poor proxy for the WORK done in it.** That is a real signal for CR0257/CR0259 - but N=6 is a
signal, not a calibration. Do not recalibrate the bands from it yet.

## Document currency (unchanged - CR0252 still the outstanding P1)

- **PRD/TRD/TSD** - STALE, self-declared v2.0.0 against a v4.1.0 product; engagement floor / ULID /
  generated team / learning loop still undocumented. Refresh is **CR0252 (P1)**, deferred to v4.2.
- **Persona** - Maya and Trevor consulted in 14 artefacts, still unnamed in the PRD (folds into
  CR0252). The phantom "Persona Index" is gone (BG0129).

## Backlog rollup (9 non-terminal)

- **Bugs (1):** BG0131 (Low - the token metric's fixed floor; corrected from a wrong High)
- **CRs (6):** CR0252 (P1, spec refresh), CR0254-0257, CR0259
- **RFCs (2, Accepted):** RFC0033 (one `audit` command), RFC0034 (sizing/velocity loop)

## Production state

v4.1.0 released and Latest on GitHub. Freeze holds until ~2026-07-21. All sprint work is on `main`
under `[Unreleased]`, forward-ported to the installed copy for internal testing. **No production
release this week.**

## For a fresh session

Start here, then `AGENTS.md`. The specs are still not a reliable product description until CR0252
lands - trust the CHANGELOG, `reference-*.md`, and the code. Highest-value pending: **CR0252** (the
specs), then the two v4.2 RFC workstreams. The sizing loop (RFC0034) now has its first real data;
CR0258's token half is unblocked (the supplier works) but the bands must not be fitted to N=6.
