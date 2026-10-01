#!/bin/bash
# Install SDLC Studio - a standard Agent Skill (SKILL.md) - into one or more
# coding agents (Claude Code, Codex, Gemini CLI, opencode, GitHub Copilot).
# Usage: curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash

set -e

# Configuration
REPO="DarrenBenson/sdlc-studio"
BRANCH="main"
SKILL_NAME="sdlc-studio"
ALL_TARGETS="claude codex gemini opencode copilot agents"

# Colours (disabled if not a terminal)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

info() { echo -e "${BLUE}==>${NC} $1"; }
success() { echo -e "${GREEN}==>${NC} $1"; }
warn() { echo -e "${YELLOW}Warning:${NC} $1"; }
error() { echo -e "${RED}Error:${NC} $1" >&2; }

# Help text
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    cat << 'EOF'
SDLC Studio Installer

SDLC Studio is a standard Agent Skill (SKILL.md), so it installs into any tool
that reads the skills directory. This script copies it into each chosen tool's
skills folder.

Usage:
    curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
    curl -fsSL ... | bash -s -- [options]
    ./install.sh [options]

Options:
    --target LIST   Comma-separated tools (repeatable). Values:
                    claude codex gemini opencode copilot | all | auto
                    Default: claude
    --global        Install to the per-user skills dir (default)
    --local         Install to the current project's skills dir
    --uninstall     Remove SDLC Studio from the resolved target dirs
    --list-targets  Print the target/directory map and what is detected
    --dry-run       Show what would be done without making changes
    --no-sweep      Skip refreshing sdlc-studio copies found in other
                    tool locations (default: refresh them all so no
                    stale version lingers; --local refreshes only this
                    project's, never the personal copies)
    --allow-downgrade  Overwrite an install/copy that is NEWER than the version
                    being installed (default: refuse, so an install from an
                    older published release cannot silently downgrade newer
                    local work - e.g. an unpushed dev checkout)
    --from DIR      Install from a LOCAL skill directory instead of downloading
                    the published release - the dev-testing path (e.g.
                    --from .claude/skills/sdlc-studio inside the source repo).
                    The same identity and downgrade guards apply
    --version VER   Install a specific version/tag, or `main` for the moving
                    branch (default: the latest published release, or main
                    when it cannot be looked up)
    --help, -h      Show this help

Targets (global / local skills directory):
    claude     ~/.claude/skills            .claude/skills
    codex      ~/.agents/skills            .agents/skills
    gemini     ~/.gemini/skills            .gemini/skills
    opencode   ~/.config/opencode/skills   .opencode/skills
    copilot    ~/.agents/skills            .github/skills
    agents     ~/.agents/skills            .agents/skills

The generic .agents/skills directory is read by Codex, Gemini CLI,
Copilot CLI, and Cursor - one "agents" install serves all four. Claude Code
does not read it; keep the claude target for Claude Code. (codex, copilot
and agents resolve to the same directory globally; it is installed once.)

Examples:
    # Claude Code, globally (the classic one-liner)
    curl -fsSL .../install.sh | bash

    # Every tool you have installed
    curl -fsSL .../install.sh | bash -s -- --target auto

    # Gemini + Codex, into this project
    curl -fsSL .../install.sh | bash -s -- --target gemini,codex --local

Native alternatives (sdlc-studio is a standard skill):
    gh skills install DarrenBenson/sdlc-studio sdlc-studio   # Copilot (gh >= 2.90)
    gemini skills install https://github.com/DarrenBenson/sdlc-studio   # Gemini
EOF
    exit 0
fi

# Parse arguments
INSTALL_MODE="global"
DRY_RUN=false
UNINSTALL=false
LIST_TARGETS=false
SWEEP=true
ALLOW_DOWNGRADE=false
LOCAL_SRC=""
VERSION="$BRANCH"
VERSION_GIVEN=false
TARGETS_RAW=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --global) INSTALL_MODE="global"; shift ;;
        --local) INSTALL_MODE="local"; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        --no-sweep) SWEEP=false; shift ;;
        --allow-downgrade) ALLOW_DOWNGRADE=true; shift ;;
        --from) LOCAL_SRC="$2"; shift 2 ;;
        --uninstall) UNINSTALL=true; shift ;;
        --list-targets) LIST_TARGETS=true; shift ;;
        --target)
            if [[ -z "${2:-}" ]]; then
                error "--target requires a value"; exit 2
            fi
            TARGETS_RAW="$TARGETS_RAW,${2}"
            shift 2 ;;
        --version)
            VERSION="${2:-}"
            if [[ -z "$VERSION" ]]; then error "--version requires a value"; exit 2; fi
            VERSION_GIVEN=true
            shift 2 ;;
        *) error "Unknown option: $1"; echo "Run with --help for usage." >&2; exit 2 ;;
    esac
