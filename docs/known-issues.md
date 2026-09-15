# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v5.1 is held to

**Zero open High-severity bugs at the tag, and every Medium disposed of or ruled.** A
finding either reaches a terminal status with its own verifiers passing, or it stays open
carrying a dated ruling that says why it ships.

## The bar v5.0.0 was held to, kept as history

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
| `BG0676` | Medium | the scheduled corpus-verify lane is red on main - 40 red criteria against a baseline of 20 - and every one of the 20 new ones passes locally |
| `BG0679` | Medium | With review.repair_plan_gate on, a repair bug set straight to Closed or Verified skips the gate |
| `BG0680` | Medium | repair_state counts a repair row once per rejection sharing its date, so closed and fixed counts are doubled |
| `BG0681` | Medium | config.py show --key crashes on a key whose value holds an unquoted YAML date, the path BG0670 left |
| `BG0682` | Medium | artifact.py revision writes a bare _identifier into the Revision History, which markdownlint refuses as MD037 |
| `BG0683` | Medium | repair_gate's review-before-repair ordering check (US0312 AC4) is dead on the wired path |
| `BG0684` | Medium | transition's two-role gate ignores a Definition of Done that stands the review.two-role tag down |
| `BG0685` | Medium | project_upgrade reads plan-review verdicts with no kind, so a repair-plan APPROVE counts as a repair story's spec review |
| `BG0686` | Medium | BG0493 AC2's test reads a fixture hook, so deleting the real pre-commit hook's lane-check block survives |
| `BG0687` | Medium | A criterion's second Verify line is recorded but never run, so a both-states requirement cannot be enforced by its selectors |
| `BG0688` | Medium | gate --require-close still counts close-owed's raw owed rows, refusing an override the tag guard and the detector now honour |
| `BG0689` | Medium | The release tag guard never reads close_owed's velocity half, so a retro owing its velocity row does not refuse the tag |

12 findings: 12 Medium, 0 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
