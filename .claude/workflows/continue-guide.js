export const meta = {
  name: 'continue-guide',
  description: 'Continue the fantasy map guide: write remaining chapters and fact-check chapters (args: {write:[...], check:[...]})',
  whenToUse: 'Resume work on the map-making guide. Default: write chapters 04-11, then fact-check 01-11.',
  phases: [
    { title: 'Write', detail: 'one research+writing agent per chapter still missing' },
    { title: 'Fact-check', detail: 'adversarial fact-check and in-place fix of each chapter' },
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

const CHAPTERS = [
  { file: '01-settlement-placement.md', title: 'Where Settlements Are Built (and Why)', scope: `Owns: why and where settlements form, and how they are spaced. NOT detailed population numbers (02), castles (04), roads/ports detail (05), village internal layout (06).
- Core siting needs: fresh water (rivers, springs, wells; flood risk; river terraces), food (good soil, a MIX of arable, meadow, pasture, woodland), fuel and building material, defence (hills, river bends, islands, spurs), communications (fords, bridging points, confluences, head of navigation, estuaries, natural harbours, the mouth of a mountain pass, crossroads), shelter and health (sunny slopes, out of the wind, away from fever marshes).
- Site vs situation (the local spot vs its place in the wider network) and why situation decides which places grow big.
- Classic site types with real examples: ford/bridge town, confluence town, lowest bridging point, head of navigation, river-bend/meander town, hilltop town, island town, spring-line villages, gap town, harbour/estuary town, oasis town, wet-point and dry-point settlements.
- By terrain/biome: fertile river valleys and plains, rolling hills, uplands and mountains (valley floors, alpine pastures, passes), coasts, marsh/fens, forest (clearings, assarting), steppe/grassland, desert, islands, cold north.
- Patterns and spacing: nucleated vs dispersed vs linear settlement; central place theory (Christaller) explained simply with what it looks like on a map; how far apart villages, market towns and cities are; chains along rivers, coasts and roads; clustering on good land and emptiness on bad land.
- How settlements change over time: reuse of ancient/Roman sites, planted "new towns" and bastides, monastic and castle-gate towns, why some places grow and others shrink, deserted medieval villages.
- Where people do NOT build, and why.
- Map advice: an order for placing settlements on an existing terrain map; a "why is it here?" test for every dot.` },
  { file: '02-population-and-sizes.md', title: 'Population and Settlement Sizes', scope: `Owns: all population and size numbers. Other chapters will link here.
- Settlement hierarchy: farmstead, hamlet, village, market town, town, city, great city. Population range and the features/services typical of each tier (church, mill, smithy, inn, weekly market, annual fair, walls, guilds, hospital, friaries, cathedral, university, mint), and suggested map symbols/label sizes.
- How many of each tier: urbanization rates by region and date; ratios of villages to towns to cities; the rank-size rule and primate cities explained simply.
- Population density per km2 and per sq mi by land quality and region/date (fertile lowland, average, hills, uplands, steppe/forest frontier, desert).
- Carrying capacity: farmland needed per person (yields, fallow, seed ratios), village territory sizes, the food hinterland needed by towns/cities of different sizes, and why big cities need river or sea supply.
- Realm populations and areas (England, France, Iberian kingdoms, German lands/HRE, Italy, Poland, Hungary, Byzantium, others) at c. 1000, 1300, 1500; Europe total.
- Biggest cities c. 1000, 1300, 1500, in Europe AND the Mediterranean/Middle East (with ranges).
- A step-by-step population calculator: area x density -> total population -> split into tiers -> number of villages/towns/cities, with a short worked mini-example.
- Change over time: growth 1000-1300, Great Famine, Black Death and recovery; effect on maps (deserted villages, shrunken towns).
- Who lives where: rough share of peasants, townspeople, clergy, nobility, soldiers.
- Briefly compare popular gaming rules of thumb (e.g. S. John Ross, "Medieval Demographics Made Easy") with historical data, noting where they agree or differ.` },
  { file: '03-capitals-and-borders.md', title: 'Capitals, Realms and Borders', scope: `Owns: capitals, political divisions and borders. Castles/forts detail belongs to 04 (link to it).
- What makes a capital: rich core region, river/sea access, centrality vs defensibility vs frontier ("forward capital"), sacred or legitimacy sites, coronation city vs administrative capital. Itinerant (travelling) courts in the Early/High Middle Ages and when and why fixed capitals emerged, with real examples (Paris, Westminster/London, Prague, Krakow, Buda, Toledo/Valladolid/Madrid, Constantinople, Cairo...).
- What is IN or NEAR a capital: palace/royal castle, cathedral, royal burial church, treasury, chancery, law courts, mint, university, royal hunting forests and lodges, circuit of royal residences.
- Political units and their sizes: kingdom, duchy/principality, county, barony/lordship, manor, shire/hundred; typical area and population of each; where each lord's seat sits; the town that is the seat of a county.
- Borders: what they follow (rivers sometimes, watersheds, mountain ridges, forests, marshes, empty wasteland, old boundaries); frontier zones vs border lines; marches (e.g. Welsh March, Spanish March), buffer states, enclaves and exclaves, contested lands, border markers and crossings.
- Kinds of states and how they look on a map: feudal kingdom patchwork, city-states and their contado, leagues (Hanseatic, Swiss), large composite empires (HRE), nomadic empires, church states and prince-bishoprics, maritime empires (Venice).
- How big a realm can be: governance range by messenger travel time; realistic realm sizes; number of counties/duchies in a kingdom.
- Map advice: drawing borders, capitals, regional seats, colour and labels.` },
  { file: '04-military-sites.md', title: 'Castles, Forts and Military Outposts', scope: `Owns: every kind of fortification and military site.
- What fortifications are FOR: control a route (pass, ford, bridge, river), protect a town or port, hold a border, dominate conquered land, serve as a lord's home and admin centre, provide refuge, watch and signal.
- Types across the period, with dates and real examples: motte-and-bailey, stone keeps, shell keeps, curtain-wall castles, concentric castles, tower houses and peel towers, fortified manor houses, fortified churches and monasteries, town walls and gates, citadels, fortified bridges, watchtowers, coastal towers, beacon chains, hillforts reused, crusader castles, Islamic ribats and frontier fortresses, military-order castles (e.g. Teutonic Order), siege castles.
- Where to put them: topography rules (crossings, passes, spurs, river bends, coastal headlands, above towns); density and counts (e.g. England after 1066, Welsh March, France, Germany, Iberian frontier); control radius; much higher density in borderlands and conquered lands; chains of border forts; how castles and towns pair together.
- Garrisons: peace vs war sizes, small royal castles vs great fortresses; how many soldiers a realm could field relative to its population.
- Military geography and logistics: army march speeds, campaign seasons, supply by river and forage, muster points, armouries/arsenals, naval bases and war fleets (e.g. Venice Arsenal), invasion ports.
- Outposts in wild or contested land: frontier posts, toll castles on rivers (e.g. on the Rhine), robber-knight castles, military-order commanderies, watch-and-warning systems.
- Briefly: battlefield geography (where battles happen and why).
- Later-era callouts: gunpowder changes (lower thicker walls, bastions, trace italienne/star forts, artillery towers, coastal device forts, citadels).
- Map advice: symbols for different fort types; ruined vs active castles; how many to draw per region.` },
  { file: '05-trade-routes-and-transport.md', title: 'Trade Routes, Roads and Transport', scope: `Owns: travel speeds and costs, roads, rivers, sea lanes, bridges, ports, inns, and trade networks.
- Modes of transport and their speed per day and relative cost; why water beats land for bulk goods.
- Roads: Roman legacy, kinds of medieval roads (royal highways, local tracks, hollow ways, causeways), who maintained them, road quality by season; bridges (when stone bridges were built, bridge chapels, bridge tolls), fords, ferries; mountain passes and pass hospices (e.g. Great St Bernard, Brenner, St Gotthard); inns and stages roughly a day apart; toll and customs stations; caravanserais and their spacing.
- Rivers: navigable rivers, head of navigation, portages, towpaths, river ports, conflict with mill weirs, staple rights (e.g. Cologne).
- Sea: coastal hopping vs open sea; ship types (cog, galley, hulk; later carrack/caravel); what makes a good harbour; lighthouses; sailing seasons (e.g. Mediterranean winter); how far apart galley stops were.
- Trade nodes: market towns, fairs (e.g. Champagne fairs), staple towns, entrepots (Bruges, Venice, Alexandria...), merchant colonies and kontors/fondachi (Hanseatic Steelyard, Bergen, Novgorod, Fondaco dei Tedeschi), customs houses.
- Major real trade networks as templates for fantasy maps: Hanseatic Baltic-North Sea, Venetian and Genoese Mediterranean, Silk Roads, trans-Saharan, Indian Ocean monsoon trade, Rhine corridor, Russian river routes, Amber Road, salt routes, wine trade, pilgrim roads (link to 08).
- What is traded: bulk vs luxury goods; which goods go far (high value per weight) and which stay local; a table of typical goods by region type.
- How to draw a route network: hierarchy of roads, sea lanes, labelling, which places become hubs.
- Later-era callouts: ocean routes, Atlantic ports, pound-lock canals, postal routes and posting stations, better roads.` },
  { file: '06-villages-and-countryside.md', title: 'Villages, Farms and the Countryside', scope: `Owns: local-area/rural features (this is the chapter for local-scale maps).
- Village forms and layout: green villages, street/row villages, nucleated villages, dispersed farmsteads and hamlets; what is in a village (church, manor house, mill, smithy, alehouse, pond, green, pound/pinfold, cottages with tofts and crofts); regional differences (English open-field Midlands vs upland/Celtic areas vs Mediterranean hill villages vs German Waldhufendorf forest villages, etc.).
- Fields and land use: open-field systems (two- and three-field), strips, furlongs, headlands, ridge and furrow; meadow (hay by rivers), pasture, commons, waste; woodland management (coppice, pollards, wood-pasture, pannage); orchards, vineyards (and climate limits), gardens; infield-outfield in uplands; terraces and irrigation in the Mediterranean (norias, qanats, acequias); rings of land use around a village.
- Sizes and distances: village territory/parish area, how far peasants walk to fields, typical number of households.
- Mills: watermills (with numbers such as Domesday), windmills (from c. 1180s), tide mills, horse mills; leats/mill races, millponds, weirs.
- Other features: fishponds, dovecotes, deer parks, rabbit warrens, royal forests (legal forest vs woodland), hunting lodges, monastic granges, sheepfolds, shielings and transhumance (summer pastures), tithe barns, boundary stones/banks/hedges, hollow ways and footpaths, wells, wayside crosses, limekilns.
- Reclaimed land: drained fens, dikes and polders, salt-marsh grazing, assarts (forest clearings).
- Local administration: parish, manor, hundred/wapentake; moot sites.
- Map advice for local-scale maps: what to show, scale, symbols.` },
  { file: '07-industry-and-resources.md', title: 'Industry, Resources and Special Towns', scope: `Owns: resource extraction, industry and specialized town types.
- Mining: silver (e.g. Goslar/Rammelsberg, Freiberg, Kutna Hora, Iglesias), copper (Falun), iron (Erzberg in Styria, Siegerland, Basque country), tin (Cornwall/Devon stannary towns), lead (Derbyshire, Mendips), gold (Kremnica), coal (late medieval Newcastle, Liege). What mining towns look like, their sizes, privileges, location (up valleys, needing wood and water power).
- Salt: brine springs (Luneburg, Droitwich, Halle, Salins), rock salt mines (Wieliczka, Hallstatt), sea-salt pans (Bay of Bourgneuf, Venetian lagoon/Chioggia, Ston); salt roads.
- Stone and clay: quarries (building stone, millstones, slate), brick-making (and brick regions), lime kilns, pottery.
- Forest industries: timber, charcoal burning, potash, tar and pitch, forest glass, iron smelting (bloomeries; later blast furnaces) near forests and water.
- Textiles: wool production regions, cloth towns (Flanders: Ghent, Ypres, Bruges; Florence), fulling mills (water power), dye crops (woad, madder), linen, silk.
- Fishing: herring (Scania, North Sea), stockfish/cod (Lofoten, Bergen), fishing villages, fish weirs, salting and curing.
- Shipbuilding and naval stores, arsenals.
- Metalworking and craft towns (Nuremberg, Milan armour, Solingen/Passau blades), tanneries, breweries, wine regions (Bordeaux, Rhine, Burgundy).
- Where industry sits relative to towns: smelly or dirty trades downstream or outside walls; industry following water power, fuel and ore.
- Specialized town types and how to spot them on a map: mining town, port, fishing village, cloth town, fair town, spa/bath town (briefly), plus links to 08 for university and pilgrimage towns.
- A table: resource -> what it needs -> where it goes on the map -> what settlement it creates.` },
  { file: '08-religious-cultural-and-ancient-sites.md', title: 'Religious, Cultural, Legal and Ancient Sites', scope: `Owns: religious, cultural, legal and older/ruined human-made layers.
- Parish churches and chapels: one per parish, density, chapels of ease; how church towers act as landmarks.
- Dioceses and cathedrals: numbers and sizes of dioceses in different regions (e.g. England vs Italy vs France), archbishoprics, cathedral cities.
- Monasteries and their siting by order: Benedictines, Cistercians (remote valleys with water), Carthusians (isolated), Augustinian canons, mendicant friars (Franciscans, Dominicans) in towns (friaries as a sign of town size), nunneries, military orders' commanderies; numbers of religious houses (e.g. in England c. 1500); monastic granges (link to 06).
- Pilgrimage: shrines, major routes (Santiago de Compostela, Rome/Via Francigena, Canterbury, Jerusalem), pilgrim hostels and hospices, pilgrim towns.
- Hospitals, leper houses (outside towns), almshouses.
- Universities: founding dates and locations of the major medieval universities; schools.
- Legal and civic sites: gallows (often on high ground near roads or boundaries), pillories, courts, moot sites, town halls, guildhalls, market crosses.
- Burial: churchyards, charnel houses, Jewish cemeteries outside walls.
- Minorities and other faiths: Jewish quarters, mosques in Iberia and Sicily, Orthodox and other communities; where they were placed.
- Ancient and ruined layers (older human-made features a medieval map would include): Roman roads and ruins, hillforts, burial mounds and barrows, standing stones, abandoned villages, ruined castles and abbeys; where ruins tend to be and how medieval people reused them.
- Map advice: symbols, density, and how religion shapes the map.` },
  { file: '09-later-era-1500-1650.md', title: 'What Changes After 1500', scope: `Owns: changes in the period c. 1500-1650 (with brief pointers to what came soon after). Write it as a guide for someone whose map is set slightly later than the medieval baseline.
- Population growth and bigger cities (e.g. Naples, Paris, London, Seville, Lisbon, Antwerp, Amsterdam, Istanbul), shifting rank of cities, the Atlantic shift.
- Military: artillery and the gunpowder revolution; bastioned trace italienne and star forts (dates, where first), citadels, coastal fort lines, larger armies, castles abandoned or turned into palaces and country houses.
- Trade and transport: oceanic routes, chartered companies, trading posts/factories abroad, postal routes and posting stations (e.g. Taxis post), improved roads, pound-lock canals, bigger ships (carrack, galleon), exchanges and banking centres, printing towns.
- Politics: fixed capitals and palace complexes (e.g. El Escorial), more centralized states, borders becoming lines, surveying and mapping.
- Countryside: enclosure, new crops arriving, drainage with windmills (Dutch polders), large estates and country houses.
- Industry: blast furnaces spreading, mining booms (e.g. Joachimsthal, Potosi), paper mills, gunpowder mills, shipyards.
- Religion: Reformation effects on the map (dissolution of the monasteries in England, ruins, re-used buildings, religious borders).
- A comparison table: medieval baseline vs 1500-1650 for each kind of map feature.
- Map advice: how to show a world in transition (old castles next to new star forts, etc.).` },
  { file: '10-fantasy-variants.md', title: 'Fantasy Variants: Magic, Monsters and Other Races', scope: `Owns: how fantasy elements change the realistic rules. Method: apply the real rules first, then ask what each fantasy element changes among the inputs (water, food, defence, travel cost, threats, resources). Ground every adaptation in a REAL historical analogue where possible.
- Dangerous wilderness and monsters: more nucleated and walled villages, fewer isolated farms, palisades, watchtower networks, guarded roads, frontier forts, "points of light" design, hunter/ranger lodges; historical analogues (frontier zones, steppe raids, Viking-age coasts, wolves).
- Magic, effect by effect: food/fertility magic (higher density, bigger cities), water magic (desert cities), healing (population growth), teleport circles/portals (become hubs like ports or crossroads; effect on capitals and trade), flying mounts/airships (fortifications facing the sky, aeries on peaks, trade over mountains), weather control, magical resources (crystals, ley lines treated like ore or rivers: mines, boom towns, fortress guarding), mage towers and academies (placement like monasteries/universities), magical defences.
- Common non-human peoples as archetypes, each with a real-world analogue: dwarves (mountain holds, mines, underground roads, trade towns at mountain gates), elves (forest realms, low density, few clearings), halflings (fertile farmland), orcs and other "horde" peoples (careful: model them on nomadic/steppe societies with real logistics, not as mindless), merfolk (coastal trade), giants and dragons (no-go zones, tribute).
- Contact zones between peoples: frontier markets and trading posts (real analogues such as Hanseatic kontors or treaty-port style trade towns), mixed cities, borders.
- Gods with real power, undead/blights, dangerous seas: how each changes settlements, routes and fortifications.
- A "what changes if..." table: fantasy element -> what changes on the map -> real analogue.
- A consistency checklist: if X exists in your world, what else must also exist or change.` },
  { file: '11-common-mistakes.md', title: 'Common Mistakes and How to Fix Them', scope: `Owns: frequent errors in human-made features on fantasy maps. Research what experienced mapmakers and worldbuilders point out (mapmaking and worldbuilding communities, blogs, guides; e.g. Cartographers' Guild, worldbuilding Q&A sites, well-known fantasy-cartography guides) and check each against real history.
- Cover at least 25 mistakes, including: cities with no water source, cities in deserts with no oasis/river, too few or too many settlements for the area, evenly spaced settlements, everything on the coast or nothing on the coast, empty interiors, capital at the exact geometric centre without reason, castles on random hills, border lines that are straight without reason, borders ignoring rivers/mountains entirely, roads that go nowhere or that cross mountains without passes, no roads at all, trade routes through deserts/mountains without water or stops, ports on cliffs or exposed coasts, no farmland around cities, huge cities without water transport, ignoring travel time and scale, too many castles / too few castles, single-product economies, isolated towns with no reason to exist, every town walled, no ruins or older layers, mixing eras without reason, unrealistic city sizes for the era, labels clutter.
- For each mistake: why it looks wrong, how to fix it, and the exception (when it CAN be right, with a real example).
- End with a short "sanity check" checklist (10-20 yes/no questions) for a finished map.
(Note: geography errors like rivers splitting are only relevant if they affect human features; mention them briefly in one section at most.)` },
]

const BASELINE_SCHEMA = {
  type: 'object',
  properties: {
    markdown: { type: 'string', description: 'The full baseline numbers sheet in Markdown' },
    uncertainItems: { type: 'array', items: { type: 'string' } },
  },
  required: ['markdown', 'uncertainItems'],
}

const CHAPTER_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    approxWords: { type: 'number' },
    sections: { type: 'array', items: { type: 'string' } },
    keyNumbers: { type: 'array', items: { type: 'object', properties: { topic: { type: 'string' }, value: { type: 'string' } }, required: ['topic', 'value'] } },
    baselineDisagreements: { type: 'array', items: { type: 'string' } },
    gapsNotCovered: { type: 'array', items: { type: 'string' } },
  },
  required: ['file', 'approxWords', 'sections', 'keyNumbers', 'baselineDisagreements', 'gapsNotCovered'],
}

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    claimsChecked: { type: 'number' },
    corrections: { type: 'array', items: { type: 'object', properties: { before: { type: 'string' }, after: { type: 'string' }, reason: { type: 'string' } }, required: ['before', 'after', 'reason'] } },
    softenedOrRemoved: { type: 'array', items: { type: 'string' } },
    sourceAndLinkFixes: { type: 'array', items: { type: 'string' } },
    baselineConflicts: { type: 'array', items: { type: 'string' } },
    remainingConcerns: { type: 'array', items: { type: 'string' } },
  },
  required: ['file', 'claimsChecked', 'corrections', 'softenedOrRemoved', 'sourceAndLinkFixes', 'baselineConflicts', 'remainingConcerns'],
}

