param(
    [Parameter(Mandatory = $true)]
    [string]$Source,

    [string]$Name,

    [string]$Destination = (Join-Path $PSScriptRoot "..\images"),

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$sourcePath = Resolve-Path -LiteralPath $Source
$destinationRoot = Resolve-Path -LiteralPath $Destination
$targetName = if ([string]::IsNullOrWhiteSpace($Name)) { $sourcePath.Path | Split-Path -Leaf } else { $Name }
$targetPath = Join-Path $destinationRoot.Path $targetName

Write-Host "Source: $($sourcePath.Path)"
Write-Host "Destination: $targetPath"

if ($DryRun) {
    Write-Host "Dry run only. No file was copied."
    return
}

Copy-Item -LiteralPath $sourcePath.Path -Destination $targetPath -Force
Write-Host "Copied asset into tracked site images."