done

# Skills directory for a (target, scope). Echoes the parent dir that should
# contain the sdlc-studio/ skill folder, or empty when not applicable.
target_dir() {
    local target="$1" scope="$2"
    case "$target:$scope" in
        claude:global)   echo "$HOME/.claude/skills" ;;
        claude:local)    echo ".claude/skills" ;;
        codex:global)    echo "$HOME/.agents/skills" ;;
        codex:local)     echo ".agents/skills" ;;
        gemini:global)   echo "$HOME/.gemini/skills" ;;
        gemini:local)    echo ".gemini/skills" ;;
        opencode:global) echo "$HOME/.config/opencode/skills" ;;
        opencode:local)  echo ".opencode/skills" ;;
        copilot:global)  echo "$HOME/.agents/skills" ;;   # read by Copilot CLI (BG0852)
        copilot:local)   echo ".github/skills" ;;
        agents:global)   echo "$HOME/.agents/skills" ;;
        agents:local)    echo ".agents/skills" ;;
        *) echo "" ;;
    esac
}

# Is a tool present on this machine?
is_detected() {
    case "$1" in
        claude)   command -v claude >/dev/null 2>&1 || [[ -d "$HOME/.claude" ]] ;;
        codex)    command -v codex  >/dev/null 2>&1 || [[ -d "$HOME/.codex" || -d "$HOME/.agents" ]] ;;
        gemini)   command -v gemini >/dev/null 2>&1 || [[ -d "$HOME/.gemini" ]] ;;
        opencode) command -v opencode >/dev/null 2>&1 || [[ -d "$HOME/.config/opencode" ]] ;;
        # gh and a .github folder are repo signals, so they count only for a --local install: a
        # global one must not be steered by the directory it happens to run from (CR0208).
        copilot)  command -v copilot >/dev/null 2>&1 || [[ -d "$HOME/.copilot" ]] \
                      || { [[ "$INSTALL_MODE" == local ]] && { command -v gh >/dev/null 2>&1 || [[ -d ".github" ]]; }; } ;;
        agents)   [[ -d "$HOME/.agents" ]] || command -v codex >/dev/null 2>&1 || command -v cursor >/dev/null 2>&1 \
                      || command -v copilot >/dev/null 2>&1 ;;
        *) return 1 ;;
    esac
}

# Per-tool note on how to use the skill once installed.
invoke_note() {
    case "$1" in
        claude)   echo "Claude Code: run /sdlc-studio (or it is model-invoked)." ;;
        codex)    echo "Codex: auto-discovered by description, or mention \$sdlc-studio / run /skills." ;;
        gemini)   echo "Gemini CLI: run /skills to confirm it is discovered; then it is used automatically." ;;
        opencode) echo "opencode: discovered automatically via the skill tool." ;;
        copilot)  echo "Copilot: Copilot CLI reads ~/.agents/skills, and .github/skills in a repo; run \`copilot skill list\` to confirm, then invoke from chat." ;;
        agents)   echo "Generic .agents/skills: read by Codex, Gemini CLI, Copilot, and Cursor (one copy serves all four; Claude Code does NOT read it)." ;;
    esac
}

# Native installer one-liner, printed only when the tool's CLI is present.
# Explicit `if`s, not trailing `&&` tests: an absent CLI must still return 0, or `set -e`
# aborts the installer mid-way through its Next steps (BG0774, the BG0054 shape).
native_hint() {
    case "$1" in
        gemini)
            if command -v gemini >/dev/null 2>&1; then
                echo "  native: gemini skills install https://github.com/$REPO"
            fi ;;
        copilot)
            if command -v gh >/dev/null 2>&1; then
                echo "  native: gh skills install $REPO $SKILL_NAME"
            fi ;;
    esac
}

# Display name for the hint below.
tool_name() {
    case "$1" in
        codex)    echo "Codex" ;;
        gemini)   echo "Gemini CLI" ;;
        opencode) echo "opencode" ;;
        copilot)  echo "Copilot CLI" ;;
        agents)   echo "Cursor" ;;
    esac
}

# Is the tool itself on this host? Stricter than is_detected, which serves --target auto: a shared
# folder (~/.agents) or a repo signal (gh, .github) is no evidence of a tool, and the hint below
# must not name one the host lacks. Cursor is what the agents target stands for here.
tool_present() {
    case "$1" in
        codex)    command -v codex >/dev/null 2>&1 || [[ -d "$HOME/.codex" ]] ;;
        gemini)   command -v gemini >/dev/null 2>&1 || [[ -d "$HOME/.gemini" ]] ;;
        opencode) command -v opencode >/dev/null 2>&1 || [[ -d "$HOME/.config/opencode" ]] ;;
        copilot)  command -v copilot >/dev/null 2>&1 || [[ -d "$HOME/.copilot" ]] ;;
        agents)   command -v cursor >/dev/null 2>&1 ;;
        *) return 1 ;;
    esac
}

