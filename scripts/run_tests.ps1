$ErrorActionPreference = "Stop"

Write-Host "== eMotor-Studio tests =="
python -m pytest
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL: pytest failed"
    exit $LASTEXITCODE
}

Write-Host "PASS: pytest passed"
