# NFC Tag Payload Format

This document defines the **exact JSON payload** written to NFC tags.

The payload acts only as an **identifier and router**.
All content lives inside the app bundle.

---

## 1. Design Principles

- Payloads are small
- Payloads never contain game content
- Payloads must remain stable across app updates
- Payloads are readable JSON for debugging

---

## 2. Payload Structure


{
  "tag_id": "TAG001",
  "game": {
    "game_id": "FamilyHunt2026",
    "version": "260113.01"
  },
  "location": {
    "level": "Main",
    "room": "Foyer",
    "wall": "North",
    "object": "StartBlock"
  }
}

---

## 3. Field Definitions

### tag_id
- **Required**
- Must exactly match the corresponding node filename
- Format: TAG### (example: TAG001)
- Used as the primary lookup key by the app

---

### game.game_id
- **Required**
- Logical identifier for the scavenger hunt
- Enables multiple hunts to coexist in the same app

Example value:
- FamilyHunt2026

---

### game.version
- **Required**
- Content version identifier
- Allows new content bundles without rewriting NFC tags

Example value:
- 260113.01

---

### location
- **Optional but strongly recommended**
- Human-readable metadata describing where the tag is placed
- Used for debugging, validation, and maintenance
- Not required for routing or gameplay logic

Location fields:
- level — Floor or level (e.g., Basement, Main, Upper)
- room — Room name
- wall — Optional orientation (North, South, etc.)
- object — Physical object the tag is attached to

---

## 4. Encoding Rules

- UTF-8 encoding
- Stored as an NDEF Text or MIME record
- JSON only (no comments, no trailing commas)
- Keep payload compact to fit typical NFC tag limits

---

## 5. Error Handling Expectations

If the app encounters:

- Unknown tag_id  
  → Display a friendly “This tag doesn’t belong to this hunt” message

- Game or version mismatch  
  → Explain the mismatch and suggest updating the app or using the correct tag

- Malformed JSON  
  → Fail gracefully and guide the user to try again

A malformed or incorrect tag must never crash the app.

---

## 6. Stability Contract

Once NFC tags are written and placed:

- Tag payloads should not change
- Content evolves via bundled JSON updates inside the app
- Rewriting NFC tags is a last resort

Think of NFC tags as street signs, not destinations.
