# BG0939: install.ps1 rejects every release download: the .sha256 sidecar is read as bytes, so the digest never matches

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** install.ps1, tools/tests/test_lean_install_ps1_checksum_bytes.py, CHANGELOG.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T16:42:56Z

## Summary

install.ps1 reads the release asset's sidecar with (Invoke-WebRequest ...).Content and splits it on whitespace. GitHub serves the sidecar as application/octet-stream, for which PowerShell's .Content is a byte array, so the split yields decimal byte values, not the digest, and every release install throws 'Checksum mismatch' before extraction. The v6.0.0 asset matches its published sha256 exactly (verified with sha256sum), so the asset is sound. Latent since BG0575; exposed when BG0934 made the latest release the default, and caught by the windows-smoke CI step on 125cc8f9 (Lint run 37133734434). A Windows user installing with no version argument cannot install.

## Steps to Reproduce

1. pwsh: ./install.ps1 (no -Version) on Windows CI, or -Version v6.0.0. 2. The asset downloads. 3. It throws 'Checksum mismatch for v6.0.0: expected <a number>, got <the real digest>'.

## Proposed Fix

Read the sidecar as text whatever its content type (decode a byte-array Content as UTF-8, or download it to a file and read that), then take the first whitespace-separated field. No new refusal; the checksum check itself stays.

## Acceptance Criteria

- [ ] **AC1** Given install.ps1 run under pwsh with the asset download and its sidecar stubbed so the sidecar's Content is a byte array (as GitHub's octet-stream gives) holding the asset's real sha256, when it installs, then the checksum verifies and the install completes; a sidecar holding a different digest still aborts before extraction. Fails on: the current code, which reads the byte array's numbers as the digest and aborts on the matching sidecar
  - **Verify:** pytest tools/tests/test_lean_install_ps1_checksum_bytes.py::InstallPs1ChecksumBytesTests::test_a_byte_array_sidecar_verifies
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
