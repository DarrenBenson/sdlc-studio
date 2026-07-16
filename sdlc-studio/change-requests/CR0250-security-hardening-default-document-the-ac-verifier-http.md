# CR-0250: Security hardening: default-document the AC-verifier http host allowlist and the rolling-install checksum

> **Status:** Complete
> **Size:** S
> **Priority:** P3
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-verify.md, README.md

## Summary

Two low-severity defence-in-depth notes from the security review, both WITHIN the maintainers' stated trust model (neither is a vulnerability). L1: the http Verify verb's host allowlist (`SDLC_VERIFY_HTTP_HOSTS)` is opt-in, so by default a Verify line can reach a link-local metadata endpoint (169.254.169.254) - fully mitigated for untrusted content by --no-shell and external-provenance gating, but worth a reference-verify.md recommendation to set the allowlist on cloud/CI hosts. L2: the classic 'curl | bash' installs main, for which no .sha256 sidecar is published, so `verify_download` warns and proceeds - escapable via `SDLC_STUDIO_REQUIRE_CHECKSUM`=1 or a tagged --version; worth a one-line README note for sensitive environments.

## Impact

A well-intentioned-but-mistaken Verify line on a cloud host could reach a metadata service; users installing in sensitive environments may not know to pin a tag + require checksum. Both are documentation/default hardening, not defects.

**Effort:** S

## Acceptance Criteria

- [ ] `reference-verify.md` recommends setting the AC-verifier http host allowlist on a cloud or CI host, and the README's install section tells a sensitive-environment user to pin a tagged release and require the checksum.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
