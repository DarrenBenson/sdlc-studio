# BG0575: The documented sensitive-environment install refuses to install, at every version, because the sidecar it verifies against cannot exist at the URL install.sh reads

> **Status:** Fixed
> **Verification depth:** functional (wiring: all six criteria drive the shipped install.sh end to end as a script over a PATH-stubbed curl and a local origin, because a unit test of verify_download cannot see the defect - that function was always correct and the bug was the URL handed to it; mutation: 9 declared mutants across install.sh and the release workflow, each anchor asserted unique, bytecode purged and python3 -B, all 9 killed with the unmutated suite green as the positive control, two of them found SURVIVING by review before the repair; PowerShell: verified in CI rather than locally, pwsh being absent here - windows-smoke run 31691593701 reports the green, red and 404 controls all OK under real PowerShell; release: the bug's own reproduction re-run against the published v5.0.1 assets completes and prints a digest matching the published sidecar)
> **Created:** 2026-08-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** install.sh, install.ps1, README.md, docs/INSTALL.md, .github/workflows/release.yml, .github/workflows/lint.yml, tools/release_assets.py, tools/tests/test_release_assets.py, tools/runbook.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md
> **Severity:** High
> **Points:** 5

## Summary

README's 'Installing in a sensitive environment?' block documents `SDLC_STUDIO_REQUIRE_CHECKSUM`=1 with a pinned tag as the verified install path. It has never worked. install.sh:250 derives the expected digest from a best-effort sidecar at <archive-url>.sha256, and the archive URL it builds (install.sh:290) is `https://github.com/<repo>/archive/refs/tags/<version>.tar.gz` - a GitHub-generated source archive, for which GitHub serves no sidecar and never will. So the fallback resolves empty, `REQUIRE_CHECKSUM`=1 makes empty fatal (install.sh:252-254), and the one command the README offers to a reader who asked for verification is the one command that cannot complete. The reader's options are to drop the requirement they came for, or to abandon the install.

This is the shape the project files against others: a documented path with nothing exercising it. No test invokes install.sh with `REQUIRE_CHECKSUM`=1, so the block has been consumer-facing since it was written and green the whole time.

It reaches a consumer at v5.0.0 the moment the release is announced, and it is worst for exactly the reader it was written for: someone installing into an environment where an unverified download is not acceptable.

## Steps to Reproduce

1. `curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh -o install.sh`
2. `HOME=$(mktemp -d) SDLC_STUDIO_REQUIRE_CHECKSUM=1 bash install.sh --version v5.0.0 --target claude --no-sweep`

Observed 2026-08-12, exit 1, on stderr: `Error: No published sha256 for v5.0.0 and SDLC_STUDIO_REQUIRE_CHECKSUM=1 - refusing to install`. Nothing is installed.

The cause is independent of the version. `curl -o /dev/null -w '%{http_code}' https://github.com/DarrenBenson/sdlc-studio/archive/refs/tags/v5.0.0.tar.gz.sha256` returns 404, and the same URL for v4.1.0 returns 404, while the tarball itself returns 302. `gh release view v4.1.0 --json assets` returns an empty asset list, so no release has ever published one either.

Note that `--dry-run` does NOT reproduce it: the dry-run path returns before the download, so the checksum is never reached. A reader confirming the command with --dry-run first is told it would succeed.

## Proposed Fix

Publish, as release assets on the tag, a tarball the project builds and its .sha256, and have install.sh prefer a tagged version's release asset over the GitHub-generated archive so both the bytes and the digest are ones this repo produced. Verifying a GitHub-generated archive against a recorded digest is the weaker alternative: those archives are not contractually byte-stable, so a pin that is correct today can rot without anybody changing the tag. Whichever is chosen, the regression test must invoke install.sh itself with `REQUIRE_CHECKSUM`=1 - a library-level check of the digest helper cannot see a sidecar URL that resolves to nothing.

## Acceptance Criteria

- **AC1:** Given a tagged version whose release publishes a `.tar.gz` asset and a `.sha256` beside it, when `install.sh` is run with `SDLC_STUDIO_REQUIRE_CHECKSUM=1`, then it completes, reports the digest of THAT asset, and what it installs carries the asset's marker rather than the generated archive's. Mutant: drop the release-asset branch from `prepare_source` so a tagged version uses the generated archive; must redden.
- **Verify:** pytest tools/tests/test_release_assets.py -k completes_from_the_release_asset
- **AC2:** Given the asset URL fails with a transport error rather than a 404, when the install runs, then it aborts and says so, rather than falling back to the unverified source archive. Mutant: fall back on any non-zero from the asset fetch instead of only on absence; must redden.
- **Verify:** pytest tools/tests/test_release_assets.py -k transport_error
- **AC3:** Given the asset URL answers with an HTTP status at or above 400 that is NOT 404 - a 403, a rate-limiting 429, a CDN 503 - when the install runs, then it aborts rather than reading a fault as an absence. `curl -f` exits 22 for all of them, so the status must be read rather than inferred. Mutant: treat any status at or above 400 as absence; must redden.
- **Verify:** pytest tools/tests/test_release_assets.py -k server_error
- **AC4:** Given a tag with no published asset, when the install runs under `SDLC_STUDIO_REQUIRE_CHECKSUM=1`, then it falls back to the generated archive, finds no digest and refuses, because the fix is forward-only and must not widen what counts as verified. Mutant: make the missing-digest branch warn and proceed; must redden.
- **Verify:** pytest tools/tests/test_release_assets.py -k refuses_honestly
- **AC5:** Given a sidecar whose digest does not match the asset, when the install runs, then it aborts BEFORE extraction and installs nothing, proven by a `tar` that never ran. Mutant: remove the digest comparison, OR move verification after extraction; must redden on both.
- **Verify:** pytest tools/tests/test_release_assets.py -k aborts_before_extraction
- **AC6:** Given the release workflow's own `git archive` lines, when THOSE commands are executed, then each produces exactly one `sdlc-studio-*` top directory with `CHANGELOG.md` at its root, which is what the installers' extraction and `ship_changelog` read. The commands are read from the workflow, never restated, or the test asserts that git honours `--prefix` rather than that this release does. Mutant: drop `--prefix` from either line, or delete the zip line; must redden.
- **Verify:** pytest tools/tests/test_release_assets.py -k builds_the_layout
- **AC7:** Given the filenames the workflow's build commands actually write, when they are compared with the URLs the installers construct, then they agree. Taken from each command's own `-o` path, never from anywhere the name merely appears - the name is repeated on the digest line, so a rename in the `-o` alone leaves an "it is mentioned" assertion green. Mutant: rename the published asset in the workflow; must redden.
- **Verify:** pytest tools/tests/test_release_assets.py -k names_the_workflow_publishes

## Verification depth

Full. Every criterion is executed against the shipped `install.sh` as a script, driven end to end
with a `PATH`-stubbed `curl` serving a local origin, because the defect is in the WIRING - the URL
handed to `verify_download` - and a library test of that function cannot see it. Nine mutants were
executed and all nine killed on 2026-08-12, with the unmutated suite green as the positive control.

Two of those nine SURVIVED a first pass and were found by review, not by me: the layout criterion
ran its own `git archive` instead of the workflow's, and "aborts before extraction" was
unobservable because the installer deletes its temp directory either way. Recorded because the
first version of this section claimed four mutants killed and the claim was worth less than it
read.

Not yet verified, and not to be read as if it were: the documented command against the REAL
published assets. Everything above is measured against a local origin. Until a release publishes
the four assets and the reproduction in this bug is re-run end to end and completes, the fix is
evidenced rather than demonstrated.

Stated plainly rather than implied: **the PowerShell half is not verified locally.** `pwsh` is not
present on this machine, so `install.ps1`'s equivalent change was not executed here. It is covered
by the `windows-smoke` job in `.github/workflows/lint.yml`, which runs `install.ps1` under real
PowerShell on every push, and the REQUIRE_CHECKSUM case must be demonstrated green-and-red there
before this bug is closed. A test asserting over the TEXT of `install.ps1` would be a strictly
weaker claim than the criterion and is not a substitute.

## Impact

The only verified-install path the project documents cannot be completed by anybody, and the README presents it as the answer for sensitive environments. Filed High rather than Medium because it is consumer-facing at the v5.0.0 release boundary, it defeats a security control rather than degrading a convenience, and the failure mode teaches the reader that the requirement is the problem.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | install.sh `prepare_source`: set `asset_url=""` for a tagged version, so it uses GitHub's generated archive | Given a tagged version whose release publishes a `.tar.gz` asset and a `.sha256` beside it, when `install.sh` is run with `SDLC_STUDIO_REQUIRE_CHECKSUM=1`, then it completes, reports the digest of THAT asset, and what it installs carries the asset's marker rather than the generated archive's. Mutant: drop the release-asset branch from `prepare_source` so a tagged version uses the generated archive; must redden. |
| AC2 | install.sh `prepare_source`: change the `22)` case arm to `*)`, so any non-zero falls back | Given the asset URL fails with a transport error rather than a 404, when the install runs, then it aborts and says so, rather than falling back to the unverified source archive. Mutant: fall back on any non-zero from the asset fetch instead of only on absence; must redden. |
| AC3 | install.sh `download_to`: change the `404)` arm to `4??\|5??)`, so any HTTP error reads as absence | Given the asset URL answers with an HTTP status at or above 400 that is NOT 404 - a 403, a rate-limiting 429, a CDN 503 - when the install runs, then it aborts rather than reading a fault as an absence. `curl -f` exits 22 for all of them, so the status must be read rather than inferred. Mutant: treat any status at or above 400 as absence; must redden. |
| AC4 | install.sh `verify_download`: replace the REQUIRE_CHECKSUM `error`+`exit 1` with a `warn`, so it proceeds | Given a tag with no published asset, when the install runs under `SDLC_STUDIO_REQUIRE_CHECKSUM=1`, then it falls back to the generated archive, finds no digest and refuses, because the fix is forward-only and must not widen what counts as verified. Mutant: make the missing-digest branch warn and proceed; must redden. |
| AC5 | install.sh `verify_download`: `if [[ "$actual" != "$expected" ]]` -> `if false`; ALSO move `verify_download` below `tar -xzf` | Given a sidecar whose digest does not match the asset, when the install runs, then it aborts BEFORE extraction and installs nothing, proven by a `tar` that never ran. Mutant: remove the digest comparison, OR move verification after extraction; must redden on both. |
| AC6 | release.yml: drop `--prefix="$prefix"` from the tar.gz `git archive` line; ALSO delete the zip line entirely | Given the release workflow's own `git archive` lines, when THOSE commands are executed, then each produces exactly one `sdlc-studio-*` top directory with `CHANGELOG.md` at its root, which is what the installers' extraction and `ship_changelog` read. The commands are read from the workflow, never restated, or the test asserts that git honours `--prefix` rather than that this release does. Mutant: drop `--prefix` from either line, or delete the zip line; must redden. |
| AC7 | release.yml: rename the built asset in its `-o` path, `sdlc-studio-$tag.tar.gz` -> `sdlcstudio-$tag.tar.gz` | Given the filenames the workflow's build commands actually write, when they are compared with the URLs the installers construct, then they agree. Taken from each command's own `-o` path, never from anywhere the name merely appears - the name is repeated on the digest line, so a rename in the `-o` alone leaves an "it is mentioned" assertion green. Mutant: rename the published asset in the workflow; must redden. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-12 | sdlc-studio | Created via `new` (deterministic) |
