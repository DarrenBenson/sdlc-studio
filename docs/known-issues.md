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
| `BG0350` | Low | 25 Done stories carry no independent critic verdict, waived rather than cleared |
| `BG0421` | Medium | Twenty-one Open Questions reached a terminal status unanswered, and are now owned here rather than given rulings nobody made |
| `BG0463` | Medium | Twenty non-blocking findings from the RUN-01KYTKA1 batch-boundary review: stale counts, dead code, unmarked truncation, over-claiming docstrings an... |
| `BG0486` | Medium | duplicate verifiers are grouped on a normalised string, so two ACs running the same command can read as distinct |
| `BG0490` | Medium | four bug repairs are Fixed with half their title undelivered and no recorded narrowing |
| `BG0491` | Medium | lane-check scans only stories, so 487 bugs are outside the number a blocking decision would rest on |
| `BG0493` | Medium | four more verifiers pass on a delivery that has been made inert |
| `BG0508` | Medium | the close report's sibling imports sit outside its advisory try, so an ImportError escapes after the run is already stamped closed |
| `BG0509` | Medium | the close-time-repair split uses day granularity and a global override map, so a same-day terminal is excused and an override never expires |
| `BG0512` | Medium | batch add-epic and batch swap mutate a live batch without the ungroomed census, so a unit the plan gate would refuse can enter a run |
| `BG0519` | Medium | the tools leg's remaining slowdown inside the full runner is unattributed, and the assertion that fails when it is slow is still unnamed |
| `BG0526` | Medium | loop_guard budget has no programmatic caller: the appetite breaker is fully fed and pulled only if the driving agent remembers |
| `BG0529` | Medium | four RUN-01KZ9315 units carry no verifier that enters the shipped entry point, so the wiring each one exists to add is pinned by nothing |
| `BG0531` | Medium | a hand-applied mutant is registered with no assertion that its anchor was unique, so a mutation run can report a false SURVIVED for a function it n... |
| `BG0532` | Medium | alias_map decodes every artefact in the project with a bare read_text, so one unreadable file takes down any command that resolves an id |
| `BG0534` | Medium | testplan derive's edit-verb check is an enumeration, so it refuses honest mutants written with a verb nobody listed |
| `BG0537` | Medium | check_root_docs reads raw lines while check_body_links blanks code spans, so a link inside backticks is an example in one directory and a broken re... |
| `BG0538` | Medium | a release cut mints an affects-unresolvable warning for every unit that declared its own changelog fragment, because compose deletes the file the u... |
| `BG0539` | Medium | critic record cannot tell a review ROUND from a panel SEAT, so the ordinary reject-fix-approve loop escalates as an unresolved split |
| `BG0540` | Medium | a retro that was never written reports `ran` on the close checklist, because a missing file is graded as a structural error rather than an absence |
| `BG0544` | Medium | _ck_closing_review reports `ran` for a unit the shared coverage reading calls uncovered, when its latest sprint-level verdict is APPROVE |
| `BG0545` | Medium | testplan derive and the bug criteria floor each mis-slice a checkbox-shaped Acceptance Criteria section, so one refuses a sound plan and the other... |
| `BG0546` | Medium | critic.py record refuses a plan-review finding for carrying no diff origin, when a plan review has no diff to attribute one to |
| `BG0547` | Medium | one advisory silently replaces another: the transition gate ladder assigns its warning variable where its own docstring says the warnings accumulate |
| `BG0548` | Medium | the acceptance-criteria parser silently drops a criterion whose heading is not AC<digits>, so a whole criterion and its Verify line vanish without... |
| `BG0549` | Medium | the non-convergence escalation is sticky: a converging APPROVE still reports that the panel is not converging, because the notice counts historical... |
| `BG0550` | Medium | register drops a file's earlier registered mutants without saying so, so an edit after registering silently empties a unit's evidence |
| `BG0552` | Medium | a registered mutant cannot be joined to a measured one, so a cross-provenance contradiction in the mutation ledger is undetectable |
| `BG0553` | Medium | a mistyped mutation verdict cannot be corrected, and the contradiction check now turns that from a wrong number into a refusal in every mode |
| `BG0554` | Medium | survivor severity under-rates the explicit return-None idiom, which is the shape that matters most in this codebase |
| `BG0555` | Medium | twelve scripts declare --root only per-subcommand, a grammar defect the conformance sweep could not see because it silently skipped them |
| `BG0556` | Medium | no guard catches a --root that selects the file written but not the content read |
| `BG0561` | Medium | a re-plan over an open run resets the appetite to the standing capacity while leaving the resize record standing, so the ledger and the breaker dis... |
| `BG0562` | Medium | _then_clause strips the bold markers off a non-bulleted Then line before testing for them, so the criterion falls back to its whole block and the o... |
| `BG0563` | Medium | the test-plan edit-verb vocabulary enumerates only subtractive verbs, so a mutant that ADDS something cannot be stated and gets reworded until it p... |
| `BG0564` | Medium | a creation whose basename is a common one - `__init__.py`, `README.md` - is still refused as a typo, so the greenfield repair is incomplete for exa... |
| `BG0565` | Medium | has_run_history is non-recursive, so a project that archives its retros into a subdirectory reads as never having closed a sprint and is silently s... |
| `BG0567` | Medium | the upgrading-project baseline compares against this tree minus one branch, not against the base ref, so a regression the epic introduced elsewhere... |
| `BG0571` | Medium | The repaired spec-agreement guards pin word patterns rather than claims, so a passage stating the OPPOSITE rule passes |
| `BG0572` | Medium | The repo-writes guard attributes any concurrent edit to the test run, so editing during a 15-minute background commit refuses it and names the auth... |
| `BG0574` | Medium | A --dry-run takes the allocation lock on the target repository, so a preview writes into the tree it was asked only to describe |

41 findings: 40 Medium, 1 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
