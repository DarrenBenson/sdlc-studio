#!/usr/bin/env bash
# Drive the two paths every adopter arrives on, through the shipped CLI, on fixtures built from
# nothing.
#
# Every other check in this repository runs against this repository. The two situations a user is
# actually in - a project that has just been created, and a project being upgraded from v4 - are
# the two this repository cannot occupy, and both were found broken the first time anybody walked
# them. Twenty minutes of walking them by hand turned up three consumer-facing defects that a
# 6000-test suite, twenty gate lanes and a 250-point backlog had all missed.
#
#   rehearse-release.sh greenfield   init a project from nothing, reach a written sprint plan
#   rehearse-release.sh upgrade      build a v4-era workspace, migrate it, gate it
#   rehearse-release.sh all          both
#
# Exit 0 only when the path completes. Every command is invoked as the shipped CLI and its exit
# status is read directly - never through a pipe, because a pipe reports the last stage's status
# and this repository has read a red suite as green that way twice in one session.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$REPO/.claude/skills/sdlc-studio/scripts"
BASELINE="$REPO/tools/release-rehearsal-baseline.txt"
PY="${PYTHON:-python3}"

# Fixtures are built under a temporary root and NOTHING is written inside the repository. A
# caller-supplied root that defaulted to `.` once destroyed 23 mutation registrations in this
# working tree, so the root here is never taken from an argument.
WORK="$(mktemp -d)"
# REFUSE a work root inside the repository, before the cleanup trap is armed. The trap is
# `rm -rf "$WORK"`, so a work root pointed at the repository deletes the working tree - a
# reviewer applying this file's own declared mutant lost a git worktree that way. The guard
# costs one comparison and removes the whole class.
case "$WORK" in
  "$REPO"|"$REPO"/*) echo "rehearsal REFUSED: the work root must not be inside the repository ($WORK)" >&2; exit 2 ;;
esac
trap 'rm -rf "$WORK"' EXIT

fail() { echo "rehearsal FAILED: $*" >&2; exit 1; }
step() { echo "  - $*"; }

# ---------------------------------------------------------------- greenfield

rehearse_greenfield() {
  echo "greenfield: a project that has just been created reaches a written sprint plan"
  local root="$WORK/greenfield"
  mkdir -p "$root"

  step "init run"
  "$PY" "$SCRIPTS/init.py" --root "$root" run >/dev/null 2>&1 \
    || fail "greenfield: \`init run\` did not complete"

  # An ordinary first story: it describes code nobody has written, so NONE of its declared paths
  # exists. That is the whole point of the fixture - it is the shape every greenfield story has.
  cat > "$root/sdlc-studio/stories/US0001-signup.md" <<'STORY'
# US0001: a visitor can sign up with an email address

> **Status:** Ready
> **Epic:** EP0001
> **Priority:** High
> **Affects:** src/auth/signup.py, tests/test_signup.py
> **Points:** 3

## Acceptance Criteria

### AC1: an account is created

- **Given** a valid email address
- **When** the signup form is submitted
- **Then** an account exists
- **Verify:** shell true
STORY

  echo "US0001" > "$root/worklist.txt"

  step "sprint plan --write"
  "$PY" "$SCRIPTS/sprint.py" --root "$root" plan --worklist "$root/worklist.txt" --write \
        --sprint-goal "a visitor can sign up" >/dev/null 2>&1 \
    || fail "greenfield: \`sprint plan --write\` refused a first sprint (exit $?)"

  [ -f "$root/sdlc-studio/.local/run-state.json" ] \
    || fail "greenfield: sprint plan exited 0 but wrote no run"
  grep -q "US0001" "$root/sdlc-studio/.local/run-state.json" \
    || fail "greenfield: a run was written but the story is not in its batch"

  echo "greenfield: OK"
}

# ------------------------------------------------------------------- upgrade

# The upgrade does NOT reach a green gate today: conformance, reconcile and index-derived all fail
# on a freshly migrated project, and the remedy is the grandfathering work in a later charter.
# Claiming green here would be exactly the false claim this rehearsal exists to prevent, so the
# failing lanes are compared against a recorded baseline and the comparison reddens in BOTH
# directions - a new failure blocks, and a baselined lane that starts passing blocks too, because
# a baseline that only ever tolerates is one that never empties.
rehearse_upgrade() {
  echo "upgrade: a v4-era project migrates, and its gate matches the recorded baseline"
  local root="$WORK/upgrade"
  mkdir -p "$root"

  step "init run, then age the workspace back to v4"
  "$PY" "$SCRIPTS/init.py" --root "$root" run >/dev/null 2>&1 \
    || fail "upgrade: \`init run\` did not complete"
  "$PY" - "$root" <<'AGE'
import pathlib, sys
root = pathlib.Path(sys.argv[1])
cfg = root / "sdlc-studio" / ".config.yaml"
cfg.write_text(cfg.read_text(encoding="utf-8").replace("schema_version: 3", "schema_version: 2"),
               encoding="utf-8")
(root / "sdlc-studio" / "stories" / "US0001-legacy.md").write_text(
    "# US0001: legacy login\n\n> **Status:** Done\n> **Epic:** EP0001\n> **Priority:** High\n\n"
    "## Acceptance Criteria\n\n- [x] **AC1** a valid password logs the user in\n", encoding="utf-8")
(root / "sdlc-studio" / "stories" / "US0002-legacy.md").write_text(
    "# US0002: legacy reset\n\n> **Status:** Ready\n> **Epic:** EP0001\n> **Priority:** Medium\n\n"
    "## Acceptance Criteria\n\n- [ ] **AC1** a reset link sets a new password\n", encoding="utf-8")
(root / "sdlc-studio" / "change-requests" / "CR0001-legacy.md").write_text(
    "# CR-0001: legacy request\n\n> **Status:** Approved\n> **Priority:** Medium\n"
    "> **Effort:** M\n\n## Summary\n\nAdd SSO.\n", encoding="utf-8")
AGE

  step "migrate --apply"
  echo "    order: migrate" 
  "$PY" "$SCRIPTS/migrate.py" --root "$root" --apply >/dev/null 2>&1 \
    || fail "upgrade: \`migrate --apply\` did not complete"

  step "gate"
  echo "    order: gate"
  local out; out="$("$PY" "$SCRIPTS/gate.py" --root "$root" 2>&1)"
  local failing; failing="$(echo "$out" | sed -n 's/^  \[FAIL\] \([a-z-]*\) .*/\1/p' | sort -u)"
  local baselined; baselined="$(sed -n 's/^\([a-z-]*\)|.*/\1/p' "$BASELINE" | sort -u)"

  local new_failures; new_failures="$(comm -23 <(echo "$failing") <(echo "$baselined"))"
  local now_passing; now_passing="$(comm -13 <(echo "$failing") <(echo "$baselined"))"

  if [ -n "$new_failures" ]; then
    echo "$out" >&2
    fail "upgrade: lane(s) failing that the baseline does not record: $(echo "$new_failures" | tr '\n' ' ')"
  fi
  if [ -n "$now_passing" ]; then
    fail "upgrade: baselined lane(s) now PASS and must be removed from $BASELINE: $(echo "$now_passing" | tr '\n' ' ')"
  fi

  while IFS='|' read -r lane artefact _rest; do
    case "$lane" in ''|\#*) continue ;; esac
    [ -n "$artefact" ] || fail "upgrade: baseline row for '$lane' names no clearing artefact"
    echo "    known gap: $lane -> $artefact"
  done < "$BASELINE"
  echo "upgrade: OK ($(echo "$baselined" | wc -w) known gap(s), none new)"
}

case "${1:-all}" in
  greenfield) rehearse_greenfield ;;
  upgrade)    rehearse_upgrade ;;
  all)        rehearse_greenfield && rehearse_upgrade ;;
  *)          echo "usage: rehearse-release.sh [greenfield|upgrade|all]" >&2; exit 2 ;;
esac