# Every skills folder each tool reads, one per line: its personal folders for a global install,
# its project folders for a --local one. Wider than target_dir, which names the one folder this
# installer writes. Sources: `copilot skill --help` (Copilot CLI 1.0.71); the skills docs of
# opencode, Gemini CLI, Codex and Cursor (Cursor stands for the agents target).
read_dirs() {
    case "$1:$2" in
        claude:global)   printf '%s\n' "$HOME/.claude/skills" ;;
        claude:local)    printf '%s\n' ".claude/skills" ;;
        codex:global)    printf '%s\n' "$HOME/.agents/skills" "$HOME/.codex/skills" ;;
        codex:local)     printf '%s\n' ".agents/skills" ".codex/skills" ;;
        gemini:global)   printf '%s\n' "$HOME/.gemini/skills" "$HOME/.agents/skills" ;;
        gemini:local)    printf '%s\n' ".gemini/skills" ".agents/skills" ;;
        opencode:global) printf '%s\n' "$HOME/.config/opencode/skills" "$HOME/.claude/skills" "$HOME/.agents/skills" ;;
        opencode:local)  printf '%s\n' ".opencode/skills" ".claude/skills" ".agents/skills" ;;
        copilot:global)  printf '%s\n' "$HOME/.copilot/skills" "$HOME/.agents/skills" ;;
        copilot:local)   printf '%s\n' ".github/skills" ".agents/skills" ".claude/skills" ;;
        agents:global)   printf '%s\n' "$HOME/.agents/skills" "$HOME/.cursor/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" ;;
        agents:local)    printf '%s\n' ".agents/skills" ".cursor/skills" ".claude/skills" ".codex/skills" ;;
    esac
}

# Is the skill already where tool $1 reads it: a copy in any folder in read_dirs, or one this run
# installs ($2, space-delimited install folders, so a dry run counts what it would write)? A copy
# is what the sweep would call one (is_skill_copy): an empty or foreign sdlc-studio folder serves
# nothing.
tool_served() {
    local installing="$2" f
    while IFS= read -r f; do
        if [[ -z "$f" ]]; then continue; fi
        if [[ "$installing" == *" $f "* ]] || is_skill_copy "$f/$SKILL_NAME"; then return 0; fi
    done <<READ_DIRS
$(read_dirs "$1" "$INSTALL_MODE")
READ_DIRS
    return 1
}

# A default install serves Claude Code only. Name each other tool on this host that finds no copy
# of the skill in any folder it reads, and the --target that would add one, so a Copilot CLI user
# following the quick start is not left with no skill and no reason (BG0852). A copy anywhere the
# tool reads - installed earlier, refreshed by this run's sweep, or written by this run - serves
# it, so hinting it would only load the skill twice (BG0856). One target per install folder: codex
# and copilot share ~/.agents/skills, so both are named and one added.
# Explicit `if`s, so a run that finds nothing still returns 0 under set -e.
undetected_hint() {
    local targets="$1" t dir names="" list="" installing=" " seen
    for t in $targets; do installing="$installing$(target_dir "$t" "$INSTALL_MODE") "; done
    seen="$installing"
    for t in $ALL_TARGETS; do
        dir=$(target_dir "$t" "$INSTALL_MODE")
        if [[ -z "$dir" || " $targets " == *" $t "* ]]; then continue; fi
        if ! tool_present "$t" || tool_served "$t" "$installing"; then continue; fi
        names="$names, $(tool_name "$t")"
        if [[ "$seen" != *" $dir "* ]]; then
            seen="$seen$dir "
            list="$list,$t"
        fi
    done
    if [[ -n "$list" ]]; then
        echo ""
        info "Detected but not installed for: ${names#, }. To add: --target ${targets// /,}$list (or --target auto)."
    fi
}

# Resolve the requested target list into a clean, de-duplicated set.
resolve_targets() {
    local raw="${1#,}" out="" t
    [[ -z "$raw" ]] && raw="claude"
    raw="${raw//,/ }"
    local expanded=""
    for t in $raw; do
        case "$t" in
            all)  expanded="$expanded $ALL_TARGETS" ;;
            auto)
                local d
                for d in $ALL_TARGETS; do
                    # Globally copilot resolves to ~/.agents/skills, never .github/skills in the
                    # current directory, so auto may select it (CR0208, BG0852).
                    is_detected "$d" && expanded="$expanded $d"
                done ;;
            claude|codex|gemini|opencode|copilot|agents) expanded="$expanded $t" ;;
            *) error "Unknown target: $t (valid: $ALL_TARGETS all auto)"; exit 2 ;;
        esac
    done
    for t in $expanded; do
        case " $out " in *" $t "*) ;; *) out="$out $t" ;; esac
    done
    echo "${out# }"
}

