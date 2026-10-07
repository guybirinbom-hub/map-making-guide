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
| Cross-chapter follow-ups (`research/followups.json`) | Done |
| `guide/00-step-by-step.md` | Written |
| `guide/12-worked-example.md` | Done, with a drawn schematic map of the example kingdom |
| `guide/13-quick-reference.md` | Done (includes the master legend and a table reconciling the numbers between chapters) |
| `README.md` | Done |

## What is left (next session)

The workflow is `.claude/workflows/assemble-guide.js`. Run it by name, or by `scriptPath` if the name is not listed:

1. The worked-example map is done (`guide/images/worked-example-kingdom.svg` plus a PNG preview). Its legend uses its own symbols; a later pass could match it to chapter 13's master legend.
2. **Audit gaps for 00 and 12** (in `research/audit.json`): a "what to draw at which scale" table with target counts for 00, and time slices of the worked kingdom for 12. Run `{"mode": "fix", "files": ["00-step-by-step.md", "12-worked-example.md"]}`.
3. **Final numbers check:** `{"mode": "final"}` compares 13 and 00 against the owner chapters.
4. Run `python3 tools/check_links.py`. It should report 0 problems.
5. Small leftovers from the follow-up round:
   - Chapter 05's table row "Total length of the red route lines" should say this is the length of the reconstructed roads (Oksanen & Brookes 2025), not lines drawn on the map. The map has about 190 red lines. Chapter 11 could match 05's fuller Gough Map date wording (c. 1360–70 conventionally; Smallwood 2010 suggests after 1400).
   - Chapter 10 could note that sources differ on the Belgorod Line's end date (1646 or 1654).
   - Check: Corsican towers in 09 (should say about 85–90, from the 1617 list of 86). Hillfort counts in 11 #28 ("over 2,000 in Britain") should match 08 (4,147 in Britain and Ireland, Atlas of Hillforts 2017). Chapter 02's density table (hills/uplands 2–10) should match its calculator step 2 (hills 8–15; uplands 2–5).
   - Chapter 02's carrying-capacity section says "about 1,300 kcal a day", but the baseline gives 1,250–1,800 kcal. Align them.
   - Symbol tables inside chapters 02–08 still use their own symbols. Chapter 13's master legend resolves the clashes. Each chapter's symbol table should either match 13 or point to it.
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
