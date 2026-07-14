#!/usr/bin/env bash
# Enable the tracked git hooks for this clone.
# Git hooks live outside version control by default; this points core.hooksPath
# at the tracked .githooks/ directory. Run once per clone.
#
# Enables two tracked hooks:
#   - pre-commit  the full guard gate (style, links, budgets, tests, drift).
#   - commit-msg  warns when a subject names more than one work-item id (US/BG/CR)
#                 without a `Refs: <id>` trailer, so the engagement floor can attribute
#                 a shared commit per id. Warns only; export SDLC_ENGAGEMENT_STRICT=1
#                 to make it block instead.
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
git config core.hooksPath .githooks
echo "Enabled: core.hooksPath -> .githooks (pre-commit gate + commit-msg nudge active)."
echo "Make the commit-msg hook block instead of warn: export SDLC_ENGAGEMENT_STRICT=1"
echo "Bypass a single commit in an emergency with: git commit --no-verify"
