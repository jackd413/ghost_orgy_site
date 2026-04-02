param(
    [string]$Config = "canon-sync.local.json",
    [switch]$Mirror,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

if ([System.IO.Path]::IsPathRooted($Config)) {
    $configPath = $Config
}
else {
    $configPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $Config))
}

if (-not (Test-Path -LiteralPath $configPath)) {
    throw "Config not found at '$configPath'. Start from canon-sync.example.json."
}

$syncConfig = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$mappingsProperty = $syncConfig.PSObject.Properties['mappings']

if (-not $mappingsProperty -or -not $mappingsProperty.Value) {
    throw "No mappings were found in '$configPath'."
}

$mappings = @($mappingsProperty.Value)

foreach ($mapping in $mappings) {
    $source = [string]$mapping.source
    $destination = [string]$mapping.destination

    if ([string]::IsNullOrWhiteSpace($source)) {
        throw "Each mapping must include a source."
    }

    if ([string]::IsNullOrWhiteSpace($destination)) {
        throw "Each mapping must include a destination."
    }

    $sourcePath = Resolve-Path -LiteralPath $source
    $destinationPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $destination))

    if (-not (Test-Path -LiteralPath $destinationPath)) {
        if ($DryRun) {
            Write-Host "Would create destination: $destinationPath"
        }
        else {
            New-Item -ItemType Directory -Path $destinationPath -Force | Out-Null
        }
    }

    $patterns = @()
    if ($mapping.PSObject.Properties['include'] -and $mapping.include) {
        $patterns = @($mapping.include)
    }

    if ($patterns.Count -eq 0) {
        $patterns = @("*.*")
    }

    $robocopyArgs = @(
        $sourcePath.Path
        $destinationPath
    ) + $patterns + @(
        "/E"
        "/FFT"
        "/R:1"
        "/W:1"
        "/COPY:DAT"
        "/DCOPY:DAT"
    )

    if ($Mirror) {
        $robocopyArgs += "/MIR"
    }

    if ($DryRun) {
        $robocopyArgs += "/L"
    }

    Write-Host ""
    Write-Host "Syncing $($sourcePath.Path) -> $destinationPath"
    Write-Host "Patterns: $($patterns -join ', ')"

    & robocopy @robocopyArgs
    $exitCode = $LASTEXITCODE

    if ($exitCode -ge 8) {
        throw "robocopy failed for '$destination' with exit code $exitCode"
    }

    Write-Host "robocopy completed with exit code $exitCode"
}
