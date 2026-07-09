# v4.0.0-rc.1 readiness checklist (US0109 / CR0198)

Cutting `v4.0.0-rc.1` is a checklist read, not a judgement call. Every gate below has a live
check command; recompute them immediately before tagging (do not trust a stale number). The tag
cut, freeze lift, and push to consuming projects are an explicit operator action once ALL gates
read green.

> **Computed:** 2026-07-09 · re-run each check before the tag.

| Gate | Live check | State (2026-07-09) |
| --- | --- | --- |
| Portable gate green | `scripts/gate.py --root .` | GREEN - `gate: PASS` |
| Version homed at 4.0.0-rc.1 | `tools/check_versions.py --strict` | GREEN - consistent (core 4.0.0) |
| Migration rehearsed on 2 real projects | `sdlc-studio/reviews/v4-migration-rehearsal.md` | GREEN - rehearsed; BG0070 found, fixed, re-rehearsed sub-second |
| EP0014 closed | `scripts/status.py backlog --type epic` (or grep EP0014 status) | GREEN - EP0014 Done |
| Open-bug count 0 | `scripts/status.py backlog --type bug` | GREEN - 0 non-terminal bugs (`Fixed` is a terminal/resolved status per the shared vocab; BG0067-0070 are Fixed. US0112 further closes them to `Closed` as completeness) |
| Reconcile drift 0 | `scripts/reconcile.py detect` | GREEN - drift 0 |
| Full suites green | script + tools unittest discover | GREEN - 1455 + 108 (recomputed 2026-07-09, RV0007) |
| Full repo lint green (not just the portable gate) | `npm run lint` exits 0 | GREEN - fixed under BG0075 (was RED at rc prep: six commits landed markdown breakage while the hook was disabled) |
| Commit gate enabled in the tagging clone | `git config core.hooksPath` = `.githooks` | GREEN - enabled under BG0075; run `bash tools/enable-hooks.sh` in any new clone |
| Eval scenarios re-run for the major | 4 scenarios per `evals/README.md`; record the run | GREEN - 4/4 PASS 2026-07-10, see `v4-eval-run-2026-07-10.md` (BG0079; gate added - it was missing from this checklist despite release-gate sections 1 and 8 mandating it) |

## Verdict

**GREEN on the rc gates (2026-07-09).** Every gate above reads green: the open-bug gate uses the
shared vocabulary's terminal set (via `status.py backlog`), under which `Fixed` is resolved, so
the non-terminal bug count is 0. US0112 additionally closes the four Fixed bugs to `Closed` for
completeness, but that is polish, not an rc blocker. The tag cut, freeze lift, and push remain an
explicit operator action - the checklist being green makes it a clean go/no-go, not a judgement
call. Re-run each check immediately before tagging.
