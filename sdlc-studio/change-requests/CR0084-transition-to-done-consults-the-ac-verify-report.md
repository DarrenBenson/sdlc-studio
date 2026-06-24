# CR-0084: transition to Done consults the AC-verify report - definition-of-done safety net on the hand-driven path

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature

## Summary

A field agent marked seven stories `Done` off its own green Jest suite without ever
running the stories' executable ACs; when it finally ran `verify_ac.py`, US0001 was
**0/7**. The deterministic status setter (`transition.py set --status Done`, also reached
by `artifact close`) gates **nothing** on AC verification - it only warns on index sync.
The autosprint conformance gate (`conformance.py`: ... -> verified -> ...) does enforce
this, but the **hand-driven path bypasses it entirely**, so a diligent agent can ship
"green by its own lights" and silently drift from the contract. Make `-> Done` consult
the AC-verify report so it cannot happen unnoticed.

## Problem

From the implementation reflection (verbatim): *"Nothing stopped me transitioning seven
stories to Done with a red AC verifier. `transition.py set --status Done` should be able
to consult the latest verify report and refuse (or warn loudly) when ACs are
unverified."* And: *"the implementation phase's weakness is conformance not being on the
rails by default - the executable-AC/critic/gate machinery exists but nothing forces you
through it."*

The report already exists: `verify_ac` writes `sdlc-studio/.local/verify-report.json`
with per-AC state (`yes`/`no`/`stale`/`manual`). Nothing reads it at the Done boundary on
the manual path. This is the safety-net complement to the autosprint gate, in the spirit
of the project's other advisory checks (doc-freshness CR0073, disclosure CR0063).

## Proposed Changes

The posture is **hybrid by source**, settled by the field agent's calibration: the
deterministic verifier **blocks**; a critic's semantic finding **warns**. Pure-advisory
fails (the agent *"knew better and shipped"* the 0/7 - a warning would have been
dismissed); pure-hard-gate on a critic's opinion fails (false-positive wave stalls).

### Item 1: Hard-gate the deterministic verify result on -> Done

**Priority:** High
**Effort:** 2

When `transition` (or `artifact close`) moves a story to a `Done`-equivalent status, read
the latest `verify-report.json`. If any AC is `no`/`stale`, **refuse the transition by
default** with a message naming the failing ACs. This is the one mechanical, unarguable
fact (N ACs, M executed) and it is exactly what was bypassed - so it blocks, it does not
merely warn. Manual ACs are accepted (author-attested); an absent report blocks with
"ACs never verified - run `verify_ac` first". A recorded `--force` (or
`quality.done_requires_verified: false`) is the explicit, logged escape for the rare
legitimate case - opt-out, not opt-in.

### Item 2: Advisory-warn the critic's semantic findings

**Priority:** Medium
**Effort:** 1

Semantic findings that need judgement and carry false-positive risk - an AC-vs-diff gap
(the CORS miss), an out-of-epic AC (CR0086) - **warn loudly but never stall** a wave. The
critic surfaces them; the operator decides. This keeps the blocking surface limited to
the deterministic fact.

### Item 3: Surface it in status and the gate

**Priority:** Medium
**Effort:** 1

`status` flags stories marked Done with unverified ACs as a drift class; `gate` adopts the
blocking form for CI. Reuses the existing report - no new verification machinery.

## Dependencies

CR0084 and **CR0085 only work as a pair.** The hard gate is only a *clean* signal once the
test-spec bridge (CR0085) forces the AC's test name and the real test title to converge -
otherwise the verifier goes red for the wrong reason (a broken filename), which is red
noise, not an AC signal. Sequence CR0085 with or before CR0084.

| CR | Title | Status | Required Before |
| --- | --- | --- | --- |
| [CR-0085](CR0085-authored-verify-lines-must-use-the-verifier-dsl.md) | enforce the test-spec as the AC-to-test bridge | Proposed | the hard gate to be a clean signal |

## Acceptance Criteria

- [x] moving a story to Done with a `no`/`stale` AC in `verify-report.json` is **refused
      by default**, naming the failing ACs; `--force` is a recorded opt-out (a
      `quality.done_requires_verified` config toggle is **deferred** - `--force` covers the
      override need today)
- [x] manual ACs do not block (author-attested); a story with executable ACs but no report
      blocks with "never verified - run `verify_ac`"
- [x] critic semantic findings never block: the gate blocks **only** the deterministic
      verifier result, so AC-vs-diff / out-of-epic findings (CR0086) stay advisory by
      construction (the gate never consults them)
- [x] the check reuses `verify-report.json` (no new verification path) - **deferred:** a
      `status` "Done with unverified ACs" drift class (status.py does not read the report yet)
- [x] unit tests cover: red AC blocks, never-verified blocks, manual passes, green passes,
      `--force` overrides; CHANGELOG `[Unreleased]` entry same commit (LL0004)

> **Deferred:** the `quality.done_requires_verified` config toggle and the `status` drift
> class. The enforcing core - the hard story->Done gate on the verifier result, with
> `--force` - lands here, scoped to stories so CR/epic/bug closures are unaffected.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
| 2026-06-24 | sdlc | Calibrated to hybrid (agent verdict): hard-gate the deterministic verify result, advisory-warn the critic's semantic findings. Pure-advisory let the 0/7 ship; pure-hard-gate on critic opinions stalls waves. Paired with CR0085 |
