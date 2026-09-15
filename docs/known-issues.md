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
| `BG0659` | Medium | a code span whose value ends in a space cannot be recorded in any review ledger - markdownlint MD038 refuses the row |
| `BG0661` | Medium | revert-check never names the units it set aside, and once one unit is examined their count vanishes from the lane line too |
| `BG0662` | Medium | nothing checks a changelog fragment's SHAPE until the release cut, and 59 of 119 had drifted past it |
| `BG0664` | Medium | the pre-push boundary gate runs NO boundary-only test, so the marker's own promise is false at the boundary it names |
| `BG0666` | Medium | an UNAUTHORED Test Plan row is exempt from the quality guard an authored one must pass, so leaving the placeholder buys a clean derive |
| `BG0667` | Medium | the root-effect control's real-tree marker is bound to an id range this project has already outgrown, so its evidence window closes as ids advance |
| `BG0671` | Medium | critic.py's brief-practice and claim-pass checks are called by no production path, while reference-review.md says the brief verb refuses a brief th... |
| `BG0672` | Medium | critic record accepts a --brief fingerprint no brief produced, recording the row as briefed with only a stderr note |
| `BG0673` | Medium | the repair-plan gate (EP0106) is wired into nothing: no command records a plan or verdict, and turning review.repair_plan_gate on refuses nothing a... |
| `BG0674` | Medium | sprint next materialises a charter's discovery items (CRs) that sprint plan then refuses, so the charter at the head of the queue produces a batch... |
| `BG0675` | Medium | an author-declared Points value sets a unit's review tier: route.estimate's spec subscore reads Points, which D0150 rules out of review depth |
| `BG0676` | Medium | the scheduled corpus-verify lane is red on main - 40 red criteria against a baseline of 20 - and every one of the 20 new ones passes locally |
| `BG0677` | Medium | critic.py repair cannot close a finding whose text carries the closure separator early, so the rejection raising it can never be retired |
| `BG0678` | Medium | A wired repair-plan gate keeps no rounds, no brief and no approval pin, so a rejected plan can never be retired and a re-recorded plan keeps its ap... |
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

25 findings: 25 Medium, 0 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
