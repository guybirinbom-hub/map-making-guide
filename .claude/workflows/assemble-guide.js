export const meta = {
  name: 'assemble-guide',
  description: 'Stage 2 of the fantasy map guide: audit (gaps + consistency), fix chapters, write 00/12/13, final numbers check. args.mode = audit | fix | write | final',
  whenToUse: 'After chapters 01-11 exist and are fact-checked. Run mode audit first, then fix (args.jobs=[{file, instructions:[...]}]) and write (args.targets), then final.',
  phases: [
    { title: 'Audit' }, { title: 'Fix' }, { title: 'Write' }, { title: 'Final check' },
  ],
}

const REPO = '/home/user/map-making-guide'
const GUIDE = REPO + '/guide'
const BASE_FILE = REPO + '/research/baseline-numbers.md'

const TOOLS_NOTE = 'Tools: first load the web tools with ToolSearch query "select:WebSearch,WebFetch". WebSearch needs mode:"standard" (use "extended" only when standard results are thin or for hard-to-find facts). Do real research. Prefer scholarly and reference sources (Wikipedia is fine as a starting point, but follow its citations when numbers matter; also academic papers, university and museum sites, Historic England / English Heritage, Britannica, well-known books). Do NOT run any git commands. Only create or edit the file(s) you are told to.'

const STYLE = `AUDIENCE AND GOAL
- Reader: a hobbyist drawing a fantasy map at continent, kingdom and local-area scales (NOT detailed city street maps). They are not a historian, and English may not be their first language.
- Goal: tell them WHERE to put each human-made thing, HOW MANY, HOW BIG, HOW FAR APART, and WHY, so the map feels real.
- Baseline era: High to Late Middle Ages, mainly Europe (c. 1000-1500 AD). Use the Mediterranean, Middle East, steppe and other regions too when it helps (e.g. caravanserais, oases, qanats), and say where an example is from.
- Later era: where things change in c. 1500-1650 (gunpowder, star forts, ocean trade, canals...), add a short callout. (A full later-era chapter exists separately.)
- Fantasy: realistic first. Only add a short "Fantasy twist" callout where a typical fantasy element (magic, monsters, dwarves/elves, flying mounts) would clearly change the rule. The full fantasy chapter is separate; do not duplicate it.

WRITING STYLE
- Plain, clear English. Short sentences. Explain any technical term the first time, e.g. "motte (a man-made earth mound)".
- Order inside a topic: rule of thumb -> why -> numbers -> real examples -> map advice.
- Use tables for numbers and comparisons. Give distances in both km and miles, e.g. "30 km (19 mi)". Give populations as ranges, not false precision.
- Use exactly these callout formats (GitHub Markdown blockquotes):
  > **Map tip:** practical drawing advice (what to draw, where, which symbol, what to label)
  > **Rule of thumb:** a short memorable rule
  > **Later era (1500s+):** what changes after the medieval period
  > **Fantasy twist:** how magic, monsters or other races would change this
- Each major section should end with practical map advice.
- Be honest about uncertainty ("estimates vary: 50,000-80,000").
- No invented history. Real examples must be real and correctly dated.

FILE FORMAT
- Start with "# <Chapter title>", then a 2-4 sentence intro, then "**In this chapter:**" with a bullet list of links to the ## sections (GitHub anchors: lowercase, spaces become hyphens, most punctuation removed).
- Use ## and ### headings.
- End with "## Quick summary" (5-12 bullets) and then "## Sources and further reading" (real, checkable sources: books with author and year; URLs you actually opened or saw in search results. Never invent a URL).
- Link to other chapters with relative links when a topic belongs there, e.g. [Trade routes and transport](05-trade-routes-and-transport.md).`

