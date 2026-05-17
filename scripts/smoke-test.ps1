#!/usr/bin/env pwsh
# scripts/smoke-test.ps1 — Crosstown Transit AI deploy smoke test (FR-009), Windows/pwsh port.
#
# Usage:
#   pwsh scripts/smoke-test.ps1 -FrontendUrl <url> [-Full]
#
# Exits non-zero on first failure with: FAIL at check N: <reason>  (to stderr)
# On success prints: smoke OK in <Ns> (4 checks)   or   (5 checks) for -Full
#
# Mirror of scripts/smoke-test.sh — same 4 baseline checks + --full mode.
# Honors $env:ORCHESTRATOR_URL the same way bash honors $ORCHESTRATOR_URL.
#
# All data is synthetic; rail lines L1/L2/L3 are fictional.

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$FrontendUrl,

    [switch]$Full
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($FrontendUrl)) {
    [Console]::Error.WriteLine("Usage: pwsh scripts/smoke-test.ps1 -FrontendUrl <url> [-Full]")
    exit 2
}

# ---------- helpers ----------
function Write-Err {
    param([string]$Message)
    [Console]::Error.WriteLine($Message)
}

function Fail {
    param([int]$CheckNumber, [string]$Reason)
    Write-Err "FAIL at check ${CheckNumber}: ${Reason}"
    exit 1
}

# Strip trailing slash (bash: ${var%/}).
function Trim-TrailingSlash {
    param([string]$Url)
    if ([string]::IsNullOrEmpty($Url)) { return '' }
    return $Url.TrimEnd('/')
}

# HTTP GET — sets script-scoped $script:HttpCode and $script:HttpBody.
# Mirrors bash http_get_with_status: HTTP_CODE=000 only on transport failure, not always.
function Invoke-HttpGet {
    param([string]$Url)
    $script:HttpCode = '000'
    $script:HttpBody = ''
    try {
        $resp = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 10 `
                                  -SkipHttpErrorCheck -UseBasicParsing `
                                  -ErrorAction Stop
        $script:HttpCode = [string][int]$resp.StatusCode
        $script:HttpBody = [string]$resp.Content
    }
    catch {
        # Transport failure (DNS, TCP, TLS, timeout) — leave as 000.
        $script:HttpCode = '000'
        $script:HttpBody = ''
    }
}

# HTTP POST JSON — sets script-scoped $script:HttpCode and $script:HttpBody.
function Invoke-HttpPostJson {
    param([string]$Url, [string]$JsonPayload)
    $script:HttpCode = '000'
    $script:HttpBody = ''
    try {
        # Use UTF-8 byte body so em-dash and other non-ASCII survive intact.
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($JsonPayload)
        $resp = Invoke-WebRequest -Uri $Url -Method Post `
                                  -ContentType 'application/json; charset=utf-8' `
                                  -Body $bytes `
                                  -TimeoutSec 10 -SkipHttpErrorCheck -UseBasicParsing `
                                  -ErrorAction Stop
        $script:HttpCode = [string][int]$resp.StatusCode
        $script:HttpBody = [string]$resp.Content
    }
    catch {
        $script:HttpCode = '000'
        $script:HttpBody = ''
    }
}

# Parse JSON safely — returns $null if body is empty / invalid.
function ConvertFrom-JsonSafe {
    param([string]$Body)
    if ([string]::IsNullOrWhiteSpace($Body)) { return $null }
    try { return ($Body | ConvertFrom-Json -ErrorAction Stop) }
    catch { return $null }
}

# Get a top-level scalar field. Returns '' if absent/null.
function Get-JsonField {
    param([string]$Body, [string]$Field)
    $obj = ConvertFrom-JsonSafe -Body $Body
    if ($null -eq $obj) { return '' }
    if (-not ($obj.PSObject.Properties.Name -contains $Field)) { return '' }
    $v = $obj.$Field
    if ($null -eq $v) { return '' }
    return [string]$v
}

# True iff top-level field exists as a key in the JSON object.
function Test-JsonHasKey {
    param([string]$Body, [string]$Field)
    $obj = ConvertFrom-JsonSafe -Body $Body
    if ($null -eq $obj) { return $false }
    return ($obj.PSObject.Properties.Name -contains $Field)
}

# True iff top-level field is a non-empty array.
function Test-JsonNonEmptyArray {
    param([string]$Body, [string]$Field)
    $obj = ConvertFrom-JsonSafe -Body $Body
    if ($null -eq $obj) { return $false }
    if (-not ($obj.PSObject.Properties.Name -contains $Field)) { return $false }
    $v = $obj.$Field
    if ($null -eq $v) { return $false }
    if ($v -is [System.Collections.IEnumerable] -and -not ($v -is [string])) {
        return (@($v).Count -gt 0)
    }
    return $false
}

# ---------- args ----------
$FrontendUrl = Trim-TrailingSlash -Url $FrontendUrl

$OrchestratorUrl = ''
if ($env:ORCHESTRATOR_URL) {
    $OrchestratorUrl = Trim-TrailingSlash -Url $env:ORCHESTRATOR_URL
}

Write-Host "# smoke-test: JSON parser = ConvertFrom-Json"

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

