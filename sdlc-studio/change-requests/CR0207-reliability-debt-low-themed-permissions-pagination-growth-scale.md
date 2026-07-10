# CR-0207: reliability debt (Low, themed): permissions, pagination, growth, scale and crash-window items from RV0007

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

Consolidated Low reliability findings from RV0007 (each independently verified; one artefact per the filing protocol). Items: (1) atomic_write resets file permissions to 0600 (sdlc_md.py:618-630, mkstemp mode kept by os.replace - every adoption widens it); (2) install.ps1 never ships CHANGELOG.md (install.sh:276-284 has ship_changelog; Windows capability digest permanently degrades, project_upgrade.py:381-383); (3) batch operations pay full-corpus cost per item (transition.py:441-459 per-id find_by_id + apply_type + detect_type; measured 0.32s/item linear at a 3k corpus - a 100-story close ~35s); (4) mutation.py leaves a mutant in user source on SIGKILL (mutation.py:189-199, finally-only restore, no sidecar); (5) gh issue list --limit 500 silently truncates sync beyond 500 issues (github_sync.py:111, no pagination); (6) .local state JSON writes non-atomic - a crash resets loop_guard quarantine counts silently (loop_guard.py:77, resume.py:74, verify_ac.py:646, github_sync.py:290); (7) cascade watermark uses prs[0].mergedAt not max (github_sync.py:633-635, re-reports); (8) detect_type reads each artefact up to 3x (O(corpus) re-read, BG0070-adjacent); (9) next_id.remote_ids git ls-tree has no timeout (next_id.py:119-141, sibling has one); (10) verify_ac --batch npx jest can auto-install from the registry with no TTY (verify_ac.py:485-486; use --no-install); (11) http verb scheme floor admits scheme-less URLs in unrestricted mode (verify_ac.py:365 vs docstring :27-28); (12) lint-style.sh em-dash check silently no-ops on BSD grep (grep -P, :25, stderr suppressed); (13) check_neutrality.py fails open outside a git tree and is cwd-dependent (tools/check_neutrality.py:62-64,:94-97); (14) CI runs npm test on system Python before setup-python/PyYAML (lint.yml:33-47, passes by image accident).

## Acceptance Criteria

- [ ] atomic_write preserves the existing file's mode (or applies umask for new files)
- [ ] install.ps1 ships CHANGELOG.md like install.sh
- [ ] Batch transition/new paths build the census once and run one apply/detect per type at batch end
- [ ] mutation.py writes a .sdlc-orig sidecar and recovers leftovers on startup
- [ ] github_sync paginates issue listing past 500
- [ ] loop_guard/resume/verify-report/sync-state writes go through atomic_write
- [ ] cascade watermark = max(mergedAt)
- [ ] next_id.remote_ids gets a timeout; detect_type single-read per file where cheap
- [ ] npx jest runs with --no-install (or which-preflight); empty URL scheme refused in every mode
- [ ] lint-style em-dash check is portable or fails loud without grep -P; check_neutrality exits non-zero when it scanned nothing and takes --root; lint.yml orders setup-python before npm test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Raised |

## Delivered vs deferred (US0119)

**Delivered:** atomic_write mode preservation; loop_guard/resume .local writes atomic; cascade watermark max(mergedAt); next_id ls-tree timeout; npx jest --no-install; http scheme-less URL refused in every mode; check_neutrality fail-loud; em-dash guard grep-P-free (BSD-portable); install.ps1 ships CHANGELOG (parity); lint.yml installs PyYAML before the first Python run.

**Deferred (larger, follow-up):** batch-operation O(corpus) amortisation; detect_type triple-read; gh issue list pagination past 500; mutation.py SIGKILL .orig sidecar. These are non-trivial and each warrants its own unit; recorded here rather than rushed into the themed batch.
