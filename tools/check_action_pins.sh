#!/usr/bin/env bash
# Supply-chain guard: every GitHub Action in .github/workflows/ must be pinned to a
# full 40-hex commit SHA, not a mutable @vN or @branch tag. A moved tag can point at
# attacker-controlled code that then runs in CI with the workflow token; a SHA cannot
# be repointed. The house convention keeps the human-readable version in a trailing
# comment: `uses: actions/checkout@<sha> # v7`.
#
# Fails (non-zero) listing every unpinned ref. Run via `npm run lint` (CI runs it), the
# pre-commit gate, or directly: bash tools/check_action_pins.sh
# An optional first argument scans a different tree (used by the unit test).
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scan_root="${1:-$repo_root}"
wf_dir="$scan_root/.github/workflows"

if [ ! -d "$wf_dir" ]; then
  echo "action-pins: no .github/workflows/ directory - nothing to check"
  exit 0
fi

# Collect every `uses:` ref whose @ref is not a 40-hex SHA. Local `./path` and
# reusable-workflow `./.github/...` refs have no @ and are skipped by the pattern.
unpinned="$(grep -rhoE 'uses:[[:space:]]+[^@[:space:]]+@[^[:space:]]+' "$wf_dir" \
  | sed -E 's/uses:[[:space:]]+//' \
  | grep -vE '@[0-9a-f]{40}$' || true)"

if [ -n "$unpinned" ]; then
  echo "action-pins: the following Actions are not pinned to a commit SHA:" >&2
  echo "$unpinned" | sed 's/^/  /' >&2
  echo "" >&2
  echo "Pin each to the tag's full commit SHA (keep the version in a trailing comment):" >&2
  echo "  resolve with: gh api repos/<owner>/<repo>/git/refs/tags/<tag> --jq .object.sha" >&2
  echo "  then write:   uses: <owner>/<repo>@<40-hex-sha> # <tag>" >&2
  exit 1
fi

echo "action-pins: all Actions pinned to commit SHAs"
exit 0