const FILES = [
  ['00-step-by-step.md', 'Step-by-step: from blank map to living world (written later)'],
  ['01-settlement-placement.md', 'Where Settlements Are Built (and Why)'],
  ['02-population-and-sizes.md', 'Population and Settlement Sizes'],
  ['03-capitals-and-borders.md', 'Capitals, Realms and Borders'],
  ['04-military-sites.md', 'Castles, Forts and Military Outposts'],
  ['05-trade-routes-and-transport.md', 'Trade Routes, Roads and Transport'],
  ['06-villages-and-countryside.md', 'Villages, Farms and the Countryside'],
  ['07-industry-and-resources.md', 'Industry, Resources and Special Towns'],
  ['08-religious-cultural-and-ancient-sites.md', 'Religious, Cultural, Legal and Ancient Sites'],
  ['09-later-era-1500-1650.md', 'What Changes After 1500'],
  ['10-fantasy-variants.md', 'Fantasy Variants: Magic, Monsters and Other Races'],
  ['11-common-mistakes.md', 'Common Mistakes and How to Fix Them'],
  ['12-worked-example.md', 'Worked Example: Populating a Kingdom (written later)'],
  ['13-quick-reference.md', 'Quick Reference Cheat Sheet (written later)'],
]
const FILE_LIST = FILES.map(([f, t]) => `- ${f}: ${t}`).join('\n')
const FILE_LIST_SHORT = FILES.map(([f]) => f).join(', ')


const AUDIT_GAPS = {
  type: 'object',
  properties: {
    gaps: { type: 'array', items: { type: 'object', properties: {
      file: { type: 'string', description: 'guide file that should own the addition, e.g. 06-villages-and-countryside.md' },
      missing: { type: 'string' },
      whyItMatters: { type: 'string' },
      suggestedAddition: { type: 'string', description: 'concrete content guidance with real numbers/examples' },
      priority: { type: 'string', enum: ['high', 'medium', 'low'] },
    }, required: ['file', 'missing', 'whyItMatters', 'suggestedAddition', 'priority'] } },
  },
  required: ['gaps'],
}
const AUDIT_FIXES = {
  type: 'object',
  properties: {
    fixes: { type: 'array', items: { type: 'object', properties: {
      file: { type: 'string' },
      kind: { type: 'string', enum: ['contradiction', 'duplicate', 'cross-reference', 'terminology', 'other'] },
      instruction: { type: 'string', description: 'exact fix: quote the current text and give the replacement or action' },
      evidence: { type: 'string' },
    }, required: ['file', 'kind', 'instruction', 'evidence'] } },
  },
  required: ['fixes'],
}
const DONE = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    summary: { type: 'string' },
    notDone: { type: 'array', items: { type: 'string' } },
    crossFileProblems: { type: 'array', items: { type: 'string' } },
  },
  required: ['file', 'summary', 'notDone', 'crossFileProblems'],
}

const READ_ALL = `Read these first: ${REPO}/PROGRESS.md (the author's decisions), ${REPO}/research/baseline-numbers.md, and every chapter file in ${GUIDE}/ (01 to 11).`
const mode = (args && args.mode) || 'audit'

