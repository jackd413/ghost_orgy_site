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
        "https://$ZoneName/index.html",
        "https://$ZoneName/404.html",
        "https://$ZoneName/artifacts/",
        "https://$ZoneName/licensing/",
        "https://$ZoneName/listen/",
        "https://$ZoneName/lore/",
        "https://$ZoneName/nine-sisters/",
        "https://$ZoneName/press/",
        "https://$ZoneName/salt/",
        "https://$ZoneName/scripts/fourthwall-fixes.js",
        "https://$ZoneName/shop/",
        "https://$ZoneName/styles/fourthwall-theme.css",
        "https://$ZoneName/threshold/",
        "https://$ZoneName/updates/",
        "https://$ZoneName/sisters/limbo.html",
        "https://$ZoneName/sisters/lust.html",
        "https://$ZoneName/sisters/gluttony.html",
        "https://$ZoneName/sisters/greed.html",
        "https://$ZoneName/sisters/wrath.html",
        "https://$ZoneName/sisters/heresy.html",
        "https://$ZoneName/sisters/violence.html",
        "https://$ZoneName/sisters/fraud.html",
        "https://$ZoneName/sisters/treachery.html"
    )
}

try {
    Invoke-CfApi -Method Post -Path "/zones/$ZoneId/purge_cache" -Body $purgeBody | Out-Null
    Write-Output "Purged Cloudflare cache for $($purgeBody.files.Count) public $ZoneName URLs."
} catch {
    Write-Error "Cloudflare cache purge failed: $($_.Exception.Message)"
    throw
}
