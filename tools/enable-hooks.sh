#!/usr/bin/env bash
# Enable the tracked git hooks for this clone.
# Git hooks live outside version control by default; this points core.hooksPath
# at the tracked .githooks/ directory. Run once per clone.
#
# Enables the tracked hooks, which together are one gate ordered cheapest first:
#   - pre-commit  every cheap guard (style, links, budgets, drift), plus the decision on
#                 whether this commit needs the unit suites.
#   - commit-msg  REFUSES a commit whose subject names more than one work-item id
#                 (US/BG/CR) without a `Refs: <id>` trailer per owning id, so the
#                 engagement floor can attribute a shared commit per id. It prints the
#                 trailer lines to paste. A single-id subject, and a merge / revert /
#                 rebase replay, pass untouched. It then runs the unit suites, which sit
#                 here rather than in pre-commit because git writes the commit message
#                 after pre-commit has run: a message defect must not cost a full suite.
#   - pre-push    the BOUNDARY lanes (release-rehearsal, revert-check): a branch ref is the push
#                 boundary, a tag ref the release boundary. Minutes per push, announced first;
#                 D0180 records the ruling to pay it.
#
# The list printed below is DERIVED from .githooks/ - every file, with line 2 of each hook as
# its one-line description - so the next hook added cannot be enabled unannounced.
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
git config core.hooksPath .githooks
echo "Enabled: core.hooksPath -> .githooks. Hooks now active:"
for hook in .githooks/*; do
  [ -f "$hook" ] || continue
  line="$(sed -n '2p' "$hook")"
  case "$line" in
    "#"*) desc="$(printf '%s' "$line" | sed -e 's/^#[[:space:]]*//')" ;;
    *) desc="" ;;
  esac
  [ -n "$desc" ] || desc="(no description)"
  printf '  %-14s %s\n' "$(basename "$hook")" "$desc"
done
echo "A multi-id commit subject now needs a 'Refs: <id>' trailer per owning id."
echo "Bypass a single commit in an emergency with: git commit --no-verify; a single push with: git push --no-verify"
