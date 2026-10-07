# Worked Example: Populating a Kingdom

This chapter builds one invented kingdom from an empty terrain map to a full kingdom map and one local map. It uses only the guide's own numbers, shows every calculation in a table, and links each number to the chapter that owns it. Treat it as a template: put in your own areas and land types and redo the arithmetic. The kingdom, its places and its history are invented; the real examples quoted come from the other chapters.

**In this chapter:**

- [The kingdom at a glance](#the-kingdom-at-a-glance)
- [Step 1: Land and population](#step-1-land-and-population)
- [Step 2: Cities, towns and villages](#step-2-cities-towns-and-villages)
- [Step 3: The capital](#step-3-the-capital)
- [Step 4: Duchies, counties and the North March](#step-4-duchies-counties-and-the-north-march)
- [Step 5: Castles and fortifications](#step-5-castles-and-fortifications)
- [Step 6: Roads, rivers and the sea](#step-6-roads-rivers-and-the-sea)
- [Step 7: The Church](#step-7-the-church)
- [Step 8: Industry and special towns](#step-8-industry-and-special-towns)
- [Step 9: Ruins and older layers](#step-9-ruins-and-older-layers)
- [Step 10: Zoom in on the Leyford area](#step-10-zoom-in-on-the-leyford-area)
- [Step 11: A fantasy variant](#step-11-a-fantasy-variant)
- [Quick summary](#quick-summary)
- [Sources and further reading](#sources-and-further-reading)

The order of steps follows [Step by Step](00-step-by-step.md). The coordinates of every place, road, river and border are in [worked-example-layout.json](images/worked-example-layout.json) (canvas 1000 × 800 units, 2 units = 1 km).

---

## The kingdom at a glance

> **Rule of thumb:** Draw the terrain first and decide the date. Every number below depends on the land and on the year.

**Daravel** is a centralised feudal kingdom in the year **1300**, the crowded peak before the Great Famine and the Black Death (see [Change over time](02-population-and-sizes.md#change-over-time-growth-famine-and-plague)).

| Feature | Daravel |
|---|---|
| Area | About 116,500 km² (45,000 sq mi): about 390 km (240 mi) east to west and 380 km (235 mi) north to south. England is 130,000 km². |
| Coast | East and south, on the Grey Sea |
| Estuary | The Ambre estuary, 83 km (52 mi) from the open sea to its head |
| Main river | The Ambre, navigable for river boats 158 km (98 mi) above the estuary; its tributary the Lisk joins it at Liskmeet |
| Mountains | The Fells along the whole west border. The crest is the border. One cart pass (the Wyndgap) and one mule path (the Carrow Gap). |
| Forest | The Harnwood, about 11,000 km² in the north |
| Marsh | The Holm Fens north of the estuary, the Saltings salt marsh on its south shore, small levels at the Wend mouth |
| Other land | The Whitridge (a limestone ridge that the Ambre cuts at Ridgegate), Brackenheath (sandy heath), the Wend Downs and the Brim Wolds (chalk and limestone hills) |
| Neighbours | Thelland to the north (hostile), Morvane to the west across the Fells (at peace) |

> **Map tip:** Before any dot goes down, mark the navigable stretch of each river, the tidal limit, the fords, the pass and the land types. This is step 1 of the method in [Where Settlements Are Built](01-settlement-placement.md#placing-settlements-on-your-map-a-method).

---

## Step 1: Land and population

**Method:** measure each land type, multiply by a density from [Population density](02-population-and-sizes.md#by-type-of-land), and add up ([calculator, steps 1–3](02-population-and-sizes.md#step-by-step-population-calculator)).

| Land type | Area | Density used (range) | People |
|---|---|---|---|
| Fertile lowland (Ambre vale, coastal plains) | 44,500 km² (17,200 sq mi) | 35 per km² (30–40) | 1,557,500 |
| Mixed farmland and rolling hills (downs, wolds, foothills) | 33,500 km² (12,900 sq mi) | 20 (15–25) | 670,000 |
| Heath and poor sandy land | 3,000 km² (1,200 sq mi) | 10 (7–15) | 30,000 |
| Uplands and mountains (the Fells) | 20,500 km² (7,900 sq mi) | 5 (2–10) | 102,500 |
| Forest (Harnwood, Kingswood) | 11,500 km² (4,400 sq mi) | 4 (1–5) | 46,000 |
| Marsh and fen | 3,500 km² (1,400 sq mi) | 5 (2–5) | 17,500 |
| **Total** | **116,500 km² (45,000 sq mi)** | **~21 per km² (54 per sq mi)** | **~2.4 million (range 1.9–2.9 million)** |

**Checks:**

- A realm the size of England should have 2–5 million people ([Realm populations](02-population-and-sizes.md#realm-populations-and-areas)). Daravel, at 2.4 million, is less crowded than England in 1290 (~36 per km²) and close to the European average of about 20 per km² c. 1300. ✔
- **Food:** at about 1 ha (2.5 acres) of ploughland per person, Daravel needs about 24,000 km² of arable, under a third of its 78,000 km² of lowland and mixed land. At 2–3 ha (5–7 acres) of all land per person it needs 48,500–73,000 km² ([Carrying capacity](02-population-and-sizes.md#carrying-capacity-how-much-land-feeds-people)). It has room to grow. ✔

> **Map tip:** Shade the map lightly in these six land types before you place anything. The shading is your population map: crowded vale, ordinary hills, thin Fells, nearly empty forest and fen.

---

## Step 2: Cities, towns and villages

**Method:** choose an urban profile and split the people into tiers, then divide by a typical size ([calculator, steps 4–5](02-population-and-sizes.md#step-by-step-population-calculator)). Daravel uses the **average** profile (England, France and Germany c. 1300).

| Tier | Share | People | Typical size | Number of places |
|---|---|---|---|---|
| Cities of 10,000+ | ~3% | ~73,000 | sized by rank (below) | 4 |
| Towns of 2,000–10,000 | ~5% | ~121,000 | ÷ 3,000–4,000 | 30–40 → **38** |
| Small market towns | ~6% | ~145,000 | ÷ ~800 | **~180** |
| Villages, hamlets, farms | ~86% | ~2,084,000 | ÷ 250 (lowland) or 100–150 (hills) | **~7,700 villages** |

Quick-ratio check for an average realm, per million people: 1–2 cities, 12–18 towns, 60–90 market towns, 2,500–3,500 villages. For 2.4 million that is 2–5, 29–44, 145–220 and 6,000–8,500. Daravel fits every row. ✔

### The top of the ladder

The capital of a strong kingdom holds about 1–2% of its people and is 3–7 times bigger than the second city ([Rank-size rule](02-population-and-sizes.md#the-rank-size-rule-and-primate-cities)). The rank-size rule predicts the 2nd place at ½ of the largest, the 3rd at ⅓, and so on.

| Rank | Place | People | Rank-size prediction | Why it is here |
|---|---|---|---|---|
| 1 | **Hallowbridge** (capital) | 40,000 (1.65% of the realm) | — | Lowest bridge on the Ambre, at the tidal limit |
| 2 | Liskmeet | 12,000 | 20,000 | Confluence of the Ambre and Lisk; old imperial city |
| 3 | Wendmouth | 11,000 | 13,300 | Harbour at the mouth of the Wend |
| 4 | Brimhaven | 10,000 | 10,000 | Wool port at the mouth of the Brim |
| 5 | Tenterford | 8,000 | 8,000 | Cloth town at the mouth of a fast hill stream |
| 6 | Ridgegate | 7,000 | 6,700 | Gap town and second bridge where the Ambre cuts the Whitridge |
| 7 | Norburgh | 6,500 | 5,700 | Rear fortress and muster town of the North March |
| 8 | Wyndfoot | 5,000 | 5,000 | Pass town below the Wyndgap |
| 9 | Holmstow | 4,500 | 4,400 | Abbey town and shrine on a fen island |
| 10–13 | Saltwich 4,000 (brine springs), Hawkridge 4,000 (western march fortress), Cheapford 3,800 (ford, head of navigation, wool fair), Silverhope 3,500 (silver mines) | | | |

Hallowbridge is 3.3 times the size of Liskmeet: a primate capital, like London c. 1377 at 3–4 times York. Below it, the sizes follow the rule closely. ✔

**The other 29 towns** (2,000–3,600 each, 74,700 people in all):

| Region | Towns |
|---|---|
| Crownlands | Kingsmoat 3,000; Ashenden 2,800; Ambremouth 2,400 |
| Duchy of Lisk | Forgeham 2,800; Brockhurst 2,700; Wythmoor 2,600; Harnbury 2,500; Sedgeworth 2,400; Kingsferry 2,200 |
| Duchy of the Fells | Carrowdale 2,400; Leadgill 2,200; Fellstead 2,000 |
| North March | Skelbridge 2,800; Coldhaven 2,200; Scarwick 2,100; Wolfhope 2,000 |
| Earldom of Brim | Woldby 3,300; Gullhaven 3,000; Eastwold 2,800; Stowford 2,500; Brimstead 2,300 |
| Duchy of Wend | Wendbury 3,600; Merrow 3,100; Meremouth 2,800; Abbotsmere 2,800; Downholme 2,700; Bramling 2,400; Seacombe 2,300; Saltcove 2,000 |

### Villages

Rural people per zone are the zone's total minus the townspeople living there. Village sizes follow [step 5 of the calculator](02-population-and-sizes.md#step-by-step-population-calculator); spacing uses the hexagon rule from [How far apart](01-settlement-placement.md#how-far-apart-the-numbers) (each place "owns" 0.87 × spacing²).

| Zone | Rural people | Share in villages | Typical village | Villages | Land per village | Spacing |
|---|---|---|---|---|---|---|
| Fertile lowland | ~1,300,000 | 90% | 250 | ~4,700 | ~9.5 km² | ~3.3 km (2 mi) |
| Mixed farmland | ~613,000 | 75% | 200 | ~2,300 | ~14.6 km² | ~4.1 km (2.5 mi) |
| Heath | ~29,000 | 70% | 150 | ~140 | ~21 km² | ~4.9 km (3 mi) |
| Fells | ~85,000 | 50% | 125 | ~340 | ~60 km² | ~8.3 km (5 mi) |
| Forest | ~44,000 | 50% | 125 | ~180 | ~64 km² | ~8.6 km (5 mi) |
| Marsh | ~13,000 | 60% | 125 | ~60 | ~58 km² | ~8 km (5 mi) |
| **Total** | **~2,084,000** | **~83%** | | **~7,700** | | |

The other ~355,000 country people live in hamlets (10–75 people) and farmsteads (5–15), mostly in the Fells, the forest and the fen edge.

**Spacing checks** ([Patterns and spacing](01-settlement-placement.md#patterns-and-spacing)):

- Lowland villages ~3.3 km apart (rule: 1.5–4 km, 1–2.5 mi). Fell parishes ~60 km² (rule: 50–100+ km²). ✔
- 222 market centres (180 market towns, 38 towns, 4 cities) give one per ~525 km², about 25 km (15 mi) apart. Add 100–200 villages with a weekly market (the same ratio as the mini-example in chapter 02), most of them in the vale, and lowland markets end up 14–16 km (9–10 mi) apart. Nobody walks more than 6–10 km to market. ✔
- 8 places of 5,000+ are about 130 km (80 mi) apart, like Britain. 4 cities of 10,000+ are about 180 km (115 mi) apart, between France (130–170 km) and Britain (260–400 km). ✔
- All four cities sit on navigable water or the coast. Tenterford, at 8,000, is inland, which is allowed under 10,000 ([the "why is it here?" test](01-settlement-placement.md#the-why-is-it-here-test)). ✔

> **Later era (1500s+):** By 1600 draw the capital 2–4 times bigger (80,000–160,000) with suburbs far outside its walls, and grow Brimhaven or Wendmouth fastest if ocean trade arrives ([Population and bigger cities](09-later-era-1500-1650.md#population-and-bigger-cities)).

> **Map tip:** On the kingdom map, draw the capital, the 3 cities, all 38 towns and only 30–40 of the ~180 market towns. Show villages as texture in the vale, not as 7,700 dots.

---

## Step 3: The capital

**Hallowbridge** stands at the lowest bridging point of the Ambre, at the tidal limit, 83 km (52 mi) up the estuary. On tidal coasts big ports sat 50–120 km (30–75 mi) inland ([Notes on site types](01-settlement-placement.md#notes-on-the-most-important-types)). It meets all five needs from [What makes a capital](03-capitals-and-borders.md#what-makes-a-capital):

| Need | Hallowbridge |
|---|---|
| Rich core region | The lower Ambre vale: about 10,000 km² of lowland in the Crownlands (the royal domain) |
| River or sea access | Sea ships to its quays; river boats 158 km (98 mi) up the Ambre. A city of 40,000 needs an overland hinterland of roughly 40–55 km (25–35 mi), so water supply is essential ([Feeding towns](02-population-and-sizes.md#feeding-towns-the-hinterland)). |
| Defensible core | The White Keep on a low bluff on the north bank, with the river in front |
| Loyalty | The Crownlands are the dynasty's home lands |
| Legitimacy | Royal burial abbey at Westhallow; coronation in the old city of Liskmeet |

It is **not central**: it lies in the east, 322 km (200 mi) in a straight line from the far north-west corner, like Paris or London ([Common mistakes, no. 12](11-common-mistakes.md#12-the-capital-at-the-exact-centre)). By road that corner is about 350–400 km away, 4–8 days for a royal messenger (50–90 km a day): a normal kingdom ([How big can a realm be](03-capitals-and-borders.md#distance-from-the-capital-and-what-it-means)).

**The royal landscape** ([Around the capital](03-capitals-and-borders.md#around-the-capital-the-royal-landscape)):

| Feature | Place | Distance | Rule |
|---|---|---|---|
| Palace quarter and royal burial abbey | Westhallow | 4 km (2.5 mi) upstream | Like Westminster, ~3 km from London; burial church 0–20 km |
| Royal residences | Elmhurst manor, Redwater Castle, Kingsmoat castle, Kingswood lodge | 14, 31, 37 and 43 km (9, 19, 23, 27 mi) | 3–6 residences within ~60 km |
| Royal forest | Kingswood Chase | 30–55 km (19–34 mi) | 10–100 km |
| Coronation city | Liskmeet cathedral | 119 km (74 mi) | 50–150 km; Reims is ~130 km from Paris |

> **Map tip:** Draw Hallowbridge as two linked parts: the walled merchant city with the White Keep at its upstream corner, and the palace and abbey of Westhallow a little upstream. Put the port quays below the bridge, never above it ([Bridges](05-trade-routes-and-transport.md#crossing-rivers-bridges-fords-and-ferries)).

---

## Step 4: Duchies, counties and the North March

**Method:** divide the realm into 4–8 great fiefs, then into counties of 50–70 km (30–45 mi) across, each with a seat near its middle, and add 1–3 special zones ([Political units](03-capitals-and-borders.md#political-units-and-their-sizes)). People below come from each region's land types × the densities of step 1.

| Region | Area | People | Counties | Seat | Character |
|---|---|---|---|---|---|
| Crownlands (royal domain) | 14,000 km² (5,400 sq mi) | ~400,000 | 5 | Hallowbridge | Lower Ambre vale |
| Duchy of Lisk | 17,600 km² (6,800 sq mi) | ~420,000 | 6 | Liskmeet | Middle Ambre, Lisk valley, south Harnwood |
| Duchy of Wend | 24,100 km² (9,300 sq mi) | ~650,000 | 7 | Wendmouth | South coast, downs, heath |
| Earldom of Brim | 9,400 km² (3,600 sq mi) | ~240,000 | 3 | Brimhaven | Wolds and north-east coast; small but rich |
| Duchy of the Fells | 25,100 km² (9,700 sq mi) | ~330,000 | 5 | Wyndfoot | Mountains, pass, mines, cloth valley |
| North March | 23,900 km² (9,200 sq mi) | ~365,000 | 6 | Norburgh | Frontier facing Thelland |
| Liberty of Holmstow | 2,600 km² (1,000 sq mi) | ~15,000 | 1 | Holmstow | The abbot's church territory in the fens |
| **Kingdom** | **116,500 km² (45,000 sq mi)** | **~2.4 million** | **33** | | |

**Checks:** the duchies are 9,400–25,100 km² (rule: 10,000–50,000; Flanders was ~10,000 km² and as powerful as a duchy). The 33 counties average 3,500 km² (1,370 sq mi), about 59 km (37 mi) across, with ~73,000 people each (England averaged ~3,300 km² and ~120,000; the guide suggests 30–40 counties for an England-sized realm). ✔ The North March has ~15 people per km² against 27–29 in the Crownlands and Wend: emptier, as a march should be ([Marches](03-capitals-and-borders.md#marches-militarised-border-provinces)).

**Smaller units:** about 750 hundreds (district courts) of ~155 km² each, each meeting at an open-air moot site and holding 10–11 parishes ([Local administration](06-villages-and-countryside.md#local-administration-parish-manor-hundred)); roughly 150–200 baronies, each with a castle at its head manor (*caput*); and one to three manors per village.

**Borders** ([Borders and frontiers](03-capitals-and-borders.md#borders-and-frontiers)):

- **West:** the crest of the Fells (the watershed). At the Wyndgap pass, Daravel's Wyndgap Castle and Morvane's castle face each other about 17 km (11 mi) apart.
- **North:** hill crests and the northern Harnwood in the west, then the River Skel to the sea. A hatched **frontier band 30 km (19 mi) deep** runs along it (the guide's band is 10–50 km).
- **Oddities:** the **Debatable Land**, a disputed strip 16 × 6 km (10 × 4 mi) on the north border (the size of the real one), and the Liberty of Holmstow.
- **Inside:** duchy borders follow the Whitridge, the Fell foothills, the fen edge and forest edges, never straight lines ([Common mistakes, no. 13](11-common-mistakes.md#13-straight-borders-without-a-reason)).

> **Map tip:** Draw the realm border thick, duchy borders as medium dashes and county borders not at all at kingdom scale. Label the North March and the Debatable Land by name, and give the Liberty its own colour.

---

## Step 5: Castles and fortifications

**Method:** apply the densities per 1,000 km² from [How many to draw](04-military-sites.md#how-many-to-draw) zone by zone. About one-third of all castle sites are in use at once.

| Zone | Area | Rate used | Sites ever built | Active c. 1300 | Gap between active castles |
|---|---|---|---|---|---|
| Peaceful core (Crownlands, Lisk, Wend, Brim, Liberty) | 68,000 km² | 6 sites, 2 active per 1,000 km² (rule: 4–8 and 1–3) | ~410 | ~135 | ~24 km (15 mi) |
| Duchy of the Fells (mostly mountain) | 25,100 km² | 4 sites, 1 active (low end of the core rule) | ~100 | ~25 | ~34 km (21 mi) |
| North March | 23,900 km² | One site per 110–130 km², like the Anglo-Scottish border | ~200 | ~65 | ~20 km (12 mi) |
| **Total** | 116,500 km² | | **~710** | **~225** | |

Working castles in the core are 20–30 km (12–19 mi) apart, as the guide expects for a peaceful core ([Borderlands](04-military-sites.md#borderlands-and-conquered-land)). Daravel has about 1.9 active castles per 1,000 km² against about 4 in England and Wales, because it has fewer people and no Welsh-style march of tiny lordships. A gaming rule of one castle per 50,000 people would give only ~48, far too few ([Gaming rules](02-population-and-sizes.md#gaming-rules-of-thumb-vs-history)).

**What the ~225 active castles are** ([Types of fortification](04-military-sites.md#types-of-fortification)):

| Type | Number | Where and why (its one-word job) |
|---|---|---|
| Royal citadel: great stone tower and curtain wall | 1 | White Keep, Hallowbridge: *town*, *bridge*, royal armoury |
| County-town castles: stone keeps, shell keeps on old mottes, curtain walls | 31 | One at the edge of every county town except the capital and Holmstow. Norburgh, Hawkridge and Skelbridge are rebuilt as concentric castles. |
| Pass fortress (concentric) | 1 | Wyndgap Castle: *pass* |
| Forward line on the north border | 10 | Small castles and towers at fords and passes, 29–43 km (18–27 mi) apart, about a day's march |
| Estuary castle | 1 | Ness Castle at the estuary mouth: *harbour* |
| Royal residence castle | 1 | Redwater Castle |
| Baronial castles and fortified manor houses | ~180 | At the head manors of baronies: *estate* |

- **Garrisons:** 5–20 men at an ordinary castle and 30–60 at the 14 frontier castles: about 1,500–5,000 men in peacetime, under 0.2% of the people ([Garrisons and armies](04-military-sites.md#garrisons-and-armies)).
- **Field army:** 0.2–0.5% of 2.4 million = about **5,000–12,000** soldiers. An all-out 1% (~24,000) lasts only weeks.
- **Behind the front:** muster towns at Norburgh (north) and Wyndfoot (west), the main armoury in the White Keep, and the fleet at Brimhaven ([Military geography](04-military-sites.md#military-geography-and-logistics)).
- **Walls:** the capital, the 3 cities and the frontier towns (Ridgegate, Norburgh, Hawkridge, Wyndfoot, Skelbridge) have stone walls; Tenterford and Saltwich have a ditch and gates; the rest are open ([Common mistakes, no. 25](11-common-mistakes.md#25-every-town-walled)).
- **Beacons:** 10 beacons about 16 km (10 mi) apart run from Skelbridge to the capital (rule: 5–20 km in hilly country). A fire warning arrives within the hour; a rider takes 2–3½ days ([Watchtowers and beacons](04-military-sites.md#watchtowers-beacons-and-coastal-warning)).
- **Ruins:** the other ~485 sites are abandoned mottes and ringworks from the conquest era.

> **Later era (1500s+):** Put bastioned star forts at Skelbridge and Norburgh, a citadel at Hallowbridge and low gun forts at the estuary mouth. Turn most inland castles into ruins, palaces or manor houses ([Gunpowder and the new fortifications](09-later-era-1500-1650.md#gunpowder-and-the-new-fortifications)).

> **Map tip:** On the kingdom map draw the 33 county castles, the 15 frontier and royal castles and about one major baronial castle per 2,000–3,000 km² (about 25), plus a few grey ruined mottes. Leave the remaining ~150 baronial castles for local maps.

---

## Step 6: Roads, rivers and the sea

**Water first** ([Rivers as roads](05-trade-routes-and-transport.md#rivers-as-roads)):

| Waterway | Stretch | Length | Traffic |
|---|---|---|---|
| Ambre estuary | Mouth to Hallowbridge | 83 km (52 mi) | Sea ships (cogs) |
| Ambre | Hallowbridge – Ridgegate – Liskmeet – Cheapford | 158 km (98 mi) | River boats; towpaths; Cheapford is the head of navigation |
| Lisk | Liskmeet to Forgeham | ~65 km (40 mi) | River boats carrying iron and timber |
| Brim | Brimhaven to Norburgh | ~100 km (60 mi) | Small boats: they supply the march fortress |
| Wend | Wendmouth to Wendbury | ~60 km (37 mi) | Small boats |

**Main roads** (royal highways; [Roads](05-trade-routes-and-transport.md#roads)):

| Road | Route | Length |
|---|---|---|
| The King's Way | Hallowbridge – Leyford – Ridgegate – Liskmeet – Cheapford – Wyndfoot – Wyndgap pass | 285 km (177 mi) |
| The North Road | Hallowbridge – Eastwold – Norburgh – Skelbridge | 170 km (106 mi) |
| The South Road | Hallowbridge – Kingsmoat – Bramling – Wendmouth | 173 km (107 mi) |
| Old Street (an old imperial road) | Liskmeet – Wythmoor – Abbotsmere – Wendmouth, dead straight | 167 km (104 mi) |
| The Brim Road | Eastwold – Woldby – Brimhaven | 109 km (68 mi) |

About 900 km of royal highway needs an inn or inn town every 15–30 km (10–19 mi): **30–60 stopping places**, most of them in existing towns and villages ([Inns](05-trade-routes-and-transport.md#inns-hospices-and-caravanserais)). Regional roads (the Downs Road, the Fells Road, the Harn Road, the Salt Roads, the Pilgrims' Way) link every market town to its neighbours.

**Crossings, passes and tolls:**

- **The Ambre** has only 4 fixed bridges: Hallowbridge, Ridgegate (71 km upstream), Liskmeet (51 km further) and small Wyndfoot (95 km further). Between them are the fords at Cheapford and Ambrefold and ferries at Kingsferry and Thornwick ([Crossing rivers](05-trade-routes-and-transport.md#crossing-rivers-bridges-fords-and-ferries)).
- **The Wyndgap** is a low cart pass with a hospice near the summit, a toll, Wyndgap Castle and a chain of villages up the valley to Wyndfoot. The Carrow Gap is a summer mule path with no towns ([Mountain passes](05-trade-routes-and-transport.md#mountain-passes)).
- **Tolls** at the Hallow bridge (pontage) and port customs, the Ridgegate bridge, the Liskmeet bridges, the Wyndgap and the Skel bridge into Thelland ([Tolls](05-trade-routes-and-transport.md#tolls-and-customs)).

**Ports and the sea:** Hallowbridge (main port, below the bridge), Ambremouth (outport and pilots, with the only lighthouse, on Ambre Ness), Brimhaven (port and royal shipyard), Wendmouth, Gullhaven, Meremouth, Coldhaven, Seacombe and Saltcove. Sea lanes hug the coast north to Thelland and south-west to Morvane, with one open-sea crossing east ([The sea](05-trade-routes-and-transport.md#the-sea-ships-harbours-and-sea-lanes)).

**Travel times** at the guide's [speeds per day](05-trade-routes-and-transport.md#speed-per-day): walker 25–35 km, ox cart 15–25 km, royal messenger 50–90 km, river boat 40–100 km downstream and 10–20 km upstream, sailing ship 40–100 km.

| From Hallowbridge to | Distance | On foot | Ox cart | Messenger | By water |
|---|---|---|---|---|---|
| Ridgegate | 70 km (44 mi) | 2–3 days | 3–5 days | 1 day | — |
| Liskmeet | 120 km (75 mi) | 3½–5 days | 5–8 days | 1½–2½ days | Downstream 1½–3 days; upstream 6–12 days |
| Norburgh | 127 km (79 mi) | 4–5 days | 5–9 days | 1½–2½ days | — |
| Brimhaven | 167 km (104 mi) road; 182 km (113 mi) sea | 5–7 days | 7–11 days | 2–3½ days | Sailing ship 2–5 days |
| Skelbridge (border) | 170 km (106 mi) | 5–7 days | 7–11 days | 2–3½ days | An army with baggage: 9–13 days |
| Wendmouth | 173 km (107 mi) road; 373 km (232 mi) sea | 5–7 days | 7–12 days | 2–3½ days | Sailing ship 4–9 days |
| Wyndfoot | 218 km (135 mi) | 6–9 days | 9–15 days | 2½–4½ days | — |
| Wyndgap pass | 285 km (177 mi) | 8–11 days | 11–19 days | 3–6 days | — |

> **Map tip:** Draw the navigable Ambre thicker up to Cheapford, the 4 bridges as bars, the fords as dashes and the ferries as small boats. Write the travel days on the long roads ("Norburgh 4 days"). Every road must end somewhere: a town, a port, a pass, a mine or a shrine ([Drawing the route network](05-trade-routes-and-transport.md#drawing-the-route-network)).

---

## Step 7: The Church

**Method:** use the English densities and rules in [Religious, Cultural, Legal and Ancient Sites](08-religious-cultural-and-ancient-sites.md#the-religious-map-at-a-glance).

| Feature | Daravel | Rule from chapter 08 |
|---|---|---|
| Parish churches | ~8,000 (7,700 villages plus ~300 in towns and cities; one per ~14.5 km², 5.6 sq mi) | ~73 per 1,000 km² would give ~8,500 |
| Dioceses (cathedrals) | 13, about 9,000 km² (3,500 sq mi) each | English style: one per 5,000–10,000 km² |
| Archbishop | 1, at Liskmeet: the oldest city, not the capital | Oldest or richest city |
| University | 1, at Liskmeet | 1 per 3–4 million people c. 1300 |
| Religious houses | ~730 (one per ~160 km²) | about 1 per 150 km² |
| Hospitals open c. 1300 | ~280: one per market town, 2–5 per walled town | Gates, bridges, main roads |
| Leper houses | ~50: one outside each town of 2,000+, one on each main road out of the capital and cities | 1–2 km outside the gate |

**Cathedral cities:** Liskmeet (archbishop), Hallowbridge, Wendmouth, Brimhaven, Ridgegate, Norburgh, Wyndfoot, Holmstow (a monastic cathedral, like Ely), Hawkridge, Wendbury, Merrow, Carrowdale and Woldby. In an English-style realm a cathedral marks a main town, so 12 of the 13 are cities or larger towns ([Dioceses](08-religious-cultural-and-ancient-sites.md#dioceses-cathedrals-and-archbishops)).

**Religious houses by order** (England's numbers scaled to Daravel's area; [Monasteries](08-religious-cultural-and-ancient-sites.md#monasteries-friaries-and-military-orders)):

| Order | Number | Where |
|---|---|---|
| Benedictine and Cluniac monks | ~165 | In or beside old towns: Westhallow (royal), Holmstow (shrine), Abbotsmere (a monastery town) |
| Cistercian monks | ~60 | Empty, well-watered valleys: Harnvale, Greywater, Coldwater, Stillwater, Mirefield. Harnvale cleared a village to get its "desert". |
| Carthusians | 1 | Sallowhope, deep in the Fells. England had only two charterhouses by 1300 (Witham 1178, Hinton 1227); seven more came later. |
| Augustinian and other canons | ~270 | At town edges, hospitals and castles |
| Nunneries | ~130 | Quiet rural sites |
| Friaries | ~75 | Inside towns: 6 in the capital, 3 in each city, 2 in each large town, 1–2 in most county towns |
| Military-order commanderies | ~25 | One farm estate per inland county (Temple Ambre is shown) |

Each big abbey gets 5–40 granges (outlying farms), most within about 25 km (15 mi), a day's walk for the lay brothers.

**The pilgrimage:** the shrine of the invented national saint, St Aldwen, at **Holmstow Abbey** on its fen island. The Pilgrims' Way runs 87 km (54 mi) from the capital round the fen edge to the pilgrim town of Stowford, then by causeway (or by boat down the Holm Lode) to the shrine. At about 20 km (12 mi) per pilgrim stage that is 4–5 stages, with a hospice at Stowford and a leper house on the last stretch ([Pilgrimage](08-religious-cultural-and-ancient-sites.md#pilgrimage-shrines-routes-and-hostels)).

> **Map tip:** At kingdom scale, show only the 13 cathedrals (with a bigger symbol for Liskmeet), the great abbeys, the shrine and the university. Save the 8,000 parish churches and the friaries for local and town maps.

---

## Step 8: Industry and special towns

**Method:** for every industry, find the resource, the fuel and the way out ([The basic rules](07-industry-and-resources.md#the-basic-rules-what-pulls-industry-to-a-place)). The guide suggests 1–3 mining districts, 1–3 salt sources, one cloth region, one or two fair towns and several ports per kingdom ([Special town types](07-industry-and-resources.md#special-town-types-and-how-to-spot-them)).

| Industry | Resource, fuel and way out | Special place | Size |
|---|---|---|---|
| Silver and lead | Veins in the Fells; wood and fast streams; road down the Hope Water to Wyndfoot | Silverhope (royal mint), Leadgill, Orsdale: 24–28 km (15–17 mi) apart | 3,500; 2,200; ~900. A mining town usually has 1,000–5,000 ([Mining](07-industry-and-resources.md#mining-and-metals)). |
| Brine salt | Brine springs; fuel by water (Harnwood timber, fen peat); three Salt Roads, one to a landing on the estuary 26 km (16 mi) away | Saltwich | 4,000 ([Salt](07-industry-and-resources.md#salt)) |
| Sea salt | Salterns (boiling sea water) on the Saltings; small output, as in the north | Hamlets on the marsh edge | — |
| Building stone and lime | Limestone of the Whitridge right beside the Ambre | Chalkhythe quarries and kilns | Hamlet ([Stone, clay and lime](07-industry-and-resources.md#stone-clay-and-lime)) |
| Iron, charcoal, glass | Ore, coppiced woods and streams of the Harnwood; iron goes down the navigable Lisk | Forgeham, forge ponds, a glasshouse | 2,800 ([Forest industries](07-industry-and-resources.md#forest-industries)) |
| Wool and cloth | Sheep on the Fells, Wend Downs and Brim Wolds; fulling mills on the fast Tenter Water | Tenterford (cloth town); Cheapford (wool fair); Brimhaven (wool export) | 8,000; 3,800; 10,000 ([Textiles](07-industry-and-resources.md#textiles)) |
| Fish | Autumn herring off the north-east coast; salt from Saltwich | Gullhaven herring fair; fishing hamlets a few km apart on sheltered coasts | 3,000 ([Fishing](07-industry-and-resources.md#fishing)) |
| Ships | Harnwood oak via the Brim; tar imported | Royal shipyard at Brimhaven, facing Thelland | Part of the city |
| Wine and brick | South-facing slopes at Abbotsmere (small monastic vineyards); estuary clay | Abbotsmere; brickfields outside Hallowbridge | — |

Every region still grows its own grain first. The mining towns import food from the vale through Wyndfoot ([Common mistakes, no. 26](11-common-mistakes.md#26-single-product-economies)).

> **Map tip:** Give each special place a visible reason: crossed hammers at Silverhope, salt pans on the Saltings, a quarry notch at Chalkhythe, a fair meadow at Cheapford, tenter frames at Tenterford. Label the three roads out of Saltwich "Salt Road".

---

## Step 9: Ruins and older layers

> **Rule of thumb:** Every medieval landscape stands on older ones. Old things survive far from towns; near towns their stone is carted away ([Ancient and ruined layers](08-religious-cultural-and-ancient-sites.md#ancient-and-ruined-layers)).

| Layer | In Daravel | Real model |
|---|---|---|
| Roads of an older empire | Old Street (Liskmeet–Wendmouth) and Fell Street (Liskmeet–Hawkridge): straight, still used | Roman roads such as Watling Street |
| Old towns and forts | Liskmeet and Hawkridge stand on old imperial sites. **Wendchester**, a walled town of the old empire, is a ruin in the fields about 10 km (6 mi) from Wendmouth. | Wroxeter, abandoned, 8 km from Shrewsbury ([Reuse of ancient sites](01-settlement-placement.md#reuse-of-ancient-and-roman-sites)) |
| Hillforts | Hundreds on the downs, wolds and hill edges; show 6 on the kingdom map. **Old Harrow**, above Wyndfoot, has a ruined church: the bishop moved down to the river town. | Old Sarum and Salisbury |
| Barrows and stones | Barrow groups along the Wend Downs ridge; the Grey Wives stone circle in the Fells | Chalk downs; Avebury |
| Old border | The Thelling Dyke, an earth bank 25 km (16 mi) inside today's border | Offa's Dyke |
| Abandoned castles | ~485 grassy mottes and ringworks; show about 10 | One-third of English castle sites in use at once |
| Deserted villages | Few in 1300: Old Harnvale (cleared by the Cistercians), Lostwick (cleared for the royal forest), Skelby (burnt in border raids) | Most English desertions came after 1350 ([Deserted villages](01-settlement-placement.md#deserted-medieval-villages)) |

> **Map tip:** Draw ruins grey or dotted. If you redate the map to 1450, add dozens of "lost village" symbols in the clay vale, shrink the towns inside their walls and turn hill fields back into pasture.

---

## Step 10: Zoom in on the Leyford area

The local map covers 10 × 10 km (6 × 6 mi), 100 km² (39 sq mi), of rich vale on the south bank of the Ambre, 38 km (24 mi) west of the capital on the King's Way. At 35 people per km² it should hold about 3,500 people. It is centred on the market town of **Leyford**, where the King's Way crosses the Ley Brook.

**Features** compared with the English averages per 100 km² in [How many features](06-villages-and-countryside.md#how-many-features-england-c-1300-averages):

| Feature | Leyford area | English average per 100 km² |
|---|---|---|
| Market town | 1 (Leyford) | 1–2 market places |
| Villages with a parish church | 9, plus Leyford's church | ~7 (this is the richest part of the vale) |
| Hamlets | 5 | 0–5 in open-field lowland |
| Mills | 11 (10 watermills, 1 windmill) | ~8–11 |
| Manors | 9 lay manors and 1 monastic grange; 5 of them moated | ~4–5 moated sites |
| Deer parks | 2 (Stanmere Park about 1.1 km across, Ashlade Park about 0.8 km) | ~2–3 |
| Fishponds | 2 groups (a chain of 4 below Stanmere Hall; 2 at the grange) | at least 1–2 |
| Hundred meeting place | 1: Ley Low, a mound beside the King's Way | ~0.5–0.7 |
| Other | St John's hospital at Leyford bridge, Gallows Hill, two wayside crosses, a rabbit warren on the heath | — |

**Households** (4.5–5 people each; [Village territory](06-villages-and-countryside.md#sizes-territory-and-walking-distances)):

| Place | Households | People | Notes |
|---|---|---|---|
| Leyford (market town) | 160 | 720–800 | Market place and cross, 2 inns, town mill, hospital, bridge |
| Stanmere | 75 | 340–375 | Moated hall, dovecote, fishponds, deer park |
| Thornwick | 70 | 315–350 | Two manors; ferry over the Ambre |
| Kettlebury | 60 | 270–300 | Moated Kettlebury Court |
| Hollowell | 55 | 250–275 | Moated hall |
| Ashlade | 50 | 225–250 | Moated manor, small park |
| Crossby | 50 | 225–250 | Windmill, crossroads cross |
| Oxlade | 45 | 200–225 | Cistercian grange with a great barn nearby |
| Upper Ley | 40 | 180–200 | Heath-edge commons |
| Brackenhurst | 35 | 160–175 | Heath-edge commons |
| 5 hamlets | 40 | 180–200 | Mill End, Fennick End, Heathcot, Woodside, Coldhams |
| Mills, grange, lodges | 12 | 55–60 | Millers, warrener, park keepers, lay brothers |
| **Total** | **692** | **~3,100–3,450 (31–35 per km²)** | |

**How it is laid out:**

- **Spacing:** villages are 1.5–3.4 km (1–2 mi) apart (rule: 1.5–4 km). The farthest village, Brackenhurst, is 5.5 km (3.4 mi) from Leyford's market, an easy walk there and back in a day.
- **Rings of land use** ([Rings of land use](06-villages-and-countryside.md#rings-of-land-use-around-a-village)): tofts and crofts by the houses; two or three great open fields within about 1.2–1.7 km (0.7–1 mi) of each village; meadow on the Ambre flood plain and in ribbons along the brooks; four coppice woods at the parish edges; Ley Heath (common pasture and the warren) on the sandy ground in the south.
- **Water and mills:** the Ley Brook, the Hollow Beck and the Ash Brook run north into the Ambre. The Ley's four mills are 1.6–2.8 km apart. The navigable Ambre has no mill weir. The village on the rise with no stream gets the windmill ([Mills](06-villages-and-countryside.md#mills-and-water-management)).
- **Roads:** the King's Way crosses east to west, cleared 200 ft (61 m) on each side under the Statute of Winchester; lanes run from every village to Leyford like spokes; drove tracks lead to the heath; a lane runs down to the Thornwick ferry.
- **Villages** sit on terraces above the flood plain, not in it, each with its church beside the manor house ([Village forms](06-villages-and-countryside.md#village-forms-and-layouts)).

> **Map tip:** At this scale every square kilometre has an owner and a name. Draw parish boundaries as dash-dot lines along brooks and wood edges, put a mill on every village's stream, and keep empty white space only for the heath, which you label.

---

## Step 11: A fantasy variant

Apply the real rules first, then change one input and follow the chain ([The method](10-fantasy-variants.md#the-method-change-the-inputs-not-the-rules)). Here are two changes.

**A. Monsters in the Harnwood** ([Dangerous wilderness](10-fantasy-variants.md#dangerous-wilderness-and-monsters)):

| Feature | Realistic Daravel | With monsters |
|---|---|---|
| Forest people | ~46,000 in ~180 open villages and many hamlets | Fewer, packed into 30–50 walled villages of 300–1,000 at the forest edge; the interior is empty |
| Refuges | None needed | Refuge forts a day's walk (24–32 km, 15–20 mi) apart round the forest's ~390 km (240 mi) edge: about 12–16 forts |
| Forest roads | The Lisk Road (154 km) and Fell Street | Cleared about 60 m (200 ft) each side, fortified stops every 15–30 km, patrols |
| Rangers | — | Lodges at the forest edge, fords and road entries, 15–30 km (10–20 mi) apart |
| Iron and glass | Forgeham smelts with Harnwood charcoal | Charcoal burners need guards; iron costs more or is imported |

**B. Dwarves under the Fells** ([Dwarves](10-fantasy-variants.md#dwarves-mountain-holds-and-gate-towns)):

- A hold of about 10,000 dwarves under Silverhope would need farmland within about 55 km (35 mi) on marginal land. The Fells cannot provide it, so the hold must buy food.
- At 200–250 kg of grain per person a year, that is 2,000–2,500 tonnes: 17,000–25,000 pack-horse loads of 100–120 kg, or about 45–70 loads every day.
- So grain comes by boat to Cheapford, the head of navigation, then about 90 km (56 mi) by road to a **gate town** at Fellbridge on the valley floor. Fellbridge grows from a market town into one of the Fells' main towns. Metal and coin flow back down the same road.
- A dwarven tunnel under the Wyndgap would be a pass with no snow season ([Mountain passes](05-trade-routes-and-transport.md#mountain-passes)). It would draw traffic off the pass, and its toll would go to the dwarves. Real tunnels were short (about 8–9 km between two Cappadocian underground towns), so draw one tunnel, not a network.

> **Fantasy twist:** Change no more than these two inputs. The vale, the rivers, the capital, the counties and the 7,700 villages stay exactly where the real rules put them. That contrast is what makes the fantasy parts feel real.

---

## Quick summary

- **Land × density:** 116,500 km² (45,000 sq mi) of six land types gives about 2.4 million people (1.9–2.9 million), ~21 per km² (54 per sq mi).
- **Average urban profile:** 4 cities, 38 towns, ~180 market towns and ~7,700 villages, about 3.3 km (2 mi) apart in the vale.
- **Primate capital:** Hallowbridge, 40,000 (1.65% of the realm), 3.3 times the second city, at the lowest bridge on the Ambre, 83 km (52 mi) up its estuary.
- **Royal landscape:** palace and burial abbey 4 km (2.5 mi) upstream, 5 residences within 43 km (27 mi), a royal forest, and coronation in the old archbishop's city 119 km (74 mi) away.
- **Politics:** 6 great fiefs plus the Crownlands, 33 counties of ~3,500 km² (1,370 sq mi), ~750 hundreds, a North March with a 30 km (19 mi) frontier band, a Debatable Land and a church liberty.
- **Castles:** ~710 sites ever built, ~225 in use: 20–30 km (12–19 mi) apart in the core, a forward line every 29–43 km (18–27 mi) on the border, a beacon chain to the capital, and a field army of 5,000–12,000.
- **Routes:** water first (83 km of estuary, 158 km of navigable river), ~900 km of royal highway with an inn every 15–30 km, only 4 bridges on the Ambre, one cart pass; the capital is 4–5 days' walk from Liskmeet.
- **Church:** ~8,000 parishes, 13 dioceses, ~730 religious houses (~75 of them friaries), 1 university and one great shrine 4–5 pilgrim stages from the capital.
- **Industry:** one mining district, two salt sources, one cloth region, two fairs, a quarry, a forest iron district and 9 ports, each with a visible reason on the map.
- **Time and fantasy:** add the old empire's roads and ruins, abandoned mottes and a few deserted villages; then change only one or two fantasy inputs and follow their consequences.

---

## Sources and further reading

All numbers come from the chapters of this guide and the shared baseline ([research/baseline-numbers.md](../research/baseline-numbers.md)). Their full source lists are in chapters [01](01-settlement-placement.md#sources-and-further-reading) to [11](11-common-mistakes.md#sources-and-further-reading). The works below are the ones this example leans on most.

**Books and articles**

- Beresford, Maurice, and H. P. R. Finberg (1973). *English Medieval Boroughs: A Handlist*. Newton Abbot: David & Charles.
- Bosker, Maarten, Eltjo Buringh and Jan Luiten van Zanden (2013). "From Baghdad to London: Unraveling Urban Development in Europe, the Middle East, and North Africa, 800–1800." *Review of Economics and Statistics* 95(4): 1418–1437.
- Broadberry, Stephen, Bruce M. S. Campbell, Alexander Klein, Mark Overton and Bas van Leeuwen (2015). *British Economic Growth, 1270–1870*. Cambridge: Cambridge University Press.
- Christaller, Walter (1933). *Die zentralen Orte in Süddeutschland*. Jena: Gustav Fischer.
- Creighton, Oliver (2002). *Castles and Landscapes: Power, Community and Fortification in Medieval England*. London: Continuum.
- Dyer, Christopher (2002). *Making a Living in the Middle Ages: The People of Britain 850–1520*. New Haven: Yale University Press.
- Holder, Nick (2017). *The Friaries of Medieval London: From Foundation to Dissolution*. Woodbridge: Boydell. (Friaries per town: one in small towns such as Ware or Maldon, four at Bristol, five at Norwich, seven in London.)
- Hutchings, J. B. (1969). "Milton Ernest: a field survey." *Bedfordshire Archaeological Journal* 4: 69–78.
- Knowles, David, and R. Neville Hadcock (1971). *Medieval Religious Houses: England and Wales*. 2nd ed. London: Longman.
- Langdon, John, and Jordan Claridge (2011). "Transport in medieval England." *History Compass* 9(11): 864–875.
- Masschaele, James (1993). "Transport costs in medieval England." *Economic History Review* 46(2): 266–279.
- Rackham, Oliver (1986). *The History of the Countryside*. London: J. M. Dent.
- Roberts, Brian K., and Stuart Wrathmell (2000). *An Atlas of Rural Settlement in England*. London: English Heritage.

**Web pages consulted**

- Cambridge University Press, Holder, *The Friaries of Medieval London*, introduction: https://www.cambridge.org/core/books/friaries-of-medieval-london/introduction/39C6190AAE813E8D0FC51293F059250B
- Beauvale Priory (Wikipedia; the third of nine English charterhouses, 1343): https://en.wikipedia.org/wiki/Beauvale_Priory
- English Heritage, the Carthusians (Mount Grace Priory): https://www.english-heritage.org.uk/visit/places/mount-grace-priory/history-and-stories/carthusians/
- Historic England, *The Carthusian Monastery at Hinton Charterhouse*: https://historicengland.org.uk/research/results/reports/92-1995
- Hundred (county division) (Wikipedia): https://en.wikipedia.org/wiki/Hundred_(county_division)
- Archaeology Data Service, *Domesday Shires and Hundreds of England*: https://archaeologydataservice.ac.uk/archives/collections/view/1003676/
- Bremen cog (Wikipedia): https://en.wikipedia.org/wiki/Bremen_cog
