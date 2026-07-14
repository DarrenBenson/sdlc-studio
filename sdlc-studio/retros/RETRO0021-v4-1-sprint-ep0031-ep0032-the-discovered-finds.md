# RETRO-0021: v4.1 sprint: EP0031 + EP0032 + the discovered-finds tail

> **Date:** 2026-07-14
> **Batch:** EP0031 + EP0032 (12 planned units) plus 12 discovered-finds units
> **Goal:** done (backlog-clear for the v4.1 tag)
> **Delivered:** 24 / 24   **Blocked:** 0

## Delivered

- **EP0031 release integrity (7):** BG0111 (lessons written to the untracked install - data
  loss), BG0108 (the deterministic creators emit what the deterministic validator accepts),
  BG0109 (creators record the authorship they were given), CR0233 (`gate --release`, one exit
  code), BG0110 (leg-presence gate + the reusable waiver primitive), CR0229 (mechanical
  engagement floor), CR0236 (the lessons close-loop is a mechanism, not doctrine).
- **EP0032 run-close and agent DX (5):** CR0223 (the handoff guide + the run-state object),
  CR0225 (appetite breaker, built on it), CR0224 (cross-repo `Depends on:` resolution), CR0234
  (uniform CLI grammar + a conformance sweep), CR0235 (planning template tier).
- **Discovered-finds tail (12), all Target v4.1 per D0025:** BG0112 (template lint), BG0113
  (`_put_section` subsection preservation), BG0114 (the coverage guard was blind across three
  checks), BG0115 (creator-field metadata/RCE injection), BG0116 (first retro/review index
  bootstrap), BG0117 (prose-field metadata forge), BG0118 + BG0119 (engagement-floor file
  recogniser), BG0120 + BG0121 (fresh-index lint + bootstrap unification), CR0237 (verify_ac
  manual-vs-unspecified), CR0238 (consolidation filer routes through the shared row writer),
  CR0239 (the `Refs:` commit trailer closes the floor's shared-commit gap).
- **Design dispositions:** RFC0030 parked (accepted in principle, build on demand - D0027),
  RFC0031 status-quo (a content-less scaffold is meant to fail validation until filled - D0028),
  the benchmark CRs re-homed to `sdlc-bench` (RFC0029). Decisions D0018-D0029 recorded.

## Blocked / deferred

- None blocked. Nothing deferred out of v4.1: per the operator's correction (D0025), v4.1
  absorbs everything the sprint finds; the week of local forward-port testing is what makes the
  backlog-clear rule reachable, not a reason to push finds to a later tag.

## What went well

- **The independence gate earned its keep on almost every unit.** Roughly 12 of 14 first-pass
  reviews rejected, and the rejections were substantive, not stylistic - each behind a green
  test suite. Delivering agents and reviewing agents were always separate instances; the reviewer
  re-ran its own reproductions before an approve.
- **The worst finds would all have shipped green.** BG0115: a `--ac` newline injected an
  executable `Verify:` line the AC runner then ran (RCE), and the first fix still passed because
  the guard checked the stripped value while the writer emitted the raw one - a leading newline
  slipped through. CR0223: the handoff could silently omit remaining work by two routes. CR0234:
  the mechanical `--root` migration made `verify_ac run` compute its verdict against the wrong
  tree. CR0229: a safety gate that did not actually gate (three rounds to an honest close).
  CR0239: a `Refs:` trailer, meaning "see also" in universal git usage, silently disarmed a
  solo commit's own floor check.
- **Parallel fan-out with disjoint file surfaces held.** Waves of 3-4 agents on grouped surfaces
  merged cleanly; the one cross-agent collision (a flaky mock test under full discovery) was
  caught by running the full suite at assembly, not by the individual agents.
- **Mechanisms replaced doctrine.** CR0236 gated the lessons close-loop that was previously prose;
  BG0114 made three coverage guards derive from real emission vocabulary rather than a hardcoded
  answer key.

## What was hard / what stalled

- **The "mirror another reader exactly" class kept re-surfacing.** BG0117 took three rounds - the
  escape mirrored `extract_field`'s line-start anchor but not its inline `·` branch (round 1),
  then its anchor tokens but not its whitespace class - an invisible NBSP leaked (round 2), until
  it matched across anchor set and whitespace class (round 3). CR0229's engagement floor moved its
  hole down a layer each round (prose downgrade, omitted `Affects`, `Affects: n/a`, batch-commit
  understatement) until it reached a real limit git cannot cross.
- **Some claims were true but incomplete, and the gap was the defect.** BG0114 fixed one check
  while asserting the others were clean; two more had the identical blind spot. CR0238's first test
  proved escaping, not the routing it claimed. The reviewer's job was as much "is the claim
  honest" as "does the code work".
- **A safety gate honest about its limit beats one that overstates.** CR0229 shipped only once the
  guarantee wording named exactly what it catches (pure omission, solo-commit understatement) and
  what it does not (shared-commit understatement, tracked as CR0239), rather than chasing a
  git-log limit that has no clean resolution.

## Lessons

- **When you mirror another regex, mirror its character classes and anchor set, not just its
  anchor tokens, and prove the mirror across the whole class the target matches - not an ASCII
  sample.** (L-0006 generalised by BG0117's three rounds.)
- **A guard that enumerates the kinds it checks against a hardcoded list exempts the one it
  forgot; derive the expected set from the real emission vocabulary.** (BG0114.)
- **On an injection surface, the value that is checked must be byte-identical to the value that is
  written - any normalisation between check and write is a bypass.** (BG0115, and its round-2
  leading-newline miss.)
- **A safety gate must state its guarantee precisely and file the residual as tracked work, not
  chase a limit the signal cannot deliver.** (CR0229 / D0026 / CR0239.)
- **A test that cannot distinguish the fixed behaviour from the broken one guards nothing** - when
  the output is identical either way, guard the structure at source. (CR0238.)
- **A convention that collides with a universal meaning is a footgun** - `Refs:` means "see also"
  everywhere, so keying a safety check on it had to be strictly one-directional-safe. (CR0239.)

## Close loop (gated)

`gate --require-retro RETRO0021` (this retro's id, file form) fails until all three are true:

- [x] this retro exists (`artifact new --type retro`)
- [x] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [x] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Units: 24 delivered, 0 blocked · Critic rejects: ~12 of 14 first-pass (every one repaired and
  re-verified) · Follow-ons filed from reviews: BG0119-BG0121, CR0237-CR0239, RFC0030-RFC0031 ·
  Backlog at close: empty (the v4.1 tag precondition).
