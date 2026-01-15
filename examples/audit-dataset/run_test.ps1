# AEE Protocol - Integrity Audit Test (PowerShell)
# This script tests AEE on Windows systems

$ProjectRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
$DatasetPath = "$PSScriptRoot\dataset.csv"
$ExpectedOutputFile = "$PSScriptRoot\expected_output.txt"

Write-Host ""
Write-Host "AEE - Integrity Audit Test" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"
Write-Host "Dataset: $(Split-Path $DatasetPath -Leaf)"
Write-Host ""

# Check if dataset exists
if (-not (Test-Path $DatasetPath)) {
    Write-Host "ERROR: dataset.csv not found at $DatasetPath" -ForegroundColor Red
    exit 1
}

# Run test 1: Generate anchor
Write-Host "STEP 1: Generate Integrity Anchor"
Write-Host "=================================="
$GenerateOutput = & python "$ProjectRoot\main.py" --hash $DatasetPath --user "audit-test"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to generate anchor" -ForegroundColor Red
    Write-Host $GenerateOutput
    exit 1
}

Write-Host $GenerateOutput
Write-Host ""

# Extract anchor from output (last line is the hash)
$Lines = $GenerateOutput -split "`n"
$Anchor = $Lines[-1].Trim()

Write-Host "Extracted anchor: $Anchor" -ForegroundColor Yellow
Write-Host ""

# Run test 2: Verify anchor
Write-Host "STEP 2: Verify Integrity"
Write-Host "=================================="
$VerifyOutput = & python "$ProjectRoot\main.py" --verify $DatasetPath --anchor $Anchor

if ($LASTEXITCODE -eq 0) {
    Write-Host $VerifyOutput -ForegroundColor Green
    Write-Host "✔ Test finished successfully." -ForegroundColor Green
} else {
    Write-Host $VerifyOutput -ForegroundColor Red
    Write-Host "✖ Verification failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=================================="
Write-Host "Test Results: PASSED" -ForegroundColor Green
Write-Host "=================================="