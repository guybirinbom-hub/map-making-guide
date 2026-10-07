# Progress and how to continue

This guide is being written in stages. This file records what is done, what is left, and how to pick up the work in a new Claude Code session.

## Decisions already made (from the author)

- **Era:** medieval to late medieval (c. 1000–1500), with short notes on the period after (c. 1500–1650).
- **Magic and other races:** realistic history first, then a separate chapter on how magic, monsters and races change things.
- **Map scales covered:** continent/world, single kingdom/region, local area. City street maps are out of scope.
- **Format:** Markdown files in this repo.

## Status

| File | Status |
|---|---|
| `research/baseline-numbers.md` | Done; corrected after the chapter fact-checks |
| `guide/01` – `guide/11` | Written and fact-checked (60–90 claims checked per chapter, 17–30 corrections each) |
| `guide/00-step-by-step.md` | In progress (stage 2) |
| `guide/12-worked-example.md` + `guide/images/` map | In progress (stage 2) |
| `guide/13-quick-reference.md` | To do: write after the audit fixes |
| Audit (gaps + cross-chapter consistency) | In progress; then apply fixes per chapter |
| `README.md` | Stub; finish last |

## How to continue (next session)

Stage 1 (chapters 01–11) is finished. Stage 2 uses `.claude/workflows/assemble-guide.js`. Run it by name, or by `scriptPath` if the name is not listed yet, in this order:

1. `{"mode": "audit"}` returns `gaps` and `fixes` but does not edit anything.
2. Group the audit output by file, then run `{"mode": "fix", "jobs": [{"file": "04-military-sites.md", "instructions": ["...", "..."]}]}`. Split the jobs across several parallel runs, because each run only does 2 agents at a time on this machine.
3. `{"mode": "write", "targets": ["00", "12"]}` can run alongside the fixes. Run `{"mode": "write", "targets": ["13"]}` only after the fixes.
4. `{"mode": "final"}`, then run `python3 tools/check_links.py` and finish `README.md`.

Known cross-chapter items for the consistency pass: Ghent c. 1300 (02 says 40–65k; 07 was aligned to the old 55–70k baseline), and the "towns above 10k on navigable water" rule now has exceptions (02, 07).

## Style rules (summary)

Every chapter follows these rules, written out in full in the workflow script:
- Plain English for readers who may not have English as a first language.
- Distances in both km and miles.
- Populations given as ranges.
- Callouts: **Map tip**, **Rule of thumb**, **Later era (1500s+)**, **Fantasy twist**.
- Each chapter ends with "Quick summary" and "Sources and further reading", using real sources only.
