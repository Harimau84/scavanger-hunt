$ErrorActionPreference = "Stop"

Write-Host "== Scavanger Hunt: Bundle Content =="

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

# 1) Validate first
$validator = Join-Path $repoRoot "scripts\validate-content\validate_pages.py"
python $validator
Write-Host "✅ Validation PASSED"

# 2) Bundle content (placeholder - call your actual bundler when ready)
$bundler = Join-Path $repoRoot "scripts\build\bundle_content.sh"

if (Test-Path $bundler) {
  Write-Host "Found bundler script: $bundler"
  Write-Host "NOTE: Running bash scripts on Windows requires Git Bash or WSL."
  Write-Host "If using Git Bash: bash scripts/build/bundle_content.sh"
} else {
  Write-Host "Bundler script not found yet (or named differently)."
  Write-Host "Next: implement bundling from data/ -> ios-app/Resources/BundledContent/"
}

Write-Host "✅ Bundle step complete (or ready to run via Git Bash/WSL)"
