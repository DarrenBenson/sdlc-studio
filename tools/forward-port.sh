#!/usr/bin/env bash
# tools/forward-port.sh - the dev-repo rsync to the installed copy, as a guarded
# one-liner. The canonical incantation was hand-typed per port; a wrong --delete
# without the .local exclude destroys the installed copy's local state, and running
# it the other way round clobbers the git-tracked working tree. This wraps it:
#
#   dry-run by default (prints the itemised diff), --yes to apply
#   refuses a non-dev-repo cwd (run it from the repo root)
#   refuses a target inside the repo, or CONTAINING the repo - both sweep
#   directions that destroy tracked files; symlink targets are fully resolved
#
# --check turns the same comparison into a gate. The installed copy is what every
# OTHER project on the machine loads, so the window between a fix landing here and
# the mirror running is a window in which a fix believed shipped is not in force
# anywhere. Nothing reported that window, so it rested on someone remembering to
# ask. --check exits non-zero and names the count of differing files. Two states
# are reported rather than failed: no installed copy at all, and a copy pinned by
# a `.local/forward-port.pin` marker - a machine that deliberately does not mirror
# is not held to a drift verdict.
#
# Usage: bash tools/forward-port.sh [--yes | --check] [--target DIR]
#   --target defaults to ~/.claude/skills/sdlc-studio (the installed copy)
set -euo pipefail

SRC=".claude/skills/sdlc-studio"
#: A target carrying this file says "held here deliberately, do not report drift".
PIN=".local/forward-port.pin"
TARGET=""
APPLY=0
CHECK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) APPLY=1; shift ;;
    --check) CHECK=1; shift ;;
    --target) TARGET="${2:?--target needs a directory}"; shift 2 ;;
    *) echo "unknown argument: $1 (usage: forward-port.sh [--yes | --check] [--target DIR])" >&2
       exit 2 ;;
  esac
done

if [[ "$CHECK" -eq 1 && "$APPLY" -eq 1 ]]; then
  echo "refused: --check reports drift and writes nothing; --yes applies. Pick one." >&2
  exit 2
fi

if [[ -z "$TARGET" ]]; then
  if [[ -z "${HOME:-}" ]]; then
    echo "refused: HOME is unset and no --target given - nowhere to port to" >&2
    exit 2
  fi
  TARGET="${HOME}/.claude/skills/sdlc-studio"
fi

# Guard 1: run from the DEV REPO root - the installed copy has no tools/ or nested
# skill tree, so these structural markers only hold in the repo.
if [[ ! -f "$SRC/SKILL.md" || ! -f "tools/forward-port.sh" ]]; then
  echo "refused: this is not the dev repo root (missing $SRC/SKILL.md or tools/) -" \
       "run from the sdlc-studio repo, never from an installed copy" >&2
  exit 2
fi

# Guard 2: fully resolve the target PHYSICALLY - including a symlink leaf and
# not-yet-existing tails - creating NOTHING on disk, then refuse either
# destructive direction: a target inside the repo (the sweep clobbers tracked
# files) or a target containing the repo (the sweep deletes the repo itself).
if [[ -e "$TARGET" && ! -d "$TARGET" ]]; then
  echo "refused: target $TARGET exists and is not a directory" >&2
  exit 2
fi
if [[ -L "$TARGET" && ! -e "$TARGET" ]]; then
  echo "refused: target $TARGET is a dangling symlink - it cannot be resolved, so" \
       "the direction guards cannot vouch for it" >&2
  exit 2
fi
resolve_physical() {
  local p="$1" suffix=""
  while [[ ! -d "$p" ]]; do
    suffix="/$(basename "$p")$suffix"
    p="$(dirname "$p")"
  done
  printf '%s%s\n' "$(cd "$p" && pwd -P)" "$suffix"
}
repo_abs="$(pwd -P)"
target_abs="$(resolve_physical "$TARGET")"
case "$target_abs/" in
  "$repo_abs"/*)
    echo "refused: target $target_abs is inside the repo - the forward-port only" \
         "runs repo -> installed copy, never the reverse" >&2
    exit 2 ;;
esac
case "$repo_abs/" in
  "$target_abs"/*)
    echo "refused: target $target_abs contains the repo - the --delete sweep would" \
         "remove the repo itself as extraneous" >&2
    exit 2 ;;
esac

# .pytest_cache is gitignored rather than absent, and rsync copies untracked files - so a dev
# machine that has run the suite (which the gate does) shipped its test cache into the installed
# skill, and --delete then churned it on every port.
RSYNC=(rsync -rci --delete --exclude='.local' --exclude='__pycache__' \
       --exclude='.pytest_cache' "$SRC/" "$target_abs/")

if [[ "$CHECK" -eq 1 ]]; then
  # Report, never fail, the two states that are not drift.
  if [[ ! -d "$target_abs" ]]; then
    echo "forward-port check: no installed copy at $target_abs - nothing to compare"
    exit 0
  fi
  if [[ -e "$target_abs/$PIN" ]]; then
    echo "forward-port check: $target_abs is pinned ($PIN present) - drift not reported"
    exit 0
  fi
  # The itemised diff of the SAME rsync the mirror runs, so the exclusions the mirror
  # honours are the exclusions the comparison honours: `.local` is the consuming copy's
  # own state and bytecode/test caches are deployment junk. Neither is drift.
  #
  # Counting is over FILES, not rsync lines: a created directory (`cd+++++++++ sub/`)
  # and a deleted one (`*deleting extra/`) are consequences of the files inside them,
  # so counting them would inflate the number the operator is asked to act on. rsync
  # pads the itemise flag to 11 characters, so the path starts at column 13 in both the
  # itemise and the `*deleting` forms.
  drift="$("${RSYNC[@]}" -n | awk '
    /^\*deleting/ { p = substr($0, 13); if (p !~ /\/$/) print; next }
    /^[<>ch.][fLDS]/ { print; next }
  ')"
  if [[ -z "$drift" ]]; then
    echo "forward-port check: in sync - $target_abs matches $repo_abs/$SRC"
    exit 0
  fi
  printf '%s\n' "$drift"
  echo "forward-port check: $(printf '%s\n' "$drift" | wc -l | tr -d ' ') file(s) differ" \
       "between $repo_abs/$SRC and $target_abs - run 'bash tools/forward-port.sh --yes' to mirror"
  exit 1
fi

echo "forward-port: $repo_abs/$SRC -> $target_abs (dry-run)"
"${RSYNC[@]}" -n
if [[ "$APPLY" -ne 1 ]]; then
  echo "dry-run only - nothing written. Re-run with --yes to apply."
  exit 0
fi
mkdir -p "$target_abs"
"${RSYNC[@]}"
# Excluding a path also removes it from --delete's view, so a cache already sitting in the target
# would survive every future port - the exclude turns a reaped orphan into a permanent one. Two
# kinds of exclude are in play and they need opposite treatment: `.local` is the consuming copy's
# real state and must be preserved, while bytecode and test caches are deployment junk. Reap the
# junk explicitly. NOT `--delete-excluded`, which cannot tell them apart and would destroy
# `.local`.
# Scoped away from `.local`: the reap must never walk the consuming copy's own state, even to
# look. Only the two junk kinds are named, so a directory this script does not know about is
# left alone rather than swept by a general emptiness rule.
find "$target_abs" -name '.local' -prune -o \
     \( -name '__pycache__' -o -name '.pytest_cache' \) -type d -prune \
     -exec rm -rf {} + 2>/dev/null || true
echo "forward-port applied -> $target_abs (.local preserved; bytecode and test caches reaped)"
