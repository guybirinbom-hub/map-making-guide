# Map-Making Guide: Everything Human-Made

A research-based guide to the human side of a fantasy map:
- where settlements go, how big they are, and how far apart they sit
- capitals and borders
- castles, forts and military outposts
- trade routes, roads, bridges and ports
- villages, fields and mills
- mines, saltworks and other industry
- churches, monasteries, pilgrim roads and ruins

It is built on real history, mainly Europe from about **1000 to 1500 AD**, with examples from the Mediterranean, the Middle East, Asia, Africa and the Americas where they help. It adds notes on what changes **from 1500 to 1650**, and it has a separate chapter on how **magic, monsters and other races** change the rules.

It covers three map scales: **continent/world**, **kingdom/region**, and **local area** (a valley or county). City street plans are out of scope.

**The whole guide as one PDF book:** [map-making-guide.pdf](map-making-guide.pdf). It has a clickable chapters page, two-column pages and bookmarks.

## How to use this guide

1. **Start with [Step by Step](guide/00-step-by-step.md).** It is the method from blank map to finished map, in order, at each scale. Each step links to the chapter that explains it.
2. **Keep the [Quick Reference](guide/13-quick-reference.md) open while you draw.** It has every key number on one page, plus a master map legend.
3. **Dip into the chapters** when you want the reasons, the real examples and the fine detail.
4. **See it done:** the [Worked Example](guide/12-worked-example.md) builds a whole kingdom with the guide's numbers.
5. **Check your map** against [Common Mistakes](guide/11-common-mistakes.md) when you are done.

Every chapter uses the same callouts: **Map tip** (what to draw), **Rule of thumb**, **Later era (1500s+)** and **Fantasy twist**. Distances are given in km and miles.

## Chapters

| # | Chapter | What it answers |
|---|---|---|
| 00 | [Step by Step: From Blank Map to Living World](guide/00-step-by-step.md) | In what order do I place everything, at each scale? |
| 01 | [Where Settlements Are Built (and Why)](guide/01-settlement-placement.md) | Why is a town *here*? Site types, terrain and climate, spacing, nomad camps, naming places. |
| 02 | [Population and Settlement Sizes](guide/02-population-and-sizes.md) | How big is a village, town or city? How many people per km²? How many towns per kingdom? |
| 03 | [Capitals, Realms and Borders](guide/03-capitals-and-borders.md) | Where is the capital? How is a realm divided? Where do borders run? |
| 04 | [Castles, Forts and Military Outposts](guide/04-military-sites.md) | What kind of fort, where, how many, and how many soldiers? |
| 05 | [Trade Routes, Roads and Transport](guide/05-trade-routes-and-transport.md) | How fast and how costly is travel? Roads, bridges, rivers, ports, sea lanes and trade goods. |
| 06 | [Villages, Farms and the Countryside](guide/06-villages-and-countryside.md) | What does the land around a village look like? Fields, mills, woods, commons. |
| 07 | [Industry, Resources and Special Towns](guide/07-industry-and-resources.md) | Mines, salt, quarries, cloth, fishing, sugar, peat, and the towns they create. |
| 08 | [Religious, Cultural, Legal and Ancient Sites](guide/08-religious-cultural-and-ancient-sites.md) | Churches, monasteries, pilgrim roads, universities, gallows, ruins and older layers. |
| 09 | [What Changes After 1500](guide/09-later-era-1500-1650.md) | Star forts, ocean trade, bigger capitals, canals and post roads. |
| 10 | [Fantasy Variants: Magic, Monsters and Other Races](guide/10-fantasy-variants.md) | What changes if magic, monsters, dwarves, elves or flying mounts exist? |
| 11 | [Common Mistakes and How to Fix Them](guide/11-common-mistakes.md) | Why does my map feel wrong? Mistakes, fixes, and a sanity checklist. |
| 12 | [Worked Example: Populating a Kingdom](guide/12-worked-example.md) | The whole method applied to one kingdom, with the arithmetic and a map. |
| 13 | [Quick Reference Cheat Sheet](guide/13-quick-reference.md) | Every key number and the master legend on one page. |

## How it was made

Each chapter was researched separately, then checked by a fact-checker. The checker verified the numbers and real-world examples against sources and corrected or softened anything it could not confirm (typically 50–90 claims checked per chapter). A final audit looked for missing topics and for numbers that disagreed between chapters.

Every chapter ends with **Sources and further reading**. Figures are given as ranges because historians' estimates vary; where a number is the guide's own estimate, the text says so.

Shared numbers used across chapters: [research/baseline-numbers.md](research/baseline-numbers.md).

## Working on the guide

- [PROGRESS.md](PROGRESS.md) records the decisions behind the guide and how to continue the work.
- `tools/check_links.py` checks every relative link and section anchor: `python3 tools/check_links.py`
- `tools/build_pdf.py` rebuilds the PDF from the chapters and checks that no text was lost (needs `pip install weasyprint markdown-it-py mdit-py-plugins linkify-it-py beautifulsoup4`): `python3 tools/build_pdf.py`
- `tools/find_stranded.py` lists section headings left alone at the foot of a PDF page: `python3 tools/find_stranded.py map-making-guide.pdf`
- `.claude/workflows/` holds the research and assembly workflows used to write and check the chapters.
