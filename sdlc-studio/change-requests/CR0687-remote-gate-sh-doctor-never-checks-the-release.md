# CR-0687: `remote-gate.sh doctor` never checks the release gate's prerequisites, so a host reads ready and then refuses at the release cut

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Enhancement
> **Size:** S
> **Affects:** tools/remote-gate.sh, tools/tests/test_remote_gate_doctor.py, tools/tests/test_gate_prereqs.py
> **Evidence:** devserver1 on 2026-11-07, after the operator installed Python 3.10.22 and pdftotext 26.01.0. `ssh devserver1 '. ~/sdlc-gate/gate-env.sh; command -v python3.10 uv'` found neither. After the PATH fix, `gate_prereqs.py check --refusing --host --release` on the host exited 0.
> **Date:** 2026-11-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-07T17:06:10Z

## Summary

`remote-gate.sh doctor` calls `gate_prereqs.gaps(Path("."), host=True)` without `release=True` (`tools/remote-gate.sh`, the doctor's embedded check). It therefore never reports Python 3.10 or pdftotext, the two tools the release gate's own criteria run (BG1220). The host's preflight refuses on them only when `remote-gate.sh release` is already running, with exit 4. Found on 2026-11-07 before the 6.3 cut: the operator had installed Python 3.10 in `~ops/.local/bin` on devserver1, which an ssh command's PATH does not include. The host's `~/sdlc-gate/gate-env.sh` did not add it either, so under the gate's PATH neither `python3.10` nor `uv` resolved, and the release preflight would have refused at the cut. Nothing before the release said so. `doctor` exited 0, and `enable-hooks.sh` runs `doctor`. The orchestrator found it only by sourcing `gate-env.sh` by hand over ssh, then fixed the host by appending `$HOME/.local/bin` to that file's PATH.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Have `doctor` also report the release prerequisites, as notes that do not change its push verdict, or behind a `doctor --release` that exits 1 on a gap. Either way the check must run under `gate-env.sh`, as the gate does. Name the fix in each line: put the tool on the PATH `gate-env.sh` sets, last, so the venv's `python3` still wins.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-07 | Claude Opus 5.5 | Raised |
