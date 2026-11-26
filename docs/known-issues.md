# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v6.5 is held to

**Fewer than 50 open bugs at the tag, and none at Medium or above.** The release waits for
that target rather than for a date. A finding either reaches a terminal status or ships open at
Low severity, listed below by id.

**Low findings ship open, listed here by id, triaged to v6.6.** Each is a real
defect with a reproduction and, in most cases, a proposed fix. None of them stops the
lifecycle running. They are listed rather than closed, because closing a bug to make a
release look clean is the practice this tool exists to prevent.

Each id below is a file in `sdlc-studio/bugs/` in the source repository, carrying the
evidence, the reproduction and the proposed fix in full.

## The bar v6.0 was held to, kept as history

**Zero open Critical or High finding at the tag, and every open Medium ruled by one triage
decision.** A finding either reaches a terminal status with its own verifiers passing, or it
stays open under the triage target below, which one recorded decision rules for the whole list
rather than a waiver per finding.

## The bar v5.1 was held to, kept as history

**Zero open High-severity bugs at the tag, and every Medium disposed of or ruled.** A
finding either reaches a terminal status with its own verifiers passing, or it stays open
carrying a dated ruling that says why it ships.

## The bar v5.0.0 was held to, kept as history

**Zero open High-severity bugs at the tag.** Every High finding raised against v5 was
fixed and closed before the tag was cut. The bar was originally zero open bugs of any
severity; it moved on 2026-08-11, because holding a release for findings that are real
but not release-blocking had cost a month and was buying nothing a disclosure could not
buy honestly.

## Triaged to v6.6

| Id | Severity | Finding |
| --- | --- | --- |
| `BG0946` | Low | reports/_index.md Last Updated is not restamped when a report is filed |
| `BG0953` | Low | Full-template story and TSD ship unrendered {{config.story_quality.*}} placeholders |
| `BG0964` | Low | help/refine.md never mentions `--into`, so a story added to an already-refined epic is made with `artifact.py new` and carries no Delivers link |
| `BG0966` | Low | review_prep persona_usage calls a persona unused unless its file's H1 appears verbatim in prd.md - stories, CRs and consult logs are never read |
| `BG0977` | Low | help/status.md documents '/sdlc-studio status --brief' but status.py has no --brief, so the documented one-line summary errors |
| `BG0984` | Low | Changing a criterion's Verify expression keeps the old Verified date and evidence when the new one passes |
| `BG1008` | Low | A waiver recorded before the run can answer a checklist row while the page's Waivers in force section says no gate stood down |
| `BG1011` | Low | LL0056 ships with its label doubled and the template's placeholder sections left in, and nothing refuses a lesson with an unfilled placeholder |
| `BG1018` | Low | refine apply --question leaves the request ending on a blank line, which markdownlint refuses (MD012) |
| `BG1024` | Low | verify_ac's grep verb takes a leading flag as the pattern, so `grep -q -e X file` and `grep -E ... file` Verify lines fail |
| `BG1055` | Low | A retro scaffolded by the close and committed before the close re-runs turns the release-verify lane red |
| `BG1064` | Low | 15 of 69 shipped scripts are tracked without the executable bit the TRD's script contract requires, a regression of CR0064's fix |
| `BG1079` | Low | A unit carried at the review cap gets a criterion for every ISSUES item, including info rulings and pre-existing findings already filed |
| `BG1146` | Low | lessons.py revalidate --close appends its Status bullet straight after a paragraph, so the lessons log fails markdownlint MD032 |
| `BG1200` | Low | mutation.changed_lines reports no lines when git's color.ui or color.diff is always, because the +++ b/ header arrives wrapped in ANSI codes |
| `BG1276` | Low | The footprint counter splits Affects on every comma, so a path inside a bracketed note is dropped from the unit's file count |
| `BG1277` | Low | The close's closing-review row does not credit a unit carried at the review cap whose carrying bug was fixed and approved in the same run |
| `BG1283` | Low | One old Codex thread whose rollout file is gone makes every later Codex reading in that workspace unmetered, permanently |
| `BG1319` | Low | Five Copilot model ids priced from the shared OpenAI entries stay token-priced under `pricing.copilot_billing: requests`, so a request-billed Copil... |
| `BG1365` | Low | sprint_report.py build of a signed run ignores the time window saved on its signed page |
| `BG1435` | Low | retitle leaves a reference-style link definition and a link in the project-root README dangling, while its changelog says it finds every link to th... |
| `BG1466` | Low | A signed report's signoff principal and signed_at figures still read not yet signed, though the evidence schema says they hold who signed and when |
| `BG1467` | Low | A review-cap carry bug copies the carried unit's Affects verbatim, so it declares the unit's changelog fragment, not its own |
| `BG1566` | Low | The generated reference catalogue in help/references.md links all 58 references to paths that do not exist |
| `BG1572` | Low | The evidence pack crashes with a traceback on a malformed report instead of refusing it by name |
| `BG1576` | Low | The skill-tests lane's serial_only collection may read empty under an inherited -q, so serial tests could be skipped unseen |
| `BG1613` | Low | ci.wait_timeout_minutes has no reader: the trunk guidance's wait fence hardcodes `timeout 30m`, so a project's override changes nothing |
| `BG1615` | Low | mutation.py run --edits counts an edit that does not compile as killed and exits 0, and silently ignores --format and --max-mutations |
| `BG1642` | Low | config.py show prints a RuntimeError traceback without PyYAML instead of the one-line refusal |
| `BG1665` | Low | critic.py record refuses a parallel second seat's verdict once the first seat's REJECT is recorded, so its REJECT never reaches the ledger |
| `BG1669` | Low | reference-scripts-review.md does not describe persona_review.py owed |
| `BG1670` | Low | persona_review.remedy names a brief command for a card held by a blocking rule, whose PASS persona_review.py record then refuses |
| `BG1671` | Low | init.py writes no personas.standard, so a project created at the persona-standard release is switched to report mode by its first later project upg... |
| `BG1679` | Low | transition.py moves a story from Draft to Ready without checking its Definition of Ready, so Draft to Ready to Done skips the gate BG0954 adds |
| `BG1696` | Low | sprint drive's headless review passes no effort, while the sprint report says the reviewer ran at the plan's stamp |
| `BG1708` | Low | verify_ac.py ts-check reports two test ids pytest collects: a file under a dotted directory in importlib form, and a def whose decorator gives it a... |
| `BG1722` | Low | `conformance.adopt_after` takes a schema v3 cutoff on a schema v2 project, so the conformance lane exempts every sequential unit |
| `BG1733` | Low | transition.py drops a status decoration such as '(partially superseded)' on every move |
| `BG1738` | Low | A run whose sessions all run on Claude and hold their subagents drops a claude -p lane run's delegated total |
| `BG1740` | Low | reference-review.md lists the optional claim surfaces without the declared pages |
| `BG1741` | Low | The retro judges a run whole from another harness's session when the closing session has no closing stamp, and drops a supplied delegated total |
| `BG1753` | Low | A high-risk unit goes Fixed on one seat's round-two APPROVE after the second seat's REJECT |
| `BG1754` | Low | A story moved to Blocked by decision defer --block stays Blocked after its last blocking decision is resolved |
| `BG1755` | Low | The prose escaper spans a bare URL written straight against an author's code span so the two spans touch |
| `BG1756` | Low | A plan refused for a criteria problem other than a missing Verify line names only the Affects and Points template |
| `BG1757` | Low | A commit can stage a review-ledger row whose ruling cites a decision the commit does not carry |
| `BG1764` | Low | The cost anatomy reads no reviewer recorded with its seat, so the report's reviewer row shows 0 agents and review spend lands under other |
| `BG1765` | Low | A carry is always filed at Medium, so a unit that checks a release bar barring Medium cannot close its own carry |