const BASE = 'Read the shared baseline numbers file FIRST with the Read tool: ' + BASE_FILE + ' . It is the single source of truth for settlement sizes, densities, travel speeds and spacing.'
const WRITE = (args && args.write) || ['04', '05', '06', '07', '08', '09', '10', '11']
const CHECK = (args && args.check) || ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11']
const num = (ch) => ch.file.slice(0, 2)
const ITEMS = CHAPTERS.filter(ch => WRITE.includes(num(ch)) || CHECK.includes(num(ch)))
log('Write: ' + WRITE.join(',') + ' | Fact-check: ' + CHECK.join(','))

const writePrompt = (ch) => `You are researching and writing ONE chapter of a practical guide for fantasy mapmakers: "${ch.title}".
Write it to: ${GUIDE}/${ch.file} (create the guide/ directory if needed; use the Write tool).

${STYLE}

THE WHOLE GUIDE (for cross-links, and to avoid overlap: stay inside YOUR scope and link to other chapters for their topics instead of re-explaining them):
${FILE_LIST}

YOUR SCOPE:
${ch.scope}

SHARED BASELINE NUMBERS (all chapters use these so the guide is consistent). Use these values whenever you mention these topics. If your research shows a baseline value is clearly wrong or misleading, write the better-supported value in your chapter but report it in baselineDisagreements with evidence.
<baseline>
${BASE}
</baseline>

PROCESS
1. ${TOOLS_NOTE}
2. Research your scope properly: at least 12-20 searches and several fetched pages. Collect concrete numbers, real examples with dates, and rules of thumb.
3. Write the chapter: roughly 3,000-5,000 words, dense and practical, with tables wherever numbers are compared. Cover every item in your scope.
4. Re-read your file once and fix anything unclear, unsupported or out of scope.

Return the structured summary (keyNumbers = the most important numeric claims you made; gapsNotCovered = anything in scope you could not cover well).`