check_deps() {
    local missing=()
    command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 || missing+=("curl or wget")
    command -v tar >/dev/null 2>&1 || missing+=("tar")
    if [[ ${#missing[@]} -gt 0 ]]; then error "Missing required tools: ${missing[*]}"; exit 1; fi
}

# Temp dir for the download, cleaned up when the script exits.
TMP_DIR=""
SRC=""
# The || true matters: under set -e, a false test in the EXIT trap would
# overwrite the script's real exit status with 1.
cleanup() { { [[ -n "$TMP_DIR" ]] && rm -rf "$TMP_DIR"; } || true; }
trap cleanup EXIT

# Best-effort fetch of a URL to stdout (empty on failure; used for the checksum sidecar).
fetch_stdout() {
    if command -v curl >/dev/null 2>&1; then curl -fsSL "$1" 2>/dev/null
    else wget -qO- "$1" 2>/dev/null; fi
}

# The tag of the latest published release (GitHub's releases/latest skips pre-releases), or
# empty when it cannot be looked up - offline, rate-limited, or a reply naming no plain tag. A
# tag goes into download URLs, so anything but [A-Za-z0-9._-] is treated as no answer.
latest_release_tag() {
    local api="https://api.github.com/repos/$REPO/releases/latest" body tag
    if command -v curl >/dev/null 2>&1; then body=$(curl -fsSL --max-time 15 "$api" 2>/dev/null) || body=""
    else body=$(wget -qO- -T 15 "$api" 2>/dev/null) || body=""; fi
    tag=$(printf '%s\n' "$body" | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
    [[ "$tag" =~ ^[A-Za-z0-9._-]+$ ]] && echo "$tag"
    return 0
}

# sha256 of a file, or empty if no hasher is on PATH.
sha256_of() {
    if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
    elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
    else echo ""; fi
}

# Download $1 to $2. Returns 0, or 22 when the server said 404 - the artefact is NOT THERE - or
# 1 for anything else.
#
# The three-way answer is the point (BG0575). A caller falls back to the unverified source
# archive on 22 and only on 22, so "no asset was published for this tag" is distinguished from
# "we could not reach the one that was". Reading a fault as an absence silently downgrades a user
# from bytes we published to bytes we did not, and reports it as a missing digest rather than as
# the failure it is.
#
# THE STATUS HAS TO BE READ, not inferred from the exit code. `curl -f` exits 22 for EVERY status
# at or above 400, so a 403, a rate-limiting 429 or a CDN 503 is indistinguishable from a 404 by
# exit code alone - and each of those is a fault, not an absence. `-w '%{http_code}'` without
# `-f` reports the status itself. wget collapses the same range onto exit 8, so its `-S` trace is
# read for the status line.
#
# Both branches delete a partial file on failure: `curl` without `-f` writes the error body to
# the output path, and `wget -O` leaves a zero-length file behind, either of which a later `tar`
# would read as a corrupt archive rather than as the absence it is.
download_to() {
    local url="$1" dest="$2" rc=0 code="" err=""
    if command -v curl >/dev/null 2>&1; then
        code=$(curl -sSL -o "$dest" -w '%{http_code}' "$url") || rc=$?
        if [[ "$rc" -ne 0 ]]; then rm -f "$dest"; return 1; fi
        case "$code" in
            2??) return 0 ;;
            404) rm -f "$dest"; return 22 ;;
            *)   rm -f "$dest"; return 1 ;;
        esac
    fi
    err=$(wget -q -S "$url" -O "$dest" 2>&1) || rc=$?
    if [[ "$rc" -eq 0 ]]; then return 0; fi
    rm -f "$dest"
    printf '%s' "$err" | grep -qE 'HTTP/[0-9.]+ 404' && return 22
    return 1
}

# Verify the downloaded tarball against a published sha256 BEFORE extraction, so a
# swapped artefact cannot inject code. The expected digest comes from (in order):
# SDLC_STUDIO_SHA256 (an explicit pin), else a best-effort sidecar `<url>.sha256`.
# With no published digest we warn and proceed for a rolling install, unless
# SDLC_STUDIO_REQUIRE_CHECKSUM=1 makes a missing digest fatal.
#
# The sidecar is fetched beside whatever was ACTUALLY downloaded, which is why the caller
# passes the resolved url rather than the one it first tried. GitHub serves no sidecar next to
# a generated source archive and never will, so before BG0575 this fallback could only ever
# resolve empty and REQUIRE_CHECKSUM=1 could only ever refuse.
verify_download() {
    local file="$1" url="$2" expected actual
    expected="${SDLC_STUDIO_SHA256:-}"
    [[ -z "$expected" ]] && expected=$(fetch_stdout "$url.sha256" | tr -d '\r' | awk 'NR==1{print $1}')
    if [[ -z "$expected" ]]; then
        if [[ "${SDLC_STUDIO_REQUIRE_CHECKSUM:-}" == "1" ]]; then
            error "No published sha256 for $VERSION and SDLC_STUDIO_REQUIRE_CHECKSUM=1 - refusing to install"
            exit 1
        fi
        warn "No published sha256 for $VERSION - installing unverified (set SDLC_STUDIO_SHA256 to pin)"
        return 0
    fi
    actual=$(sha256_of "$file")
    if [[ -z "$actual" ]]; then
        error "A sha256 was published for $VERSION but no sha256sum/shasum tool is available to verify it"
        exit 1
    fi
    # Lower-case with tr, not ${var,,}: the latter needs bash 4, but macOS ships bash 3.2.
    actual=$(printf '%s' "$actual" | tr 'A-Z' 'a-z')
    expected=$(printf '%s' "$expected" | tr 'A-Z' 'a-z')
    if [[ "$actual" != "$expected" ]]; then
        error "Checksum mismatch for $VERSION: expected $expected, got $actual - aborting before extraction"
        exit 1
    fi
    info "Checksum verified (sha256 $actual)"
}

# Download + extract once; set SRC to the extracted skill directory. With --from,
# skip the download entirely and install the given LOCAL tree - the dev-testing
# path (unreleased work cannot be downloaded; the published release may be older).
prepare_source() {
    local url extracted asset_url rc
    if [[ -n "$LOCAL_SRC" ]]; then
        if [[ ! -d "$LOCAL_SRC" ]] || ! is_skill_copy "$LOCAL_SRC"; then
            error "--from: $LOCAL_SRC is not an sdlc-studio skill directory (no matching SKILL.md)"
            exit 2
        fi
        SRC=$(canon "$LOCAL_SRC")
        VERSION="local:$(installed_version "$SRC")"
        info "Installing from local source: $SRC ($VERSION)"
        return
    fi
    # A tagged version prefers the RELEASE ASSET over GitHub's generated source archive, because
    # the asset and its `.sha256` are published together by this project's release workflow. That
    # is what makes the verified install possible at all: the digest belongs to bytes we produced,
    # so the pair cannot drift. GitHub's generated archives carry no digest we control and are not
    # guaranteed byte-stable, so verifying against one would turn a routine regeneration into a
    # `Checksum mismatch`, which reads exactly like an attack.
    #
    # Tags cut before the workflow existed have no assets, so the fallback stays - and with it,
    # honestly, a `REQUIRE_CHECKSUM=1` install of those tags still refuses. They genuinely have no
    # published digest; the fix is forward-only and must not pretend otherwise.
    url="https://github.com/$REPO/archive/refs/heads/$VERSION.tar.gz"
    asset_url=""
    if [[ "$VERSION" != "main" ]]; then
        url="https://github.com/$REPO/archive/refs/tags/$VERSION.tar.gz"
        asset_url="https://github.com/$REPO/releases/download/$VERSION/sdlc-studio-$VERSION.tar.gz"
    fi
    TMP_DIR=$(mktemp -d)
    info "Downloading SDLC Studio ($VERSION)..."
    if [[ -n "$asset_url" ]]; then
        rc=0
        download_to "$asset_url" "$TMP_DIR/archive.tar.gz" || rc=$?
        case "$rc" in
            0)  url="$asset_url" ;;
            22) info "No release asset for $VERSION - falling back to the source archive"
                download_to "$url" "$TMP_DIR/archive.tar.gz" \
                    || { error "Failed to download from $url"; exit 1; } ;;
            *)  error "Failed to reach $asset_url - a transport error, not a missing asset."
                error "Refusing to fall back to an unverified download on a network fault."
                exit 1 ;;
        esac
    else
        download_to "$url" "$TMP_DIR/archive.tar.gz" \
            || { error "Failed to download from $url"; exit 1; }
    fi
    verify_download "$TMP_DIR/archive.tar.gz" "$url"
    info "Extracting..."
    tar -xzf "$TMP_DIR/archive.tar.gz" -C "$TMP_DIR"
    extracted=$(find "$TMP_DIR" -maxdepth 1 -type d -name "sdlc-studio-*" | head -1)
    [[ -z "$extracted" ]] && { error "Failed to find extracted directory"; exit 1; }
    SRC="$extracted/.claude/skills/$SKILL_NAME"
}

