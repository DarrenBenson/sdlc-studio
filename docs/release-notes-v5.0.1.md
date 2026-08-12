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

Unchanged from v5.0.0: **40 open defects, 39 Medium and 1 Low, zero Critical and zero High**,
listed by id in [docs/known-issues.md](known-issues.md) and triaged to v5.1. The page is
generated from the bug corpus and guarded in both directions, so a finding filed after it was
written cannot silently be missing from it.

- [README](../README.md) - installation and quick start
- [v5.0.0 release notes](release-notes-v5.0.0.md) - what the v5 line actually is
- [CHANGELOG.md](../CHANGELOG.md) - the per-unit record
