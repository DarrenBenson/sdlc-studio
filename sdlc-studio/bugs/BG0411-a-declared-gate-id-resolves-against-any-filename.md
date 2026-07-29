# BG0411: A declared gate id resolves against any filename matching the id pattern, and a withheld narrowing is announced only under SDLC_DEBUG

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; each repair verified by applying its own mutant and watching it redden, bytecode purged, python3 -B)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Round-2 independent review of commit 06c806d7, repair 3. Walk cost measured at 3ms/2,032 files and 18ms/11,041 files, so the resolution itself is cheap.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** round-2 independent review; human; v1

## Summary

Requiring a declared id to resolve does close the reported false green - a typo'd `BG288` for `BG0288` no longer narrows the tree to nothing, and the mutant that voids the check is killed. Two problems remain.

**It is defeated by an unrelated file, not only by an adversary.** `_path_artefact_id` matches the BASENAME against `^(?P<id>[A-Z]{2,4}-?\d{3,4})[-.]` - any file, any extension, with no check that it is an artefact. One stray `sdlc-studio/BG288-repro.png` makes the typo resolve and restores the false green in full:

```text
scopes: {'sdlc-studio': frozenset({'BG288'})}
is_test_relevant('sdlc-studio/bugs/BG0288-named.md', structural={...}) -> False
```

A screenshot, an attachment or a scratch note is enough. The check validates a filename pattern, not the existence of the artefact it claims to require.

**The failure is silent.** The only report of a withheld narrowing is `sdlc_md.debug(...)`, a no-op unless `SDLC_DEBUG=1` (lib/`sdlc_md.py`:322). In a commit whose stated thesis is that these nine defects "fail SILENTLY - the direction this project's design says a guard must never fail", this one converts a silent false green into a silent permanent full-suite penalty. The declaration is dead and nobody is told; the author sees only a gate that never gets faster.

Ordering nit while the file is open: `_declared_ids(...)` is called at gate.py:2277, BEFORE the `rel not in paths`, protected-prefix and `isdir` filters - so an entry immediately discarded still pays its walk.

## Steps to Reproduce

1. Declare a typo'd id (`BG288` for `BG0288`) and confirm the narrowing is correctly withheld.
2. `touch sdlc-studio/BG288-repro.png`, re-run: the id resolves and the false green returns.
3. Declare an id that resolves to nothing and run the gate without `SDLC_DEBUG=1`: nothing is printed about the withheld narrowing.
4. Read gate.py:2277 - the walk precedes the filters that would discard the entry.

## Proposed Fix

1. Resolve a declared id against the ARTEFACT index rather than a filename pattern - the id has to name a real artefact, which is what the check says it requires. `sdlc_md`'s by-id index already answers this and is memoised.
2. Report a withheld narrowing on the normal output path, not through `debug`. A declaration that has stopped working should be as visible as one that never worked; today it is less visible.
3. Move the `_declared_ids` call after the filters that can discard the entry.

## Acceptance Criteria

- [ ] A declared id resolves only when it names a real artefact; a file merely matching the id filename pattern does not satisfy it.
- [ ] A withheld narrowing is reported on the gate's normal output, naming the declaration and why it did not resolve, without `SDLC_DEBUG.`
- [ ] A test asserts that a stray non-artefact file named after a typo'd id does not restore the narrowing.
- [ ] `_declared_ids` is not called for an entry the subsequent filters discard.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | round-2 independent review | Filed |
