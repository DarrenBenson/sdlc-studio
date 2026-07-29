#!/usr/bin/env bash
# Markdown mechanics over EVERY tracked markdown file, split into the two rule sets.
#
# The set is DERIVED from `git ls-files`, never from a glob. `markdownlint '**/*.md'` cannot
# enter a dot-directory at all, so the npm lanes were the root glob plus one hand-added
# `.claude/**/*.md` - a list of the dot-directories somebody remembered, silently exempting the
# ones they forgot. Three tracked files under `.github/` matched neither, so a markdown defect
# in them passed `npm run lint` and every CI job that calls it.
#
# The pre-commit hook already derives its set this way. Two lanes with two enumerations is the
# same defect waiting to recur on whichever one is not updated next, so both now read the
# tracked set and this script is the one place that decides what "every markdown file" means.
#
# Usage: tools/lint-md.sh [--fix]
set -uo pipefail

cd "$(git rev-parse --show-toplevel)" || exit 1

if [ -x node_modules/.bin/markdownlint ]; then
  md_cmd="node_modules/.bin/markdownlint"
elif command -v markdownlint >/dev/null 2>&1; then
  md_cmd="markdownlint"
else
  echo "markdownlint not found - run 'npm install' to enable it locally." >&2
  exit 1
fi

fix_flag=""
[ "${1:-}" = "--fix" ] && fix_flag="--fix"

# The same partition the pre-commit hook makes, and for the same reasons: transient agent
# worktrees are never shipped payload, and the shipped payload has its own config (template and
# example rules relaxed, mechanics still enforced).
md_root=(); md_payload=()
while IFS= read -r -d '' f; do
  case "$f" in
    .claude/worktrees/*) continue ;;
    .claude/*) md_payload+=("$f") ;;
    *) md_root+=("$f") ;;
  esac
done < <(git ls-files -z -- '*.md')

rc=0
if [ "${#md_root[@]}" -gt 0 ]; then
  # shellcheck disable=SC2086  # fix_flag is a single optional word
  $md_cmd $fix_flag "${md_root[@]}" || rc=1
fi
if [ "${#md_payload[@]}" -gt 0 ]; then
  # shellcheck disable=SC2086
  $md_cmd --config .claude/skills/sdlc-studio/.markdownlint.json $fix_flag "${md_payload[@]}" || rc=1
fi
# `--fix` rewrites what it can and reports what it cannot; it is a repair pass, not a verdict,
# so it exits 0 and the checking lane above is what a gate reads.
[ -n "$fix_flag" ] && exit 0
exit $rc