ship_changelog() {
    # `project upgrade` digests the CHANGELOG between the project's recorded
    # version and the installed one; ship it with the payload so the digest
    # works offline (absent -> the tool degrades with an explicit message).
    local src="$1" dest="$2"
    local repo_root="${src%/.claude/skills/$SKILL_NAME}"
    [[ -f "$repo_root/CHANGELOG.md" ]] && cp "$repo_root/CHANGELOG.md" "$dest/CHANGELOG.md"
    return 0
}

# Stage a copy into a temp sibling then swap it into place, so a failed copy can never
# destroy or half-overwrite the existing install (CR0205). Returns non-zero on a copy
# failure, leaving the previous install byte-for-byte intact.
swap_install() {
    # dest on its OWN line: on a single `local` line bash expands every RHS before applying
    # any assignment, so `$parent` would resolve to the CALLER's dynamic-scoped parent, not
    # this line's `$1` - an `rm -rf "$dest"` riding on that coincidence is a latent footgun.
    local parent="$1" src="$2"
    local dest="$parent/$SKILL_NAME"
    local staging="$parent/.$SKILL_NAME.new-$$"
    mkdir -p "$parent"
    rm -rf "$staging"
    if ! cp -r "$src" "$staging"; then
        rm -rf "$staging"
        return 1
    fi
    ship_changelog "$src" "$staging"
    rm -rf "$dest"
    mv "$staging" "$dest"
}

