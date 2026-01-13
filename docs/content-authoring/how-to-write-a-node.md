# How to Write a Node (Scavenger Hunt Content)

This document explains how to author a single scavenger hunt **node**.
A node represents one physical NFC tag and one step in the hunt sequence.

Each node:
- Is unlocked by scanning exactly one NFC tag
- Contains age-appropriate content for multiple difficulty tracks
- Enforces gating rules (order, prerequisites)
- Provides clues leading to the *next* physical location

Nodes are authored as JSON files and validated against the official schema.

---

## 1. What Is a Node?

A node is a **self-contained content bundle** that includes:
- Metadata (tag reference, node number, game info)
- Global defaults (timers, hints)
- Gating rules
- One or more **pages**, each mapped to a difficulty level

Think of a node as:
> “What happens when this tag is scanned?”

---

## 2. File Naming and Location

Node files must:
- Be named after the NFC tag ID  
  Example: `TAG001.node.json`
- Live under:

---

## 3. Required Top-Level Sections

Every node JSON file must contain:

| Section     | Purpose |
|------------|---------|
| `tagRef`   | Identifies the physical tag and its location |
| `node`     | Sequential node number (1-based) |
| `game`     | Game name and version |
| `defaults` | Timing and hint limits |
| `gating`   | Unlock rules |
| `pages`    | Age-specific content |

Do not remove or rename these fields.

---

## 4. Writing Pages (Age Tracks)

Each node must include one page per supported age track:

- Kiddos
- Tweens
- Youths
- Adults

Each page contains:
- A title and subtitle
- Narrative or instructional content
- A challenge or question
- One or more acceptable answers
- Success and failure responses
- A clue pointing to the *next* location

### Key Rules
- Pages must all refer to the **same physical location**
- Difficulty should scale by:
- reading level
- abstraction
- puzzle complexity
- Never reference internal node numbers in user-facing text

---

## 5. Writing Good Clues

Clues should:
- Reference **physical features**, not coordinates
- Be solvable without prior nodes (once unlocked)
- Avoid explicit room names for younger players when possible
- Increase abstraction with age

Bad clue:
> “Go to the upstairs bathroom.”

Good clue:
> “Find the room where echoes splash and porcelain waits.”

---

## 6. Validation Checklist (Before Commit)

Before committing a node:
- Schema validation passes
- Tag ID matches filename
- Node number matches index
- All age tracks are present
- Media references exist (if used)
- Next-location clue is correct

If validation fails, **fix the content**, not the schema.

---

## 7. Possible Prompt for Jarvis:

see file: /docs/content-authoring/generation-prompt.md

## 8. Philosophy

Nodes should feel:
- Playful, not punitive
- Curious, not cryptic
- Progressive, not repetitive

A good node teaches, rewards, and invites movement.

A great node makes players forget they are holding a phone.
