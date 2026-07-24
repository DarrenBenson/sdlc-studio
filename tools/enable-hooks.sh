#!/usr/bin/env bash
# Enable the tracked git hooks for this clone.
# Git hooks live outside version control by default; this points core.hooksPath
# at the tracked .githooks/ directory. Run once per clone.
#
# Enables two tracked hooks, which together are one gate ordered cheapest first:
#   - pre-commit  every cheap guard (style, links, budgets, drift), plus the decision on
#                 whether this commit needs the unit suites.
#   - commit-msg  REFUSES a commit whose subject names more than one work-item id
#                 (US/BG/CR) without a `Refs: <id>` trailer per owning id, so the
#                 engagement floor can attribute a shared commit per id. It prints the
#                 trailer lines to paste. A single-id subject, and a merge / revert /
#                 rebase replay, pass untouched. It then runs the unit suites, which sit
#                 here rather than in pre-commit because git writes the commit message
#                 after pre-commit has run: a message defect must not cost a full suite.
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
git config core.hooksPath .githooks
echo "Enabled: core.hooksPath -> .githooks (pre-commit gate + commit-msg gate active)."
echo "A multi-id commit subject now needs a 'Refs: <id>' trailer per owning id."
echo "Bypass a single commit in an emergency with: git commit --no-verify"
