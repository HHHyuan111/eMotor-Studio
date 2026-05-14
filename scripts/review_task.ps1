$ErrorActionPreference = "Continue"
$failed = $false

function Step($name) {
    Write-Host ""
    Write-Host "== $name =="
}

Step "Branch"
git branch --show-current
if ($LASTEXITCODE -ne 0) { $failed = $true }

Step "Git status"
git status --short
if ($LASTEXITCODE -ne 0) { $failed = $true }

Step "Recent commits"
git log --oneline -5
if ($LASTEXITCODE -ne 0) { $failed = $true }

Step "Pytest"
python -m pytest
if ($LASTEXITCODE -ne 0) { $failed = $true }

Step "Required docs"
if (Test-Path "docs\code_provenance.md") {
    Write-Host "OK: docs\code_provenance.md"
} else {
    Write-Host "FAIL: docs\code_provenance.md missing"
    $failed = $true
}

if (Test-Path "docs\auto_review_system.md") {
    Write-Host "OK: docs\auto_review_system.md"
} else {
    Write-Host "FAIL: docs\auto_review_system.md missing"
    $failed = $true
}

Step "External tracking check"
$externalTracked = git ls-files external 2>$null
if ($externalTracked) {
    Write-Host "FAIL: external/ is tracked by git"
    $externalTracked
    $failed = $true
} else {
    Write-Host "OK: external/ is not tracked"
}

$referenceTracked = git ls-files reference_projects 2>$null
if ($referenceTracked) {
    Write-Host "WARNING: reference_projects/ is tracked by git"
    $referenceTracked
} else {
    Write-Host "OK: reference_projects/ is not tracked"
}

Step "Result"
if ($failed) {
    Write-Host "FAIL"
    exit 1
}

Write-Host "PASS"
exit 0
