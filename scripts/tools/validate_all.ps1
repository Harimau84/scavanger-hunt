$ErrorActionPreference = "Stop"

Write-Host "== Scavanger Hunt: Validate Content =="

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$validator = Join-Path $repoRoot "scripts\validate-content\validate_pages.py"

if (-not (Test-Path $validator)) {
  throw "Validator not found: $validator"
}

python $validator
Write-Host "✅ Validation PASSED"
