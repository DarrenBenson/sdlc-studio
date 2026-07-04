#!/usr/bin/env bash
# Enable the tracked git hooks (the pre-commit gate) for this clone.
# Git hooks live outside version control by default; this points core.hooksPath
# at the tracked .githooks/ directory. Run once per clone.
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
git config core.hooksPath .githooks
echo "Enabled: core.hooksPath -> .githooks (pre-commit gate active)."
echo "Bypass a single commit in an emergency with: git commit --no-verify"
