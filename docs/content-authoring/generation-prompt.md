# Jarvis Prompt — Node Content Generation

This document contains the **standard prompt** used to ask Jarvis to generate
age-appropriate content for a newly created scavenger hunt node JSON file.

Use this prompt **after** running the node-generation script
(e.g., `new_node.ps1`) and **before** manually editing the node file.

Jarvis should generate **text only**, never modify structure, and never invent
new fields.

---

## Purpose

This prompt is used to generate the following per-age-level content:

- Title
- Subtitle
- Background dialogue
- Question
- Multiple-choice answers
- Success response
- Failure response
- Clue to the next location
- Progressive hints to the next location

All generated content must be **pasted into an existing, schema-valid node JSON file**.

---

## Standard Prompt Template (Copy & Paste)

Use the following prompt exactly.  
Fill in the placeholders before sending it to Jarvis.

---

### Prompt

Jarvis — help me populate a newly generated scavenger hunt node JSON file.

Context  
- This is an NFC-based scavenger hunt iOS app.  
- Do **NOT** change JSON structure or field names.  
- Do **NOT** invent new fields.  
- Only provide updated **text values** for existing fields.  
- Write content for **four age levels**:
  - kiddos (ages 5–8)
  - tweens (ages 9–12)
  - youths (ages 13–17)
  - adults (ages 18+)
- Content must be age-appropriate, playful, and concise.

Current Node Information  
- tagID: TAG###  
- node number: ##  
- current location (where the tag is found):  
  - room: <CURRENT ROOM>  
  - object: <CURRENT OBJECT>  

Next Location  
- The clue and hints must lead the player to:  
  - <NEXT LOCATION DESCRIPTION>  

Optional Theme  
- Theme or lesson focus: <THEME OR “random fun fact”>

---

## Content Requirements (Per Level)

For **each age level**, generate the following:

1. **title**  
   - Brief and witty  
   - Based on the current room or object  

2. **subtitle**  
   - One supporting sentence that follows naturally from the title  

3. **backgroundText**  
   - 2–4 sentences  
   - Age-appropriate dialogue or narration  
   - Based on a random fact, observation, or light lesson  
   - Must NOT reveal the next location  

4. **question**  
   - Short and clear  
   - Directly answerable from the backgroundText  

5. **answers**  
   - Exactly four answer choices  
   - Labeled A, B, C, D  
   - Exactly ONE correct answer  
   - Wrong answers must be plausible for the age group  

6. **correctAnswer**  
   - Specify which option is correct (A, B, C, or D)  

7. **successResponse**  
   - 1–2 sentences  
   - Encouraging and age-appropriate  

8. **failureResponse**  
   - 1–2 sentences  
   - Supportive and non-punitive  
   - No shaming language  

9. **clueText**  
   - A riddle or clue pointing to the next location  
   - Age-appropriate wording  
   - Must point to: <NEXT LOCATION DESCRIPTION>  
   - Must NOT include tag IDs, node numbers, or file names  

10. **hints**  
    - Exactly three hints:
      - Hint1: subtle
      - Hint2: clearer
      - Hint3: most direct  
    - All hints must point to the next location  
    - No tag IDs or technical references  

---

## Output Format (Required)

Jarvis must output **ONLY** the following structure for each level.  
No extra commentary. No JSON. No explanations.

---

LEVEL: <kiddos | tweens | youths | adults>

title:  
subtitle:  

backgroundText:  

question:  

answers:  
- A)  
- B)  
- C)  
- D)  

correctAnswer:  

successResponse:  

failureResponse:  

clueText:  

hints:  
- Hint1:  
- Hint2:  
- Hint3:  

---

## Final Instruction to Jarvis

Now generate the content using the rules above for:

- tagID: TAG###  
- node: ##  
- current location: <CURRENT ROOM> — <CURRENT OBJECT>  
- next location: <NEXT LOCATION DESCRIPTION>  
- theme: <THEME OR “random fun fact”>

---

## Notes for Authors

- Paste generated text **only into existing fields** in the node JSON file.
- Do not rename keys.
- Do not add comments to JSON.
- After pasting content, always run: .\scripts/tools/ci.ps1

Green output means the node is safe to ship.