install_to() {
    local parent="$1" src="$2" dest="$1/$SKILL_NAME"
    if [[ -d "$dest" && "$(canon "$dest")" == "$(canon "$src")" ]]; then
        info "skipping $dest: it IS the --from source"; return 0
    fi
    # A folder holding something that is not an sdlc-studio copy is the user's, not ours to
    # replace: skipped as the sweep skips it. An empty folder holds nothing and is installed into.
    if [[ -d "$dest" ]] && ! is_skill_copy "$dest" && [[ -n "$(ls -A "$dest" 2>/dev/null)" ]]; then
        warn "skipping $dest (no sdlc-studio SKILL.md - not touching it)"
        return 0
    fi
    if would_downgrade "$dest" "$(installed_version "$src")"; then
        return 0   # refused: a downgrade of newer local work is a skip, not a failure
    fi
    if [[ "$DRY_RUN" == true ]]; then
        info "[dry run] would install to: $dest"; return
    fi
    if ! swap_install "$parent" "$src"; then
        error "install failed: could not copy to $dest (previous install left untouched)"
        return 1
    fi
    success "installed: $dest"
}

uninstall_from() {
    local dest="$1/$SKILL_NAME"
    if [[ ! -d "$dest" ]]; then info "not present: $dest"; return; fi
    if [[ "$DRY_RUN" == true ]]; then info "[dry run] would remove: $dest"; return; fi
    rm -rf "$dest"; success "removed: $dest"
}

# Canonical physical path of an existing directory (portable: no readlink -f).
canon() { (cd "$1" 2>/dev/null && pwd -P) || echo "$1"; }

# Version recorded inside an installed copy (templates/version.yaml).
installed_version() {
    local v
    v=$(grep -m1 '^skill_version:' "$1/templates/version.yaml" 2>/dev/null \
        | sed 's/^skill_version:[[:space:]]*"\{0,1\}\([^"#]*\)"\{0,1\}.*/\1/' \
        | tr -d ' ')
    echo "${v:-unknown}"
}

# True when version $1 is strictly older than $2. Semver cores compare via `sort -V`;
# when cores are equal, pre-release precedence applies (4.0.0-rc.1 is OLDER than 4.0.0 -
# plain sort -V gets this backwards, BG0106). A non-semver token (a branch name, or
# `unknown`) never compares as older, so it is never a false downgrade.
version_lt() {
    [[ "$1" == "$2" ]] && return 1
    case "$1$2" in *[!0-9.rc+-]*) return 1 ;; esac  # not both semver-ish -> not comparable
    local c1="${1%%-*}" c2="${2%%-*}" s1="" s2=""
    [[ "$1" == *-* ]] && s1="${1#*-}"
    [[ "$2" == *-* ]] && s2="${2#*-}"
    if [[ "$c1" != "$c2" ]]; then
        [[ "$(printf '%s\n%s\n' "$c1" "$c2" | sort -V | head -n1)" == "$c1" ]]
        return
    fi
    [[ -n "$s1" && -z "$s2" ]] && return 0   # pre-release precedes its release
    [[ -z "$s1" ]] && return 1               # release never older than its pre-release
    [[ "$s1" == "$s2" ]] && return 1
    [[ "$(printf '%s\n%s\n' "$s1" "$s2" | sort -V | head -n1)" == "$s1" ]]
}

