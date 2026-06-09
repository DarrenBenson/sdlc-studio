#!/bin/bash
# Install SDLC Studio - a standard Agent Skill (SKILL.md) - into one or more
# coding agents (Claude Code, Codex, Gemini CLI, opencode, GitHub Copilot).
# Usage: curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash

set -e

# Configuration
REPO="DarrenBenson/sdlc-studio"
BRANCH="main"
SKILL_NAME="sdlc-studio"
ALL_TARGETS="claude codex gemini opencode copilot"

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
    --version VER   Install a specific version/tag (default: main)
    --help, -h      Show this help

Targets (global / local skills directory):
    claude     ~/.claude/skills            .claude/skills
    codex      ~/.agents/skills            .agents/skills
    gemini     ~/.gemini/skills            .gemini/skills
    opencode   ~/.config/opencode/skills   .opencode/skills
    copilot    (repo-scoped)               .github/skills

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
VERSION="$BRANCH"
TARGETS_RAW=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --global) INSTALL_MODE="global"; shift ;;
        --local) INSTALL_MODE="local"; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
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
        copilot:global)  echo "" ;;   # repo-scoped only
        copilot:local)   echo ".github/skills" ;;
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
        copilot)  command -v gh >/dev/null 2>&1 || [[ -d ".github" ]] ;;
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
        copilot)  echo "Copilot: reads .github/skills in the repo; invoke from chat or via a slash command." ;;
    esac
}

# Native installer one-liner, printed only when the tool's CLI is present.
native_hint() {
    case "$1" in
        gemini)  command -v gemini >/dev/null 2>&1 && echo "  native: gemini skills install https://github.com/$REPO" ;;
        copilot) command -v gh >/dev/null 2>&1 && echo "  native: gh skills install $REPO $SKILL_NAME" ;;
    esac
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
                for d in $ALL_TARGETS; do is_detected "$d" && expanded="$expanded $d"; done ;;
            claude|codex|gemini|opencode|copilot) expanded="$expanded $t" ;;
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
cleanup() { [[ -n "$TMP_DIR" ]] && rm -rf "$TMP_DIR"; }
trap cleanup EXIT

# Download + extract once; set SRC to the extracted skill directory.
prepare_source() {
    local url extracted
    url="https://github.com/$REPO/archive/refs/heads/$VERSION.tar.gz"
    [[ "$VERSION" != "main" ]] && url="https://github.com/$REPO/archive/refs/tags/$VERSION.tar.gz"
    TMP_DIR=$(mktemp -d)
    info "Downloading SDLC Studio ($VERSION)..."
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$url" -o "$TMP_DIR/archive.tar.gz" || { error "Failed to download from $url"; exit 1; }
    else
        wget -q "$url" -O "$TMP_DIR/archive.tar.gz" || { error "Failed to download from $url"; exit 1; }
    fi
    info "Extracting..."
    tar -xzf "$TMP_DIR/archive.tar.gz" -C "$TMP_DIR"
    extracted=$(find "$TMP_DIR" -maxdepth 1 -type d -name "sdlc-studio-*" | head -1)
    [[ -z "$extracted" ]] && { error "Failed to find extracted directory"; exit 1; }
    SRC="$extracted/.claude/skills/$SKILL_NAME"
}

install_to() {
    local parent="$1" src="$2" dest="$1/$SKILL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        info "[dry run] would install to: $dest"; return
    fi
    mkdir -p "$parent"
    [[ -d "$dest" ]] && rm -rf "$dest"
    cp -r "$src" "$parent/"
    success "installed: $dest"
}

uninstall_from() {
    local dest="$1/$SKILL_NAME"
    if [[ ! -d "$dest" ]]; then info "not present: $dest"; return; fi
    if [[ "$DRY_RUN" == true ]]; then info "[dry run] would remove: $dest"; return; fi
    rm -rf "$dest"; success "removed: $dest"
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
        if [[ -z "$parent" && "$t" == "copilot" ]]; then
            warn "Copilot skills are repo-scoped; using ./.github/skills"
            parent=$(target_dir copilot local)
        fi
        [[ -z "$parent" ]] && { warn "no $scope dir for $t; skipping"; continue; }
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
    fi

    echo ""
    for item in $resolved; do install_to "${item#*:}" "$SRC"; done

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

main
