# BG1543: install.sh reads a failed fetch of the sha256 sidecar as no digest published and installs unverified

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** install.sh, install.ps1, docs/INSTALL.md, tools/tests/test_install_sidecar_fault.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at install.sh `fetch_stdout` (lines 332-336) and `verify_download` (lines 403-413)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:27Z

## Summary

The checksum step in install.sh fails open. The release asset is downloaded through `download_to`, which since BG0575 never reads a transport fault as an absence, but the digest it is checked against is fetched with `fetch_stdout`, which discards errors and returns nothing on any failure. In `verify_download` an empty digest prints a warning that no sha256 is published and returns 0, so the archive is extracted and installed. A 403, 429, 5xx or timeout on the sidecar of a release asset that was itself just downloaded therefore downgrades a verified install to an unverified one, and the warning misreports the fault as an absence. docs/INSTALL.md says the default install verifies the download against its published digest. Only `SDLC_STUDIO_REQUIRE_CHECKSUM` set to 1 or a pinned `SDLC_STUDIO_SHA256` closes the gap today.

## Steps to Reproduce

1. Serve a release asset from a local test server that answers 200 for the archive and 503 for the same address with .sha256 appended.
2. Run install.sh against that server with neither `SDLC_STUDIO_SHA256` nor `SDLC_STUDIO_REQUIRE_CHECKSUM` set.
3. Observed: the warning that no sha256 is published for the version and that it is installing unverified, then the install completes with exit 0.
4. Expected: a refusal saying the digest could not be fetched, since the release asset was found and its sidecar is expected to exist.
5. Positive control: the same run with the sidecar answering 404 on the source archive fallback still warns and proceeds, and with a correct sidecar the install verifies.

## Proposed Fix

Fetch the sidecar with the same three-way status reader `download_to` uses, so a 2xx, a 404 and any other outcome are told apart. When the url being verified is the release asset, refuse on anything but a 2xx with a message that names the fault. Keep warn and proceed only for a real 404 on the source archive fallback, where no sidecar is published. Reword the warning so it is printed only for a true absence. Check install.ps1 for the same reading and bring docs/INSTALL.md into line with the behaviour. Pin it with an install test that serves a faulted sidecar beside a good asset.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The checksum step in install.sh fails open.
- [ ] **AC2** The proposed fix lands, pinned by a test: Fetch the sidecar with the same three-way status reader `download_to` uses, so a 2xx, a 404 and any other outcome are told apart.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
