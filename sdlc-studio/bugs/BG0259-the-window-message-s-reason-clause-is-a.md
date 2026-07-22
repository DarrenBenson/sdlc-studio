# BG0259: The window message's reason clause is a single static string, so an assertion on it pins a WORD and an inverted clause survives the whole suite

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py,.claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by round 7 of RUN-01KY3MFX. `window open`'s whole-tree branch prints one static sentence naming all five causes (empty, `.`, absolute, traversal, glob) for EVERY input that reaches it. Round 6 had found the clause stale for globs, and the repair added an `assertIn("glob", msg)` inside the loop that covers `.`, `./`, `/etc/hosts`, `*`, `**` and `?*`. That assertion fires identically for all six, including the three that are not globs, so it cannot do what its own failure message claims - 'the reason clause must cover why THIS claim is total'. Proven by mutation: rewriting the clause to 'a glob matching no path at all such as `zz` or `qq` - none of these match everything' left the FULL shipped suite green, 3,939 tests, run as a whole discovery rather than the narrow class precisely because sibling guards have masked branches five times on this sprint. A message that contradicts itself in one sentence is currently green. A second mutant deleting the four original causes and keeping only the glob clause also survived. This is the defect the module in the very same delta exists to reject: a substring grep is a presence check, and presence does not establish meaning.

## Steps to Reproduce

1. Edit the whole-tree scope string in mutation.py's `cmd_window` so the clause asserts the opposite of what it means, for example replacing 'a glob matching every path such as `*` or `**` - all of these match everything, not nothing' with 'a glob matching no path at all such as `zz` or `qq` - none of these match everything'. 2. Purge `__pycache__` and run the full skill suite with python3 -B. Observed: 3,939 tests pass. Expected: the assertion covering the glob shapes fails, because the sentence it reads now denies the verdict the same command prints.

## Proposed Fix

Print only the cause that APPLIES to the claim in hand, rather than a static list of five. Once the sentence varies with the input, a per-claim assertion becomes possible and the surviving mutants die: the test can assert that a dot-claim's reason names the dot and not a glob. Related and worth fixing together: the clause says 'a glob matching every path', but `claims_everything` probes six paths, so `[a-zA-Z.]*` matches every probe without matching every path and is announced as WHOLE TREE while a commit staging `9data.txt` proceeds. Over-warning, which is the safe direction, but the words claim more than the code establishes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