if (mode === 'audit') {
  phase('Audit')
  const [gaps, fixes] = await parallel([
    () => agent(`You are reviewing a nearly finished guide for fantasy mapmakers about ALL human-made map features (medieval to late medieval, with notes for 1500-1650; scales: continent, kingdom, local area; city street maps are out of scope).
${READ_ALL}
${TOOLS_NOTE}

Your job: find what is MISSING or too thin. Think like a mapmaker drawing a continent, then a kingdom, then one valley. List every human-made thing they might draw: settlements of every size and type; seasonal and nomad camps; roads, bridges, fords, ferries, causeways, inns, tolls, passes; ports, harbours, lighthouses, canals; castles, forts, towers, walls, beacons, battlefields, camps; capitals, regional seats, borders, markers; farms, fields, mills, ponds, parks, forests, terraces, irrigation, dikes, polders; mines, quarries, saltworks, kilns, workshops; churches, monasteries, shrines, pilgrim routes, universities, hospitals; gallows, moot sites, cemeteries; ruins and older layers. Also consider mapmaker needs beyond features: what place names reveal and how to name settlements realistically (e.g. -ford, -bridge, -burg, -chester, -by, -thorpe, -wick), symbols and label hierarchy, climate and region variants (desert, steppe, arctic, tropical, Mediterranean, non-European models), and how the map changes with time. For each feature, check that the guide answers: where, how many, how big, how far apart, and why.
Return gaps. Each needs: the owner file (from: ${FILE_LIST_SHORT}), a concrete suggestedAddition (real numbers and examples you have checked), and a priority. Do NOT edit files. Aim for the 15-40 most valuable gaps, not trivia.`, { label: 'audit:gaps', phase: 'Audit', schema: AUDIT_GAPS }),
    () => agent(`You are the consistency editor for a multi-chapter guide for fantasy mapmakers.
${READ_ALL}
${TOOLS_NOTE}

Find, across ALL files:
1. Contradictions: the same quantity given with different values in different files (village/town/city population ranges, people per km2, travel per day by mode, transport cost ratios, market-town spacing, castle counts and garrisons, city populations, dates), unless the difference is explained. Topic owners: 02 = population numbers, 05 = travel speeds and costs, 04 = fortification numbers, 03 = political units and capitals, baseline file = the default. When unsure which value is right, check with web research.
2. Duplicated explanations that should be shortened to a link to the owner chapter.
3. Wrong cross-references (e.g. "see chapter X" where X does not cover it, or wrong file names).
4. Terminology drift (e.g. different names or cut-offs for the same settlement tier).
Return one fix per file location with an exact instruction (quote the current text, give the replacement). Do NOT edit files.`, { label: 'audit:consistency', phase: 'Audit', schema: AUDIT_FIXES }),
  ])
  return { gaps: gaps ? gaps.gaps : null, fixes: fixes ? fixes.fixes : null }
}

if (mode === 'fix') {
  phase('Fix')
  const AUDIT = args.auditFile || (REPO + '/research/audit.json')
  const jobs = args.jobs || (args.files || []).map(f => ({ file: f }))
  const changes = (job) => job.instructions
    ? job.instructions.map((s, i) => (i + 1) + '. ' + s).join('\n')
    : `Read ${AUDIT} with the Read tool. Apply EVERY entry in its "gaps" array and its "fixes" array whose "file" field is "${job.file}". For a gap: add the missing content (follow suggestedAddition; verify its numbers and examples before using them; put it in the most fitting section, or a new ## section). For a fix: apply the instruction (line numbers may have shifted slightly; match the quoted text).`
  const out = await pipeline(jobs, (job) => agent(`You are editing ONE file of a guide for fantasy mapmakers: ${GUIDE}/${job.file}.
Apply ALL of the following changes (additions and fixes). For new content, research it with the web tools and use only real, checkable sources; add any new sources to the "Sources and further reading" section. If you add a ## section, add it to the "In this chapter" list. Keep the chapter's style. Do not edit any other guide chapter or research file; edit files under tools/ or guide/images/ only if a change explicitly allows it. If a change is wrong after checking, skip it and say why in notDone.
${TOOLS_NOTE}

CHANGES:
${changes(job)}

Shared baseline numbers: ${REPO}/research/baseline-numbers.md (read it if a change touches numbers).

Style rules:
${STYLE}`, { label: 'fix:' + job.file.slice(0, 2), phase: 'Fix', schema: DONE }))
  return { results: out }
}