# True (and prints a warning) when writing version `$2` over the sdlc-studio copy at `$1` would
# be a DOWNGRADE (the copy is newer) and --allow-downgrade was not given. Callers skip the write,
# so an install from an older published release cannot silently revert newer local work (BG0100).
would_downgrade() {
    local dest="$1" incoming="$2" existing
    [[ "$ALLOW_DOWNGRADE" == true ]] && return 1
    [[ -d "$dest" ]] && is_skill_copy "$dest" || return 1
    existing=$(installed_version "$dest")
    if version_lt "$incoming" "$existing"; then
        warn "$dest is at $existing, NEWER than the $incoming being installed - refusing to downgrade (pass --allow-downgrade to force). Newer local work is left untouched."
        return 0
    fi
    return 1
}

# Identity guard: only ever touch a directory that is genuinely this skill.
is_skill_copy() {
    [[ -f "$1/SKILL.md" ]] && grep -q '^name: sdlc-studio[[:space:]]*$' "$1/SKILL.md"
}

# Refresh every sdlc-studio copy found in a known location of the install's reach that was not
# already written this run, so no stale version lingers. A --local install reaches this project
# only: it pins a version here, and the personal copies are what every other project loads.
sweep_stale() {
    local src="$1" done_list="$2"
    local t scope scopes="global local" parent dest old new_ver found=false parents=()
    [[ "$INSTALL_MODE" == local ]] && scopes="local"
    if [[ "$DRY_RUN" == true ]]; then new_ver="$VERSION"; else new_ver=$(installed_version "$src"); fi
    for t in $ALL_TARGETS; do
        for scope in $scopes; do parents+=("$(target_dir "$t" "$scope")"); done
    done
    # Copilot CLI also reads ~/.copilot/skills. The installer writes ~/.agents/skills, so a copy
    # placed there by hand is reached only by naming the folder here (BG0852).
    if [[ "$INSTALL_MODE" != local ]]; then parents+=("$HOME/.copilot/skills"); fi
    for parent in "${parents[@]}"; do
        [[ -z "$parent" || ! -d "$parent" ]] && continue
        parent=$(canon "$parent")
        dest="$parent/$SKILL_NAME"
        case " $done_list " in *" $dest "*) continue ;; esac
        [[ -d "$dest" ]] || continue
        if [[ "$(canon "$dest")" == "$(canon "$src")" ]]; then
            info "sweep: skipping $dest (it IS the install source)"
            continue
        fi
        done_list="$done_list $dest"
        if ! is_skill_copy "$dest"; then
            warn "sweep: skipping $dest (no sdlc-studio SKILL.md - not touching it)"
            continue
        fi
        old=$(installed_version "$dest")
        # Never silently downgrade a copy that is newer than what we are installing - the
        # sweep spreading an older published release over a newer dev checkout is BG0100.
        if [[ "$DRY_RUN" != true ]] && would_downgrade "$dest" "$new_ver"; then
            continue
        fi
        found=true
        if [[ "$DRY_RUN" == true ]]; then
            info "[dry run] would refresh: $dest ($old -> $new_ver)"
        elif ! swap_install "$parent" "$src"; then
            error "refresh failed: could not copy to $dest ($old kept)"
        else
            success "refreshed: $dest ($old -> $new_ver)"
        fi
    done
    # An explicit `if` (not a trailing `&&` test): when $found is true this function's last
    # command must still return 0, or `set -e` aborts the installer after a successful sweep
    # and the success banner never prints (BG0054).
    if [[ "$found" == false ]]; then
        info "sweep: no other sdlc-studio copies found"
    fi
}

# Claude Code loads a personal skill ahead of a project skill of the same name, so a --local
# install under a personal copy is not the copy it runs. Named here, never changed: the personal
# copy is the user's. One directory reached by both paths (a --local install run from $HOME)
# shadows nothing. $1 is the project copy's version when there is no copy to read it from.
shadow_note() {
    local personal="$HOME/.claude/skills/$SKILL_NAME" project version="$1"
    if [[ ! -d "$personal" ]] || ! is_skill_copy "$personal"; then return 0; fi
    personal=$(canon "$personal")
    project=$(target_dir claude local)
    if [[ -d "$project" ]]; then project=$(canon "$project"); else project="$PWD/$project"; fi
    project="$project/$SKILL_NAME"
    if [[ -d "$project" && "$(canon "$project")" == "$personal" ]]; then return 0; fi
    if [[ "$DRY_RUN" != true ]] && is_skill_copy "$project"; then
        version=$(installed_version "$project")
    fi
    warn "Claude Code loads the personal copy $personal ($(installed_version "$personal")) ahead of this project's copy $project ($version), so this project runs the personal one. Remove or update it to run this project's."
}

