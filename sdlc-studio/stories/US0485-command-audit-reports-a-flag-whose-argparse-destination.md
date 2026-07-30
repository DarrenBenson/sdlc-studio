# US0485: command_audit reports a flag whose argparse destination no line ever reads

> **Status:** Done
> **Delivers:** CR0448
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py, .claude/skills/sdlc-studio/reference-scripts-review.md, .githooks/pre-commit, package.json, tools/tests/hookutil.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_message_first_gate.py, tools/tests/test_dead_flag_docs.py, AGENTS.md, CHANGELOG.md
> **Epic:** EP0175
> **Points:** 5

## User Story

**As a** operator trusting a documented flag to change what a command does
**I want** a flag whose destination is never read to be reported as dead
**So that** a flag cannot ship wearing live documentation while doing nothing

## Acceptance Criteria

### AC1: a flag whose destination is never CONSUMED is reported

- **Given** a module defining a flag whose parsed value is passed on but never consumed by any line that acts on it
- **When** the detector runs
- **Then** it reports that flag, naming the module and the destination - the analysis follows the value into the callee rather than counting the sites that mention it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_flag_whose_value_is_never_consumed_is_reported
- **Verified:** yes (2026-07-30)

### AC2: it is proven on verify_batch as gate.py carries it today

- **Given** gate.py's three live verify_batch sites - the argparse definition, the defaulted lookup that forwards it, and the run_gate parameter no line of the body reads - pinned as a fixture rather than described as a past state
- **When** the detector runs over that fixture
- **Then** it reports verify_batch, so the defence is validated against the exact shape that motivated it; this holds whether or not US0479 has deleted the flag, because the fixture pins the three lines
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_the_detector_catches_verify_batch_from_a_pinned_fixture
- **Verified:** yes (2026-07-30)

### AC3: a defaulted lookup whose value IS consumed is not reported

- **Given** a flag read through a defaulted attribute lookup whose receiving parameter is then acted on
- **When** the detector runs
- **Then** it does not report that flag - the discriminator is consumption, not the access pattern, which is what made the first specification unable to catch verify_batch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_a_consumed_defaulted_lookup_is_not_reported
- **Verified:** yes (2026-07-30)

### AC4: the detector runs where it can be seen

- **Given** the repo's quality gate
- **When** it runs
- **Then** the dead-flag report is one of its lanes, because a detector nothing invokes cannot stop a flag shipping
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_the_detector_is_wired_into_the_gate
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
| 2026-07-27 | Claude Fable 5 | ACs repaired against the independent adversarial review |
| 2026-07-30 | Claude Opus 5 | Delivered. Detector in `command_audit.py --dead-flags`, wired as a gate lane in `.githooks/pre-commit` and the `lint` chain; 37 tests in `test_command_audit.py` green; 14/14 mutants killed (unique anchors, purged bytecode) |

## Evidence

Run against the real `gate.py` at the revision before US0479 deleted the flag
(`git show d982e31a^:.claude/skills/sdlc-studio/scripts/gate.py`): `--verify-batch` reported
**dead**, nothing unjudged. That run needs git history, so AC2's contract is pinned as the three
lines verbatim in `GATE_FIXTURE` instead.

Getting there took four false-positive classes out, each of which named a **live** flag as dead:

| Shape | Reported dead | Verdict now |
| --- | --- | --- |
| A positional (`add_argument("cmd", choices=[...])`) | `digest`, `schema_check` | not judged - argparse enforces presence; it also printed a `--cmd` switch that does not exist |
| A shared declarator (`add_ids_argument`, `add_format_arg`, `add_global_root`) | 4 in `lib/sdlc_md.py` | not judged - the module never parses |
| A computed `getattr` (`{k: getattr(args, k, None) for k in keys}`) | 4 in `decisions`, `ledger` | not judged - the destination read cannot be named |
| A namespace read straight off `parse_args()` | `tools/whitepaper_pdf.py --out` | judged clean - `ap.parse_args().out` binds no name |

And three shapes cost the analysis its verdict on the flag that mattered, all found by running it
against the real corpus rather than the fixture: `args is not None` read as a namespace escape (it
made every flag in `gate.py` cannot-judge, the dead one included), a nested `def _git(*args)` read
as the namespace, and a verb table registered by loop variable (`for name, fn, ... :
set_defaults(func=fn)`), which left all thirteen of `retro.py`'s flags unjudged.

Live corpus: 91 modules, **0 dead**, 8 destinations not judged - each printed with its reason,
since a destination nobody could judge reads as one that passed. Lane cost ~6s, AST only.