# ---------- Check 1: frontend root ----------
Write-Host "# check 1: GET ${FrontendUrl}/ — expect 200 + Crosstown marker (not Hello World)"
Invoke-HttpGet -Url "${FrontendUrl}/"
if ($script:HttpCode -ne '200') {
    Fail 1 "GET / returned HTTP $($script:HttpCode)"
}
# Hard-fail on the ACA quickstart placeholder image first (per task spec).
if ($script:HttpBody -match '(?i)Your container app is running') {
    Fail 1 "Hello World quickstart placeholder detected"
}
# Accept either the app marker ("Crosstown") or the SPA root div as proof of the real bundle.
if ($script:HttpBody -notmatch '(?i)Crosstown|<div[^>]+id="root"') {
    $snippet = $script:HttpBody
    if ($snippet.Length -gt 80) { $snippet = $snippet.Substring(0, 80) }
    $snippet = ($snippet -replace "[\r\n]", '')
    Fail 1 "body missing 'Crosstown' / app marker — got ${snippet}"
}
Write-Host "  check 1 PASS"

# ---------- Check 2: frontend /api/health (nginx -> orchestrator /health) ----------
Write-Host "# check 2: GET ${FrontendUrl}/api/health — expect 200 JSON {status, service:orchestrator}"
Invoke-HttpGet -Url "${FrontendUrl}/api/health"
if ($script:HttpCode -ne '200') {
    Fail 2 "GET /api/health returned HTTP $($script:HttpCode) (nginx rewrite likely broken)"
}
$statusV  = Get-JsonField -Body $script:HttpBody -Field 'status'
$serviceV = Get-JsonField -Body $script:HttpBody -Field 'service'
if ($statusV -ne 'ok' -and $statusV -ne 'degraded') {
    Fail 2 "status='${statusV}', expected 'ok' or 'degraded'"
}
if ($serviceV -ne 'orchestrator') {
    Fail 2 "service='${serviceV}', expected 'orchestrator' (nginx rewrite hit wrong upstream)"
}
Write-Host "  check 2 PASS (status=${statusV})"

# ---------- Check 3: direct orchestrator /health (optional) ----------
if (-not [string]::IsNullOrEmpty($OrchestratorUrl)) {
    Write-Host "# check 3: GET ${OrchestratorUrl}/health — expect 200"
    Invoke-HttpGet -Url "${OrchestratorUrl}/health"
    if ($script:HttpCode -ne '200') {
        Fail 3 "GET ${OrchestratorUrl}/health returned HTTP $($script:HttpCode)"
    }
    Write-Host "  check 3 PASS"
}
else {
    Write-Host "  check 3 SKIP — ORCHESTRATOR_URL not set (warning, not failure)"
}

# ---------- Check 4: POST /api/turn ----------
Write-Host "# check 4: POST ${FrontendUrl}/api/turn — expect 200 + non-empty text"
Invoke-HttpPostJson -Url "${FrontendUrl}/api/turn" -JsonPayload '{"text":"status of L1?"}'
if ($script:HttpCode -ne '200') {
    Fail 4 "POST /api/turn returned HTTP $($script:HttpCode)"
}
$textV = Get-JsonField -Body $script:HttpBody -Field 'text'
if ([string]::IsNullOrEmpty($textV)) {
    Fail 4 "'text' field missing or empty in /api/turn response"
}
Write-Host "  check 4 PASS (text length=$($textV.Length))"

# ---------- Check 5 (-Full): six rehearsed demo prompts must each return citations[] ----------
if ($Full) {
    Write-Host "# check 5 (--full): 6 rehearsed demo prompts must each return non-empty citations[]"

    # Demo prompts from specs/002-tuesday-demo/spec.md User Story 2.
    # Prompts 1-3 hit log-analyst tools; prompts 4-6 hit service-advisor tools.
    # NOTE: prompt 2 contains an em-dash (U+2014) — keep this file UTF-8.
    $prompts = @(
        'Show me the most recent door-fault logs from station Atlantic',
        'Look at log L-001234 — is it part of a known pattern?',
        'Summarize incident INC-1001',
        'Is the L1 line running right now?',
        'S-Penn to S-East with the L1 disruption',
        'Are there shuttle buses for L1?'
    )

    $idx = 0
    foreach ($p in $prompts) {
        $idx += 1
        # ConvertTo-Json handles escaping (quotes, backslashes, unicode) natively.
        $payload = @{ text = $p } | ConvertTo-Json -Compress
        Write-Host "  prompt ${idx}/6: ${p}"
        Invoke-HttpPostJson -Url "${FrontendUrl}/api/turn" -JsonPayload $payload
        if ($script:HttpCode -ne '200') {
            Fail 5 "prompt ${idx} returned HTTP $($script:HttpCode)"
        }
        if (-not (Test-JsonHasKey -Body $script:HttpBody -Field 'citations')) {
            Fail 5 "prompt ${idx} response missing 'citations' key"
        }
        if (-not (Test-JsonNonEmptyArray -Body $script:HttpBody -Field 'citations')) {
            Fail 5 "prompt ${idx} returned empty citations[] (uncited turn)"
        }
    }
    Write-Host "  check 5 PASS"
}

# ---------- summary ----------
$stopwatch.Stop()
$elapsed = [int][math]::Floor($stopwatch.Elapsed.TotalSeconds)
$n = 4
if ($Full) { $n = 5 }
Write-Host "smoke OK in ${elapsed}s (${n} checks)"
exit 0
