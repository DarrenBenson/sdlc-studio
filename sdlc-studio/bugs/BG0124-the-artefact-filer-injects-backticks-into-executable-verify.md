# BG0124: The artefact filer injects backticks into executable Verify lines, producing false-green ACs

## WITHDRAWN - not a bug, the defence already exists

**This bug is wrong and is retained only as the evidence trail for [[LL0024]].**

`artifact.py` routes `--verify` through `_verifiers_of()`, which passes the command through
**verbatim** and never markdown-safes it. Its docstring already describes both failure modes this
bug "discovered" - a corrupted literal argument under a list-form verb, and command substitution
under a shell-backed one - and concludes: *"Verbatim is the only form that is both correct and
safe."* Someone had already thought this through and defended it.

Proven end-to-end, which is what should have been done before filing:

```text
artifact.py new --type story --verify "shell rg -q retro .../scripts/file_finding.py"
stored:  - **Verify:** shell rg -q retro .../scripts/file_finding.py
         (verbatim - no backticks - the guard holds)
```

**How the false finding was reached.** `_md_safe()` was called **directly**, in isolation, on a
verify-shaped string. It does backtick snake_case tokens - that is its job, and it is correct for
the prose it is actually given. But the real pipeline never hands it a Verify line. The hazard was
real; the exposure was zero; the guard was already there and documented. Testing the helper proved
nothing about the path (LL0014, LL0017).

The original AC corruption that started this hunt was self-inflicted: a shell command was written
into `--ac` **prose**, where commands do not belong, instead of into `--verify`. The tool then
correctly markdown-safed the prose it was given.

Everything below is the original, incorrect report, kept for the record.

---

> **Status:** Won't Fix
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 workstream
> **Raised-by:** sdlc-studio; agent; v1
> **Severity:** High

## Summary

artifact.py runs `file_finding._md_safe()` over every AC item, including the Verify: command. `_md_safe` backtick-wraps `snake_case` identifiers to avoid markdown emphasis lint (MD037) - correct for prose, catastrophic for a command. `verify_ac.py` executes Verify lines with shell=True, where backticks are COMMAND SUBSTITUTION. Every Python script path is `snake_case`, so the filer corrupts the very ACs that gate a story to Done. Proven three ways. Outside quotes: 'rg -q retro scripts/`file_finding.py`' is stored as 'rg -q retro scripts/`BACKTICKfile_finding.pyBACKTICK`'; the shell tries to EXECUTE `file_finding.py`, fails, substitutes empty, and rg searches the DIRECTORY instead of the file - exit code 0, AC PASSES for the wrong reason (false green). Inside quotes: backticks become literal regex characters, so the AC can never match (permanent false red). And had the backticked token been a real command on PATH, the filer would have caused it to run. This is LL0008 in the verifier itself - a tool reporting a success it did not achieve - and it undermines the trust chain that makes 'Done' mean anything.

## Steps to Reproduce

python3 -c "import sys; sys.path.insert(0,'.claude/skills/sdlc-studio/scripts'); import `file_finding` as ff; print(`ff._md_safe(`'rg -q retro scripts/`file_finding.py`'))"  # -> backticks injected around `file_finding.py`; run that under shell=True and rg searches the directory, rc=0

## Proposed Fix

Three legs. The first stops the corruption; the second and third stop it recurring invisibly.

1. **Never rewrite an executable.** `_md_safe` must not touch the command portion of an AC. Split
   each AC at its `Verify:` boundary; normalise only the prose half and pass the command half
   through byte-for-byte. Guard it with a test asserting a Verify line survives the filer
   unchanged, and validate that test against THIS bug before trusting it (LL0010) - a Verify line
   naming a snake_case path must come out identical.

2. **Announce the rewrite.** Any normalisation the filer applies to caller input must be reported
   (e.g. `normalised: 3 token(s) backticked in Summary`), not performed in silence. Silent
   mutation is why this survived: the caller passed one string, a different string was stored, and
   nothing said so. A tool that quietly rewrites its input is indistinguishable from one that
   corrupts it.

3. **Document it.** `reference-scripts.md` is the catalogue an agent is told to read before doing a
   mechanical task by hand, and it describes what each script DOES, not that it mutates what you
   give it. Record which scripts normalise caller input, and what they will and will not touch. An
   undocumented input transform is a trap for every agent after this one.

## Acceptance Criteria

- [ ] **AC1:** A Verify command survives the filer byte-for-byte, including a `snake_case` path:
      the stored line is character-for-character the one the caller supplied, with no backtick
      introduced anywhere in it. Pinned by the `md_safe` unit tests.
- [ ] **AC2:** The defence is validated against the bug it defends (LL0010): filing a story AC
      whose Verify names a `snake_case` path, then reading the artefact back and running it
      through `verify_ac`, executes the intended command - not a directory search, and not a
      command substitution. Pinned by the filer unit tests.
- [ ] **AC3:** The filer reports any normalisation it applied to caller input rather than doing it
      silently: a caller whose prose was rewritten sees which field was touched and how.
- [ ] **AC4:** The scripts catalogue (`reference-scripts.md`) records which scripts rewrite caller
      input and what they will never touch, so the next author does not rediscover this by
      shipping a corrupted verifier.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
