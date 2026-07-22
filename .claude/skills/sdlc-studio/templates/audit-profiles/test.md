# Audit Profile: test

The packaged lens pack for the claims a codebase makes **about itself** - what a test,
a docstring or a comment asserts, held against what the code beside it actually does.
Use it as the qualitative backstop to a mutation run: a surviving mutant proves a test
cannot fail, and says nothing whatever about a docstring that lies.

> **Refute panel:** shared - 3 skeptics per candidate, survive on >= 2 of 3
> (`reference-audit.md#audit-refute`). This pack does not opt out.

**Default scope: source and tests together.** The failure modes below are claims written
in prose about code, and they sit in source at least as often as in test files. Pointing
this pack at the test directory alone excludes the larger half of its own evidence.
Narrow the scope explicitly when the change under audit is test-only.

Use each row as the `{{lens}}` / `{{lens_question}}` of `audit-finder.md`, one finder
per lens, looped until-dry; then the shared refute panel and filer.

| Lens | Adversarial question | Hunts for | Drawn from |
| --- | --- | --- | --- |
| can-it-fail | Which edit to the code would leave this test green? | a guard every caller short-circuits, so deleting it changes no result; an assertion that holds whether or not the property does; a gate checking that a file exists rather than what is in it; a defence never once run against the failure it defends against; an exit-code assertion where the failure mode is "it did not run" | LL0010, LL0015, LL0023 |
| reaches-the-code | Does this test enter the branch its name claims to pin? | a cheaper guard failing first and sending the fixture down another path; a fixture too thin to reach the case named; every reference to the function under test being a patch(); a payload hand-built to the shape the parser is assumed to want; no marker asserted for the branch actually taken | LL0017, LL0022 |
| docstring-vs-assertion | Which property does this prose assert that the code does not provide? | a docstring naming a bound the code never enforces; "equivalent", "nothing is lost" or "the fallback takes over" with nothing executing the claim; a comment describing an assertion the test does not make; a summary line reporting work that was skipped; a count or version frozen in prose and since rotted | LL0008, LL0028 |
| incidentally-green | If the property under test were removed, what else would keep this green? | a fixture supplying what production must supply for itself; a mocked boundary standing in for the code the test names; a match on a string the output carries either way; a default that satisfies the assertion with the feature gone; a cached artefact meaning the pre-change code ran | LL0014, LL0020 |

## Filing (binding)

Every candidate that survives the refute panel is either filed through `file_finding.py`
or declined with a stated reason. Silence on a candidate is not an outcome of this run.
A declined candidate keeps its reason in the run report, so a later reader can tell a
judged candidate from an unexamined one.

## Notes

- This pack is declarative: a lens is a name + an adversarial question + what it hunts +
  the recorded failure modes it was drawn from. A project extends a profile by appending
  rows (see `reference-audit.md#audit-extend`), and a new row states its own evidence in
  the same way - a lens with nothing behind it is a taxonomy entry, not a lens.
- `Drawn from` cites the shipped lessons registry (`lessons/_index.md`). Read the cited
  entries into the finder's context: each carries the concrete failure that produced the
  lens, which is worth more to a finder than the lens name.
- A finding here is usually a **Bug**: prose that misdescribes code is wrong now, not an
  improvement to schedule. File the fix to the prose and to the thing the prose was wrong
  about; correcting only the sentence leaves the behaviour it advertised unbuilt.
- Read-only on source. Findings are filed as Bugs or CRs through `file_finding.py`, so
  ids and index rows are tool-allocated rather than hand-authored.
- Pair with a mutation run rather than replacing one: mutation answers `can-it-fail`
  mechanically over the diff, and this pack answers it wherever no mutant runs.