48 findings: 0 Medium, 48 Low.

## Not carried

40 findings at a barred severity were ruled `Won't Fix` on their own merits: `BG0124`,
`BG0139`, `BG0421`, `BG0537`, `BG0547`, `BG0583`, `BG0634`, `BG0691`, `BG0696`, `BG0699`,
`BG0700`, `BG0701`, `BG0703`, `BG0705`, `BG0706`, `BG0707`, `BG0708`, `BG0712`, `BG0713`,
`BG0714`, `BG0721`, `BG0723`, `BG0728`, `BG0729`, `BG0734`, `BG0739`, `BG0741`, `BG0752`,
`BG0754`, `BG0828`, `BG0830`, `BG0836`, `BG0838`, `BG0840`, `BG0857`, `BG0863`, `BG0864`,
`BG0951`, `BG1281`, `BG1509`.

32 findings at a barred severity were superseded by later work: `BG0271`, `BG0534`,
`BG0620`, `BG0632`, `BG0638`, `BG0639`, `BG0679`, `BG0680`, `BG0683`, `BG0684`, `BG0685`,
`BG0686`, `BG0688`, `BG0689`, `BG0690`, `BG0693`, `BG0694`, `BG0697`, `BG0698`, `BG0702`,
`BG0704`, `BG0710`, `BG0720`, `BG0724`, `BG0727`, `BG0732`, `BG0735`, `BG0738`, `BG0740`,
`BG0841`, `BG1052`, `BG1087`.

They are not in the list above because they are not open, and a disclosure that pads
its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py` when a release is cut, not
maintained by hand, and the pre-push hook refuses a tag whose page disagrees with the corpus.
Any open bug whose severity is Medium or Low appears here; a bug that reaches a terminal
status leaves at the next cut. Cut it with
`python3 tools/known_issues.py write --release <version>`.
