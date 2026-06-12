# Install SDLC Studio - a standard Agent Skill (SKILL.md) - into one or more
# coding agents (Claude Code, Codex, Gemini CLI, opencode, GitHub Copilot).
# Usage: irm https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.ps1 | iex
#        .\install.ps1 [-Target <list>] [-Global|-Local] [-Uninstall] [-ListTargets] [-DryRun] [-Version <tag>]

[CmdletBinding()]
param(
    [string]$Target = 'claude',
    [switch]$Global,
    [switch]$Local,
    [switch]$Uninstall,
    [switch]$ListTargets,
    [switch]$DryRun,
    [switch]$NoSweep,
    [string]$Version = 'main',
    [switch]$Help
)

# Body lives in a function so it works both as a downloaded script and when
# piped via `irm ... | iex` (see the note kept from the original installer).
function Invoke-Install {
    [CmdletBinding()]
    param(
        [string]$Target, [switch]$Global, [switch]$Local, [switch]$Uninstall,
        [switch]$ListTargets, [switch]$DryRun, [switch]$NoSweep, [string]$Version,
        [switch]$Help
    )

    $ErrorActionPreference = 'Stop'
    $Repo = 'DarrenBenson/sdlc-studio'
    $SkillName = 'sdlc-studio'
    $AllTargets = @('claude', 'codex', 'gemini', 'opencode', 'copilot', 'agents')

    # Per-tool skills directory map (global / local). opencode's Windows global
    # path follows its cross-platform ~/.config/opencode convention; adjust if a
    # future opencode release uses %APPDATA% on Windows.
    $Map = @{
        claude   = @{ global = (Join-Path $HOME '.claude\skills');          local = '.claude\skills' }
        codex    = @{ global = (Join-Path $HOME '.agents\skills');          local = '.agents\skills' }
        gemini   = @{ global = (Join-Path $HOME '.gemini\skills');          local = '.gemini\skills' }
        opencode = @{ global = (Join-Path $HOME '.config\opencode\skills'); local = '.opencode\skills' }
        copilot  = @{ global = '';                                          local = '.github\skills' }
        agents   = @{ global = (Join-Path $HOME '.agents\skills');          local = '.agents\skills' }
    }

    if ($Help) {
        @'
SDLC Studio Installer (Windows)

SDLC Studio is a standard Agent Skill (SKILL.md); this installs it into each
chosen tool's skills folder.

Usage:
    irm https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.ps1 | iex
    .\install.ps1 [options]

Options:
    -Target LIST    Comma-separated tools: claude,codex,gemini,opencode,
                    copilot,agents (generic .agents/skills - read by Codex,
                    Gemini, Copilot, Cursor) or "all" or "auto". Default: claude
    -Global         Per-user skills dir (default)
    -Local          Current project's skills dir
    -Uninstall      Remove SDLC Studio from the resolved target dirs
    -ListTargets    Print the target/directory map and what is detected
    -DryRun         Show what would be done without making changes
    -NoSweep        Skip refreshing sdlc-studio copies found in other tool
                    locations (default: refresh them all)
    -Version VER    Install a specific version/tag (default: main)
    -Help           Show this help

Native alternatives (sdlc-studio is a standard skill):
    gh skills install DarrenBenson/sdlc-studio sdlc-studio   # Copilot (gh >= 2.90)
    gemini skills install https://github.com/DarrenBenson/sdlc-studio   # Gemini
'@
        return
    }

    if ($Global -and $Local) { throw 'Cannot use -Global and -Local together' }
    $Scope = if ($Local) { 'local' } else { 'global' }

    function Write-Info($m) { Write-Host '==> ' -ForegroundColor Blue -NoNewline; Write-Host $m }
    function Write-Ok($m) { Write-Host '==> ' -ForegroundColor Green -NoNewline; Write-Host $m }
    function Write-Warn2($m) { Write-Host 'Warning: ' -ForegroundColor Yellow -NoNewline; Write-Host $m }

    function Test-Detected($t) {
        switch ($t) {
            'claude'   { [bool](Get-Command claude   -ErrorAction SilentlyContinue) -or (Test-Path (Join-Path $HOME '.claude')) }
            'codex'    { [bool](Get-Command codex    -ErrorAction SilentlyContinue) -or (Test-Path (Join-Path $HOME '.codex')) -or (Test-Path (Join-Path $HOME '.agents')) }
            'gemini'   { [bool](Get-Command gemini   -ErrorAction SilentlyContinue) -or (Test-Path (Join-Path $HOME '.gemini')) }
            'opencode' { [bool](Get-Command opencode -ErrorAction SilentlyContinue) -or (Test-Path (Join-Path $HOME '.config\opencode')) }
            'copilot'  { [bool](Get-Command gh       -ErrorAction SilentlyContinue) -or (Test-Path '.github') }
            'agents'   { (Test-Path (Join-Path $HOME '.agents')) -or [bool](Get-Command codex -ErrorAction SilentlyContinue) -or [bool](Get-Command cursor -ErrorAction SilentlyContinue) }
            default    { $false }
        }
    }

    function Resolve-Targets($raw) {
        if ([string]::IsNullOrWhiteSpace($raw)) { $raw = 'claude' }
        $req = $raw -split ',' | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ }
        $expanded = @()
        foreach ($t in $req) {
            switch ($t) {
                'all'  { $expanded += $AllTargets }
                'auto' { $expanded += ($AllTargets | Where-Object { Test-Detected $_ }) }
                { $AllTargets -contains $_ } { $expanded += $t }
                default { throw "Unknown target: $t (valid: $($AllTargets -join ' ') all auto)" }
            }
        }
        $expanded | Select-Object -Unique
    }

    # Version recorded inside an installed copy (templates/version.yaml).
    function Get-InstalledVersion($dir) {
        $vy = Join-Path $dir 'templates\version.yaml'
        if (Test-Path $vy) {
            $line = Select-String -Path $vy -Pattern '^skill_version:' | Select-Object -First 1
            if ($line) {
                $v = ($line.Line -replace '^skill_version:\s*"?([^"#\s]*)"?.*$', '$1')
                if ($v) { return $v }
            }
        }
        return 'unknown'
    }

    # Identity guard: only ever touch a directory that is genuinely this skill.
    function Test-SkillCopy($dir) {
        $sm = Join-Path $dir 'SKILL.md'
        (Test-Path $sm) -and [bool](Select-String -Path $sm -Pattern '^name: sdlc-studio\s*$' -Quiet)
    }

    function Invoke-Note($t) {
        switch ($t) {
            'claude'   { 'Claude Code: run /sdlc-studio (or it is model-invoked).' }
            'codex'    { 'Codex: auto-discovered by description, or mention $sdlc-studio / run /skills.' }
            'gemini'   { 'Gemini CLI: run /skills to confirm discovery; then it is used automatically.' }
            'opencode' { 'opencode: discovered automatically via the skill tool.' }
            'copilot'  { 'Copilot: reads .github/skills in the repo; invoke from chat.' }
            'agents'   { 'Generic .agents/skills: read by Codex, Gemini CLI, Copilot, and Cursor (Claude Code does NOT read it).' }
        }
    }

    Write-Host ''
    Write-Host 'SDLC Studio Installer' -ForegroundColor Blue
    Write-Host ''

    if ($ListTargets) {
        Write-Host ('  {0,-9} {1,-30} {2,-18} {3}' -f 'TARGET', 'GLOBAL DIR', 'LOCAL DIR', 'DETECTED')
        foreach ($t in $AllTargets) {
            $g = if ($Map[$t].global) { $Map[$t].global.Replace($HOME, '~') } else { '(repo-scoped)' }
            $d = if (Test-Detected $t) { 'yes' } else { 'no' }
            Write-Host ('  {0,-9} {1,-30} {2,-18} {3}' -f $t, $g, $Map[$t].local, $d)
        }
        return
    }

    $targets = Resolve-Targets $Target
    Write-Info "Targets: $($targets -join ' ')"
    Write-Info "Scope: $Scope"
    if (-not $Uninstall) { Write-Info "Version: $Version" }
    Write-Host ''

    # Resolve each target to a destination parent directory.
    $resolved = [ordered]@{}
    foreach ($t in $targets) {
        $dir = $Map[$t].$Scope
        if (-not $dir -and $t -eq 'copilot') {
            Write-Warn2 'Copilot skills are repo-scoped; using .\.github\skills'
            $dir = $Map['copilot'].local
        }
        if (-not $dir) { Write-Warn2 "no $Scope dir for $t; skipping"; continue }
        if ($resolved.Values -contains $dir) { continue }   # codex/agents share a dir
        $resolved[$t] = $dir
    }
    if ($resolved.Count -eq 0) { throw 'No installable targets resolved.' }

    if ($Uninstall) {
        foreach ($t in $resolved.Keys) {
            $dest = Join-Path $resolved[$t] $SkillName
            if (Test-Path $dest) {
                if ($DryRun) { Write-Info "[dry run] would remove: $dest" }
                else { Remove-Item -Path $dest -Recurse -Force; Write-Ok "removed: $dest" }
            } else { Write-Info "not present: $dest" }
        }
        Write-Host ''; Write-Ok 'Uninstall complete.'; return
    }

    # Download + extract once (skipped on dry run).
    $SourceDir = $null
    $TmpDir = Join-Path ([System.IO.Path]::GetTempPath()) "sdlc-studio-install-$([System.IO.Path]::GetRandomFileName())"
    try {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null
            $Url = if ($Version -eq 'main') {
                "https://github.com/$Repo/archive/refs/heads/$Version.zip"
            } else {
                "https://github.com/$Repo/archive/refs/tags/$Version.zip"
            }
            Write-Info "Downloading SDLC Studio ($Version)..."
            $ZipPath = Join-Path $TmpDir 'archive.zip'
            try { Invoke-WebRequest -Uri $Url -OutFile $ZipPath -UseBasicParsing }
            catch { throw "Failed to download from $Url`n$($_.Exception.Message)" }
            Write-Info 'Extracting...'
            Expand-Archive -Path $ZipPath -DestinationPath $TmpDir -Force
            $Extracted = Get-ChildItem -Path $TmpDir -Directory -Filter 'sdlc-studio-*' | Select-Object -First 1
            if (-not $Extracted) { throw 'Failed to find extracted directory' }
            $SourceDir = Join-Path $Extracted.FullName ".claude\skills\$SkillName"
            if (-not (Test-Path $SourceDir)) { throw "Skill files not found in archive at $SourceDir" }
        }

        Write-Host ''
        $installedDests = @()
        foreach ($t in $resolved.Keys) {
            $parent = $resolved[$t]
            $dest = Join-Path $parent $SkillName
            if ($DryRun) { Write-Info "[dry run] would install to: $dest" }
            else {
                New-Item -ItemType Directory -Path $parent -Force | Out-Null
                if (Test-Path $dest) { Write-Warn2 "Removing existing installation at $dest"; Remove-Item -Path $dest -Recurse -Force }
                Copy-Item -Path $SourceDir -Destination $dest -Recurse
                Write-Ok "installed: $dest"
            }
            if (Test-Path $parent) { $installedDests += (Join-Path (Resolve-Path $parent).Path $SkillName) }
        }

        # Refresh every sdlc-studio copy found in any known location that was
        # not written this run, so no stale version lingers anywhere.
        if (-not $NoSweep) {
            Write-Host ''
            Write-Info 'Sweep: checking other tool locations for stale copies...'
            $newVer = if ($DryRun) { $Version } else { Get-InstalledVersion $SourceDir }
            $found = $false
            foreach ($t in $AllTargets) {
                foreach ($sweepScope in @('global', 'local')) {
                    $parent = $Map[$t].$sweepScope
                    if (-not $parent -or -not (Test-Path $parent)) { continue }
                    $parent = (Resolve-Path $parent).Path
                    $dest = Join-Path $parent $SkillName
                    if ($installedDests -contains $dest) { continue }
                    if (-not (Test-Path $dest)) { continue }
                    $installedDests += $dest
                    if (-not (Test-SkillCopy $dest)) {
                        Write-Warn2 "sweep: skipping $dest (no sdlc-studio SKILL.md - not touching it)"
                        continue
                    }
                    $old = Get-InstalledVersion $dest
                    $found = $true
                    if ($DryRun) { Write-Info "[dry run] would refresh: $dest ($old -> $newVer)" }
                    else {
                        Remove-Item -Path $dest -Recurse -Force
                        Copy-Item -Path $SourceDir -Destination $dest -Recurse
                        Write-Ok "refreshed: $dest ($old -> $newVer)"
                    }
                }
            }
            if (-not $found) { Write-Info 'sweep: no other sdlc-studio copies found' }
        }

        Write-Host ''
        if ($DryRun) {
            Write-Ok 'Dry run complete - no changes made'
        } else {
            Write-Ok "SDLC Studio installed for: $($targets -join ' ')"
            Write-Host ''
            Write-Host 'Next steps:'
            foreach ($t in $targets) { Write-Host "  - $(Invoke-Note $t)" }
            Write-Host ''
            Write-Host 'Then: status / hint / help (e.g. Claude: /sdlc-studio status).'
        }
    } finally {
        Remove-Item -Path $TmpDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Invoke-Install -Target $Target -Global:$Global -Local:$Local -Uninstall:$Uninstall `
    -ListTargets:$ListTargets -DryRun:$DryRun -NoSweep:$NoSweep -Version $Version -Help:$Help
