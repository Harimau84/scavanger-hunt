$ErrorActionPreference = "Stop"

Write-Host "== Scavanger Hunt: Reindex + Validate =="

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$game = "FamilyHunt2026"
$version = "260113.01"

$indexer = Join-Path $repoRoot "scripts\build\generate_content_index.py"
$validator = Join-Path $repoRoot "scripts\validate-content\validate_pages.py"

if (-not (Test-Path $indexer)) {
  throw "Indexer script not found: $indexer"
}
if (-not (Test-Path $validator)) {
  throw "Validator script not found: $validator"
}

Write-Host "Generating content index for $game / $version ..."
python $indexer --game $game --version $version

Write-Host "Validating bundled content for $game / $version ..."
python $validator --game $game --version $version

Write-Host "✅ Reindex + Validate completed successfully"
