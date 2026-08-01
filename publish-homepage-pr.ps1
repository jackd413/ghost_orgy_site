[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoPath,

    [string]$BaseBranch = "main",
    [string]$BranchName = "agent/recenter-homepage",

    [switch]$InstallQaDependencies,
    [switch]$SkipPush,
    [switch]$SkipPullRequest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $Command $($Arguments -join ' ')"
    }
}

function Get-NativeOutput {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )

    $output = & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $Command $($Arguments -join ' ')"
    }
    return ($output | Out-String).Trim()
}

$payloadDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$replacement = Join-Path $payloadDir "index.html"
$repo = (Resolve-Path -LiteralPath $RepoPath).Path
$target = Join-Path $repo "index.html"

if (-not (Test-Path -LiteralPath $replacement -PathType Leaf)) {
    throw "Replacement homepage is missing: $replacement"
}
if (-not (Test-Path -LiteralPath (Join-Path $repo ".git"))) {
    throw "RepoPath is not a Git checkout: $repo"
}
if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
    throw "Repository index.html is missing: $target"
}

Push-Location $repo
try {
    $root = Get-NativeOutput git rev-parse --show-toplevel
    if ((Resolve-Path -LiteralPath $root).Path -ne $repo) {
        throw "RepoPath must point to the repository root. Git root is: $root"
    }

    $origin = Get-NativeOutput git remote get-url origin
    if ($origin -notmatch "jackd413[/:]ghost[_-]orgy[_-]site(?:\.git)?$") {
        Write-Warning "Origin does not look like jackd413/ghost_orgy_site: $origin"
    }

    $dirty = Get-NativeOutput git status --porcelain
    if ($dirty) {
        throw "The working tree is not clean. Commit or stash existing work before applying this focused homepage change.`n$dirty"
    }

    Invoke-Native git fetch origin $BaseBranch
    Invoke-Native git switch $BaseBranch
    Invoke-Native git pull --ff-only origin $BaseBranch

    $branchExists = (& git show-ref --verify --quiet "refs/heads/$BranchName"; $LASTEXITCODE -eq 0)
    if ($branchExists) {
        throw "Local branch already exists: $BranchName. Delete or rename it before rerunning."
    }

    Invoke-Native git switch -c $BranchName

    $backupDir = Join-Path $payloadDir "backups"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item -LiteralPath $target -Destination (Join-Path $backupDir "index.$timestamp.html") -Force
    Copy-Item -LiteralPath $replacement -Destination $target -Force

    Invoke-Native git diff --check

    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command py -ErrorAction SilentlyContinue
    }

    if ($python -and (Test-Path -LiteralPath (Join-Path $repo "scripts/check-site.py"))) {
        if ($InstallQaDependencies -and (Test-Path -LiteralPath (Join-Path $repo "requirements-qa.txt"))) {
            if ($python.Name -eq "py.exe" -or $python.Name -eq "py") {
                Invoke-Native py -3 -m pip install -r requirements-qa.txt
            } else {
                Invoke-Native python -m pip install -r requirements-qa.txt
            }
        }

        if ($python.Name -eq "py.exe" -or $python.Name -eq "py") {
            Invoke-Native py -3 scripts/check-site.py
        } else {
            Invoke-Native python scripts/check-site.py
        }
    } else {
        Write-Warning "Python or scripts/check-site.py was unavailable. Git diff checks passed, but repository QA was not run."
    }

    Invoke-Native git add -- index.html
    Invoke-Native git commit -m "Recenter homepage on Salt and the Orchard"

    if (-not $SkipPush) {
        Invoke-Native git push -u origin $BranchName
    }

    if (-not $SkipPullRequest) {
        $gh = Get-Command gh -ErrorAction SilentlyContinue
        if (-not $gh) {
            Write-Warning "GitHub CLI is not installed. The branch is ready; open a draft PR from '$BranchName' into '$BaseBranch'."
        } elseif ($SkipPush) {
            Write-Warning "PR creation skipped because -SkipPush was supplied. Push the branch first."
        } else {
            Invoke-Native gh auth status

            $bodyPath = Join-Path ([System.IO.Path]::GetTempPath()) "ghost-orgy-homepage-pr.md"
            @"
## What changed

- Replaced the homepage's parallel routing and conversion blocks with one authored path: entry, Salt, recovered fragments, the Nine, the Orchard, then secondary doors.
- Reduced the hero to two decisions: hear the record or enter the world.
- Kept the existing imagery, release destinations, press, licensing, shop, artifacts, updates, metadata, and legacy anchor contracts.
- Removed homepage email capture, RIYL scaffolding, copy-link widgets, and repeated destination cards from the opening experience.

## Why

The homepage had accumulated the responsibilities of a directory, press kit, release page, lore index, storefront bridge, and conversion funnel. All of those destinations remain, but the homepage once again establishes Ghost Orgy as a record and a world before asking visitors to route themselves.

## Validation

- `git diff --check`
- `python scripts/check-site.py` when Python and QA dependencies are available
- Desktop and mobile visual review
- No new JavaScript or dependencies
"@ | Set-Content -LiteralPath $bodyPath -Encoding UTF8

            Invoke-Native gh pr create --draft --base $BaseBranch --head $BranchName --title "Recenter the homepage on Salt and the Orchard" --body-file $bodyPath
        }
    }

    Write-Host ""
    Write-Host "Homepage implementation complete." -ForegroundColor Green
    Write-Host "Branch: $BranchName"
    Write-Host "Backup: $backupDir"
} finally {
    Pop-Location
}
