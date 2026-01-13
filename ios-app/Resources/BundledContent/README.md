# Bundled Content (DO NOT EDIT)

This directory contains **generated game content** that is bundled directly into the iOS application.

🚫 **DO NOT EDIT THESE FILES BY HAND**

All content in this directory is produced automatically by validation and build scripts.

---

## What Lives Here

This directory contains:

- JSON schemas used to validate node content
- Game content organized by game name and version
- Content indexes used by the app for fast lookup
- Node JSON files tied to NFC tags
- Optional media assets referenced by nodes

Everything here is **read-only at runtime**.

---

## Source of Truth

Human-authored content lives in: /data

Scripts validate and bundle that content into this directory.

If you want to change game behavior:
- Edit files in `data/`
- Run validation
- Run the bundling script

---

## How This Directory Is Generated

Typical workflow:

1. Author or update content under `data/`
2. Run content validation
3. Run bundling script
4. Scripts copy validated content here
5. App loads content from this directory

This directory should be safe to delete and regenerate at any time.

---

## Key Files and Folders

- `schemas/`
  - JSON schemas for node validation
- `games/`
  - One folder per game
- `<GameName>/<GameVersion>/indexes/content-index.json`
  - Primary routing table for NFC tag scans
- `<GameName>/<GameVersion>/nodes/`
  - One node file per NFC tag
- `<GameName>/<GameVersion>/media/`
  - Optional media assets

---

## Runtime Contract

The iOS app assumes:

- All content is valid
- All paths listed in the index exist
- No network access is required
- No runtime mutation is allowed

If something breaks here, the fix belongs in:
- content authoring
- validation scripts
- bundling scripts

Not in the app UI.

---

## If You Think You Need to Edit This Folder

You probably don’t.

Go edit: /data

Then regenerate the bundle.

---

## Final Reminder

This directory is **generated output**.

Treat it like a compiled binary:
- trusted
- deterministic
- disposable