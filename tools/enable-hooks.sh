#!/usr/bin/env bash
# Enable the tracked git hooks for this clone.
# Git hooks live outside version control by default; this points core.hooksPath
# at the tracked .githooks/ directory. Run once per clone.
#
# Enables two tracked hooks:
#   - pre-commit  the full guard gate (style, links, budgets, tests, drift).
#   - commit-msg  REFUSES a commit whose subject names more than one work-item id
#                 (US/BG/CR) without a `Refs: <id>` trailer per owning id, so the
#                 engagement floor can attribute a shared commit per id. It prints the
#                 trailer lines to paste. A single-id subject, and a merge / revert /
#                 rebase replay, pass untouched.
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
git config core.hooksPath .githooks
echo "Enabled: core.hooksPath -> .githooks (pre-commit gate + commit-msg gate active)."
echo "A multi-id commit subject now needs a 'Refs: <id>' trailer per owning id."
echo "Bypass a single commit in an emergency with: git commit --no-verify"