if (mode === 'write') {
  phase('Write')
  const targets = args.targets || ['00', '12']
  const tasks = []
  if (targets.includes('00')) tasks.push(() => agent(`Write ${GUIDE}/00-step-by-step.md: "Step by Step: From Blank Map to Living World". It is the master method that ties the guide together.
${READ_ALL}
${TOOLS_NOTE} (You may not need the web: this chapter summarizes the others.)

Structure:
- Intro: what this chapter is, and that it assumes terrain (coasts, mountains, rivers, climate) is already drawn. Add a short "before you start" box: decide era, scale, how much magic.
- A Mermaid flowchart (GitHub renders \`\`\`mermaid blocks) showing the order of steps.
- Part A: Continent / world scale. Part B: Kingdom / region scale. Part C: Local area scale.
- Each step: what to place; the key rules with numbers; a link to the exact chapter section that explains it (relative link with anchor); and a "Check:" question to test the result.
- Suggested order: terrain and water check, good farmland, population budget, realms and borders, capitals, great cities and ports, trade routes and sea lanes, regional cities and towns, market towns, castles and fortifications, roads and crossings, church geography (dioceses, monasteries, pilgrim routes), industry and resource sites, villages, local features, ruins and older layers, fantasy adjustments, final sanity check.
- End with a printable checklist (Markdown task list "- [ ]") and the standard "Quick summary" (no separate Sources section needed; link to chapters instead).
Every number must be copied from the chapters; do not invent new ones. About 2,500-4,000 words.
Style rules:
${STYLE}`, { label: 'write:00', phase: 'Write', schema: DONE }))
  if (targets.includes('12')) tasks.push(() => agent(`Write ${GUIDE}/12-worked-example.md: "Worked Example: Populating a Kingdom".
${READ_ALL}
${TOOLS_NOTE}

Invent ONE fictional kingdom with a clearly made-up name (about the size of England, 100,000-150,000 km2; give it a coast with a good estuary, a major navigable river, a range of hills/mountains with a pass, a forest, some marsh, and a mix of good and poor land; date c. 1300). Walk through every step of the guide with the guide's own numbers, showing the arithmetic in tables:
1. Land types and areas -> population by density -> total population.
2. Urbanization -> how many people in towns -> list of cities and towns with populations (rank-size check) and the number of market towns and villages.
3. Capital: where and why (and a secondary/coronation/religious centre if fitting).
4. Political units: duchies/counties/baronies, their seats, borders and a march.
5. Castles and fortifications: how many, of which types, where and why.
6. Roads, river and sea routes, bridges and fords, ports, inns, tolls: the network and travel times between main places.
7. Church: dioceses, cathedral cities, monasteries by order, parish count, a pilgrimage site.
8. Industry and resources: mines, salt, quarries, cloth, fishing; the special towns they create.
9. Ruins and older layers.
10. Zoom-in: one local area of about 10 x 10 km (6 x 6 mi) with its villages, manor, church, mill, fields, woods, roads and households.
11. Optional fantasy variant: how two fantasy elements from chapter 10 would change this kingdom.
Every number must come from the chapters (link to the section); if the chapters disagree, say so in crossFileProblems. Give all distances in km and mi. About 3,000-5,000 words. End with "Quick summary".
ALSO write a plain-text file ${GUIDE}/images/worked-example-layout.json describing coordinates (0-1000 x 0-800 canvas) of: coastline points, river polylines, hills/mountain areas, forest and marsh areas, every named settlement (name, tier, x, y), castles, monasteries, roads (polylines), border lines, ports. Another agent will draw the map from it.
Style rules:
${STYLE}`, { label: 'write:12', phase: 'Write', schema: DONE }).then(r => agent(`Draw a clean schematic map as SVG for the worked example of a fantasy-mapmaking guide.
Inputs: ${GUIDE}/12-worked-example.md and ${GUIDE}/images/worked-example-layout.json.
Output: ${GUIDE}/images/worked-example-kingdom.svg (self-contained SVG, viewBox 0 0 1000 800, readable on white and in GitHub dark mode: put an explicit light parchment background rect).
Draw: sea and coastline, rivers, hills/mountains (simple symbols), forest and marsh (light patterns or tints), borders (dashed), roads (thin lines; main roads thicker), settlements with symbols scaled by tier (capital star or large square, city, town, market town, village dot), castles, monasteries, ports, a legend, a scale bar in km and mi, a compass, and labels that do not overlap.
Then check your work visually: render it to PNG with Chromium (Playwright is installed; use executablePath '/opt/pw-browsers/chromium' if needed, or find the chromium binary under /opt/pw-browsers; do not run "playwright install"), save the PNG in ${GUIDE}/images/worked-example-kingdom.png, view it with the Read tool, and fix overlaps or ugliness. Iterate at least twice.
Finally add the image to 12-worked-example.md near the top: ![Schematic map of the worked-example kingdom](images/worked-example-kingdom.svg) and make sure the map matches the text (names and counts). Do not edit other files.`, { label: 'map:12', phase: 'Write', schema: DONE })))
  if (targets.includes('13')) tasks.push(() => agent(`Write ${GUIDE}/13-quick-reference.md: "Quick Reference Cheat Sheet".
${READ_ALL}
A dense one-stop sheet a mapmaker keeps open while drawing: tables, not prose. Sections: settlement tiers (population, features, symbol); population density by land type; urbanization and how many of each tier; spacing (villages, market towns, towns, cities, inns, castles); travel per day by mode and transport cost ratios; political units and sizes; capitals checklist; fortification types by date and where they go; trade goods and route types; rural features; industry siting table; religious sites siting table; city sizes by era (c. 1000 / 1300 / 1500); later-era changes (1500-1650); fantasy adjustments; a 15-question sanity checklist.
Also read ${REPO}/research/audit.json and include every entry in "gaps" whose "file" is "13-quick-reference.md" (master legend and label hierarchy, a 'what exists by which date' table, and a reconciliation of numbers). Before choosing symbols, grep the chapters for their symbol suggestions and resolve clashes as the audit proposes.
Every number must be copied from the owner chapter (02 population, 05 travel and costs, 04 fortifications, 03 political units, others for their topics), with a link to the source chapter section under each table. If chapters disagree, do not choose silently: list the disagreement in crossFileProblems and use the owner chapter's value. No Sources section needed (link to chapters instead). End with nothing after the last table except a one-line note pointing to 00-step-by-step.md.
Style rules:
${STYLE}`, { label: 'write:13', phase: 'Write', schema: DONE }))
  const out = await parallel(tasks)
  return { results: out }
}

