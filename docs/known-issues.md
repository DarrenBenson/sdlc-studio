# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v5.0.0 was held to

**Zero open High-severity bugs at the tag.** Every High finding raised against v5 was
fixed and closed before the tag was cut. The bar was originally zero open bugs of any
severity; it moved on 2026-08-11, because holding a release for findings that are real
but not release-blocking had cost a month and was buying nothing a disclosure could not
buy honestly.

**Medium and Low findings ship open, listed here by id, triaged to v5.1.** Each is a real
defect with a reproduction and, in most cases, a proposed fix. None of them stops the
lifecycle running. They are listed rather than closed, because closing a bug to make a
release look clean is the practice this tool exists to prevent.

Each id below is a file in `sdlc-studio/bugs/` in the source repository, carrying the
evidence, the reproduction and the proposed fix in full.

## Triaged to v5.1

| Id | Severity | Finding |
| --- | --- | --- |
| `BG0463` | Medium | Twenty non-blocking findings from the RUN-01KYTKA1 batch-boundary review: stale counts, dead code, unmarked truncation, over-claiming docstrings an... |
| `BG0486` | Medium | duplicate verifiers are grouped on a normalised string, so two ACs running the same command can read as distinct |
| `BG0490` | Medium | four bug repairs are Fixed with half their title undelivered and no recorded narrowing |
| `BG0493` | Medium | four more verifiers pass on a delivery that has been made inert |
| `BG0509` | Medium | the close-time-repair split uses day granularity and a global override map, so a same-day terminal is excused and an override never expires |
| `BG0519` | Medium | the tools leg's remaining slowdown inside the full runner is unattributed, and the assertion that fails when it is slow is still unnamed |
| `BG0526` | Medium | loop_guard budget has no programmatic caller: the appetite breaker is fully fed and pulled only if the driving agent remembers |
| `BG0529` | Medium | four RUN-01KZ9315 units carry no verifier that enters the shipped entry point, so the wiring each one exists to add is pinned by nothing |
| `BG0545` | Medium | testplan derive and the bug criteria floor each mis-slice a checkbox-shaped Acceptance Criteria section, so one refuses a sound plan and the other... |
| `BG0552` | Medium | a registered mutant cannot be joined to a measured one, so a cross-provenance contradiction in the mutation ledger is undetectable |
| `BG0553` | Medium | a mistyped mutation verdict cannot be corrected, and the contradiction check now turns that from a wrong number into a refusal in every mode |
| `BG0567` | Medium | the upgrading-project baseline compares against this tree minus one branch, not against the base ref, so a regression the epic introduced elsewhere... |
| `BG0571` | Medium | The repaired spec-agreement guards pin word patterns rather than claims, so a passage stating the OPPOSITE rule passes |
| `BG0578` | Medium | test-file attribution is decided by name frequency, so mentioning one more module silently changes a file's owner |

14 findings: 14 Medium, 0 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
