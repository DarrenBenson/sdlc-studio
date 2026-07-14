# Unified Review – 2026-07-14 (close) – internal-hardening sprint delivered

> **Review type:** Sprint-close review (refreshed by the new `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1
> **Date:** 2026-07-14
> **Triggered by:** the CR0253 review-currency gate, which correctly flagged this anchor stale
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

The internal-hardening sprint's first two clusters shipped: the `verify_ac` grep verb is fixed and
tested (BG0125, BG0128), `verify_ac run` takes `--file` (CR0251), the persona-index miscount is
gone (BG0129), and - the P1 - **the sprint-close review is now a hard gate** (CR0253). That last one
closed the exact hole this anchor kept falling into: a stale `LATEST.md` reaching a close. The gate
proved itself by flagging *this* review stale (18 artefacts changed) before it was refreshed.

The spec docs remain the outstanding gap: PRD/TRD/TSD are still self-declared v2.0.0 against a
v4.1.0 product (CR0252, P1, not in this sprint).

## What shipped this sprint

| Unit | Status | What |
| --- | --- | --- |
| BG0125 | Fixed | grep verb expands globs; documented `src/**/*.ts` example no longer false-REDs; verb now tested |
| BG0128 | Fixed | rg-vs-grep dialect difference documented (POSIX-ERE portability) |
| CR0251 | Complete | `verify_ac run/lint` accept `--file` as an alias for `--story` |
| BG0129 | Fixed | `review_prep` no longer counts `personas/index.md` as a phantom persona |
| CR0253 | Complete | `gate --require-review` - the sprint close now blocks on a stale `LATEST.md` |

## Document currency (unchanged from the prior review - CR0252 still pending)

- **PRD/TRD/TSD** - STALE, self-declared v2.0.0; engagement floor / ULID / generated team / learning
  loop still undocumented. Refresh is CR0252 (P1, deferred to v4.2).
- **Persona** - Maya and Trevor consulted in 14 artefacts, still unnamed in the PRD (folds into
  CR0252). The phantom "Persona Index" is gone as of BG0129.

## Backlog rollup (14 non-terminal)

- **Bugs (1):** BG0126, BG0127 (meta_new lock, atomic_write - deferred heavy-file cluster)
- **CRs (11):** CR0248/0249/0250/0252/0254-0259
- **RFCs (2, Accepted):** RFC0033 (one `audit` command), RFC0034 (sizing/velocity loop)

## Production state

v4.1.0 released and Latest on GitHub. Freeze holds until ~2026-07-21; all sprint work is on `main`
under `[Unreleased]`, forward-ported to the installed copy for internal testing. **No production
release this week.**

## For a fresh session

Start here, then `AGENTS.md`. The specs are still not a reliable product description until CR0252
lands - trust the CHANGELOG, `reference-*.md`, and the code. Highest-value pending: CR0252 (specs),
then the two v4.2 RFC workstreams. The internal-hardening sprint's second half (BG0126/BG0127 and
CR0248/0249/0250) remains on the backlog.
