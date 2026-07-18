$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "FAIL: Python was not found on PATH." -ForegroundColor Red
    exit 1
}

if (Test-Path ".\demo-output") {
    Remove-Item ".\demo-output" -Recurse -Force
}

python -m pip install -e ".[dev]"
python -m pytest -q
tkp-authority-extract ".\fixtures\sanitized_normalized_conversation.json" ".\demo-output"

Write-Host "PASS: Public authority fixture completed." -ForegroundColor Green
