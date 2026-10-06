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
| `research/baseline-numbers.md` | Done: shared numbers every chapter uses (sizes, density, travel speeds, spacing). Not separately fact-checked yet. |
| `guide/01-settlement-placement.md` | Drafted, not fact-checked |
| `guide/02-population-and-sizes.md` | Drafted, not fact-checked |
| `guide/03-capitals-and-borders.md` | Drafted, not fact-checked |
| `guide/04-military-sites.md` | To do |
| `guide/05-trade-routes-and-transport.md` | To do |
| `guide/06-villages-and-countryside.md` | To do |
| `guide/07-industry-and-resources.md` | To do |
| `guide/08-religious-cultural-and-ancient-sites.md` | To do |
| `guide/09-later-era-1500-1650.md` | To do |
| `guide/10-fantasy-variants.md` | To do |
| `guide/11-common-mistakes.md` | To do |
| `guide/00-step-by-step.md` | To do (stage 2) |
| `guide/12-worked-example.md` | To do (stage 2) |
| `guide/13-quick-reference.md` | To do (stage 2) |
| `README.md` | Stub; full version in stage 2 |

## How to continue (next session)

### Stage 1: finish the chapters and fact-check them

The workflow `.claude/workflows/continue-guide.js` holds the full chapter scopes and style rules. Start a session on branch `claude/fantasy-map-settlements-ld6k5n` and say:

> Run the `continue-guide` workflow, then commit and push.

By default it writes chapters 04–11, then fact-checks 01–11. Each fact-checker verifies the numbers and examples against sources and fixes them in the file. To run only part of it, pass args, for example `{"write": ["04", "05"], "check": ["01", "02", "03"]}`.

If the usage limit interrupts a run, commit whatever chapters are finished. Then rerun the workflow with only the missing numbers in `write` and `check`.

### Stage 2: assemble the guide

This runs after all chapters exist and are checked.

1. **Completeness critic:** read every chapter and list missing human-made features or topics. Also flag numbers that contradict each other between chapters. Fix them in the chapter that owns each topic. Owners: 02 for population numbers, 05 for travel speeds and costs, 04 for fortifications.
2. **`guide/00-step-by-step.md`:** the master method for continent, then kingdom, then local area. Terrain and water → farmland → villages → market towns → cities → capital → roads and rivers → castles and borders → industry → religious sites → ruins → sanity check. Each step links to its chapter.
3. **`guide/12-worked-example.md`:** populate one sample kingdom from start to finish. Choose an area and terrain, compute the population, count villages, towns and cities, then place the capital, castles, routes and monasteries, with the numbers shown.
4. **`guide/13-quick-reference.md`:** a one-page cheat sheet of every key number. It must match the chapters exactly.
5. **`README.md`:** introduction, how to use the guide, table of contents.
6. **Final consistency pass:** check that links work, numbers match across files, and the callout formats are consistent.

## Style rules (summary)

Every chapter follows these rules, written out in full in the workflow script:
- Plain English for readers who may not have English as a first language.
- Distances in both km and miles.
- Populations given as ranges.
- Callouts: **Map tip**, **Rule of thumb**, **Later era (1500s+)**, **Fantasy twist**.
- Each chapter ends with "Quick summary" and "Sources and further reading", using real sources only.