if (mode === 'final') {
  phase('Final check')
  const RULE = `Owner chapters: 02 population numbers, 05 travel speeds/costs/spacing of routes, 04 fortification numbers, 03 political units and capitals, 06 rural features, 07 industry, 08 religious sites; master map symbols: 13's 'Master legend and label hierarchy'. Do not edit chapters 01-11; report chapter-vs-chapter problems in crossFileProblems with exact quotes.`
  const out = await parallel([
    () => agent(`Final numbers check for ${GUIDE}/13-quick-reference.md.
${READ_ALL}
Compare EVERY number in 13 (tables, notes, the reconciliation table) against the owner chapter's CURRENT text, section by section. Fix 13 in place wherever it differs from the owner chapter. Also check that each 'Source:' link under a table points to a heading that exists (run python3 ${REPO}/tools/check_links.py at the end). ${RULE} Do not edit 00 or 12.`, { label: 'final:13', phase: 'Final check', schema: DONE }),
    () => agent(`Final numbers check for ${GUIDE}/00-step-by-step.md and ${GUIDE}/12-worked-example.md.
${READ_ALL} Then read 00, 12 and 13.
Compare every number in 00 and 12 against the owner chapter's CURRENT text, and every symbol they name against 13's master legend. Fix 00 and 12 in place. In 12, keep the arithmetic self-consistent (re-add sums), and if you change a count that the map shows (guide/images/worked-example-kingdom.svg, generated by tools/make_map.py), report it instead of changing it. Run python3 ${REPO}/tools/check_links.py at the end. ${RULE} Do not edit 13.`, { label: 'final:00+12', phase: 'Final check', schema: DONE }),
  ])
  return { results: out }
}
}
