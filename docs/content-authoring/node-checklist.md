# Node Authoring Checklist

Use this checklist **every time** you create or modify a scavenger hunt node.

If every item is checked, the node should:
- validate successfully
- index correctly
- load in the app without surprises
- feel fair and fun for all age tracks

---

## 1. File and Naming

- [ ] File is named after the NFC tag  
      Example: `TAG004.node04.json`
- [ ] Filename tag (`TAG004`) matches:
  - [ ] `tagRef.tagID`
  - [ ] NFC tag payload `tag_id`
- [ ] File is placed under the correct directory: ios-app/Resources/BundledContent/games/<GameName>/<GameVersion>/nodes/

---

## 2. Core Metadata

- [ ] `node` number is correct and sequential
- [ ] `game.gameName` matches the game folder name
- [ ] `game.gameVersion` matches the version folder name
- [ ] `tagRef.room` and `tagRef.object` describe the physical placement

---

## 3. Defaults and Gating

- [ ] `defaults` values are intentional (not placeholders)
- [ ] `gating.strictOrder` is set correctly
- [ ] `gating.requires` is correct (empty for linear hunts)
- [ ] `unlockOnScan` behavior matches design intent

---

## 4. Pages and Age Tracks

- [ ] Exactly one page exists for each required age track:
- [ ] Kiddos
- [ ] Tweens
- [ ] Youths
- [ ] Adults
- [ ] Each page has:
- [ ] Unique `pageID`
- [ ] Correct age range
- [ ] Clear title and subtitle
- [ ] Difficulty increases with age track
- [ ] All pages reference the **same physical location**

---

## 5. Page IDs and Media

- [ ] Page IDs follow the correct pattern: P###-#
- [ ] Page ID numbers align with the node number
- [ ] Media folder exists **only if needed**: media/P###
- [ ] No unused media files are present

---

## 6. Lesson and Challenge Content

- [ ] Lesson text is:
- [ ] Age appropriate
- [ ] Clear and concise
- [ ] Free of spoilers
- [ ] Challenge prompt is:
- [ ] Unambiguous
- [ ] Solvable with provided information
- [ ] Answer list includes all reasonable acceptable answers
- [ ] Answer casing and spacing are normalized where possible

---

## 7. Responses and Feedback

- [ ] Success response is encouraging and rewarding
- [ ] Failure response is supportive and non-punitive
- [ ] Failure does **not** reveal the answer
- [ ] Tone matches the age track style guide

---

## 8. Clues to the Next Location

- [ ] Clue points clearly to the next physical location
- [ ] Clue avoids explicit room names for younger players
- [ ] Clue does not reference:
- [ ] Tag IDs
- [ ] Node numbers
- [ ] File names
- [ ] Clue increases abstraction with age track

---

## 9. Validation and Indexing

- [ ] Node validates against JSON schema
- [ ] `reindex_validate.ps1` runs clean (green ✅)
- [ ] Node appears correctly in `content-index.json`
- [ ] `nodeFile` path in index matches filename

---

## 10. Physical Reality Check

- [ ] NFC tag is placed exactly where described
- [ ] Tag scans reliably on multiple devices
- [ ] Placement is safe, accessible, and intentional
- [ ] The clue makes sense *in the real world*

---

## 11. Final Sanity Pass

- [ ] Read each age track out loud
- [ ] Imagine a first-time player encountering this node
- [ ] Confirm the node teaches, rewards, and moves the player forward
- [ ] Confirm nothing here depends on future nodes to make sense

---

## Final Rule

If a node feels confusing, frustrating, or unfair in real life,
**fix the content — not the app.**