print_list() {
    echo ""
    echo -e "${BLUE}SDLC Studio - targets${NC}"
    printf '  %-9s %-28s %-18s %s\n' TARGET "GLOBAL DIR" "LOCAL DIR" DETECTED
    local t g l d
    for t in $ALL_TARGETS; do
        g=$(target_dir "$t" global); l=$(target_dir "$t" local)
        [[ -z "$g" ]] && g="(repo-scoped)"
        if is_detected "$t"; then d="yes"; else d="no"; fi
        printf '  %-9s %-28s %-18s %s\n' "$t" "${g/#$HOME/~}" "$l" "$d"
    done
    echo ""
}

main() {
    echo ""
    echo -e "${BLUE}SDLC Studio Installer${NC}"
    echo ""

    if [[ "$LIST_TARGETS" == true ]]; then print_list; exit 0; fi

    # No --version: install the latest published release, which goes down the tagged path and
    # is verified against its published sha256. `main` publishes none, so it is installed only
    # when asked for by name, or when the lookup fails (an offline machine still installs).
    if [[ "$UNINSTALL" == false && -z "$LOCAL_SRC" && "$VERSION_GIVEN" == false ]]; then
        local latest; latest=$(latest_release_tag)
        if [[ -n "$latest" ]]; then
            VERSION="$latest"
        else
            warn "could not resolve the latest release (offline or rate-limited?) - installing $BRANCH"
        fi
    fi

    local targets; targets=$(resolve_targets "$TARGETS_RAW")
    info "Targets: $targets"
    info "Scope: $INSTALL_MODE"
    [[ "$UNINSTALL" == false ]] && info "Version: $VERSION"
    echo ""

    # Resolve each target to a destination parent dir for the chosen scope.
    local t scope parent resolved=""
    for t in $targets; do
        scope="$INSTALL_MODE"
        parent=$(target_dir "$t" "$scope")
        [[ -z "$parent" ]] && { warn "no $scope dir for $t; skipping"; continue; }
        case " $resolved " in *":$parent "*) continue ;; esac   # codex/agents share a dir
        resolved="$resolved $t:$parent"
    done
    [[ -z "$resolved" ]] && { error "No installable targets resolved."; exit 1; }

    if [[ "$UNINSTALL" == true ]]; then
        for item in $resolved; do uninstall_from "${item#*:}"; done
        echo ""; success "Uninstall complete."; exit 0
    fi

    if [[ "$DRY_RUN" == false ]]; then
        check_deps
        prepare_source
        [[ ! -d "$SRC" ]] && { error "Skill files not found in archive at $SRC"; exit 1; }
    elif [[ -n "$LOCAL_SRC" ]]; then
        # A dry run skips the download, but --from must still be VALIDATED - reporting
        # "would install" from a directory that would be refused for real is a false preview.
        prepare_source
    fi

    echo ""
    local installed_dests="" dest_parent
    for item in $resolved; do
        install_to "${item#*:}" "$SRC"
        dest_parent=$(canon "${item#*:}")
        installed_dests="$installed_dests $dest_parent/$SKILL_NAME"
    done

    if [[ "$SWEEP" == true ]]; then
        echo ""
        info "Sweep: checking other tool locations for stale copies..."
        sweep_stale "$SRC" "$installed_dests"
    fi
    if [[ "$INSTALL_MODE" == local && " $targets " == *" claude "* ]]; then
        echo ""
        shadow_note "$VERSION"
    fi
    if [[ -z "$TARGETS_RAW" ]]; then undetected_hint "$targets"; fi

    echo ""
    if [[ "$DRY_RUN" == true ]]; then
        success "Dry run complete - no changes made"
    else
        success "SDLC Studio installed for: $targets"
        echo ""
        echo "Next steps:"
        for t in $targets; do
            echo "  - $(invoke_note "$t")"
            native_hint "$t"
        done
        echo ""
        echo "Then: status / hint / help (e.g. Claude: /sdlc-studio status)."
    fi
}

# Run main only when executed, not when sourced (so the functions above are
# unit-testable in isolation - e.g. tools/tests/test_install_sweep.py).
# Piped (curl | bash) there is no source file, so BASH_SOURCE[0] is unset and
# the :-$0 fallback is what makes main run in the README's advertised install.
if [[ "${BASH_SOURCE[0]:-$0}" == "${0}" ]]; then
    main
fi
