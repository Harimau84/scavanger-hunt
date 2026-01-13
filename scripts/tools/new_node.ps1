<#
scripts/tools/new_node.ps1

Creates a new node by cloning an existing valid node file (default: the lowest node file found),
then rewriting tag/node/pageIDs/room/object.

Writes into:
  ios-app/Resources/BundledContent/games/<Game>/<Version>/nodes/

Default naming convention:
  TAG004.node04.json

Usage examples:
  .\scripts\tools\new_node.ps1 -Tag TAG004 -Node 4
  .\scripts\tools\new_node.ps1 -Tag TAG004 -Node 4 -Room "Upper Hall" -Object "Common Bathroom Toilet"
  .\scripts\tools\new_node.ps1 -Tag TAG004 -Node 4 -CreateMedia -RunCI

This guarantees schema compliance because it uses your actual node structure.
#>

param(
  [Parameter(Mandatory=$true)]
  [ValidatePattern("^TAG\d{3}$")]
  [string]$Tag,

  [Parameter(Mandatory=$true)]
  [ValidateRange(1,999)]
  [int]$Node,

  [string]$Game = "FamilyHunt2026",
  [string]$Version = "260113.01",

  [string]$Room = "RoomName",
  [string]$Object = "PhysicalObject",

  [switch]$CreateMedia,
  [switch]$RunCI,
  [switch]$Force,

  # Optional: specify exactly which existing node to clone
  [string]$CloneFrom = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$versionRoot = Join-Path $repoRoot "ios-app\Resources\BundledContent\games\$Game\$Version"
$nodesDir    = Join-Path $versionRoot "nodes"
$mediaRoot   = Join-Path $versionRoot "media"

if (-not (Test-Path $nodesDir)) { throw "Nodes directory not found: $nodesDir" }
if (-not (Test-Path $mediaRoot)) { New-Item -ItemType Directory -Path $mediaRoot -Force | Out-Null }

# Choose clone source
$clonePath = $null
if ($CloneFrom -and $CloneFrom.Trim().Length -gt 0) {
  $candidate = Join-Path $nodesDir $CloneFrom
  if (-not (Test-Path $candidate)) { throw "Clone source not found: $candidate" }
  $clonePath = $candidate
} else {
  $existing = Get-ChildItem $nodesDir -Filter "*.json" | Sort-Object Name
  if ($existing.Count -lt 1) { throw "No existing node JSON files found in: $nodesDir" }
  $clonePath = $existing[0].FullName
}

# Output naming convention: TAG004.node04.json
$nodePad = "{0:d2}" -f $Node
$outFileName = "$Tag.node$nodePad.json"
$outPath = Join-Path $nodesDir $outFileName

if ((Test-Path $outPath) -and (-not $Force)) {
  throw "Output file already exists: $outPath`nUse -Force to overwrite."
}

# Load clone as object
$cloneText = Get-Content -Raw -Encoding UTF8 $clonePath
$obj = $cloneText | ConvertFrom-Json

# Update core fields
$obj.tagRef.tagID = $Tag
$obj.tagRef.room  = $Room
$obj.tagRef.object = $Object
$obj.node = $Node
$obj.game.gameName = $Game
$obj.game.gameVersion = $Version

# Update pageIDs based on node number: P004-1..4
$pPrefix = "P{0:d3}" -f $Node
foreach ($p in $obj.pages) {
  $lvl = [int]$p.level
  $p.contents.pageID = "$pPrefix-$lvl"
}

# Write pretty JSON
$jsonOut = $obj | ConvertTo-Json -Depth 60
Set-Content -Path $outPath -Value ($jsonOut + "`n") -Encoding UTF8

Write-Host "✅ Created node (cloned from $([System.IO.Path]::GetFileName($clonePath))): $outPath"

# Optionally create media folder: media/P###
if ($CreateMedia) {
  $mediaNodeDir = Join-Path $mediaRoot $pPrefix
  if (-not (Test-Path $mediaNodeDir)) {
    New-Item -ItemType Directory -Path $mediaNodeDir -Force | Out-Null
    Write-Host "✅ Created media folder: $mediaNodeDir"
  } else {
    Write-Host "ℹ️ Media folder already exists: $mediaNodeDir"
  }
}

# Optionally run CI
if ($RunCI) {
  $ci = Join-Path $repoRoot "scripts\tools\ci.ps1"
  if (-not (Test-Path $ci)) { throw "CI script not found: $ci" }
  Write-Host ""
  Write-Host "Running CI..."
  & $ci -Game $Game -Version $Version
}
