<#
scripts/tools/ci.ps1

"Green button" content pipeline:
1) Generate content-index.json for a game/version
2) Validate bundled content

Usage:
  .\scripts\tools\ci.ps1
  .\scripts\tools\ci.ps1 -Game FamilyHunt2026 -Version 260113.01

This version correctly fails the script if python returns a non-zero exit code.
#>

param(
  [string]$Game = "FamilyHunt2026",
  [string]$Version = "260113.01"
)

$ErrorActionPreference = "Stop"

function Assert-LastExitCode([string]$StepName) {
  if ($LASTEXITCODE -ne 0) {
    throw "❌ $StepName failed (exit code $LASTEXITCODE)."
  }
}

Write-Host "== Scavanger Hunt CI: Reindex + Validate =="

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$indexer  = Join-Path $repoRoot "scripts\build\generate_content_index.py"
$validator = Join-Path $repoRoot "scripts\validate-content\validate_pages.py"

if (-not (Test-Path $indexer)) { throw "Indexer script not found: $indexer" }
if (-not (Test-Path $validator)) { throw "Validator script not found: $validator" }

Write-Host ""
Write-Host "Game   : $Game"
Write-Host "Version: $Version"
Write-Host ""

Write-Host "[1/2] Generating content index..."
python $indexer --game $Game --version $Version
Assert-LastExitCode "Index generation"

Write-Host ""
Write-Host "[2/2] Validating bundled content..."
python $validator --game $Game --version $Version
Assert-LastExitCode "Validation"

Write-Host ""
Write-Host "✅ CI PASSED: $Game / $Version"
