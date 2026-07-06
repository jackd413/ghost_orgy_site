param(
    [string]$ZoneName = "unholyghost.org",
    [string]$ZoneId = $env:CLOUDFLARE_ZONE_ID,
    [string]$ApiToken = $env:CLOUDFLARE_API_TOKEN,
    [string]$RulesetPath = "cloudflare/security-headers-transform-ruleset.json",
    [switch]$UseWranglerOAuth
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RulesetFile = Resolve-Path (Join-Path $Root $RulesetPath)
$ApiBase = "https://api.cloudflare.com/client/v4"

function Get-WranglerOAuthToken {
    $configPath = Join-Path $env:APPDATA "xdg.config\.wrangler\config\default.toml"
    if (-not (Test-Path -LiteralPath $configPath)) {
        throw "Wrangler OAuth config not found at $configPath."
    }

    $config = Get-Content -Raw -LiteralPath $configPath
    $match = [regex]::Match($config, 'oauth_token\s*=\s*"([^"]+)"')
    if (-not $match.Success) {
        throw "Wrangler OAuth token was not found in $configPath."
    }

    return $match.Groups[1].Value
}

if (-not $ApiToken -and $UseWranglerOAuth) {
    $ApiToken = Get-WranglerOAuthToken
}

if (-not $ApiToken) {
    throw "Set CLOUDFLARE_API_TOKEN with Zone Transform Rules Write permission, or pass -UseWranglerOAuth if that token has Rulesets access."
}

$Headers = @{
    Authorization = "Bearer $ApiToken"
    "Content-Type" = "application/json"
}

function Invoke-CfApi {
    param(
        [string]$Method,
        [string]$Path,
        [object]$Body = $null
    )

    $params = @{
        Method = $Method
        Uri = "$ApiBase$Path"
        Headers = $Headers
    }
    if ($null -ne $Body) {
        $params.Body = ($Body | ConvertTo-Json -Depth 20)
    }

    $response = Invoke-RestMethod @params
    if (-not $response.success) {
        throw ($response.errors | ConvertTo-Json -Compress)
    }
    return $response.result
}

if (-not $ZoneId) {
    $zones = Invoke-CfApi -Method Get -Path "/zones?name=$ZoneName"
    $zone = @($zones) | Select-Object -First 1
    if (-not $zone) {
        throw "Cloudflare zone not found: $ZoneName"
    }
    $ZoneId = $zone.id
}

$desired = Get-Content -Raw -LiteralPath $RulesetFile | ConvertFrom-Json
$desiredRule = @($desired.rules) | Where-Object { $_.ref -eq "ghost_orgy_security_headers_v1" } | Select-Object -First 1
if (-not $desiredRule) {
    throw "Desired rule with ref ghost_orgy_security_headers_v1 was not found in $RulesetFile."
}

$rulesets = Invoke-CfApi -Method Get -Path "/zones/$ZoneId/rulesets"
$phaseRuleset = @($rulesets) | Where-Object { $_.phase -eq "http_response_headers_transform" -and $_.kind -eq "zone" } | Select-Object -First 1

if ($phaseRuleset) {
    $current = Invoke-CfApi -Method Get -Path "/zones/$ZoneId/rulesets/$($phaseRuleset.id)"
    $mergedRules = @($current.rules | Where-Object { $_.ref -ne "ghost_orgy_security_headers_v1" })
    $mergedRules += $desiredRule

    $payload = [ordered]@{
        name = $current.name
        description = $current.description
        kind = "zone"
        phase = "http_response_headers_transform"
        rules = $mergedRules
    }

    $updated = Invoke-CfApi -Method Put -Path "/zones/$ZoneId/rulesets/$($phaseRuleset.id)" -Body $payload
    "Updated response header transform ruleset $($updated.id) for $ZoneName."
} else {
    $created = Invoke-CfApi -Method Post -Path "/zones/$ZoneId/rulesets" -Body $desired
    "Created response header transform ruleset $($created.id) for $ZoneName."
}
