param(
    [string]$ZoneName = "unholyghost.org",
    [string]$ZoneId = $env:CLOUDFLARE_ZONE_ID,
    [string]$ApiToken = $env:CLOUDFLARE_API_TOKEN
)

$ErrorActionPreference = "Stop"

if (-not $ApiToken) {
    Write-Output "CLOUDFLARE_API_TOKEN is not set. Skipping cache purge. "
    exit 0
}

if (-not $ZoneId) {
    Write-Output "CLOUDFLARE_ZONE_ID is not set. Skipping cache purge."
    exit 0
}

$apiBase = "https://api.cloudflare.com/client/v4"
$headers = @{
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
        Uri = "$apiBase$Path"
        Headers = $headers
    }

    if ($null -ne $Body) {
        $params.Body = ($Body | ConvertTo-Json -Depth 20)
    }

    $result = Invoke-RestMethod @params
    if (-not $result.success) {
        throw ($result.errors | ConvertTo-Json -Compress)
    }
    return $result.result
}

$purgeBody = @{
    files = @(
        "https://$ZoneName/",
        "https://$ZoneName/index.html"
    )
}

try {
    Invoke-CfApi -Method Post -Path "/zones/$ZoneId/purge_cache" -Body $purgeBody | Out-Null
    Write-Output "Purged Cloudflare cache for $ZoneName root and index.html."
} catch {
    Write-Error "Cloudflare cache purge failed: $($_.Exception.Message)"
    throw
}
