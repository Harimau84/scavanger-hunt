# Content Index Format (BundledContent)

This document defines the **content index** file format used by the iOS app to quickly locate and load scavenger hunt node JSON files (and optional media) from the app bundle.

The index is part of the **BundledContent contract**:
- Humans author content under `data/`
- Scripts validate and bundle content into `ios-app/Resources/BundledContent/`
- The app reads the bundled index + node files **offline**

If this index is correct and the node files validate, the game should run reliably without network access.

---

## 1. Purpose

The content index exists to:
- Provide a **single lookup table** from `tag_id` → node file path
- Provide ordering and metadata needed for gating and navigation
- Avoid guessing filenames or scanning directories at runtime
- Support multiple games and versions in a single bundle

The app should load:
1) the index file  
2) the node file referenced by the index  
3) optional media referenced by the node

---

## 2. Location in the Repo

In the bundled iOS resources, the index lives at: ios-app/Resources/BundledContent/games/<GameName>/<GameVersion>/indexes/content-index.json
(i.e., ios-app/Resources/BundledContent/games/FamilyHunt2026/260113.01/indexes/content-index.json)


---

## 3. Naming

The canonical filename is: content-index.json


Do not version the filename. Versioning is handled by the containing directory (`<GameVersion>`).

---

## 4. Index JSON Schema (Conceptual)

The index is a JSON object with:
- high-level game/version identifiers
- generation metadata
- an ordered list of nodes
- a fast lookup map by tag ID (optional but recommended)

The app may rely on **either** the list, the map, or both.

---

## 5. Required Structure (Drop-in Example)

This is the recommended index format. Fields marked “Required” should be treated as mandatory by tooling.

{
    "indexFormatVersion": "1.0",
    "game": {
    "gameName": "FamilyHunt2026",
    "gameVersion": "260113.01"
    },
    "generated": {
        "generatedAt": "2026-01-13T18:40:00Z",
        "generatedBy": "scripts/build/bundle_content",
        "sourceRoot": "data"
    },
    "defaults": {
        "locale": "en-US"
    },
    "nodes": [
        {
            "node": 1,
            "tagID": "TAG001",
            "nodeFile": "nodes/TAG001.node.json",
            "pageIDs": ["P001-1", "P001-2", "P001-3", "P001-4"],
            "mediaDir": "media/P001"
        },
        {
            "node": 2,
            "tagID": "TAG002",
            "nodeFile": "nodes/TAG002.node.json",
            "pageIDs": ["P002-1", "P002-2", "P002-3", "P002-4"],
            "mediaDir": "media/P002"
        },
        {
            "node": 3,
            "tagID": "TAG003",
            "nodeFile": "nodes/TAG003.node.json",
            "pageIDs": ["P003-1", "P003-2", "P003-3", "P003-4"],
            "mediaDir": "media/P003"
        }
    ],
    "tagToNode": {
        "TAG001": 1,
        "TAG002": 2,
        "TAG003": 3
    }
}


---

## 6. Field Definitions

### indexFormatVersion (Required)
- String
- Version of this index contract
- Example: `1.0`

### game (Required)
#### game.gameName (Required)
- Must match the folder name under `/games/`
- Example: `FamilyHunt2026`

#### game.gameVersion (Required)
- Must match the version folder name under the game
- Example: `260113.01`

### generated (Recommended)
Provides traceability for debugging.
- `generatedAt`: ISO 8601 timestamp (UTC recommended)
- `generatedBy`: script or tool identifier
- `sourceRoot`: where the authored content came from (`data`)

### defaults (Optional)
Defaults used by the bundle or app (non-authoritative).
- Example: `locale`

### nodes (Required)
Ordered list of node entries.

Each node entry must contain:

#### node (Required)
- Integer, 1-based
- Sequence order for strict gating

#### tagID (Required)
- NFC tag identifier, must be `TAG###`
- Must match:
  - NFC payload `tag_id`
  - node JSON `tagRef.tagID`
  - filename (e.g., `TAG001.node.json`)

#### nodeFile (Required)
- Relative path from the version root
- Must point to a JSON file
- Example: `nodes/TAG001.node.json`

#### pageIDs (Optional but recommended)
- List of page IDs contained in that node
- Used for diagnostics and optional UI “progress” views
- Example: `["P001-1", "P001-2", "P001-3", "P001-4"]`

#### mediaDir (Optional)
- Relative path to a folder containing media for the node/pages
- Example: `media/P001`
- May be absent if `picture: false` for all pages

### tagToNode (Optional but recommended)
- Map of `tagID` → `node` number for fast routing
- Allows constant-time gating checks without scanning arrays
- The app may still verify this matches the `nodes` list

---

## 7. Consistency Rules (Must Pass Validation)

A bundle is invalid if any of the following are untrue:

1. Every `nodes[i].tagID` matches the filename in `nodes[i].nodeFile`
2. Every `nodes[i].node` is unique and contiguous (1..N)
3. Every `nodes[i].tagID` is unique
4. `tagToNode` (if present) matches the `nodes` list
5. Each `nodeFile` exists in the bundle
6. Each `mediaDir` (if present) exists in the bundle
7. `gameName` and `gameVersion` match the folder path

---

## 8. Runtime Usage (iOS App Expectations)

The app should:
1. Load `content-index.json` for the selected game/version
2. Parse NFC payload `tag_id`
3. Look up the node entry:
   - Prefer `tagToNode` if present, otherwise scan `nodes`
4. Load `nodeFile` from bundle resources
5. Decode and display the correct difficulty page
6. Enforce gating using the node sequence number and prior completion

The app must remain fully functional **offline**.

---

## 9. Future-Proofing Notes

Allowed growth without breaking older apps:
- Adding optional fields to node entries
- Adding new top-level metadata sections
- Adding additional games/versions in parallel

Breaking changes require incrementing:
- `indexFormatVersion`

---

## 10. Related Files

- Node schema:
  - `ios-app/Resources/BundledContent/schemas/nfc-hunt-page.schema.json`
- Node JSON files:
  - `ios-app/Resources/BundledContent/games/<GameName>/<GameVersion>/nodes/*.node.json`
- Optional media:
  - `ios-app/Resources/BundledContent/games/<GameName>/<GameVersion>/media/`

---

## 11. Authoritative Rule

If the index disagrees with a node file, the bundle is invalid.

Fix the content or bundling script—do not “patch around” it in the app.