const verifyPrompt = (ch, w) => `You are an adversarial fact-checker for one chapter of a fantasy-mapmaking guide grounded in real medieval history.
File: ${GUIDE}/${ch.file} (chapter: "${ch.title}").
The writer reported these key numbers: ${w && w.keyNumbers ? JSON.stringify(w.keyNumbers) : '(not available: read the file)'}

${TOOLS_NOTE}

TASK
1. Read the whole file.
2. List every load-bearing factual claim: numbers (populations, areas, distances, speeds, dates, counts, percentages), named real-world examples (place + what is claimed about it + date), and "historically X happened" claims.
3. Verify at least the 25 most important with web research (prioritize table values and specific named examples). Default to doubt: a plausible claim you cannot confirm should be softened ("about", a range, "estimates vary") or removed. Wrong claims must be corrected.
4. Check the "Sources and further reading" section: every URL must be real and relevant (fetch it or see it in search results). Remove or replace any you cannot confirm. Never add an invented URL.
5. Check consistency with the shared baseline numbers below. Where the chapter disagrees without good reason, align it. Where the chapter is right and the baseline is wrong, keep the chapter and report it in baselineConflicts.
6. Check the format rules: the four callout formats, km and miles both given, relative links only to these files: ${FILE_LIST_SHORT}; "In this chapter" anchor links match real headings (GitHub anchor style); "Quick summary" and "Sources and further reading" sections exist. Fix problems.
7. Plain-English check: break up very long sentences and define jargon. Do NOT rewrite wholesale and do not cut useful content. The chapter should stay about the same length or get longer.
Edit the file in place with the Edit tool.

Style rules the chapter must follow:
${STYLE}

<baseline>
${BASE}
</baseline>

Return the structured report.`

const results = await pipeline(
  ITEMS,
  (ch) => WRITE.includes(num(ch))
    ? agent(writePrompt(ch), { label: `write:${num(ch)}`, phase: 'Write', schema: CHAPTER_SCHEMA })
    : Promise.resolve({ skipped: true }),
  (w, ch) => CHECK.includes(num(ch))
    ? agent(verifyPrompt(ch, w), { label: `check:${num(ch)}`, phase: 'Fact-check', schema: VERIFY_SCHEMA }).then(v => ({ file: ch.file, written: w, verified: v }))
    : Promise.resolve({ file: ch.file, written: w, verified: null }),
)

return {
  chapters: results.map((r, i) => r || { file: ITEMS[i].file, failed: true }),
}
