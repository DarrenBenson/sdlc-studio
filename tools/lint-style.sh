#!/usr/bin/env bash
# Style guard for SDLC Studio markdown (house style: see CLAUDE.md).
#
#   1. No em-dash (U+2014). Use an en-dash with spaces ( - ) instead.
#   2. No corporate jargon (synergy, leverage, robust, journey), unless the
#      offending line contains a substring listed in tools/style-allowlist.txt.
#
# Prints every offender and exits non-zero on any violation. Run via
# `npm run lint` (which CI runs), or directly: bash tools/lint-style.sh
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
allowlist="$repo_root/tools/style-allowlist.txt"
status=0
cd "$repo_root"

# 1. Em-dash: never allowed, no exceptions.
if em_hits="$(grep -rInP '\x{2014}' --include='*.md' --exclude-dir=node_modules . 2>/dev/null)"; then
  echo "Style error: em-dash (U+2014) found. Use an en-dash with spaces ( - ) instead."
  printf '%s\n' "$em_hits"
  status=1
fi

# 2. Corporate jargon, filtered through the allowlist.
jargon_hits="$(grep -rInwiE 'synergy|leverage|robust|journey' --include='*.md' --exclude-dir=node_modules . 2>/dev/null || true)"
if [ -n "$jargon_hits" ] && [ -f "$allowlist" ]; then
  # Strip comment and blank lines, then drop any hit whose text contains an
  # allowlisted substring (case-insensitive, fixed string).
  allow="$(grep -vE '^[[:space:]]*(#|$)' "$allowlist" || true)"
  if [ -n "$allow" ]; then
    jargon_hits="$(printf '%s\n' "$jargon_hits" | grep -ivF -- "$allow" || true)"
  fi
fi
if [ -n "$jargon_hits" ]; then
  echo "Style error: corporate jargon found. Reword, or add the line's context to tools/style-allowlist.txt."
  printf '%s\n' "$jargon_hits"
  status=1
fi

exit "$status"
