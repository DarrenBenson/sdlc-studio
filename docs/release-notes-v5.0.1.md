# SDLC Studio v5.0.1

**A patch release for one defect: the verified install path did not work, and had never worked.**

Everything in [v5.0.0](release-notes-v5.0.0.md) is the substantive release. This one exists
because v5.0.0 was tagged with a High-severity defect nobody had looked for, and the honest
response to finding it hours later was to fix it and cut again rather than to publish a release
whose notes claimed zero open High findings while its own tree carried one.

---

## What was wrong

README and the documentation offered this as the path for anyone who would not accept an
unverified download:

```bash
curl -fsSL .../install.sh | SDLC_STUDIO_REQUIRE_CHECKSUM=1 bash -s -- --version <tag>
```

It refused, at every version, for everybody. Both installers looked for a `.sha256` sidecar
beside GitHub's **generated** source archive, and GitHub serves no such sidecar for any tag.
So the digest resolved empty, the requirement made an empty digest fatal, and the one command
offered to a reader who asked for verification was the one command guaranteed to fail. Their
only options were to drop the requirement they came for, or to abandon the install.

Nothing exercised it, so it had been that way since it was written, and every test was green
the whole time. That is the shape this project files against other people's code.

## What changed

**Releases now publish their own artefacts.** Each tag builds a `.tar.gz` and a `.zip` with
pinned commands, records each digest from the file actually uploaded, verifies both pairs
before publishing anything, and attaches them to the release. Both the bytes and the digest
are produced by this project in the same step, so they cannot drift apart.

**A tagged install verifies against those**, not against GitHub's generated archive. Generated
archives are regenerated rather than published and are not guaranteed byte-stable, so a digest
recorded for one can stop matching with nobody touching the tag - and that reaches a user as
`Checksum mismatch`, which is indistinguishable from an attack.

**A fault is no longer read as an absence.** Falling back to the unverified archive happens on
a 404 and only on a 404. This needed the HTTP status to be read rather than inferred: `curl -f`
exits 22 for every status at or above 400, so a 403, a rate-limiting 429 and a CDN 503 were
indistinguishable from a genuine "not published". The first version of this fix claimed to
separate them and did not; a review caught it.

**Tags before v5.0.1 still refuse under `SDLC_STUDIO_REQUIRE_CHECKSUM=1`**, because they have
no published artefacts and therefore nothing to verify against. The fix is forward-only and
says so rather than widening what counts as verified.

Full detail, including what is verified and what deliberately is not, is in
[docs/INSTALL.md](INSTALL.md#verifying-the-download).

---

## Also in this release

- The toolchain runbook gained a **Release** step. Everything after the tag was previously
  un-tooled, which is why two releases shipped without artefacts and nobody noticed.
- `docs/INSTALL.md` documents download verification at all, which it did not before.

---

## Upgrading

Nothing to do beyond installing normally. No artefact, configuration or command changed.

If you install into an environment where an unverified download is not acceptable, the
documented command now works, pinned to `v5.0.1` or later.

---

## Known issues

**v5.0.1 was TAGGED with zero Critical and zero High open against it.** That was true at the tag
and is not a standing claim: fourteen High findings have since been raised against this code, every
one of them by adversarial review, by dogfooding or by measurement after the tag. **Six are open
now - BG0586, BG0588, BG0607, BG0609, BG0610 and BG0611.** Four have been fixed and independently reviewed (BG0585, BG0593, BG0597, BG0598), and
BG0583 was raised at High and then closed WON'T FIX when its premise did not survive
re-measurement.

BG0604 was raised at High and RE-TRIAGED to Medium on 2026-08-24, against the rubric: a
workaround exists and the shipped tooling already prints it. It is worth stating plainly anyway,
because it is a defect in this project's own review procedure rather than in its code. The oracle rule recorded in D0149 requires a reviewer to
take a unit's base revision BY HAND, and names no restore step; a reviewer ran it against the main
working tree rather than their own worktree and destroyed a session's uncommitted work. Nothing
could restore it, because the work had never been committed. The rule's substance was right - a
tool's own output is not evidence of that tool's correctness - and what was missing is which tree
the manual check runs in.

`tools/known_issues.py --bar` reads the live corpus rather than this sentence, so it reports the
open set directly; a disagreement between the two is the guard working, not drift to be edited
away. This paragraph has now been wrong in both directions at once - naming three findings that
had been fixed while missing one that was open - which is the argument for reading the command
rather than the prose. All six are carried to v5.1, and BG0606's fix has already shipped - it stays open only because
closing it needs a test-plan review for work an independent seat has already approved.

**v5.0.1 discloses 14 open defects: 14 Medium, 0 Low.** The six High findings above are
listed separately because they sit ABOVE the disclosure bar rather than under it. Listed by id in
[docs/known-issues.md](known-issues.md) and triaged to v5.1. The page is generated from the bug
corpus and guarded in both directions, so a finding filed after it was written cannot silently be
missing from it.

Down from the 40 v5.0.0 disclosed. 32 closed while clearing the bug backlog - and five of
those were never defects at all: two had already been repaired with their bugs left open, two
carried premises that had expired (one asserting 21 unresolved Open Questions where the corpus
now holds 0), and one was a duplicate. That is BG0577, filed because nothing detects any of those
states and every plan sized from the backlog inherits the error.

**The stale-criteria count, re-measured.** v5.0.0's notes reported 50 executable acceptance
criteria failing when run, of 1,918 across 673 stories at Done. Re-run for this release the
figure is **52 of 1,906 across 670**. No story file changed between the two tags, so the
denominators disagreeing means the two runs were not measuring the same set - and the gap
between their red counts therefore says nothing about anything getting worse. The earlier
reading could not be reproduced and is not carried forward.

That is the fourth time this number has moved in this project's own records (106, 53, 58, 50,
now 52), which is the argument for putting it on a schedule rather than a footnote to it. The
repairs remain a v5.1 sweep with their own review: a repair that merely makes a criterion pass
converts a visible stale selector into an invisible vacuous one, which is worse than the red it
replaced.

- [README](../README.md) - installation and quick start
- [v5.0.0 release notes](release-notes-v5.0.0.md) - what the v5 line actually is
- [CHANGELOG.md](../CHANGELOG.md) - the per-unit record
