# Install SDLC Studio skill for Claude Code (Windows)
# Usage: irm https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.ps1 | iex
#        .\install.ps1 [-Local] [-DryRun] [-Version <tag>]

[CmdletBinding()]
param(
    [switch]$Global,
    [switch]$Local,
    [switch]$DryRun,
    [string]$Version = 'main',
    [switch]$Help
)

# Body lives in a function so it works both as a downloaded script and when
# piped via `irm ... | iex`. Under iex the script runs in the caller's session,
# where `exit` would close the window and a bare $ErrorActionPreference would
# leak into the shell. A function scopes the preference and lets throw/return
# surface errors without killing the host.
function Invoke-Install {
    [CmdletBinding()]
    param(
        [switch]$Global,
        [switch]$Local,
        [switch]$DryRun,
        [string]$Version = 'main',
        [switch]$Help
    )

    $ErrorActionPreference = 'Stop'

    # Configuration
    $Repo = 'DarrenBenson/sdlc-studio'
    $SkillName = 'sdlc-studio'

    if ($Help) {
        @'
SDLC Studio Installer (Windows)

Usage:
    irm https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.ps1 | iex
    .\install.ps1 [options]

Options:
    -Global         Install to $HOME\.claude\skills\ (default)
    -Local          Install to .\.claude\skills\ (current project)
    -DryRun         Show what would be done without making changes
    -Version VER    Install specific version/tag (default: main)
    -Help           Show this help

Examples:
    # Install globally (recommended)
    .\install.ps1

    # Install to current project
    .\install.ps1 -Local

    # Install specific version
    .\install.ps1 -Version v1.5.0
'@
        return
    }

    if ($Global -and $Local) {
        throw 'Cannot use -Global and -Local together'
    }

    # Determine install directory
    $InstallMode = if ($Local) { 'local' } else { 'global' }
    $InstallDir = if ($Local) {
        Join-Path (Get-Location) '.claude\skills'
    } else {
        Join-Path $HOME '.claude\skills'
    }
    $SkillDir = Join-Path $InstallDir $SkillName

    function Write-Info($Message) { Write-Host '==> ' -ForegroundColor Blue -NoNewline; Write-Host $Message }
    function Write-Success($Message) { Write-Host '==> ' -ForegroundColor Green -NoNewline; Write-Host $Message }
    function Write-Warn($Message) { Write-Host 'Warning: ' -ForegroundColor Yellow -NoNewline; Write-Host $Message }

    Write-Host ''
    Write-Host 'SDLC Studio Installer' -ForegroundColor Blue
    Write-Host ''
    Write-Info "Install mode: $InstallMode"
    Write-Info "Install path: $SkillDir"
    Write-Info "Version: $Version"
    Write-Host ''

    # Build download URL (zip - branch or tag)
    $Url = if ($Version -eq 'main') {
        "https://github.com/$Repo/archive/refs/heads/$Version.zip"
    } else {
        "https://github.com/$Repo/archive/refs/tags/$Version.zip"
    }

    $TmpDir = Join-Path ([System.IO.Path]::GetTempPath()) "sdlc-studio-install-$([System.IO.Path]::GetRandomFileName())"
    New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null

    try {
        Write-Info "Downloading SDLC Studio ($Version)..."
        $ZipPath = Join-Path $TmpDir 'archive.zip'
        try {
            Invoke-WebRequest -Uri $Url -OutFile $ZipPath -UseBasicParsing
        } catch {
            throw "Failed to download from $Url`n$($_.Exception.Message)"
        }

        Write-Info 'Extracting...'
        Expand-Archive -Path $ZipPath -DestinationPath $TmpDir -Force

        # Find extracted directory (handles both branch and tag naming)
        $ExtractedDir = Get-ChildItem -Path $TmpDir -Directory -Filter 'sdlc-studio-*' | Select-Object -First 1
        if (-not $ExtractedDir) {
            throw 'Failed to find extracted directory'
        }

        $SourceDir = Join-Path $ExtractedDir.FullName ".claude\skills\$SkillName"
        if (-not (Test-Path $SourceDir)) {
            throw "Skill files not found in archive at $SourceDir"
        }

        if ($DryRun) {
            Write-Info "[Dry run] Would create: $InstallDir"
            Write-Info "[Dry run] Would install to: $SkillDir"
            Write-Host ''
            Write-Success 'Dry run complete - no changes made'
        } else {
            New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

            # Remove existing installation
            if (Test-Path $SkillDir) {
                Write-Warn "Removing existing installation at $SkillDir"
                Remove-Item -Path $SkillDir -Recurse -Force
            }

            # Copy skill files
            Copy-Item -Path $SourceDir -Destination $SkillDir -Recurse

            Write-Host ''
            Write-Success 'SDLC Studio installed successfully!'
            Write-Host ''
            Write-Host 'Get started:'
            Write-Host '  /sdlc-studio help      Show command reference'
            Write-Host '  /sdlc-studio status    Check pipeline state'
            Write-Host '  /sdlc-studio hint      Get next suggested action'
            Write-Host ''
        }
    } finally {
        Remove-Item -Path $TmpDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Invoke-Install -Global:$Global -Local:$Local -DryRun:$DryRun -Version $Version -Help:$Help
