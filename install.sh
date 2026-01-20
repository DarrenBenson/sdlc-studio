#!/bin/bash
# Install SDLC Studio skill for Claude Code
# Usage: curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash

set -e

# Configuration
REPO="DarrenBenson/sdlc-studio"
BRANCH="main"
SKILL_NAME="sdlc-studio"

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

# Help text
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    cat << 'EOF'
SDLC Studio Installer

Usage:
    curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
    curl -fsSL ... | bash -s -- [options]
    ./install.sh [options]

Options:
    --global        Install to ~/.claude/skills/ (default)
    --local         Install to ./.claude/skills/ (current project)
    --dry-run       Show what would be done without making changes
    --version VER   Install specific version/tag (default: main)
    --help, -h      Show this help

Examples:
    # Install globally (recommended)
    curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash

    # Install to current project
    curl -fsSL ... | bash -s -- --local

    # Install specific version
    curl -fsSL ... | bash -s -- --version v1.0.0
EOF
    exit 0
fi

# Parse arguments
INSTALL_MODE="global"
DRY_RUN=false
VERSION="$BRANCH"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --global)
            INSTALL_MODE="global"
            shift
            ;;
        --local)
            INSTALL_MODE="local"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --version)
            VERSION="${2:-}"
            if [[ -z "$VERSION" ]]; then
                echo -e "${RED}Error: --version requires a value${NC}" >&2
                exit 2
            fi
            shift 2
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}" >&2
            echo "Run with --help for usage information" >&2
            exit 2
            ;;
    esac
done

# Determine install directory
if [[ "$INSTALL_MODE" == "global" ]]; then
    INSTALL_DIR="$HOME/.claude/skills"
else
    INSTALL_DIR=".claude/skills"
fi

SKILL_DIR="$INSTALL_DIR/$SKILL_NAME"

# Logging functions
info() { echo -e "${BLUE}==>${NC} $1"; }
success() { echo -e "${GREEN}==>${NC} $1"; }
warn() { echo -e "${YELLOW}Warning:${NC} $1"; }
error() { echo -e "${RED}Error:${NC} $1" >&2; }

# Check dependencies
check_deps() {
    local missing=()

    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        missing+=("curl or wget")
    fi

    if ! command -v tar &> /dev/null; then
        missing+=("tar")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing required tools: ${missing[*]}"
        exit 1
    fi
}

# Download and extract
download() {
    local url="https://github.com/$REPO/archive/refs/heads/$VERSION.tar.gz"
    local tmp_dir

    # Try tags if branch doesn't exist
    if [[ "$VERSION" != "main" ]]; then
        url="https://github.com/$REPO/archive/refs/tags/$VERSION.tar.gz"
    fi

    tmp_dir=$(mktemp -d)
    trap "rm -rf '$tmp_dir'" EXIT

    info "Downloading SDLC Studio ($VERSION)..."

    if command -v curl &> /dev/null; then
        if ! curl -fsSL "$url" -o "$tmp_dir/archive.tar.gz"; then
            error "Failed to download from $url"
            exit 1
        fi
    else
        if ! wget -q "$url" -O "$tmp_dir/archive.tar.gz"; then
            error "Failed to download from $url"
            exit 1
        fi
    fi

    info "Extracting..."
    tar -xzf "$tmp_dir/archive.tar.gz" -C "$tmp_dir"

    # Find extracted directory (handles both branch and tag naming)
    local extracted_dir
    extracted_dir=$(find "$tmp_dir" -maxdepth 1 -type d -name "sdlc-studio-*" | head -1)

    if [[ -z "$extracted_dir" ]]; then
        error "Failed to find extracted directory"
        exit 1
    fi

    # Install
    if [[ "$DRY_RUN" == true ]]; then
        info "[Dry run] Would create: $INSTALL_DIR"
        info "[Dry run] Would install to: $SKILL_DIR"
    else
        mkdir -p "$INSTALL_DIR"

        # Remove existing installation
        if [[ -d "$SKILL_DIR" ]]; then
            warn "Removing existing installation at $SKILL_DIR"
            rm -rf "$SKILL_DIR"
        fi

        # Copy skill files
        cp -r "$extracted_dir/.claude/skills/$SKILL_NAME" "$INSTALL_DIR/"
    fi
}

# Main
main() {
    echo ""
    echo -e "${BLUE}SDLC Studio Installer${NC}"
    echo ""

    check_deps

    info "Install mode: $INSTALL_MODE"
    info "Install path: $SKILL_DIR"
    info "Version: $VERSION"
    echo ""

    download

    if [[ "$DRY_RUN" == true ]]; then
        echo ""
        success "Dry run complete - no changes made"
    else
        echo ""
        success "SDLC Studio installed successfully!"
        echo ""
        echo "Get started:"
        echo "  /sdlc-studio help      Show command reference"
        echo "  /sdlc-studio status    Check pipeline state"
        echo "  /sdlc-studio hint      Get next suggested action"
        echo ""
    fi
}

main
