# Progress and how to continue

This guide is being written in stages. This file records what is done, what is left, and how to pick up the work in a new Claude Code session.

## Decisions already made (from the author)

- **Era:** medieval to late medieval (c. 1000–1500), with short notes on the period after (c. 1500–1650).
- **Magic and other races:** realistic history first, then a separate chapter on how magic, monsters and races change things.
- **Map scales covered:** continent/world, single kingdom/region, local area. City street maps are out of scope.
- **Format:** Markdown files in this repo.

## Status

| Item | Status |
|---|---|
| `research/baseline-numbers.md` | Done; corrected after the fact-checks and the audit |
| `guide/01` – `guide/11` | Written, fact-checked, and audit gaps/fixes applied (`research/audit.json`) |
| Cross-chapter follow-ups (`research/followups.json`) | Running at the end of the last session. Check `git log` and the files to confirm they landed. |
| `guide/00-step-by-step.md` | Written |
| `guide/12-worked-example.md` | Written; schematic map (`guide/images/worked-example-kingdom.svg`) was being drawn |
| `guide/13-quick-reference.md` | Was being written at the end of the last session |
| `README.md` | Done |

## What is left (next session)

The workflow is `.claude/workflows/assemble-guide.js`. Run it by name, or by `scriptPath` if the name is not listed:

1. **Check the last session's runs landed.** `guide/13-quick-reference.md` exists. `guide/images/worked-example-kingdom.svg` exists and is linked near the top of chapter 12. If either is missing, rerun `{"mode": "write", "targets": ["13"]}` or `["12"]`.
2. **Audit gaps for 00 and 12** (in `research/audit.json`): a "what to draw at which scale" table with target counts for 00, and time slices of the worked kingdom for 12. Run `{"mode": "fix", "files": ["00-step-by-step.md", "12-worked-example.md"]}`.
3. **Final numbers check:** `{"mode": "final"}` compares 13 and 00 against the owner chapters.
4. Run `python3 tools/check_links.py`. It should report 0 problems.
5. Small leftovers from the follow-up round:
   - Chapter 08 (around line 435) says "~1,700 castle sites"; align it with "about 1,700–1,800 (Gatehouse lists 1,761)".
   - Chapter 05's table row "Total length of the red route lines" should say this is the length of the reconstructed roads (Oksanen & Brookes 2025), not lines drawn on the map. The map has about 190 red lines. Chapter 11 could match 05's fuller Gough Map date wording (c. 1360–70 conventionally; Smallwood 2010 suggests after 1400).
   - Chapter 10 could note that sources differ on the Belgorod Line's end date (1646 or 1654).
6. Optional: chapters are long (9,000–14,000 words). A later pass could trim repetition.

Process notes:
- This machine runs only 2 agents at a time per workflow. Launch several workflows in parallel (each with a few files) to go faster.
- The web-search quota is shared by all agents and runs out. After that, agents check facts by opening known pages directly.

## Style rules (summary)

Every chapter follows these rules, written out in full in the workflow script:
- Plain English for readers who may not have English as a first language.
- Distances in both km and miles.
- Populations given as ranges.
- Callouts: **Map tip**, **Rule of thumb**, **Later era (1500s+)**, **Fantasy twist**.
- Each chapter ends with "Quick summary" and "Sources and further reading", using real sources only.
