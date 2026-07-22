# BG0250: quality.epic_requires_test_spec is documented as the caller's opt-out but is read by no Python code in the tree

> **Status:** Fixed
> **Verification depth:** functional - the four documentation surfaces were re-read against the code after the change and each now describes the read that exists; 7 of 8 new tests RED first (the eighth cannot be red before the change and exists only to stop the opt-out over-reaching to a passing run); 8 hand-mutants, bytecode purged and each patch asserted to have changed the file on disk, all 8 killed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py,.claude/skills/sdlc-studio/reference-config.md
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found while fixing BG0241. `epic_test_spec_check`'s docstring names `quality.epic_requires_test_spec` as the lever a caller uses to opt out of the hard epic-scope test-spec requirement, and AGENTS.md describes the gate as configurable in the same terms. A grep across the tree finds the key read by NO Python code. So either the gate cannot be turned off at all while the documentation says it can, or it is enforced somewhere that does not consult the key - and in both cases a consuming project setting it in good faith gets no effect and no warning. This is the project's own recurring defect class stated exactly: prose asserting a property the code does not have, which has been the surviving MAJOR in four consecutive closing reviews. It matters more now than it would have last month, because BG0241 has just made epic-ts FAIL for an epic whose only spec asserts no coverage, and the measured migration cost is 30 of 178 specs across the workspaces on this machine. Any project reaching for the documented opt-out to stage that migration will find it does nothing.

## Acceptance Criteria

- [x] **AC1:** Setting `quality.epic_requires_test_spec: false` in a project's `.config.yaml`
      changes the behaviour of the epic test-spec check, so the four documentation surfaces
      describing it as an opt-out are true of the code.
      Pinned by `test_verify_ac.EpicTestSpecOptOutTests`.
- [x] **AC2:** With the key absent, behaviour is unchanged, so an existing project sees no
      difference.
      Pinned by `test_verify_ac.EpicTestSpecOptOutTests`.
- [x] **AC3:** A non-boolean value warns naming key and value and falls back to ENFORCING, so a
      typo never silently drops a gate.
      Pinned by `test_verify_ac.EpicTestSpecOptOutTests`.
- [x] **AC4:** The findings stay the findings under the opt-out: enforcement changes the exit
      code, not what the check reports.
      Pinned by `test_verify_ac.EpicTestSpecOptOutTests`.

## Steps to Reproduce

1. Read the docstring of `epic_test_spec_check` in `verify_ac.py`, which names `quality.epic_requires_test_spec` as the caller's opt-out. 2. Search the tree for that key in Python source. Observed: no read site. 3. Set the key false in a project's sdlc-studio/.config.yaml and run the epic-ts check. Observed: behaviour is unchanged and nothing reports that the setting was ignored.

## Proposed Fix

Establish first which is true - the key is unimplemented, or it is implemented under another name - because the remedy differs and guessing produces a second false claim. If unimplemented, either wire it where the docstring says it is read, or delete the promise from the docstring and from any consuming-facing documentation; a documented lever that does nothing is worse than no lever, because it is acted on. If it is read under another name, reconcile the two. Whichever it is, add a test that sets the key and asserts the behaviour actually changes, so the documentation and the code cannot drift apart again silently. Consider a broader sweep for config keys named in prose and read by nothing - this one was found by accident.

## Resolution

Established first, as the bug asked: the key was UNIMPLEMENTED, not implemented under
another name. A grep of every `.py` in the tree found `quality.epic_requires_test_spec` in
one place only - the `epic_test_spec_check` docstring that promises it - against the three
sibling keys (`done_requires_verified`, `depth_parity_gate`, `mutation_max`) which each have
a real read site. Nothing renamed it; nothing else enforced it.

Fixed by making the code read it, not by deleting the promise. `verify_ac.py` gains
`epic_ts_enforced(repo_root)`, reading `quality.epic_requires_test_spec` from
`sdlc-studio/.config.yaml` through `sdlc_md.project_override` - the same
gracefully-degrading reader the sibling gates use, so a machine without PyYAML gets the
default rather than a config crash. `epic_test_spec_check` returns the value as `enforced`
alongside `ok`, and `epic-ts` exits 1 only when the check failed AND the project enforces.

`ok` deliberately does not move with configuration. An opt-out that flipped the verdict
would hide the specs a project mid-migration still owes, which is a worse feature than no
opt-out: the findings are printed either way, and a FAIL that exits 0 says
`advisory only (quality.epic_requires_test_spec: false)` on the verdict line, so an exit
code that disagrees with the printed word never goes unexplained.

The default is unchanged. A project that sets nothing enforces exactly as before, which is
pinned by its own test rather than argued. A value that is neither `true` nor `false`
(`maybe`, a quoted `"false"`, a list) is the same defect in miniature - a setting acted on in
good faith that cannot be honoured - so it warns on stderr naming the key and the value, and
falls back to enforcing. Failing safe matters here: guessing that a non-boolean meant "off"
would drop a gate on a typo.

All four documentation surfaces were rewritten to describe the read that now exists:
`reference-config.md`, `reference-scripts-verify.md`, `reference-epic.md` and the docstring.
Two adjacent claims were corrected while there. "Single-story work is exempt" implied a
story-scope exemption in the code; the check is epic-scope by construction, reached only
through `epic-ts --epic`, so nothing invokes it for single-story work. And `reference-epic.md`
said the requirement was "gated" before Done without saying by what: `transition.py` has no
test-spec gate, so the requirement is carried by running `epic-ts`, and the file now says so.

Pinned by `EpicTestSpecOptOutTests` in `tests/test_verify_ac.py`, 8 cases: the key false
lifts the gate; the findings survive the opt-out and the reason is printed; no config at all
still enforces; the key true enforces (killing a read of mere presence); an unrelated
`quality.*` key does not lift it (killing a read of the wrong key); a passing epic is never
reported as advisory; a non-boolean warns and keeps enforcing; the JSON output carries
`enforced`. 7 were RED first.

Mutation-proven by hand, bytecode purged and `python3 -B`, each patch asserted to have
changed the file on disk before the verdict was trusted, and the restore asserted after.
8 mutants, 8 killed, no survivors first time: invert the config read; hard-code `enforced`
true; compute the advisory from `ok` alone; a non-boolean falling back to off; delete the
unhonoured-value warning; delete the advisory reason from the verdict line; flip the
`project_override` default to false; make the advisory ignore the outcome so a passing run
reports advisory.

Left undone, deliberately, and named rather than skipped: a project can still set an unknown
or misspelt `quality.*` key and hear nothing. Fixing that class needs a registry of the keys
the tooling reads plus a check that walks `.config.yaml` against it, which lands in
`config.py` and a lint, not in `verify_ac.py`. This bug closes the one documented key that
lied; the general sweep the Proposed Fix asks for is a separate unit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-22 | claude | Fixed: the key is read by `epic_ts_enforced`, `epic-ts` gates on it, all four documentation surfaces rewritten to match; 8 tests (7 red first), 8 hand-mutants all killed |
