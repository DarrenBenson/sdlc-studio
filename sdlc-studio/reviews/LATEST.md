# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXVD74** (the evidence-earns-the-green
> sprint, 2026-07-19, RV-0014 / RETRO-0050). Supersedes the RETRO0049 picture.

## Where the pipeline is (2026-07-19)

The **evidence-earns-the-green sprint** (RUN-01KXVD74) is delivered: **10/10 units, Sprint Goal
ACHIEVED**. The batch was EP0075 (verify-line integrity) plus all seven open bugs, six of which were
the previous close's own follow-ups.

- **BG0193:** a verifier that exits 0 having run no tests no longer counts as proof. Decided per
  runner family from that family's own output: `unittest` and `pytest` print one exclusive summary
  each; `go` is empty only when every package line says so; `jest`'s "No tests found" yields to
  another project's PASS.
- **US0228:** the `grep` verb passes its pattern behind `-e` and its paths behind `--`, on both
  back-ends, so a dash-leading regex searches for what its author wrote.
- **US0226:** US0166 AC3 checks the claim it makes. As shipped it read `grep -q "..." <file>`, and
  the verb takes no flags - `-q` became the PATTERN and the quoted text a PATH, so it searched for
  the literal string `-q` across a list containing a nonexistent file, found it, and exited 0. It
  had been green on every run since it shipped.
- **US0227:** US0172/US0173 and US0163's two ACs shared selectors byte for byte. All four narrowed,
  plus a `verify_ac lint` naming any Verify command claimed by more than one AC. It reports 17
  across this workspace; 13 remain as declared pre-existing debt.
- **BG0194:** the id regexes carry a trailing boundary, so `US01010` no longer reads as `US0101`,
  and a digit-leading ULID is claimed whole rather than truncated.
- **BG0191:** the close re-renders its handoff after the sign-off cascade, so the document no longer
  lists as remaining the units the close just finished.
- **BG0195:** a retro id resolves dashed or undashed. The velocity row had not recorded for two
  sprints while the close reported success.
- **BG0196:** an unmeasured sprint is no longer reported as an unforecast one.
- **BG0192:** `ac_scope` findings carry a strength; only a multi-keyword hit blocks readiness, and
  the owning epic no longer counts towards a keyword's spread.
- **BG0187:** the TRD threat model agrees with its own write contract, guarded so it cannot silently
  return.

## CODE leg

One independent adversarial full-diff review over `ba6908e~1..HEAD`, recorded as a sprint-level
verdict. **Two rounds of REJECT**, four blocking findings. Round 1: a frequency suppression that
deleted the leaks it was meant to rank, and two unanchored substrings that failed a green
multi-package go suite. Round 2, both created by the round 1 repair: a blob-wide counter-signature
that let any co-running tool printing "N passed" **disarm the vacuity gate**, and a comment that
falsely claimed the retained threshold discounts the owning epic. Round 3 APPROVE, after the
reviewer re-ran its own reproductions and mutation-checked the new guards. Full suite 2,974 green,
tools 222 green, drift 0, every commit gated.

The sprint about honest evidence twice shipped a claim its own tests passed over. Both times the
defect was in prose justifying the code as much as in the code.

## Document legs

`CHANGELOG.md`, `sdlc-studio/trd.md` (the 9 threat-model row), and the ten groomed units. Each is
consistent with the shipped code and enforced by the gate.

## Next steps

- Follow-ups filed this sprint: **BG0197** (the mutation gate can report a mutant SURVIVED that
  never ran, via stale bytecode - a same-length mutant reuses the cached `.pyc`; this silently
  invalidated the first hour of this sprint's own mutation checks), **BG0198** (`handoff.refresh`
  re-stamps run identity from ambient run state; not reachable via the shipped close, but it
  overwrote HO-0007 twice by hand), **BG0199** (two id readers disagree on meta-id width).
- **13 duplicated Verify selectors** remain across the workspace, now reported by `verify_ac lint`
  on every run. A batch of its own, deliberately not absorbed here.
- Standing: **CR0278** (interactive-sprint token capture) - per-unit actuals were not captured this
  run, so est/actual is not-yet-captured; the sprint total can be supplied with `accuracy --tokens`.
- Residual audit CRs (CR0280-CR0306) remain, plus the seven unstarted refined epics (EP0073,
  EP0074, EP0076, EP0078, EP0079, EP0081, EP0082) for a future scheduled batch.
- Release freeze holds until ~2026-07-21; everything lands unreleased on `main`.
