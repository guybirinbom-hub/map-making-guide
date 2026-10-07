#!/usr/bin/env python3
"""Generate the schematic SVG map of Daravel from worked-example-layout.json.

Run: python3 make_map.py [out.svg]
Labels are placed greedily with collision checks against other labels and
symbols; terrain symbols are drawn afterwards around the labels.
"""
import json
import math
import random
import sys

from PIL import ImageFont

ROOT = __import__('pathlib').Path(__file__).resolve().parent.parent
LAYOUT = str(ROOT / 'guide/images/worked-example-layout.json')
OUT = sys.argv[1] if len(sys.argv) > 1 else \
    str(ROOT / 'guide/images/worked-example-kingdom.svg')
D = json.load(open(LAYOUT))
W, H = 1000, 800
random.seed(11)
import os
DEBUG = set(filter(None, os.environ.get('MAP_DEBUG', '').split('|')))

# ----------------------------------------------------------------- fonts ---
FR = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 200)
FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 200)
FONT = "Georgia, 'DejaVu Serif', 'Times New Roman', serif"


def tw(s, size, bold=False, ls=0.0):
    """Width of a text in user units (measured with DejaVu Serif, a wide font,
    so narrower fallback fonts never overlap)."""
    f = FB if bold else FR
    return f.getlength(s) * size / 200.0 + ls * len(s)


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))


def f1(v):
    s = '%.1f' % v
    if s.endswith('.0'):
        s = s[:-2]
    if s == '-0':
        s = '0'
    return s


# ---------------------------------------------------------------- colours ---
C = dict(
    bg='#ebe2c9',        # outside the realm
    realm='#f7f1e1',     # parchment inside the realm
    sea='#cde1e8',
    sea_line='#a8c8d4',
    coast='#4f8299',
    river='#3f7fa6',
    ink='#2b1d12',
    ink2='#4a3a2a',
    red='#9b2335',
    border='#8c2f39',
    purple='#5b2a86',
    road='#7a4a24',
    road2='#9b6b3e',
    mtn_fill='#ece0c4',
    mtn_shade='#c8b088',
    mtn_line='#6b5434',
    mtn_tint='#e9dcbd',
    hill_tint='#efe5ca',
    hill_line='#a08560',
    forest_tint='#dbe7c4',
    tree_fill='#a8c287',
    tree_line='#5f7f45',
    marsh_tint='#dcebe3',
    marsh_line='#5d8c79',
    heath_tint='#f1e0d6',
    heath_dot='#a67f78',
    grey='#8a8070',
    water_text='#2c6283',
    region_text='#8a6046',
    feature_text='#5a4630',
    green_text='#41622c',
)

# --------------------------------------------------------------- geometry ---


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def cr_segments(pts, closed=False, alpha=0.5):
    """Centripetal Catmull-Rom spline through pts, as cubic Bezier segments."""
    pts = [tuple(p) for p in pts]
    n = len(pts)
    if closed:
        P = [pts[-1]] + pts + [pts[0], pts[1]]
        rng = n
    else:
        P = [pts[0]] + pts + [pts[-1]]
        rng = n - 1
    segs = []
    for i in range(rng):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        d1 = dist(p0, p1) ** alpha
        d2 = dist(p1, p2) ** alpha
        d3 = dist(p2, p3) ** alpha
        if d2 < 1e-9:
            segs.append((p1, p1, p2, p2))
            continue
        if d1 < 1e-9:
            b1 = p1
        else:
            b1 = tuple((d1 * d1 * p2[k] - d2 * d2 * p0[k]
                        + (2 * d1 * d1 + 3 * d1 * d2 + d2 * d2) * p1[k])
                       / (3 * d1 * (d1 + d2)) for k in (0, 1))
        if d3 < 1e-9:
            b2 = p2
        else:
            b2 = tuple((d3 * d3 * p1[k] - d2 * d2 * p3[k]
                        + (2 * d3 * d3 + 3 * d3 * d2 + d2 * d2) * p2[k])
                       / (3 * d3 * (d3 + d2)) for k in (0, 1))
        segs.append((p1, b1, b2, p2))
    return segs


def segs_d(segs, move=True):
    out = []
    if move:
        out.append('M%s,%s' % (f1(segs[0][0][0]), f1(segs[0][0][1])))
    for p1, b1, b2, p2 in segs:
        out.append('C%s,%s %s,%s %s,%s' % (f1(b1[0]), f1(b1[1]), f1(b2[0]),
                                           f1(b2[1]), f1(p2[0]), f1(p2[1])))
    return ''.join(out)


def bez(seg, t):
    p1, b1, b2, p2 = seg
    u = 1 - t
    return (u ** 3 * p1[0] + 3 * u * u * t * b1[0] + 3 * u * t * t * b2[0] + t ** 3 * p2[0],
            u ** 3 * p1[1] + 3 * u * u * t * b1[1] + 3 * u * t * t * b2[1] + t ** 3 * p2[1])


def sample(segs, step=3.0):
    pts = [segs[0][0]]
    for s in segs:
        L = dist(s[0], s[1]) + dist(s[1], s[2]) + dist(s[2], s[3])
        k = max(2, int(L / step))
        for i in range(1, k + 1):
            pts.append(bez(s, i / k))
    return pts


def poly_d(pts, closed=True):
    s = 'M' + ' '.join('%s,%s' % (f1(x), f1(y)) for x, y in pts)
    return s + ('Z' if closed else '')


def pip(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xc = xi + (y - yi) * (xj - xi) / (yj - yi)
            if x < xc:
                inside = not inside
        j = i
    return inside


def seg_point_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return dist(p, a)
    t = max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return dist(p, (ax + t * dx, ay + t * dy))


def seg_rect(p, q, r):
    x0, y0, x1, y1 = r
    if max(p[0], q[0]) < x0 or min(p[0], q[0]) > x1 or \
            max(p[1], q[1]) < y0 or min(p[1], q[1]) > y1:
        return False
    dx = q[0] - p[0]
    dy = q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pp == 0:
            if qq < 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def rect_hit(a, b, m=0.0):
    return a[0] < b[2] + m and b[0] < a[2] + m and a[1] < b[3] + m and b[1] < a[3] + m


def path_len(pts):
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def point_at(pts, d):
    """Point and direction at arc length d along a polyline."""
    acc = 0
    for i in range(len(pts) - 1):
        L = dist(pts[i], pts[i + 1])
        if acc + L >= d and L > 0:
            t = (d - acc) / L
            p = (pts[i][0] + t * (pts[i + 1][0] - pts[i][0]),
                 pts[i][1] + t * (pts[i + 1][1] - pts[i][1]))
            ang = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
            return p, ang
        acc += L
    a, b = pts[-2], pts[-1]
    return pts[-1], math.atan2(b[1] - a[1], b[0] - a[0])


def nearest_on(pts, p):
    best = (1e9, 0)
    acc = 0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L = dist(a, b)
        if L == 0:
            continue
        t = max(0, min(1, ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / (L * L)))
        q = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        dd = dist(p, q)
        if dd < best[0]:
            best = (dd, acc + t * L)
        acc += L
    return best[1]


# ------------------------------------------------------------ base shapes ---
coast_pts = [tuple(p) for p in D['coastline']['pts']]
coast_segs = cr_segments(coast_pts, alpha=0.5)
coast_s = sample(coast_segs, 2.0)
land_poly = coast_s + [(0, 800), (0, 0)]
sea_poly = coast_s + [(1000, 800), (1000, 0)]
LAND_D = segs_d(coast_segs) + 'L0,800L0,0Z'
SEA_D = segs_d(coast_segs) + 'L1000,800L1000,0Z'
# open coast without the estuary (for water-lining)
i_n = coast_pts.index((860, 392))
i_s = coast_pts.index((858, 420))
OUTER_COAST_D = segs_d(coast_segs[:i_n]) + 'M%d,%d' % coast_pts[i_s] + segs_d(coast_segs[i_s:], move=False)
SEA_OPEN_D = segs_d(coast_segs[:i_n]) + 'L%d,%d' % coast_pts[i_s] + \
    segs_d(coast_segs[i_s:], move=False) + 'L1000,800L1000,0Z'
estuary_poly = coast_pts[i_n:i_s + 1]

borders = {b['name']: b for b in D['borders']}
north = borders['Realm border with Thelland (north)']['pts']
west = borders['Realm border with Morvane (west)']['pts']
north_segs = cr_segments(north)
west_segs = cr_segments(west)
realm_d = (segs_d(north_segs) + segs_d(coast_segs[1:], move=False)
           + segs_d(cr_segments(list(reversed(west))), move=False) + 'Z')
realm_poly = sample(north_segs, 3) + sample(coast_segs[1:], 3) + \
    list(reversed(sample(west_segs, 3)))


def in_sea(p):
    return pip(p, sea_poly)


def in_realm(p):
    return pip(p, realm_poly) and not in_sea(p)


# ------------------------------------------------------- collision index ---
class Index:
    def __init__(self, cell=25):
        self.cell = cell
        self.grid = {}
        self.items = []

    def _cells(self, r):
        c = self.cell
        for cx in range(int(math.floor(r[0] / c)), int(math.floor(r[2] / c)) + 1):
            for cy in range(int(math.floor(r[1] / c)), int(math.floor(r[3] / c)) + 1):
                yield (cx, cy)

    def add(self, r, tag=None):
        i = len(self.items)
        self.items.append((r, tag))
        for k in self._cells(r):
            self.grid.setdefault(k, []).append(i)
        return i

    def hits(self, r, m=0.0, ignore=()):
        seen = set()
        out = []
        rr = (r[0] - m, r[1] - m, r[2] + m, r[3] + m)
        for k in self._cells(rr):
            for i in self.grid.get(k, ()):
                if i in seen:
                    continue
                seen.add(i)
                rect, tag = self.items[i]
                if tag in ignore and tag is not None:
                    continue
                if rect_hit(rect, r, m):
                    out.append(tag)
        return out


class SegIndex:
    def __init__(self, cell=25):
        self.cell = cell
        self.grid = {}
        self.items = []

    def add_line(self, pts, weight, tag):
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            j = len(self.items)
            self.items.append((a, b, weight, tag))
            r = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
            c = self.cell
            for cx in range(int(r[0] // c), int(r[2] // c) + 1):
                for cy in range(int(r[1] // c), int(r[3] // c) + 1):
                    self.grid.setdefault((cx, cy), []).append(j)

    def cost(self, r):
        c = self.cell
        seen = set()
        tags = {}
        for cx in range(int(r[0] // c), int(r[2] // c) + 1):
            for cy in range(int(r[1] // c), int(r[3] // c) + 1):
                for j in self.grid.get((cx, cy), ()):
                    if j in seen:
                        continue
                    seen.add(j)
                    a, b, w, tag = self.items[j]
                    if seg_rect(a, b, r):
                        tags[tag] = max(tags.get(tag, 0), w)
        return sum(tags.values())

    def near(self, p, d):
        c = self.cell
        cx, cy = int(p[0] // c), int(p[1] // c)
        for gx in (cx - 1, cx, cx + 1):
            for gy in (cy - 1, cy, cy + 1):
                for j in self.grid.get((gx, gy), ()):
                    a, b, w, tag = self.items[j]
                    if seg_point_dist(p, a, b) < d:
                        return True
        return False


SYM = Index()      # symbols (hard obstacles for labels)
LAB = Index()      # placed labels
LINES = SegIndex()  # lines (soft cost for labels, hard for terrain glyphs)
BLOCK = Index()    # panels (hard for everything)

svg_sym = []       # symbol svg snippets (drawn above lines)
svg_lab = []       # label svg snippets
failed = []

# ----------------------------------------------------------- fixed panels ---
TITLE_BOX = (5, 5, 330, 62)
PANEL_TOP = [5, 70, 108, 0]     # x0, y0, x1, y1 (y1 computed later)
PANEL_BOT = [5, 0, 108, 795]
SCALE_BOX = (655, 752, 995, 795)
PANEL_SEA = [873, 0, 995, 747]
COMPASS = (952, 468, 26)

LEG_TOP = [
    ('h', 'Settlements'),
    ('capital', 'Capital, 40,000'),
    ('city', 'City (3), 10–12,000'),
    ('town', 'Town (38), 2–8,000'),
    ('walled', 'Walled town'),
    ('county', 'County town'),
    ('seat', 'Duchy, earldom seat'),
    ('market', 'Market town (26)'),
    ('villages', 'Villages (texture)'),
    ('h', 'Church'),
    ('cathedral', 'Cathedral (13)'),
    ('arch', 'Archbishop'),
    ('abbey', 'Abbey, priory'),
    ('commandery', 'Military order'),
    ('shrine', 'Great shrine'),
    ('h', 'Castles'),
    ('great_castle', 'Great castle (5)'),
    ('castle', 'Royal, county castle'),
    ('frontier', 'Frontier castle (10)'),
    ('baronial', 'Baronial castle (25)'),
    ('residence', 'Royal residence'),
    ('beacon', 'Beacon chain (10)'),
    ('h', 'Industry'),
    ('mine', 'Silver, lead mines'),
    ('salt', 'Salt pans'),
    ('quarry', 'Quarry, lime'),
    ('mill', 'Fulling mills'),
    ('vines', 'Vineyards'),
    ('arsenal', 'Royal shipyard'),
    ('industry', 'Other industry'),
    ('fair', 'Fair: months in label'),
]
LEG_BOT = [
    ('h', 'Routes'),
    ('royal_road', 'Royal highway'),
    ('road', 'Regional road'),
    ('old_road', 'Old road, "Street"'),
    ('pilgrim', "Pilgrims' Way"),
    ('mule', 'Mule path'),
    ('sealane', 'Sea lane'),
    ('bridge', 'Bridge'),
    ('ford', 'Ford'),
    ('ferry', 'Ferry'),
    ('pass', 'Pass'),
    ('port', 'Head, member port'),
    ('light', 'Lighthouse'),
    ('h', 'Land and water'),
    ('nav', 'Navigable river'),
    ('boat', 'Head of navigation'),
    ('stream', 'Stream'),
    ('mountains', 'Mountains'),
    ('hills', 'Hills, downs, wolds'),
    ('forest', 'Forest'),
    ('royal_forest', 'Royal forest bound'),
    ('marsh', 'Marsh, fen'),
    ('heath', 'Heath'),
    ('h', 'Borders'),
    ('realm', 'Realm'),
    ('fief', 'Duchy, earldom'),
    ('liberty', 'Church liberty'),
    ('band', 'Frontier band'),
    ('debatable', 'Debatable Land'),
    ('zoom', 'Step 10 local map'),
]
# third panel, in the open sea at the bottom right
LEG_SEA = [
    ('h', 'Older layers (grey)'),
    ('ruin', 'Ruin, labelled "(ruin)"'),
    ('deserted', 'Lost village'),
    ('motte', 'Abandoned motte'),
    ('hillfort', 'Hillfort'),
    ('dyke', 'Old dyke'),
]


ROW = 10.2


def panel_height(rows, title):
    h = 6 + (12 if title else 0)
    for kind, text in rows:
        h += 10.9 if kind == 'h' else ROW
    return h + 4


PANEL_TOP[3] = PANEL_TOP[1] + panel_height(LEG_TOP, 'KEY')
PANEL_BOT[1] = PANEL_BOT[3] - panel_height(LEG_BOT, None)
PANEL_SEA[1] = PANEL_SEA[3] - panel_height(LEG_SEA, None)
BLOCK.add(tuple(PANEL_TOP), 'panel')
BLOCK.add(tuple(PANEL_BOT), 'panel')
BLOCK.add(tuple(PANEL_SEA), 'panel')
BLOCK.add(TITLE_BOX, 'panel')
BLOCK.add(SCALE_BOX, 'panel')
BLOCK.add((COMPASS[0] - COMPASS[2] - 2, COMPASS[1] - COMPASS[2] - 13, COMPASS[0] + COMPASS[2] + 2,
           COMPASS[1] + COMPASS[2] + 2), 'panel')

# --------------------------------------------------------------- symbols ---


def add_sym(rect, tag, snippet=None, data=None):
    SYM.add(rect, tag)
    if snippet:
        if data:
            snippet = '<g data-sym="%s">%s</g>' % (esc(data), snippet)
        svg_sym.append(snippet)


def circ(x, y, r, fill, stroke=None, sw=1.0, extra=''):
    s = '<circle cx="%s" cy="%s" r="%s" fill="%s"' % (f1(x), f1(y), f1(r), fill)
    if stroke:
        s += ' stroke="%s" stroke-width="%s"' % (stroke, f1(sw))
    return s + extra + '/>'


def star_pts(x, y, R, r, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rr = R if i % 2 == 0 else r
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return pts


# Symbols follow the master legend in chapter 13 (13-quick-reference.md,
# "Master legend and label hierarchy"): one symbol, one meaning; borders are
# dash-dot lines, routes are solid or dotted lines, dashes only for fords.
RUIN_FILL = '#b9b0a0'
REALM_DASH = '6 2 1.5 2'          # thick dash-dot
FIEF_DASH = '4 1.8 1.1 1.8'       # medium dash-dot
LIBERTY_DASH = '3 1.5 0.8 1.5'    # thin dash-dot
DISPUTE_DASH = '2.2 1 0.6 1'
FOREST_DASH = '3.6 1.5 0.9 1.5'   # royal forest: green dash-dot
OLD_ROAD = '#5f5245'


def dyke_svg(pts):
    """Old dyke (earthwork bank): a grey line with short ticks on the north side."""
    out = []
    L_ = path_len(pts)
    d = 1.5
    while d < L_ - 1:
        (x, y), a = point_at(pts, d)
        nx, ny = -math.sin(a), math.cos(a)
        if ny > 0:
            nx, ny = -nx, -ny
        out.append('M%s,%sl%s,%s' % (f1(x), f1(y), f1(nx * 2.2), f1(ny * 2.2)))
        d += 3.2
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="1.1"/>' % (poly_d(pts, closed=False), C['grey']) +
            '<path d="%s" stroke="%s" stroke-width="0.7"/>' % (''.join(out), C['grey']))


def g_capital(x, y, k=1.0):
    """Realm capital: a filled star in place of the tier symbol."""
    d = poly_d(star_pts(x, y, 8.4 * k, 3.6 * k))
    return ('<path d="%s" fill="none" stroke="#fffaf0" stroke-width="%s" stroke-linejoin="round"/>' % (d, f1(2.6 * k)) +
            '<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
                d, C['red'], C['ink'], f1(0.9 * k)))


def merlons(x, y, r, n, s, col, rot=0.0):
    """Battlements: n small squares standing on a ring of radius r."""
    out = []
    for i in range(n):
        a = math.radians(rot + i * 360.0 / n)
        nx, ny = math.cos(a), math.sin(a)
        tx, ty = -ny, nx
        cx, cy = x + nx * (r + s * 0.4), y + ny * (r + s * 0.4)
        pts = [(cx + tx * s / 2 - nx * s / 2, cy + ty * s / 2 - ny * s / 2),
               (cx + tx * s / 2 + nx * s / 2, cy + ty * s / 2 + ny * s / 2),
               (cx - tx * s / 2 + nx * s / 2, cy - ty * s / 2 + ny * s / 2),
               (cx - tx * s / 2 - nx * s / 2, cy - ty * s / 2 - ny * s / 2)]
        out.append(poly_d(pts))
    return '<path d="%s" fill="%s"/>' % (''.join(out), col)


def g_city(x, y, county=True, k=1.0):
    """City: circle with a thick battlemented ring; county town adds a centre dot."""
    s = (merlons(x, y, 4.4 * k, 10, 1.55 * k, C['ink']) +
         circ(x, y, 4.4 * k, '#fffaf0', C['ink'], 1.7 * k))
    if county:
        s += circ(x, y, 1.35 * k, C['ink'])
    return s


def g_town(x, y, walled=False, county=False, k=1.0, col=None):
    """Town: circle with a ring; battlements on the ring if walled; centre dot if county town."""
    col = col or C['ink']
    s = ''
    if walled:
        s += merlons(x, y, 3.8 * k, 8, 1.2 * k, col, rot=22.5)
    s += circ(x, y, 3.8 * k, '#fffaf0', col, 0.9 * k)
    s += circ(x, y, 2.1 * k, 'none', col, 0.75 * k)
    if county:
        s += circ(x, y, 0.95 * k, col)
    return s


def g_market(x, y):
    return circ(x, y, 2.1, '#fffaf0', C['ink'], 1.0)


def g_pennant(x, y):
    """Duchy or regional seat: a small pennant; (x, y) is the foot of the staff."""
    return ('<path d="M%s,%sV%s" stroke="%s" stroke-width="0.8"/>' % (f1(x), f1(y), f1(y - 6.2), C['ink']) +
            '<path d="M%s,%sL%s,%sL%s,%sZ" fill="%s" stroke="%s" stroke-width="0.35"/>' % (
                f1(x), f1(y - 6.4), f1(x + 4.2), f1(y - 5.2), f1(x), f1(y - 4.0), C['red'], C['ink']))


def tower_path(x, y, k):
    pts = [(-3, 3.2), (-3, -3.2), (-1.8, -3.2), (-1.8, -1.9), (-0.6, -1.9), (-0.6, -3.2),
           (0.6, -3.2), (0.6, -1.9), (1.8, -1.9), (1.8, -3.2), (3, -3.2), (3, 3.2)]
    return poly_d([(x + k * a, y + k * b) for a, b in pts])


def great_castle_path(x, y, k):
    """Large castle icon: three towers, the middle one tallest."""
    pts = [(-5, 3.4), (-5, -2.8), (-4.2, -2.8), (-4.2, -2.0), (-3.4, -2.0), (-3.4, -2.8), (-2.6, -2.8),
           (-2.6, -0.6), (-1.5, -0.6), (-1.5, -4.8), (-0.9, -4.8), (-0.9, -4.0), (-0.3, -4.0), (-0.3, -4.8),
           (0.3, -4.8), (0.3, -4.0), (0.9, -4.0), (0.9, -4.8), (1.5, -4.8), (1.5, -0.6), (2.6, -0.6),
           (2.6, -2.8), (3.4, -2.8), (3.4, -2.0), (4.2, -2.0), (4.2, -2.8), (5, -2.8), (5, 3.4)]
    return poly_d([(x + k * a, y + k * b) for a, b in pts])


BARONIAL = '#8a6845'


def g_castle(x, y, kind='royal'):
    if kind == 'great':
        return '<path d="%s" fill="%s" stroke="#fffaf0" stroke-width="0.6"/>' % (great_castle_path(x, y, 0.9), C['ink'])
    if kind == 'royal':
        return '<path d="%s" fill="%s" stroke="#fffaf0" stroke-width="0.5"/>' % (tower_path(x, y, 1.0), C['ink'])
    if kind == 'county':
        return '<path d="%s" fill="%s" stroke="#fffaf0" stroke-width="0.5"/>' % (tower_path(x, y, 0.82), C['ink'])
    if kind == 'frontier':
        return '<path d="%s" fill="%s" stroke="#fffaf0" stroke-width="0.4"/>' % (tower_path(x, y, 0.8), C['border'])
    if kind == 'baronial':
        return '<path d="%s" fill="%s" stroke="#fffaf0" stroke-width="0.4"/>' % (tower_path(x, y, 0.72), BARONIAL)
    if kind == 'foreign':
        return '<path d="%s" fill="%s"/>' % (tower_path(x, y, 0.8), C['grey'])
    raise ValueError(kind)


def g_motte(x, y):
    """Abandoned motte: a grey mound with a tower tick on top."""
    return ('<path d="M%s,%sQ%s,%s %s,%sZ" fill="%s" stroke="%s" stroke-width="0.6"/>' % (
        f1(x - 3.2), f1(y + 2.2), f1(x), f1(y - 3.0), f1(x + 3.2), f1(y + 2.2), RUIN_FILL, C['grey']) +
        '<path d="M%s,%sV%s" stroke="%s" stroke-width="0.9"/>' % (f1(x), f1(y - 0.2), f1(y - 3.4), C['grey']))


def g_hillfort(x, y):
    """Hillfort: an oval of rings."""
    return ('<ellipse cx="%s" cy="%s" rx="4" ry="2.9" fill="none" stroke="%s" stroke-width="0.8"/>' % (
        f1(x), f1(y), C['grey']) +
        '<ellipse cx="%s" cy="%s" rx="2.4" ry="1.6" fill="none" stroke="%s" stroke-width="0.8"/>' % (
            f1(x), f1(y), C['grey']))


def g_stones(x, y):
    return ''.join(circ(x + 3 * math.cos(a), y + 3 * math.sin(a), 0.75, C['grey'])
                   for a in [i * math.pi / 4 for i in range(8)])


def g_barrows(x, y):
    """Barrows: small filled mounds."""
    return ''.join('<path d="M%s,%sQ%s,%s %s,%sZ" fill="%s"/>' % (
        f1(x + dx - 1.9), f1(y + dy + 0.9), f1(x + dx), f1(y + dy - 2.0), f1(x + dx + 1.9), f1(y + dy + 0.9), C['grey'])
        for dx, dy in ((-2.5, 0.8), (1, -1.5), (2.8, 1.5)))


def g_ruin_town(x, y):
    """Ruined walled town: the walled-town symbol in grey."""
    return (merlons(x, y, 3.6, 8, 1.2, C['grey'], rot=22.5) +
            circ(x, y, 3.6, RUIN_FILL, C['grey'], 0.9) + circ(x, y, 1.9, 'none', C['grey'], 0.7))


def church_path(x, y, k=1.0):
    """Small church: a tower with a spire at the west end and a nave."""
    pts = [(-2.8, 2.4), (-2.8, -2.4), (-1.8, -4.2), (-0.8, -2.4), (-0.8, -0.4), (2.8, -0.4), (2.8, 2.4)]
    return poly_d([(x + k * a, y + k * b) for a, b in pts])


def g_deserted(x, y):
    """Deserted village: a grey church alone in a field."""
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="0.6"/>' % (church_path(x, y), RUIN_FILL, C['grey'])


def g_cathedral(x, y, k=1.0):
    """Cathedral: a church front with two towers."""
    pts = [(-3.3, 3.0), (-3.3, -1.9), (-2.5, -3.9), (-1.7, -1.9), (-1.7, -0.6), (0, -2.0), (1.7, -0.6),
           (1.7, -1.9), (2.5, -3.9), (3.3, -1.9), (3.3, 3.0)]
    d = poly_d([(x + k * a, y + k * b) for a, b in pts])
    return ('<path d="%s" fill="none" stroke="#fffaf0" stroke-width="%s" stroke-linejoin="round"/>' % (d, f1(1.8 * k)) +
            '<path d="%s" fill="%s"/>' % (d, C['purple']) +
            '<path d="M%s,%sV%s" stroke="#fffaf0" stroke-width="%s"/>' % (f1(x), f1(y + 3.0 * k), f1(y + 0.9 * k),
                                                                         f1(1.1 * k)))


def g_dyke_tick(path_pts):
    pass


def g_cross(x, y, arch=False, k=1.0):
    if arch:
        d = 'M%s,%sV%sM%s,%sH%sM%s,%sH%s' % (
            f1(x), f1(y - 3.6 * k), f1(y + 3.4 * k),
            f1(x - 1.6 * k), f1(y - 2.0 * k), f1(x + 1.6 * k),
            f1(x - 2.6 * k), f1(y - 0.2 * k), f1(x + 2.6 * k))
    else:
        d = 'M%s,%sV%sM%s,%sH%s' % (f1(x), f1(y - 3.2 * k), f1(y + 3.2 * k),
                                     f1(x - 2.2 * k), f1(y - 1.0 * k), f1(x + 2.2 * k))
    return ('<path d="%s" stroke="#fffaf0" stroke-width="%s" stroke-linecap="square"/>'
            '<path d="%s" stroke="%s" stroke-width="%s"/>') % (d, f1(2.9 * k), d, C['purple'], f1(1.25 * k))


def g_abbey(x, y):
    """Abbey or priory: a church with a square cloister beside it."""
    return ('<rect x="%s" y="%s" width="6.4" height="2.2" fill="%s" stroke="#fffaf0" stroke-width="0.4"/>' % (
        f1(x - 3.2), f1(y - 3.1), C['purple']) +
        '<rect x="%s" y="%s" width="3.6" height="3.6" fill="#fffaf0" stroke="%s" stroke-width="0.9"/>' % (
            f1(x - 0.4), f1(y - 0.6), C['purple']))


def g_commandery(x, y):
    """Military-order commandery: a small church with a shield."""
    sx, sy = x + 2.3, y + 0.9
    shield = 'M%s,%sH%sV%sQ%s,%s %s,%sQ%s,%s %s,%sZ' % (
        f1(sx - 1.9), f1(sy - 1.8), f1(sx + 1.9), f1(sy + 0.2), f1(sx + 1.9), f1(sy + 1.9), f1(sx), f1(sy + 2.7),
        f1(sx - 1.9), f1(sy + 1.9), f1(sx - 1.9), f1(sy + 0.2))
    return ('<path d="%s" fill="%s"/>' % (church_path(x - 1.2, y, 0.85), C['purple']) +
            '<path d="%s" fill="#fffaf0" stroke="%s" stroke-width="0.7"/>' % (shield, C['purple']) +
            '<path d="M%s,%sV%sM%s,%sH%s" stroke="%s" stroke-width="0.6"/>' % (
                f1(sx), f1(sy - 1.4), f1(sy + 2.1), f1(sx - 1.3), f1(sy - 0.2), f1(sx + 1.3), C['purple']))


def g_scallop(x, y, k=1.0):
    """Great shrine: a scallop shell (never a star)."""
    R = 3.2 * k
    d = 'M%s,%sA%s,%s 0 0 1 %s,%sL%s,%sH%sZ' % (
        f1(x - R), f1(y + 0.4 * k), f1(R), f1(R), f1(x + R), f1(y + 0.4 * k), f1(x + 0.7 * k), f1(y + 2.8 * k),
        f1(x - 0.7 * k))
    ribs = ''.join('M%s,%sL%s,%s' % (f1(x), f1(y + 2.6 * k), f1(x + R * 0.92 * math.cos(a)),
                                    f1(y + 0.4 * k - R * 0.92 * math.sin(a)))
                   for a in [math.radians(v) for v in (35, 65, 90, 115, 145)])
    return ('<path d="%s" fill="#f0cf6e" stroke="#7a5208" stroke-width="0.6" stroke-linejoin="round"/>' % d +
            '<path d="%s" stroke="#7a5208" stroke-width="0.4"/>' % ribs)


def g_crown(x, y):
    pts = [(-3.2, 2), (-3.2, -1.6), (-1.6, 0), (0, -2.6), (1.6, 0), (3.2, -1.6), (3.2, 2)]
    return '<path d="%s" fill="#d4a017" stroke="#5a3a10" stroke-width="0.6"/>' % poly_d(
        [(x + a, y + b) for a, b in pts])


def g_anchor(x, y, k=1.0, quay=False):
    """Port: a large anchor with a quay (head port) or a small anchor (member port)."""
    d = ('M%s,%sV%s' % (f1(x), f1(y - 2.4 * k), f1(y + 3.4 * k)) +
         'M%s,%sH%s' % (f1(x - 1.9 * k), f1(y - 1.0 * k), f1(x + 1.9 * k)) +
         'M%s,%sQ%s,%s %s,%s' % (f1(x - 3.1 * k), f1(y + 1.2 * k), f1(x), f1(y + 5.2 * k), f1(x + 3.1 * k),
                                 f1(y + 1.2 * k)))
    s = ('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="#1f4f6a" stroke-width="%s"/>' % (
        f1(x), f1(y - 3.3 * k), f1(1.0 * k), f1(0.9 * min(k, 1.15))) +
        '<path d="%s" fill="none" stroke="#1f4f6a" stroke-width="%s" stroke-linecap="round"/>' % (
            d, f1(1.05 * min(k, 1.2))))
    if quay:
        s += '<rect x="%s" y="%s" width="%s" height="1.6" fill="#1f4f6a"/>' % (
            f1(x - 4.6 * k), f1(y + 5.0 * k), f1(9.2 * k))
    return s


def g_light(x, y):
    """Lighthouse: a small tower with short rays."""
    ly = y - 2.6
    rays = ''.join('M%s,%sL%s,%s' % (f1(x + 1.9 * math.cos(a)), f1(ly + 1.9 * math.sin(a)),
                                    f1(x + 3.9 * math.cos(a)), f1(ly + 3.9 * math.sin(a)))
                   for a in [math.radians(v) for v in (180, 215, 250, 290, 325, 0)])
    return ('<path d="%s" stroke="#d08a10" stroke-width="0.8" stroke-linecap="round"/>' % rays +
            '<path d="M%s,%sL%s,%sL%s,%sL%s,%sZ" fill="%s"/>' % (
                f1(x - 1.6), f1(y + 3.6), f1(x - 0.9), f1(y - 1.6), f1(x + 0.9), f1(y - 1.6), f1(x + 1.6),
                f1(y + 3.6), C['ink']) +
            circ(x, ly, 1.25, '#ffd84a', '#7a5208', 0.5))


def g_beacon(x, y):
    """Beacon: a flame dot."""
    return ('<path d="M%s,%sQ%s,%s %s,%sQ%s,%s %s,%sQ%s,%s %s,%sZ" fill="#f2a33a" stroke="#6b3010" stroke-width="0.4"/>' % (
        f1(x - 1.2), f1(y - 0.6), f1(x - 1.7), f1(y - 2.6), f1(x - 0.1), f1(y - 4.6), f1(x + 0.3), f1(y - 3.0),
        f1(x + 1.4), f1(y - 2.3), f1(x + 1.6), f1(y - 1.1), f1(x + 1.2), f1(y - 0.6)) +
        circ(x, y + 0.5, 1.55, '#e07b24', '#6b3010', 0.5))


def g_mine(x, y):
    d = ('M%s,%sL%s,%sM%s,%sL%s,%s' % (f1(x - 2.8), f1(y + 2.8), f1(x + 2.2), f1(y - 2.2),
                                      f1(x + 2.8), f1(y + 2.8), f1(x - 2.2), f1(y - 2.2)) +
         'M%s,%sL%s,%sM%s,%sL%s,%s' % (f1(x + 0.9), f1(y - 3.5), f1(x + 3.5), f1(y - 0.9),
                                      f1(x - 0.9), f1(y - 3.5), f1(x - 3.5), f1(y - 0.9)))
    return '<path d="%s" stroke="%s" stroke-width="1.1" stroke-linecap="round"/>' % (d, C['ink'])


def g_salt(x, y):
    """Salt pans: a checkerboard of small rectangles."""
    cells = ''.join('M%s,%sh2v1.8h-2Z' % (f1(x - 3 + 2 * i), f1(y - 1.8 + 1.8 * j))
                    for i in range(3) for j in range(2) if (i + j) % 2 == 0)
    return ('<rect x="%s" y="%s" width="6" height="3.6" fill="#ffffff" stroke="#3d6f86" stroke-width="0.7"/>' % (
        f1(x - 3), f1(y - 1.8)) +
        '<path d="%s" fill="#3d6f86"/>' % cells)


def g_quarry(x, y):
    return ('<path d="M%s,%sA3.2,3.2 0 0 0 %s,%s" fill="none" stroke="%s" stroke-width="1.1"/>' % (
        f1(x - 3.2), f1(y - 1.5), f1(x + 3.2), f1(y - 1.5), C['ink']) +
        '<path d="M%s,%sl0.8,-1.2M%s,%sl0,-1.4M%s,%sl-0.8,-1.2" stroke="%s" stroke-width="0.7"/>' % (
            f1(x - 2.1), f1(y + 0.4), f1(x), f1(y + 1.2), f1(x + 2.1), f1(y + 0.4), C['ink']))


def g_mill(x, y):
    """Mill: a wheel on the stream."""
    d = ''.join('M%s,%sL%s,%s' % (f1(x - 2.6 * math.cos(a)), f1(y - 2.6 * math.sin(a)),
                                 f1(x + 2.6 * math.cos(a)), f1(y + 2.6 * math.sin(a)))
                for a in [i * math.pi / 4 for i in range(4)])
    return (circ(x, y, 2.6, '#fffaf0', C['ink'], 0.8) + '<path d="%s" stroke="%s" stroke-width="0.5"/>' % (d, C['ink']) +
            circ(x, y, 0.8, C['ink']))


def g_vines(x, y):
    """Vineyards: hatched strips on a slope."""
    d = ''.join('M%s,%sL%s,%s' % (f1(x - 3 + 2 * i), f1(y + 2.4), f1(x - 1.4 + 2 * i), f1(y - 2.4))
                for i in range(3))
    return '<path d="%s" stroke="#6d3b5a" stroke-width="1.0" stroke-linecap="round"/>' % d


def g_arsenal(x, y):
    """Arsenal, naval base or royal shipyard: an anchor plus a castle tower."""
    return (g_anchor(x - 1.6, y + 0.2, 0.72) +
            '<path d="%s" fill="%s" stroke="#fffaf0" stroke-width="0.3"/>' % (tower_path(x + 2.6, y - 0.2, 0.5), C['ink']))


def g_industry(x, y):
    return '<path d="M%s,%sL%s,%sL%s,%sL%s,%sZ" fill="#6b5a45"/>' % (
        f1(x), f1(y - 2.6), f1(x + 2.2), f1(y), f1(x), f1(y + 2.6), f1(x - 2.2), f1(y))


def g_bridge(x, y, ang):
    """Bridge: two short curved lines ')(' with the road running through.
    ang is the river's direction; the road crosses it at a right angle."""
    ua, ub = math.cos(ang), math.sin(ang)     # along the river
    ra, rb = -ub, ua                         # along the road
    out = []
    for s in (-1, 1):
        e, m = 3.1 * s, 1.5 * s                # end and middle offsets from the road
        c = 2 * m - e
        p0 = (x + ua * e - ra * 3.9, y + ub * e - rb * 3.9)
        p1 = (x + ua * e + ra * 3.9, y + ub * e + rb * 3.9)
        cc = (x + ua * c, y + ub * c)
        out.append('M%s,%sQ%s,%s %s,%s' % (f1(p0[0]), f1(p0[1]), f1(cc[0]), f1(cc[1]), f1(p1[0]), f1(p1[1])))
    return '<path d="%s" fill="none" stroke="%s" stroke-width="1.15" stroke-linecap="round"/>' % (''.join(out), C['ink'])


def g_ford(x, y, ang):
    """Ford: a short dashed line across the river."""
    ra, rb = -math.sin(ang), math.cos(ang)
    return '<path d="M%s,%sL%s,%s" stroke="%s" stroke-width="1.3" stroke-dasharray="1.7 1.1"/>' % (
        f1(x - ra * 5), f1(y - rb * 5), f1(x + ra * 5), f1(y + rb * 5), C['road'])


def letter_f(x, y, h=4.4):
    """A small 'F' drawn as lines (so it is a symbol, not a text label)."""
    return ('<path d="M%s,%sV%sH%sM%s,%sH%s" fill="none" stroke="%s" stroke-width="0.9"/>' % (
        f1(x), f1(y + h / 2), f1(y - h / 2), f1(x + h * 0.55), f1(x), f1(y - h * 0.05), f1(x + h * 0.45),
        C['ink']))


def g_ferry(x, y, ang):
    """Ferry: a short dotted line across the river with 'F'."""
    ra, rb = -math.sin(ang), math.cos(ang)
    ua, ub = math.cos(ang), math.sin(ang)
    fx, fy = x + ua * 3.4 - ra * 3.6, y + ub * 3.4 - rb * 3.6
    return ('<path d="M%s,%sL%s,%s" stroke="%s" stroke-width="1.3" stroke-dasharray="0.1 1.9" stroke-linecap="round"/>' % (
        f1(x - ra * 5), f1(y - rb * 5), f1(x + ra * 5), f1(y + rb * 5), C['ink']) +
        letter_f(fx - 1, fy))


def g_boat(x, y):
    """Head of navigation: a small boat."""
    return ('<path d="M%s,%sQ%s,%s %s,%sZ" fill="#1f4f6a"/>' % (f1(x - 3.4), f1(y - 0.6), f1(x), f1(y + 3.6),
                                                             f1(x + 3.4), f1(y - 0.6)) +
            '<path d="M%s,%sV%sL%s,%sZ" fill="#1f4f6a"/>' % (f1(x - 0.2), f1(y - 1), f1(y - 4.2), f1(x + 2.2), f1(y - 1.4)))


def g_pass(x, y, ang=0.0):
    """Pass: a saddle between two peaks (the ')(' mark now means a bridge)."""
    d = 'M%s,%sL%s,%sQ%s,%s %s,%sL%s,%s' % (
        f1(x - 5), f1(y + 2.2), f1(x - 2.8), f1(y - 2.6), f1(x), f1(y + 2.4), f1(x + 2.8), f1(y - 2.6),
        f1(x + 5), f1(y + 2.2))
    return '<path d="%s" fill="none" stroke="%s" stroke-width="1.3" stroke-linejoin="round"/>' % (d, C['ink'])


# ----------------------------------------------------------------- lines ---
svg_lines = []

rivers = D['rivers']
river_geo = {}
for rv in rivers:
    segs = cr_segments(rv['pts'])
    river_geo[rv['name']] = (segs, sample(segs, 2.0))

roads = D['roads']
road_geo = {}
for rd in roads:
    if rd['class'] == 'old_road_in_use':
        pts = [tuple(p) for p in rd['pts']]
        road_geo[rd['name']] = (None, pts)
    else:
        segs = cr_segments(rd['pts'], alpha=0.5)
        road_geo[rd['name']] = (segs, sample(segs, 2.0))

for name, (segs, pts) in river_geo.items():
    w = {'Ambre': 2.0, 'Lisk': 1.6, 'Brim': 1.4, 'Wend': 1.4, 'Skel': 1.4}.get(name, 0.7)
    LINES.add_line(pts, w, 'river:' + name)
for rd in roads:
    w = 1.4 if rd['class'] == 'royal_highway' else 0.9
    LINES.add_line(road_geo[rd['name']][1], w, 'road:' + rd['name'])
LINES.add_line(coast_s, 3.0, 'coast')
border_geo = {}
for b in D['borders']:
    pts = b['pts']
    segs = cr_segments(pts, alpha=0.5)
    border_geo[b['name']] = (segs, sample(segs, 2.5))
    LINES.add_line(border_geo[b['name']][1], 1.2, 'border:' + b['name'])

# ------------------------------------------------------ symbols: places ---
S = {s['name']: s for s in D['settlements']}
cathedrals = set(D['church']['cathedrals'])
WALLED = {n for n, s in S.items() if s.get('walled') is True}

SYMR = {}   # name -> symbol radius for labels

# manual attachment offsets for crowded places: name -> {'castle': (dx,dy), 'cross': (dx,dy)}
ATTACH = {
    'Hallowbridge': {'castle': (-10.5, -10.5), 'cross': (0, -13.5)},
    'Liskmeet': {'castle': (-8.5, -7), 'cross': (-5.5, -14.5),
                 'crown': [(-10, 7), (10, 7.5), (0, 11), (-13, 0), (13, 0), (-15, -8), (-4, -17)]},
    'Norburgh': {'castle': (8.5, -6.5), 'cross': (-8.0, -7.5)},
    'Holmstow': {'cross': (-7.0, -6.5), 'shrine': (0, 9.5)},
    'Wyndfoot': {'castle': (-7, -6.5), 'cross': (7, -7)},
    'Ridgegate': {'castle': (-7, -6.5), 'cross': (7, -7)},
    'Kingsmoat': {'castle': (6.5, -5.5), 'crown': (-7, -5)},
    'Wendmouth': {'castle': (9.5, -7), 'cross': (-5.5, -12), 'pennant': (1.5, 0)},
}
# port anchors (absolute positions, in the water)
PORT_AT = {
    'Hallowbridge': (708, 419.5),
    'Ambremouth': (877, 452),
    'Brimhaven': (897, 222),
    'Gullhaven': (881, 296),
    'Coldhaven': (908, 113),
    'Wendmouth': (552, 754),
    'Meremouth': (816, 642),
    'Seacombe': (689, 714),
    'Saltcove': (386, 777),
}

# duchy and regional seats (pennant), from the region list in chapter 12, step 4
SEATS = {'Liskmeet', 'Wendmouth', 'Brimhaven', 'Wyndfoot', 'Norburgh', 'Holmstow'}
# great royal castles and fortresses (three-tower icon): the White Keep, Wyndgap Castle
# and the three county castles rebuilt as concentric castles
GREAT = {n for n, s in S.items() if s.get('castle') and ('concentric' in s['castle'] or 'White Keep' in s['castle'])}
HEAD_PORTS = {'Hallowbridge', 'Brimhaven', 'Wendmouth', 'Gullhaven'}   # head ports: names in capitals

for name, s in S.items():
    x, y = s['x'], s['y']
    tier = s['tier']
    walled = name in WALLED and tier == 'town'
    county = bool(s.get('county_seat'))
    if tier == 'capital':
        snip = g_capital(x, y)
        r = 8.8
    elif tier == 'city':
        snip = g_city(x, y, county)
        r = 6.2
    elif tier == 'town':
        snip = g_town(x, y, walled, county)
        r = 5.0 if walled else 4.2
    else:
        snip = g_market(x, y)
        r = 2.6
    SYMR[name] = r
    add_sym((x - r, y - r, x + r, y + r), 'S:' + name, snip, name)
    att = ATTACH.get(name, {})
    # castles at county towns (and the White Keep at the capital)
    if s.get('castle'):
        great = name in GREAT
        dx, dy = att.get('castle', (r + 2.2, -(r + 2.2)))
        cx, cy = x + dx, y + dy
        if great:
            add_sym((cx - 4.7, cy - 4.5, cx + 4.7, cy + 3.2), 'C:' + name, g_castle(cx, cy, 'great'), 'castle ' + name)
        else:
            add_sym((cx - 2.8, cy - 3, cx + 2.8, cy + 3), 'C:' + name, g_castle(cx, cy, 'county'), 'castle ' + name)
    if name in cathedrals:
        arch = s.get('cathedral') == 'archbishop'
        dx, dy = att.get('cross', (-(r + 2.2), -(r + 2.4)))
        cx, cy = x + dx, y + dy
        if arch:
            k = 1.25
            add_sym((cx - 2.6 * k, cy - 3.6 * k, cx + 2.6 * k, cy + 3.4 * k), 'X:' + name,
                    g_cross(cx, cy, True, k), 'cathedral ' + name)
        else:
            add_sym((cx - 3.4, cy - 4.0, cx + 3.4, cy + 3.1), 'X:' + name, g_cathedral(cx, cy), 'cathedral ' + name)
    if name in SEATS:
        px, py = x + att.get('pennant', (0, 0))[0], y - r + 0.3 + att.get('pennant', (0, 0))[1]
        add_sym((px - 0.6, py - 6.6, px + 4.4, py), 'Pn:' + name, g_pennant(px, py), 'seat ' + name)
    if 'crown' in att:
        cands = att['crown'] if isinstance(att['crown'], list) else [att['crown']]
        best_c = None
        for dx, dy in cands:
            rc = (x + dx - 3.4, y + dy - 3, x + dx + 3.4, y + dy + 2.4)
            if SYM.hits(rc, 0.8) or BLOCK.hits(rc, 1.0):
                continue
            cst = LINES.cost(rc)
            if best_c is None or cst < best_c[0] - 1e-9:
                best_c = (cst, dx, dy)
        dx, dy = (best_c[1], best_c[2]) if best_c else cands[0]
        add_sym((x + dx - 3.4, y + dy - 3, x + dx + 3.4, y + dy + 2.4), 'R:' + name,
                g_crown(x + dx, y + dy), 'residence ' + name)
    if 'shrine' in att:
        dx, dy = att['shrine']
        add_sym((x + dx - 3.4, y + dy - 3, x + dx + 3.4, y + dy + 3), 'Sh:' + name,
                g_scallop(x + dx, y + dy), 'shrine ' + name)

# ports
for p in D['ports']:
    ax, ay = PORT_AT[p['name']]
    if p['name'] in HEAD_PORTS:
        k = 1.3
        add_sym((ax - 4.7 * k, ay - 4.5 * k, ax + 4.7 * k, ay + 6.7 * k), 'P:' + p['name'],
                g_anchor(ax, ay, k, quay=True), 'port ' + p['name'])
    else:
        k = 0.85
        add_sym((ax - 3.3 * k, ay - 4.5 * k, ax + 3.3 * k, ay + 4.6 * k), 'P:' + p['name'], g_anchor(ax, ay, k),
                'port ' + p['name'])

# lighthouse on Ness Castle
NESS = (855, 425)
LIGHT = (861, 416.5)

# castles
FORWARD = set()
for c in D['castles']:
    n = c['name']
    x, y = c['x'], c['y']
    if n.startswith('White Keep'):
        continue  # drawn as the capital's castle
    if n.startswith('Kingsmoat'):
        continue
    t = c['type']
    st = c['status']
    if st == 'ruin':
        if n == 'Old Harrow castle':
            continue  # drawn as the Old Harrow hillfort
        add_sym((x - 3.3, y - 3.6, x + 3.3, y + 2.5), 'M:' + n, g_motte(x, y), n)
        continue
    if 'foreign' in n:
        add_sym((x - 2.6, y - 2.8, x + 2.6, y + 2.8), 'F:' + n, g_castle(x, y, 'foreign'), n)
        continue
    if 'forward line' in t or n == 'Harnford Tower':
        FORWARD.add(n)
        add_sym((x - 2.6, y - 2.8, x + 2.6, y + 2.8), 'T:' + n, g_castle(x, y, 'frontier'), n)
        continue
    if 'baronial' in t:
        add_sym((x - 2.6, y - 2.8, x + 2.6, y + 2.8), 'B:' + n, g_castle(x, y, 'baronial'), n)
        continue
    if n == 'Ness Castle':
        x, y = NESS
    if 'concentric' in t:
        add_sym((x - 4.7, y - 4.5, x + 4.7, y + 3.2), 'K:' + n, g_castle(x, y, 'great'), n)
        continue
    add_sym((x - 3.2, y - 3.4, x + 3.2, y + 3.4), 'K:' + n, g_castle(x, y, 'royal'), n)

add_sym((LIGHT[0] - 4.2, LIGHT[1] - 4.2, LIGHT[0] + 4.2, LIGHT[1] + 4.2), 'L:light', g_light(*LIGHT), 'lighthouse')

# royal residences (manor and lodge; the castles are drawn above)
RES_AT = {'Westhallow Palace and Abbey': (673, 418.5)}
for r_ in D['royal_residences']:
    n = r_['name']
    if 'Castle' in n or 'castle' in n:
        continue
    if n.startswith('Westhallow'):
        continue  # drawn as an abbey + palace below
    x, y = r_['x'], r_['y']
    add_sym((x - 3.4, y - 3, x + 3.4, y + 2.4), 'R:' + n, g_crown(x, y), n)

# monasteries
ABBEY_AT = {'Westhallow Abbey': (667, 414.5), 'Abbotsmere Abbey': (490, 579), 'Temple Ambre': (575, 417.5)}
for m in D['monasteries']:
    n = m['name']
    if n == 'Holmstow Abbey':
        continue  # the cathedral cross at Holmstow
    x, y = ABBEY_AT.get(n, (m['x'], m['y']))
    if 'commandery' in m['order']:
        add_sym((x - 3.6, y - 3.6, x + 4.4, y + 3.8), 'A:' + n, g_commandery(x, y), n)
        continue
    add_sym((x - 3.3, y - 3.2, x + 3.3, y + 3.1), 'A:' + n, g_abbey(x, y), n)
# Westhallow palace crown next to its abbey
add_sym((667 - 3.4, 422.5 - 3, 667 + 3.4, 422.5 + 2.4), 'R:Westhallow', g_crown(667, 422.5), 'Westhallow palace')

# ruins and old layers
for r_ in D['ruins_and_old_layers']:
    n = r_['name']
    k = r_['kind']
    if 'pts' in r_:
        continue
    x, y = r_['x'], r_['y']
    if 'walled town' in k:
        snip = g_ruin_town(x, y)
        rr = 5.1
    elif 'deserted' in k:
        snip = g_deserted(x, y)
        add_sym((x - 3.1, y - 4.5, x + 3.1, y + 2.7), 'U:' + n, snip, n)
        continue
    elif 'stone circle' in k:
        snip = g_stones(x, y)
        rr = 3.8
    elif 'barrow' in k:
        snip = g_barrows(x, y)
        rr = 4.4
    elif n == 'Old Harrow':
        # hillfort rings with the ruined church (grey) inside
        snip = (g_hillfort(x, y).replace('rx="2.4" ry="1.6"', 'rx="5.4" ry="3.9"') +
                '<path d="%s" fill="%s" stroke="%s" stroke-width="0.5"/>' % (church_path(x, y + 0.3, 0.7), RUIN_FILL,
                                                                             C['grey']))
        rr = 5.6
    else:
        snip = g_hillfort(x, y)
        rr = 4
    add_sym((x - rr, y - rr, x + rr, y + rr), 'U:' + n, snip, n)

# industry
IND_GLYPH = {
    'Silverhope mines': g_mine, 'Leadgill mines': g_mine, 'Orsdale mines': g_mine,
    # brine towns and salt landings take '(salt)' in the label, not the salt-pan symbol (chapter 13)
    'Saltwich brine pits': None, 'Saltings salterns': g_salt, 'Salthithe': None,
    'Chalkhythe quarries': g_quarry, 'Cheapford fair meadow': None, 'Gullhaven strand': None,
    'Tenter valley mills': g_mill, 'Abbotsmere vineyards': g_vines, 'Brimhaven yard': g_arsenal,
}
# fairs have no symbol of their own (chapter 13): the fair months go in the town's label
FAIRS = {'Cheapford': 'wool fair, Sept.', 'Gullhaven': 'herring fair, Sept.–Nov.', 'Saltwich': '(salt)'}
IND_AT = {
    'Silverhope mines': (186, 321), 'Leadgill mines': (226, 289), 'Orsdale mines': (186, 394),
    'Saltwich brine pits': (749, 478), 'Cheapford fair meadow': (388, 446),
    'Gullhaven strand': (867, 312), 'Brimhaven yard': (876, 237), 'Hallowbridge brickfields': (712, 431),
    'Chalkhythe quarries': (558, 451), 'Abbotsmere vineyards': (507, 593),
}
IND_TAG = {
    'Harnwood forges': 'iron', 'Harn Water forges': 'iron', 'Glasshouse clearing': 'glass',
    'Harnwood charcoal': 'charcoal', 'Brimhaven yard': 'shipyard', 'Abbotsmere vineyards': 'vines',
    'Hallowbridge brickfields': 'bricks',
}
IND_POS = {}
for it in D['industry']:
    n = it['name']
    x, y = IND_AT.get(n, (it['x'], it['y']))
    fn = IND_GLYPH.get(n, g_industry)
    if fn is None:
        continue
    IND_POS[n] = (x, y)
    add_sym((x - 3, y - 3.4, x + 3, y + 3.2), 'I:' + n, fn(x, y), n)

# beacons
for b in D['beacons']:
    x, y = b['x'], b['y']
    add_sym((x - 2.1, y - 4.8, x + 2.1, y + 2.3), 'Bc', g_beacon(x, y), 'beacon')

# passes
wy = D['passes'][0]
add_sym((wy['x'] - 5.4, wy['y'] - 3.2, wy['x'] + 5.4, wy['y'] + 3), 'Pass:Wyndgap',
        g_pass(wy['x'], wy['y']), 'Wyndgap pass')
cg = D['passes'][1]
add_sym((cg['x'] - 5.4, cg['y'] - 3.2, cg['x'] + 5.4, cg['y'] + 3), 'Pass:Carrow',
        g_pass(cg['x'], cg['y']), 'Carrow Gap')

# river crossings, drawn beside the town symbol that shares the spot


NAV_HEAD_SHIFT = 13


def river_mark(river, x, y, shift):
    pts = river_geo[river][1]
    d0 = nearest_on(pts, (x, y))
    p, ang = point_at(pts, d0 + shift)
    return p, ang


CROSS = [
    # (kind, river, x, y, shift along river)
    ('bridge', 'Ambre', 688, 421, 0),
    ('bridge', 'Ambre', 548, 440, 9),
    ('bridge', 'Ambre', 450, 418, -9),
    ('bridge', 'Ambre', 262, 446, -8),
    ('bridge', 'Skel', 665, 82, 0),
    ('bridge', 'Brim', 700, 165, -9),
    ('bridge', 'Wend', 440, 668, 8),
    ('ford', 'Ambre', 380, 438, -7.5),
    ('ford', 'Ambre', 322, 447, 6.5),
    ('ferry', 'Ambre', 500, 427, 8),
    ('ferry', 'Ambre', 606, 426, -3),
]
for kind, rv, x, y, sh in CROSS:
    (px, py), ang = river_mark(rv, x, y, sh)
    if kind == 'bridge':
        if rv == 'Ambre' and x == 688:
            px, py, ang = 688, 423.2, 0.0
        snip = g_bridge(px, py, ang)
        rr = 4.0
    elif kind == 'ford':
        snip = g_ford(px, py, ang)
        rr = 4.4
    else:
        snip = g_ferry(px, py, ang)
        ra, rb = -math.sin(ang), math.cos(ang)
        fx = px + math.cos(ang) * 3.4 - ra * 3.6 - 1
        fy = py + math.sin(ang) * 3.4 - rb * 3.6
        xs = [px - ra * 5, px + ra * 5, fx - 0.5, fx + 2.9]
        ys = [py - rb * 5, py + rb * 5, fy - 2.7, fy + 2.7]
        add_sym((min(xs), min(ys), max(xs), max(ys)), 'X%s:%s,%s' % (kind, x, y), snip, kind)
        continue
    add_sym((px - rr, py - rr, px + rr, py + rr), 'X%s:%s,%s' % (kind, x, y), snip, kind)

# head of navigation on the Ambre (Cheapford): a small boat on the river
(bx_, by_), _ = river_mark('Ambre', 380, 438, NAV_HEAD_SHIFT)
add_sym((bx_ - 3.6, by_ - 4.4, bx_ + 3.6, by_ + 3.2), 'Boat', g_boat(bx_, by_), 'head of navigation')

# zoom box
zb = D['zoom_box']
ZOOM = (zb['x0'], zb['y0'], zb['x1'], zb['y1'])
LINES.add_line([(ZOOM[0], ZOOM[1]), (ZOOM[2], ZOOM[1]), (ZOOM[2], ZOOM[3]), (ZOOM[0], ZOOM[3]), (ZOOM[0], ZOOM[1])],
               2.0, 'zoom')

# --------------------------------------------------------------- labels ---


class Block:
    def __init__(self, lines):
        # lines: list of dict(text,size,bold,italic,ls,fill)
        self.lines = lines
        self.w = max(tw(l['text'], l['size'], l.get('bold'), l.get('ls', 0)) +
                     (0.18 * l['size'] if l.get('italic') else 0) for l in lines)
        bl = []
        y = 0.76 * lines[0]['size']
        bl.append(y)
        for i in range(1, len(lines)):
            y += 0.26 * lines[i - 1]['size'] + 0.84 * lines[i]['size']
            bl.append(y)
        self.baselines = bl
        self.h = y + 0.24 * lines[-1]['size']


def L(text, size, bold=False, italic=False, ls=0.0, fill=None, caps=False, weight=None):
    return dict(text=text, size=size, bold=bold, italic=italic, ls=ls, fill=fill or C['ink'],
                weight=weight)


PREF = [('E', 0), ('NE', 0.8), ('SE', 1.3), ('W', 1.8), ('NW', 2.2), ('SW', 2.6), ('N', 2.4), ('S', 2.9)]


def block_rect(blk, pos, x, y, r, gap):
    w, h = blk.w, blk.h
    s0 = blk.lines[0]['size']
    rd = r * 0.72
    if pos == 'E':
        return (x + r + gap, y - h / 2 + 0.07 * s0 - (0.0 if len(blk.lines) == 1 else 0), w, h, 'start')
    if pos == 'W':
        return (x - r - gap - w, y - h / 2 + 0.07 * s0, w, h, 'end')
    if pos == 'NE':
        return (x + rd + gap * 0.6, y - rd - gap * 0.35 - h + 0.15 * s0, w, h, 'start')
    if pos == 'SE':
        return (x + rd + gap * 0.6, y + rd + gap * 0.35 - 0.12 * s0, w, h, 'start')
    if pos == 'NW':
        return (x - rd - gap * 0.6 - w, y - rd - gap * 0.35 - h + 0.15 * s0, w, h, 'end')
    if pos == 'SW':
        return (x - rd - gap * 0.6 - w, y + rd + gap * 0.35 - 0.12 * s0, w, h, 'end')
    if pos == 'N':
        return (x - w / 2, y - r - gap * 0.5 - h + 0.05 * s0, w, h, 'middle')
    if pos == 'S':
        return (x - w / 2, y + r + gap * 0.5 - 0.1 * s0, w, h, 'middle')


def label_ok(rect, ignore=(), pad=1.0):
    x0, y0, x1, y1 = rect
    if x0 < 2 or y0 < 2 or x1 > W - 2 or y1 > H - 2:
        return False
    if BLOCK.hits(rect, 1.0):
        return False
    if LAB.hits(rect, pad):
        return False
    if SYM.hits(rect, 0.6, ignore=ignore):
        return False
    return True


def sea_frac(rect):
    x0, y0, x1, y1 = rect
    pts = [(x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, (y0 + y1) / 2)]
    return sum(1 for p in pts if in_sea(p)) / len(pts)


def halo_for(rect):
    cx, cy = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
    if in_sea((cx, cy)):
        return C['sea']
    if not pip((cx, cy), realm_poly):
        return C['bg']
    return C['realm']


def emit_block(blk, left, top, anchor, rot=None, halo=None, cls=None, hw=2.4):
    out = []
    for ln, bl in zip(blk.lines, blk.baselines):
        if anchor == 'start':
            tx = left
        elif anchor == 'end':
            tx = left + blk.w
        else:
            tx = left + blk.w / 2
        ty = top + bl
        attrs = ['x="%s" y="%s"' % (f1(tx), f1(ty))]
        if anchor != 'start':
            attrs.append('text-anchor="%s"' % anchor)
        attrs.append('font-size="%s"' % f1(ln['size']))
        if ln.get('bold'):
            attrs.append('font-weight="bold"')
        if ln.get('italic'):
            attrs.append('font-style="italic"')
        if ln.get('ls'):
            attrs.append('letter-spacing="%s"' % f1(ln['ls']))
        attrs.append('fill="%s"' % ln['fill'])
        if halo:
            attrs.append('stroke="%s" stroke-width="%s" stroke-linejoin="round" paint-order="stroke"' % (halo, f1(hw)))
        if rot:
            attrs.append('transform="rotate(%s %s %s)"' % (f1(rot[0]), f1(rot[1]), f1(rot[2])))
        out.append('<text %s>%s</text>' % (' '.join(attrs), esc(ln['text'])))
    if len(out) > 1:
        return '<g data-block="1">%s</g>' % ''.join(out)
    return ''.join(out)


def place_point_label(name, blk, x, y, r, own=(), prefs=None, gaps=(2.0, 5.0, 9.0), allow_sea=False,
                      line_w=1.6, force=None, required=True):
    best = None
    cands = []
    plist = prefs or PREF
    if force:
        plist = [(force[0], 0)]
        gaps = (force[1],)
    for gi, g in enumerate(gaps):
        for pos, base in plist:
            left, top, w, h, anchor = block_rect(blk, pos, x, y, r, g)
            rect = (left, top, left + w, top + h)
            if not label_ok(rect, ignore=own):
                if DEBUG and name in DEBUG:
                    sys.stderr.write('%s %s g=%s blocked by sym=%s lab=%s\n' % (
                        name, pos, g, SYM.hits(rect, 0.6, ignore=own), LAB.hits(rect, 1.0)))
                continue
            cost = base + gi * 4.0
            cost += line_w * LINES.cost(rect)
            if not allow_sea:
                cost += 6.0 * sea_frac(rect)
            cands.append((cost, rect, anchor))
    if not cands:
        if required:
            failed.append(name)
        return None
    cands.sort(key=lambda c: c[0])
    cost, rect, anchor = cands[0]
    LAB.add(rect, 'lab:' + name)
    svg_lab.append(emit_block(blk, rect[0], rect[1], anchor, halo=halo_for(rect)))
    return rect


# ----- settlement labels
order = sorted(D['settlements'], key=lambda s: (
    {'capital': 0, 'city': 1, 'town': 2, 'market_town': 3}[s['tier']], -s['population']))

FORCE = {
    # name: (position, gap) chosen after looking at the render
}
SUB = {
    'Hallowbridge': None,
    'Liskmeet': 'university · (coronations)',
    'Holmstow': "St Aldwen's shrine",
}

for s in order:
    n = s['name']
    t = s['tier']
    if t == 'capital':
        lines = [L(n.upper(), 12, bold=True, ls=0.6)]
    elif t == 'city':
        # cities in bold capitals; this also puts the two head ports in capitals
        lines = [L(n.upper(), 10, bold=True, ls=0.4)]
    elif t == 'town':
        if s['population'] >= 5000:
            lines = [L(n, 9.6, bold=True)]
        elif n in HEAD_PORTS:
            lines = [L(n.upper(), 8.2, ls=0.3)]
        else:
            lines = [L(n, 8.7)]
    else:
        lines = [L(n, 7.4, italic=False, fill=C['ink2'])]
    if SUB.get(n):
        lines.append(L(SUB[n], 6.6, italic=True, fill=C['purple']))
    if n in FAIRS:
        lines.append(L(FAIRS[n], 6.4, italic=True, fill=C['feature_text']))
    blk = Block(lines)
    own = ('S:' + n,)
    if t == 'capital':
        place_point_label(n, blk, s['x'], s['y'], SYMR[n], own=own, force=FORCE.get(n),
                          gaps=(2.0, 5.0, 9.0, 13.0), allow_sea=True)
    else:
        place_point_label(n, blk, s['x'], s['y'], SYMR[n], own=own, force=FORCE.get(n))

# ----- named sites (castles, abbeys, residences, ruins)
SITE_LABELS = [
    # (text, x, y, r, style)
    ('Temple Ambre', 575, 417.5, 3.1, 'church'),
    ('Wyndgap Castle', 145, 436, 3.4, 'site'),
    ('Ness Castle', NESS[0], NESS[1], 3.4, 'site'),
    ('Redwater Castle', 630, 395, 3.4, 'site'),
    ('Westhallow\n(royal tombs)', 667, 418, 4.5, 'site'),
    ('Elmhurst', 664, 432, 3.4, 'site'),
    ('Kingswood lodge', 630, 352, 3.4, 'site'),
    ('Harnvale Abbey', 470, 215, 3.1, 'church'),
    ('Greywater Abbey', 205, 560, 3.1, 'church'),
    ('Coldwater Abbey', 205, 480, 3.1, 'church'),
    ('Stillwater Abbey', 392, 627, 3.1, 'church'),
    ('Mirefield Abbey', 742, 238, 3.1, 'church'),
    ('Sallowhope Charterhouse', 168, 525, 3.1, 'church'),
    ('Wendchester (ruin)', 524, 726, 5.1, 'ruin'),
    ('Old Harrow (ruin)', 245, 470, 5.6, 'ruin'),
    ('The Grey Wives', 185, 600, 3.8, 'ruin'),
    ('Old Harnvale (lost village)', 476, 222, 3, 'ruin'),
    ('Lostwick (lost village)', 622, 352, 3, 'ruin'),
    ('Skelby (lost village)', 620, 110, 3, 'ruin'),
    ('Chalkhythe', 558, 451, 3.2, 'ind'),
    ('Wyndgap', 130, 432, 5.0, 'pass'),
    ('Carrow Gap', 172, 640, 5.0, 'pass'),
]
STYLE = {
    'site': dict(size=7.0, italic=True, fill=C['ink2']),
    'church': dict(size=6.9, italic=True, fill=C['purple']),
    'ruin': dict(size=6.8, italic=True, fill='#6f675a'),
    'ind': dict(size=6.8, italic=True, fill=C['feature_text']),
    'pass': dict(size=7.4, italic=True, fill=C['ink'], bold=True),
}
SITE_OWN = {
    'Wyndgap Castle': 'K:Wyndgap Castle', 'Ness Castle': 'K:Ness Castle',
    'Redwater Castle': 'K:Redwater Castle (royal residence)', 'Westhallow': 'A:Westhallow Abbey',
    'Elmhurst': 'R:Elmhurst royal manor', 'Kingswood lodge': 'R:Kingswood hunting lodge',
    'Harnvale Abbey': 'A:Harnvale Abbey', 'Greywater Abbey': 'A:Greywater Abbey',
    'Coldwater Abbey': 'A:Coldwater Abbey', 'Stillwater Abbey': 'A:Stillwater Abbey',
    'Mirefield Abbey': 'A:Mirefield Abbey', 'Sallowhope Charterhouse': 'A:Sallowhope Charterhouse',
    'Temple Ambre': 'A:Temple Ambre', 'Wendchester': 'U:Wendchester', 'Old Harrow': 'U:Old Harrow',
    'The Grey Wives': 'U:The Grey Wives', 'Old Harnvale': 'U:Old Harnvale', 'Lostwick': 'U:Lostwick',
    'Skelby': 'U:Skelby', 'Chalkhythe': 'I:Chalkhythe quarries', 'Wyndgap': 'Pass:Wyndgap',
    'Carrow Gap': 'Pass:Carrow',
}
for text, x, y, r, st in SITE_LABELS:
    sty = STYLE[st]
    blk = Block([L(t_, sty['size'], bold=sty.get('bold', False), italic=sty['italic'], fill=sty['fill'])
                 for t_ in text.split('\n')])
    place_point_label(text, blk, x, y, r, own=(), gaps=(1.6, 4.0, 7.0, 10.0), force=FORCE.get(text))

# industry tags
for n, tag in IND_TAG.items():
    x, y = IND_POS[n]
    blk = Block([L(tag, 6.2, italic=True, fill=C['feature_text'])])
    place_point_label(tag + '@' + n, blk, x, y, 3.0, own=(), gaps=(1.2, 3.5), required=False)


# ----- labels along lines (rivers, roads)
def place_line_label(name, text, pts, size, fill, italic=True, bold=False, ls=0.0, prefer=None, side=(1, -1),
                     offset=None, max_dev=2.2, required=True, halo=None, step=4.0, prefer_w=0.08,
                     min_s=None, max_s=None, line_tag=None):
    """Straight rotated label parallel to a line, offset to one side."""
    wid = tw(text, size, bold, ls)
    hgt = size * 0.98
    total = path_len(pts)
    if total < wid + 4:
        if required:
            failed.append(name)
        return None
    cands = []
    d = 2.0
    while d + wid + 2 < total:
        if (min_s is not None and d < min_s) or (max_s is not None and d > max_s):
            d += step
            continue
        p0, _ = point_at(pts, d)
        p1, _ = point_at(pts, d + wid)
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        # straightness
        dev = 0
        for k in range(1, 6):
            q, _ = point_at(pts, d + wid * k / 6)
            dev = max(dev, seg_point_dist(q, p0, p1))
        if dev <= max_dev:
            deg = math.degrees(ang)
            flip = False
            if deg > 90 or deg < -90:
                p0, p1 = p1, p0
                ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
                deg = math.degrees(ang)
                flip = True
            ux, uy = math.cos(ang), math.sin(ang)
            nx, ny = -uy, ux   # normal (points 'below' the text)
            for sd in side:
                off = offset if offset is not None else (hgt * 0.5 + 2.2 + dev)
                # center of label
                mx = (p0[0] + p1[0]) / 2 + nx * off * sd
                my = (p0[1] + p1[1]) / 2 + ny * off * sd
                # collision geometry: squares along the label
                n_sq = max(1, int(math.ceil(wid / hgt)))
                rects = []
                ok = True
                for k in range(n_sq):
                    t = (k + 0.5) / n_sq - 0.5
                    cx, cy = mx + ux * wid * t, my + uy * wid * t
                    rr = (cx - hgt * 0.62, cy - hgt * 0.62, cx + hgt * 0.62, cy + hgt * 0.62)
                    if not label_ok(rr, pad=0.4):
                        ok = False
                        break
                    rects.append(rr)
                if not ok:
                    continue
                cost = abs(deg) / 60.0 + dev
                for rr in rects:
                    c = LINES.cost(rr)
                    cost += 0.8 * c
                if prefer:
                    cost += prefer_w * dist((mx, my), prefer)
                cands.append((cost, mx, my, deg, rects))
        d += step
    if not cands:
        if required:
            failed.append(name)
        return None
    cands.sort(key=lambda c: c[0])
    cost, mx, my, deg, rects = cands[0]
    for rr in rects:
        LAB.add(rr, 'lab:' + name)
    # baseline: center shifted down by ~0.33 size
    ang = math.radians(deg)
    bx = mx + (-math.sin(ang)) * 0.33 * size
    by = my + math.cos(ang) * 0.33 * size
    attrs = 'x="%s" y="%s" text-anchor="middle" font-size="%s"' % (f1(bx), f1(by), f1(size))
    if italic:
        attrs += ' font-style="italic"'
    if bold:
        attrs += ' font-weight="bold"'
    if ls:
        attrs += ' letter-spacing="%s"' % f1(ls)
    hc = halo or halo_for((mx - 1, my - 1, mx + 1, my + 1))
    attrs += ' fill="%s" stroke="%s" stroke-width="2.2" stroke-linejoin="round" paint-order="stroke"' % (fill, hc)
    attrs += ' transform="rotate(%s %s %s)"' % (f1(deg), f1(bx), f1(by))
    svg_lab.append('<text %s>%s</text>' % (attrs, esc(text)))
    return (mx, my, deg)


RIVER_LABELS = [
    ('Ambre', 'R. Ambre', 8.4, (520, 440)),
    ('Lisk', 'R. Lisk', 7.6, (425, 270)),
    ('Brim', 'R. Brim', 7.4, (745, 182)),
    ('Skel', 'R. Skel', 7.4, (560, 66)),
    ('Wend', 'R. Wend', 7.4, (400, 630)),
    ('Mere', 'R. Mere', 7.0, (650, 588)),
    ('Tenter Water', 'Tenter Water', 6.8, (290, 520)),
    ('Sedge', 'Sedge', 6.4, (660, 270)),
    ('Holm Lode', 'Holm Lode', 6.2, (785, 375)),
    ('Hope Water', 'Hope Water', 6.2, (240, 360)),
]
for rv, text, size, pref in RIVER_LABELS:
    pts = river_geo[rv][1]
    place_line_label('river ' + text, text, pts, size, C['water_text'], prefer=pref, prefer_w=0.12,
                     required=(size >= 7))

ROAD_LABELS = [
    ("The King's Way", 7.2, (300, 440)),
    ('North Road', 7.0, (690, 225)),
    ('South Road', 7.0, (595, 600)),
    ('Old Street', 7.0, (470, 470)),
    ('Fell Street', 6.8, (380, 300)),
    ('Brim Road', 6.6, (800, 245)),
    ('Downs Road', 6.4, (340, 560)),
    ('Fells Road', 6.4, (205, 260)),
    ('Lisk Road', 6.4, (420, 330)),
    ('Harn Road', 6.4, (590, 260)),
    ('Salt Road (west)', 6.0, (700, 476)),
    ('Salt Road (south)', 6.0, (705, 560)),
    ('Salt Road (to the estuary landing)', 6.0, (752, 445)),
]
ROAD_TEXT = {"The King's Way": "King's Way", 'Salt Road (west)': 'Salt Road',
             'Salt Road (south)': 'Salt Road', 'Salt Road (to the estuary landing)': 'Salt Road'}
road_by_short = {}
for rd in roads:
    nm = rd['name']
    short = nm.replace('The ', '', 1) if nm.startswith('The ') else nm
    road_by_short[nm] = rd
for key, size, pref in ROAD_LABELS:
    rd = None
    for rr in roads:
        nm = rr['name']
        if nm.startswith(key) or nm.startswith('The ' + key):
            rd = rr
            break
    if rd is None:
        failed.append('road?' + key)
        continue
    text = ROAD_TEXT.get(key, key)
    pts = road_geo[rd['name']][1]
    place_line_label('road ' + key, text, pts, size, C['road'], prefer=pref, prefer_w=0.1,
                     max_dev=2.6, required=('Salt' not in key), step=3.0)

dyke_pts = sample(cr_segments([r_ for r_ in D['ruins_and_old_layers'] if 'pts' in r_][0]['pts']), 2.0)
place_line_label('Thelling Dyke', 'Thelling Dyke', dyke_pts, 6.6, '#6f675a', prefer=(250, 150), prefer_w=0.05,
                 max_dev=3.0, step=2.0)
pil = [rr for rr in roads if rr['class'] == 'pilgrim_road'][0]
place_line_label("road Pilgrims' Way", "Pilgrims' Way", road_geo[pil['name']][1], 6.0, C['purple'],
                 prefer=(735, 330), prefer_w=0.05, max_dev=6.0, step=1.0, required=True)

# ----- area labels


def place_area_label(name, blk, anchor, radius=60, step=5, inside=None, inside_all=False, w_dist=0.06,
                     line_w=0.9, required=True, halo=None, avoid_sea=True, rot=0):
    ax, ay = anchor
    cands = []
    rng = int(radius / step)
    for ix in range(-rng, rng + 1):
        for iy in range(-rng, rng + 1):
            cx, cy = ax + ix * step, ay + iy * step
            if dist((cx, cy), anchor) > radius:
                continue
            if rot:
                w, h = blk.h, blk.w
            else:
                w, h = blk.w, blk.h
            rect = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            if not label_ok(rect, pad=1.2):
                continue
            if inside is not None:
                corners = [(rect[0], rect[1]), (rect[2], rect[1]), (rect[0], rect[3]), (rect[2], rect[3])]
                if inside_all:
                    if not all(pip(c, inside) for c in corners):
                        continue
                elif not pip((cx, cy), inside):
                    continue
            cost = w_dist * dist((cx, cy), anchor) + line_w * LINES.cost(rect)
            if avoid_sea:
                cost += 8 * sea_frac(rect)
            cands.append((cost, rect))
    if not cands:
        if required:
            failed.append(name)
        return None
    cands.sort(key=lambda c: c[0])
    cost, rect = cands[0]
    LAB.add(rect, 'lab:' + name)
    hc = halo or halo_for(rect)
    if rot:
        # rotated -90: draw block centred, rotate around centre
        cx, cy = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
        left, top = cx - blk.w / 2, cy - blk.h / 2
        svg_lab.append('<g transform="rotate(%s %s %s)">%s</g>' % (
            f1(rot), f1(cx), f1(cy), emit_block(blk, left, top, 'middle', halo=hc)))
    else:
        svg_lab.append(emit_block(blk, rect[0], rect[1], 'middle', halo=hc))
    return rect


REG = C['region_text']
region_specs = [
    ('Crownlands', [L('CROWNLANDS', 9.6, ls=2.2, fill=REG)], (640, 462), 50),
    ('Liberty of Holmstow', [L('LIBERTY OF', 6.4, ls=1.4, fill=C['purple']), L('HOLMSTOW', 8, ls=1.8, fill=C['purple'])],
     (805, 376), 26),
    ('Duchy of Lisk', [L('DUCHY OF', 6.8, ls=1.6, fill=REG), L('LISK', 10.5, ls=3, fill=REG)], (450, 380), 70),
    ('Duchy of the Fells', [L('DUCHY OF', 6.8, ls=1.6, fill=REG), L('THE FELLS', 10.5, ls=2.4, fill=REG)],
     (200, 430), 70),
    ('North March', [L('THE NORTH MARCH', 9.6, ls=2.4, fill=REG)], (470, 165), 70),
    ('Earldom of Brim', [L('EARLDOM OF', 6.8, ls=1.6, fill=REG), L('BRIM', 10.5, ls=3, fill=REG)], (770, 265), 45),
    ('Duchy of Wend', [L('DUCHY OF', 6.8, ls=1.6, fill=REG), L('WEND', 10.5, ls=3, fill=REG)], (560, 625), 60),
]
for name, lines, anc, rad in region_specs:
    place_area_label(name, Block(lines), anc, radius=rad, inside=realm_poly, inside_all=True, w_dist=0.05)

# terrain names
forest_polys = {f['name']: f['pts'] for f in D['forests']}
hill_polys = {h['name']: h['pts'] for h in D['hills']}
marsh_polys = {m['name']: m['pts'] for m in D['marshes']}
TERRAIN = [
    ('The Harnwood', [L('THE HARNWOOD', 8.6, ls=2.2, fill=C['green_text'], italic=True)], (505, 240), 55,
     forest_polys['The Harnwood']),
    ('Kingswood Chase', [L('Kingswood Chase', 7.6, italic=True, fill=C['green_text'])], (640, 335), 26, None),
    ('Holm Fens', [L('Holm Fens', 7.4, italic=True, fill='#3c6e5c')], (815, 352), 30, marsh_polys['Holm Fens']),
    ('The Saltings', [L('The Saltings', 6.4, italic=True, fill='#3c6e5c')], (800, 432), 30, None),
    ('Brackenheath', [L('Brackenheath', 7.0, italic=True, fill='#7d5551')], (628, 540), 40,
     D['heaths'][0]['pts']),
    ('Wend Downs', [L('Wend Downs', 7.2, italic=True, fill=C['feature_text'])], (420, 650), 40,
     hill_polys['Wend Downs']),
    ('Brim Wolds', [L('Brim Wolds', 7.2, italic=True, fill=C['feature_text'])], (790, 195), 40,
     hill_polys['Brim Wolds']),
    ('Skel Hills', [L('Skel Hills', 7.0, italic=True, fill=C['feature_text'])], (760, 150), 45,
     hill_polys['Skel Hills']),
    ('Mere Hills', [L('Mere Hills', 6.6, italic=True, fill=C['feature_text'])], (690, 660), 35,
     hill_polys['Mere Hills']),
    ('Lisk Hills', [L('Lisk Hills', 6.6, italic=True, fill=C['feature_text'])], (500, 340), 40,
     hill_polys['Lisk Hills']),
    ('North Hills', [L('North Hills', 6.6, italic=True, fill=C['feature_text'])], (300, 250), 40,
     hill_polys['North Hills']),
    ('Wend Levels', [L('Wend Levels', 6.0, italic=True, fill='#3c6e5c')], (505, 712), 20, None),
    ('Debatable Land', [L('The Debatable Land', 6.4, italic=True, fill=C['border'])], (316, 78), 14, None),
]
for name, lines, anc, rad, poly in TERRAIN:
    place_area_label(name, Block(lines), anc, radius=rad, inside=poly, w_dist=0.05, step=3,
                     required=name in ('The Harnwood', 'Holm Fens', 'Brackenheath', 'Kingswood Chase',
                                       'Debatable Land', 'Wend Downs', 'Brim Wolds'))

# Whitridge: vertical label along the ridge
place_area_label('Whitridge', Block([L('Whitridge', 6.8, italic=True, fill=C['feature_text'], ls=0.6)]),
                 (551, 500), radius=40, step=2, inside=hill_polys['Whitridge'], w_dist=0.05, rot=-90)
# The Fells: big spaced label
place_area_label('The Fells', Block([L('THE FELLS', 11, ls=4, fill=C['mtn_line'], italic=True)]),
                 (190, 520), radius=70, step=4, inside=D['mountains'][0]['pts'], w_dist=0.03, rot=-90)

# seas, neighbours, estuary
place_area_label('Ambre estuary', Block([L('Ambre estuary', 6.6, italic=True, fill=C['water_text'])]),
                 (812, 412), radius=14, step=1, avoid_sea=False, halo=C['sea'], line_w=0.2)
place_area_label('Grey Sea', Block([L('THE GREY SEA', 11, ls=4, italic=True, fill=C['water_text'])]),
                 (930, 585), radius=60, step=4, avoid_sea=False, halo=C['sea'], w_dist=0.02, rot=-90)
place_area_label('Thelland', Block([L('KINGDOM OF THELLAND', 9.5, ls=3, fill='#7b6d58')]),
                 (520, 28), radius=60, step=4, avoid_sea=False, halo=C['bg'])
place_area_label('Morvane', Block([L('KINGDOM OF', 6.8, ls=1.5, fill='#7b6d58'), L('MORVANE', 9.5, ls=2.4, fill='#7b6d58')]),
                 (55, 450), radius=40, step=2, avoid_sea=False, halo=C['bg'])
place_area_label('east crossing', Block([L('to the eastern kingdoms,', 6.2, italic=True, fill=C['water_text']),
                                         L('2–5 days by sea, Mar.–Nov.', 6.2, italic=True, fill=C['water_text'])]),
                 (950, 372), radius=24, step=2, avoid_sea=False, halo=C['sea'])
place_area_label('frontier band', Block([L('frontier band, 30 km', 6.2, italic=True, fill=C['border'])]),
                 (840, 92), radius=40, step=2, avoid_sea=True)
place_area_label('step10', Block([L('Step 10 map', 5.8, italic=True, fill=C['ink'])]),
                 (611, 450), radius=12, step=1)

# --------------------------------------------------- terrain glyph layer ---
mtn_poly = D['mountains'][0]['pts']
peaks = [tuple(p) for p in D['mountains'][0]['peaks']]


def glyph_free(rect, line_margin=1.2, lines=True):
    if BLOCK.hits(rect, 1.0):
        return False
    if LAB.hits(rect, 0.8):
        return False
    if SYM.hits(rect, 1.2):
        return False
    if lines:
        cx, cy = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
        rad = max(rect[2] - rect[0], rect[3] - rect[1]) / 2
        if LINES.near((cx, cy), rad * 0.85 + line_margin):
            return False
    return True


def in_land(p):
    return pip(p, land_poly)


terrain = []
glyph_rects = Index()

# mountains
mtns = []
for (px, py) in peaks:
    for dx in (0, 4, -4, 7, 10):
        s = 1.55
        rect = (px + dx - 7 * s, py - 9 * s, px + dx + 7 * s, py + 0.5)
        if glyph_free(rect, 0.5, lines=False) and not glyph_rects.hits(rect):
            mtns.append((px + dx, py, s))
            glyph_rects.add(rect)
            break
yy = 46
row = 0
while yy < 800:
    xx = 40 + (row % 2) * 9
    while xx < 330:
        jx = xx + random.uniform(-3, 3)
        jy = yy + random.uniform(-2.5, 2.5)
        s = random.uniform(0.75, 1.05)
        rect = (jx - 6.5 * s, jy - 8 * s, jx + 6.5 * s, jy + 0.5)
        corners = [(rect[0], rect[3]), (rect[2], rect[3]), (jx, rect[1])]
        if all(pip(c, mtn_poly) and in_land(c) for c in corners) and glyph_free(rect, 1.0) \
                and not glyph_rects.hits(rect, 0.5):
            mtns.append((jx, jy, s))
            glyph_rects.add(rect)
        xx += 18
    yy += 12.5
    row += 1
mtns.sort(key=lambda m: m[1])
for (x, y, s) in mtns:
    terrain.append('<use xlink:href="#mtn" transform="translate(%s %s) scale(%s)"/>' % (f1(x), f1(y), '%.2f' % s))

# hills
hills_svg = []
for hname, hp in hill_polys.items():
    yy = min(p[1] for p in hp)
    ymax = max(p[1] for p in hp)
    xmin = min(p[0] for p in hp)
    xmax = max(p[0] for p in hp)
    row = 0
    sp_x, sp_y = (14, 10) if hname != 'Whitridge' else (9, 13)
    while yy <= ymax:
        xx = xmin + (row % 2) * sp_x / 2
        while xx <= xmax:
            jx = xx + random.uniform(-2, 2)
            jy = yy + random.uniform(-2, 2)
            rect = (jx - 4.5, jy - 3.5, jx + 4.5, jy + 0.5)
            corners = [(rect[0], jy), (rect[2], jy), (jx, rect[1])]
            if all(pip(c, hp) and in_land(c) for c in corners) and not pip((jx, jy), mtn_poly) \
                    and glyph_free(rect, 1.0) and not glyph_rects.hits(rect, 1.0):
                hills_svg.append('<use xlink:href="#hill" x="%s" y="%s"/>' % (f1(jx), f1(jy)))
                glyph_rects.add(rect)
            xx += sp_x
        yy += sp_y
        row += 1

# trees
trees_svg = []
for fname, fp in forest_polys.items():
    yy = min(p[1] for p in fp)
    ymax = max(p[1] for p in fp)
    xmin = min(p[0] for p in fp)
    xmax = max(p[0] for p in fp)
    row = 0
    while yy <= ymax:
        xx = xmin + (row % 2) * 4.5
        while xx <= xmax:
            jx = xx + random.uniform(-1.5, 1.5)
            jy = yy + random.uniform(-1.5, 1.5)
            rect = (jx - 2.8, jy - 3.2, jx + 2.8, jy + 3.4)
            corners = [(rect[0], rect[1]), (rect[2], rect[1]), (rect[0], rect[3]), (rect[2], rect[3])]
            if all(pip(c, fp) for c in corners) and glyph_free(rect, 0.6) and not glyph_rects.hits(rect, 0.3):
                trees_svg.append('<use xlink:href="#tree" x="%s" y="%s"/>' % (f1(jx), f1(jy)))
                glyph_rects.add(rect)
            xx += 9
        yy += 7.5
        row += 1

# marsh tufts
marsh_svg = []
for mname, mp in marsh_polys.items():
    yy = min(p[1] for p in mp)
    ymax = max(p[1] for p in mp)
    xmin = min(p[0] for p in mp)
    xmax = max(p[0] for p in mp)
    row = 0
    while yy <= ymax:
        xx = xmin + (row % 2) * 5
        while xx <= xmax:
            jx = xx + random.uniform(-1.5, 1.5)
            jy = yy + random.uniform(-1, 1)
            rect = (jx - 3.5, jy - 2.6, jx + 3.5, jy + 0.6)
            corners = [(rect[0], jy), (rect[2], jy), (jx, rect[1])]
            if all(pip(c, mp) and in_land(c) for c in corners) and glyph_free(rect, 0.6) \
                    and not glyph_rects.hits(rect, 0.6):
                marsh_svg.append('<use xlink:href="#tuft" x="%s" y="%s"/>' % (f1(jx), f1(jy)))
                glyph_rects.add(rect)
            xx += 10
        yy += 6.5
        row += 1

# heath dots
heath_svg = []
hp = D['heaths'][0]['pts']
for _ in range(500):
    x = random.uniform(560, 700)
    y = random.uniform(480, 610)
    rect = (x - 1, y - 1, x + 1, y + 1)
    if pip((x, y), hp) and glyph_free(rect, 0.8) and not glyph_rects.hits(rect, 1.2):
        heath_svg.append('M%s,%sh0' % (f1(x), f1(y)))
        glyph_rects.add(rect)

# village texture: density follows the land types (the population map)
vill = []


def land_class(p):
    if not in_realm(p):
        return None
    if pip(p, mtn_poly):
        return 'fells'
    for fp in forest_polys.values():
        if pip(p, fp):
            return 'forest'
    for mp in marsh_polys.values():
        if pip(p, mp):
            return 'marsh'
    if pip(p, hp):
        return 'heath'
    for hpn, hpp in hill_polys.items():
        if pip(p, hpp):
            return 'hills'
    return 'lowland'


KEEP = {'lowland': 1.0, 'hills': 0.45, 'heath': 0.22, 'fells': 0.1, 'forest': 0.06, 'marsh': 0.08}
sp = 8.5
yy = 40
row = 0
while yy < 800:
    xx = 100 + (row % 2) * sp / 2
    while xx < 910:
        x = xx + random.uniform(-2.8, 2.8)
        y = yy + random.uniform(-2.8, 2.8)
        lc = land_class((x, y))
        if lc and random.random() < KEEP[lc]:
            rect = (x - 0.9, y - 0.9, x + 0.9, y + 0.9)
            if glyph_free(rect, 1.6) and not glyph_rects.hits(rect, 1.0) and not \
                    pip((x, y), [(ZOOM[0], ZOOM[1]), (ZOOM[2], ZOOM[1]), (ZOOM[2], ZOOM[3]), (ZOOM[0], ZOOM[3])]):
                vill.append('M%s,%sh0' % (f1(x), f1(y)))
        xx += sp
    yy += sp * 0.87
    row += 1

# ---------------------------------------------------------- legend panels ---
LEG = []
LEG_FS = 6.9


def leg_row(kind, x, y):
    """Draw a legend sample centred at (x, y)."""
    water = lambda dy=0: '<path d="M%s,%sh16" stroke="%s" stroke-width="2"/>' % (f1(x - 8), f1(y + dy), C['river'])
    if kind == 'capital':
        return g_capital(x, y, 0.72)
    if kind == 'city':
        return g_city(x, y, county=False, k=0.85)
    if kind == 'town':
        return g_town(x, y)
    if kind == 'walled':
        return g_town(x, y, True)
    if kind == 'county':
        return g_town(x, y, False, True)
    if kind == 'seat':
        return g_town(x - 2, y + 2.2, False, True, k=0.75) + g_pennant(x - 2, y - 0.6)
    if kind == 'market':
        return g_market(x, y)
    if kind == 'villages':
        return ''.join(circ(x + dx, y + dy, 0.65, '#8f7a5c') for dx, dy in
                       ((-5, -2), (-1, 1.5), (3, -2.5), (5.5, 2), (-4, 3), (1, -3.5)))
    if kind == 'deserted':
        return g_deserted(x, y + 0.6)
    if kind == 'ruin':
        return g_ruin_town(x, y)
    if kind == 'cathedral':
        return g_cathedral(x, y + 0.4, 0.95)
    if kind == 'arch':
        return g_cross(x, y, True, 1.1)
    if kind == 'abbey':
        return g_abbey(x, y + 0.3)
    if kind == 'commandery':
        return g_commandery(x - 1, y)
    if kind == 'shrine':
        return g_scallop(x, y - 0.6, 0.95)
    if kind == 'great_castle':
        return '<path d="%s" fill="%s"/>' % (great_castle_path(x, y + 0.6, 0.85), C['ink'])
    if kind == 'castle':
        return g_castle(x, y, 'royal')
    if kind == 'frontier':
        return g_castle(x, y, 'frontier')
    if kind == 'baronial':
        return g_castle(x, y, 'baronial')
    if kind == 'motte':
        return g_motte(x, y + 0.6)
    if kind == 'hillfort':
        return g_hillfort(x, y)
    if kind == 'dyke':
        return dyke_svg([(x - 8, y + 1.2), (x + 8, y + 1.2)])
    if kind == 'residence':
        return g_crown(x, y)
    if kind == 'beacon':
        return g_beacon(x, y + 1.2)
    if kind == 'mine':
        return g_mine(x, y)
    if kind == 'salt':
        return g_salt(x, y)
    if kind == 'quarry':
        return g_quarry(x, y)
    if kind == 'mill':
        return g_mill(x, y)
    if kind == 'vines':
        return g_vines(x, y)
    if kind == 'arsenal':
        return g_arsenal(x, y)
    if kind == 'industry':
        return g_industry(x, y)
    if kind == 'fair':
        return ('<text x="%s" y="%s" font-size="5.6" font-style="italic" text-anchor="middle" fill="%s">Sept.</text>' % (
            f1(x), f1(y + 2), C['feature_text']))
    if kind == 'royal_road':
        return '<path d="M%s,%sh16" stroke="%s" stroke-width="2.1"/>' % (f1(x - 8), f1(y), C['road'])
    if kind == 'road':
        return '<path d="M%s,%sh16" stroke="%s" stroke-width="0.9"/>' % (f1(x - 8), f1(y), C['road2'])
    if kind == 'old_road':
        return '<path d="M%s,%sh16" stroke="%s" stroke-width="2.0"/>' % (f1(x - 8), f1(y), OLD_ROAD)
    if kind == 'pilgrim':
        return ('<path d="M%s,%sh16" stroke="%s" stroke-width="0.9"/>' % (f1(x - 8), f1(y + 1.2), C['road2']) +
                g_scallop(x - 3.5, y, 0.62) + g_scallop(x + 4.5, y, 0.62))
    if kind == 'mule':
        return '<path d="M%s,%sh16" stroke="%s" stroke-width="1.1" stroke-dasharray="0.1 2.1" stroke-linecap="round"/>' % (
            f1(x - 7.5), f1(y), C['road2'])
    if kind == 'sealane':
        return '<path d="M%s,%sh16" stroke="#5d93ab" stroke-width="1.1" stroke-dasharray="0.1 2.4" stroke-linecap="round"/>' % (
            f1(x - 7.5), f1(y))
    if kind == 'bridge':
        return (water() + '<path d="M%s,%sv10" stroke="%s" stroke-width="0.9"/>' % (f1(x), f1(y - 5), C['road2']) +
                g_bridge(x, y, 0))
    if kind == 'ford':
        return (water() + g_ford(x, y, 0))
    if kind == 'ferry':
        return (water() + g_ferry(x - 2, y, 0))
    if kind == 'pass':
        return g_pass(x, y + 0.4)
    if kind == 'port':
        return g_anchor(x - 4, y - 1.6, 1.0, quay=True) + g_anchor(x + 5, y - 0.4, 0.8)
    if kind == 'light':
        return g_light(x, y + 0.6)
    if kind == 'nav':
        return '<path d="M%s,%sq4,-3 7.5,0t7.5,0" fill="none" stroke="%s" stroke-width="2.3"/>' % (
            f1(x - 7.5), f1(y), C['river'])
    if kind == 'boat':
        return ('<path d="M%s,%sq4,-3 7.5,0t7.5,0" fill="none" stroke="%s" stroke-width="2.3"/>' % (
            f1(x - 7.5), f1(y + 2), C['river']) + g_boat(x, y + 0.4))
    if kind == 'stream':
        return '<path d="M%s,%sq4,-3 7.5,0t7.5,0" fill="none" stroke="%s" stroke-width="0.9"/>' % (
            f1(x - 7.5), f1(y), C['river'])
    if kind == 'mountains':
        return ('<rect x="%s" y="%s" width="16" height="9" fill="%s"/>' % (f1(x - 8), f1(y - 4.5), C['mtn_tint']) +
                '<use xlink:href="#mtn" transform="translate(%s %s) scale(0.62)"/>' % (f1(x - 3), f1(y + 3.5)) +
                '<use xlink:href="#mtn" transform="translate(%s %s) scale(0.5)"/>' % (f1(x + 3.5), f1(y + 3.5)))
    if kind == 'hills':
        return ('<rect x="%s" y="%s" width="16" height="9" fill="%s"/>' % (f1(x - 8), f1(y - 4.5), C['hill_tint']) +
                '<use xlink:href="#hill" x="%s" y="%s"/>' % (f1(x - 2.5), f1(y + 2.5)) +
                '<use xlink:href="#hill" x="%s" y="%s"/>' % (f1(x + 3.5), f1(y - 0.5)))
    if kind == 'forest':
        return ('<rect x="%s" y="%s" width="16" height="9" fill="%s"/>' % (f1(x - 8), f1(y - 4.5), C['forest_tint']) +
                '<use xlink:href="#tree" x="%s" y="%s"/>' % (f1(x - 3.5), f1(y + 0.5)) +
                '<use xlink:href="#tree" x="%s" y="%s"/>' % (f1(x + 3.5), f1(y - 0.2)))
    if kind == 'royal_forest':
        return '<path d="M%s,%sh16" stroke="#4d7a3a" stroke-width="1.0" stroke-dasharray="%s"/>' % (
            f1(x - 8), f1(y), FOREST_DASH)
    if kind == 'marsh':
        return ('<rect x="%s" y="%s" width="16" height="9" fill="%s"/>' % (f1(x - 8), f1(y - 4.5), C['marsh_tint']) +
                '<use xlink:href="#tuft" x="%s" y="%s"/>' % (f1(x - 3), f1(y + 2.5)) +
                '<use xlink:href="#tuft" x="%s" y="%s"/>' % (f1(x + 3.5), f1(y - 0.5)))
    if kind == 'heath':
        return ('<rect x="%s" y="%s" width="16" height="9" fill="%s"/>' % (f1(x - 8), f1(y - 4.5), C['heath_tint']) +
                ''.join(circ(x + dx, y + dy, 0.6, C['heath_dot']) for dx, dy in
                        ((-5, -2), (-2, 1.5), (1, -2), (4, 1.8), (6, -1.5), (-5.5, 2.5))))
    if kind == 'realm':
        return '<path d="M%s,%sh16" stroke="%s" stroke-width="2.2" stroke-dasharray="%s"/>' % (
            f1(x - 8), f1(y), C['border'], REALM_DASH)
    if kind == 'fief':
        return '<path d="M%s,%sh16" stroke="%s" stroke-width="1.1" stroke-dasharray="%s" opacity="0.85"/>' % (
            f1(x - 8), f1(y), C['border'], FIEF_DASH)
    if kind == 'liberty':
        return ('<rect x="%s" y="%s" width="16" height="9" fill="#ece0f2"/>' % (f1(x - 8), f1(y - 4.5)) +
                '<path d="M%s,%sh16" stroke="%s" stroke-width="0.9" stroke-dasharray="%s"/>' % (
                    f1(x - 8), f1(y), C['purple'], LIBERTY_DASH))
    if kind == 'band':
        return '<rect x="%s" y="%s" width="16" height="9" fill="url(#hatch)" stroke="none"/>' % (f1(x - 8), f1(y - 4.5))
    if kind == 'debatable':
        return '<rect x="%s" y="%s" width="16" height="9" fill="url(#stripes)" stroke="%s" stroke-width="0.6" stroke-dasharray="%s"/>' % (
            f1(x - 8), f1(y - 4.5), C['border'], DISPUTE_DASH)
    if kind == 'zoom':
        return '<rect x="%s" y="%s" width="9" height="9" fill="none" stroke="%s" stroke-width="0.8"/>' % (
            f1(x - 4.5), f1(y - 4.5), C['ink'])
    raise ValueError(kind)


def legend_panel(rows, x0, y0, x1, title=None):
    out = []
    y = y0 + 6
    body = []
    if title:
        body.append('<text x="%s" y="%s" font-size="8" font-weight="bold" letter-spacing="1.2" fill="%s">%s</text>' % (
            f1(x0 + 6), f1(y + 6.5), C['ink'], esc(title)))
        y += 12
    for kind, text in rows:
        if kind == 'h':
            y += 2.5
            body.append('<text x="%s" y="%s" font-size="6.6" font-style="italic" font-weight="bold" fill="%s">%s</text>' % (
                f1(x0 + 6), f1(y + 5.4), C['region_text'], esc(text)))
            y += 8.4
            continue
        cy = y + ROW / 2
        if x0 + 26 + tw(text, LEG_FS) > x1 - 3:
            sys.stderr.write('LEGEND TOO WIDE: %s (%.1f)\n' % (text, x0 + 26 + tw(text, LEG_FS)))
        body.append(leg_row(kind, x0 + 15, cy))
        body.append('<text x="%s" y="%s" font-size="%s" fill="%s">%s</text>' % (
            f1(x0 + 26), f1(cy + 2.4), f1(LEG_FS), C['ink'], esc(text)))
        y += ROW
    y1 = y + 4
    out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="#fbf6e9" stroke="%s" stroke-width="0.9"/>' % (
        f1(x0), f1(y0), f1(x1 - x0), f1(y1 - y0), C['mtn_line']))
    out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="2" fill="none" stroke="%s" stroke-width="0.4"/>' % (
        f1(x0 + 2), f1(y0 + 2), f1(x1 - x0 - 4), f1(y1 - y0 - 4), C['mtn_line']))
    out.extend(body)
    return ''.join(out), y1


# =========================================================== assemble svg ===
P = []
P.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1000 800" width="1000" height="800" '
         'font-family="%s" role="img" aria-labelledby="map-title map-desc">' % FONT)
P.append('<title id="map-title">Schematic map of the worked-example kingdom of Daravel, c. 1300</title>')
P.append('<desc id="map-desc">Kingdom of Daravel (guide chapter 12): the capital Hallowbridge at the head of the Ambre '
         'estuary, 3 cities, 38 towns, 26 of about 180 market towns, the Fells along the west border, the Harnwood '
         'in the north, the North March frontier band facing Thelland, rivers, royal highways, castles, cathedrals, '
         'abbeys, ports and ruins. Coordinates follow worked-example-layout.json (2 units = 1 km).</desc>')

# defs
P.append('<defs>')
P.append('<clipPath id="land"><path d="%s"/></clipPath>' % LAND_D)
P.append('<clipPath id="seaopen"><path d="%s"/></clipPath>' % SEA_OPEN_D)
P.append('<pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<rect width="1.1" height="5" fill="%s" opacity="0.32"/></pattern>' % C['border'])
# alternating colours of the two claimants (Daravel red, Thelland grey-brown)
P.append('<pattern id="stripes" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<rect width="2" height="4" fill="%s" opacity="0.55"/><rect x="2" width="2" height="4" fill="#7b6d58" '
         'opacity="0.45"/></pattern>' % C['border'])
# mountain glyph: base at (0,0), width 14, height 9
P.append('<g id="mtn"><path d="M-7,0L-1.2,-9L7,0Z" fill="%s"/><path d="M-1.2,-9L7,0H1.6L0.4,-4.2Z" fill="%s"/>'
         '<path d="M-7,0L-1.2,-9L7,0" fill="none" stroke="%s" stroke-width="0.8" stroke-linejoin="round"/></g>' % (
             C['mtn_fill'], C['mtn_shade'], C['mtn_line']))
P.append('<path id="hill" d="M-4.5,0Q-1.5,-4.6 4.5,0" fill="none" stroke="%s" stroke-width="0.85" stroke-linecap="round"/>' %
         C['hill_line'])
P.append('<g id="tree"><path d="M0,3.2V0.6" stroke="%s" stroke-width="0.7"/>'
         '<circle cx="0" cy="-0.6" r="2.5" fill="%s" stroke="%s" stroke-width="0.6"/></g>' % (
             C['tree_line'], C['tree_fill'], C['tree_line']))
P.append('<path id="tuft" d="M-3.4,0H3.4M-2,-0.9H0.6M0,0V-2.3M-1.4,0L-2.2,-1.8M1.4,0L2.2,-1.8" fill="none" '
         'stroke="%s" stroke-width="0.6" stroke-linecap="round"/>' % C['marsh_line'])
P.append('</defs>')

# background
P.append('<rect width="1000" height="800" fill="%s"/>' % C['bg'])
P.append('<path d="%s" fill="%s"/>' % (realm_d, C['realm']))

# land-use tints (clipped to land)
P.append('<g clip-path="url(#land)">')
P.append('<path d="%s" fill="%s"/>' % (segs_d(cr_segments(mtn_poly, closed=True, alpha=0.5)) + 'Z', C['mtn_tint']))
for hname, hpp in hill_polys.items():
    P.append('<path d="%s" fill="%s"/>' % (segs_d(cr_segments(hpp, closed=True)) + 'Z', C['hill_tint']))
P.append('<path d="%s" fill="%s"/>' % (segs_d(cr_segments(hp, closed=True)) + 'Z', C['heath_tint']))
for fname, fp in forest_polys.items():
    P.append('<path d="%s" fill="%s" stroke="#b9cf9c" stroke-width="0.7"/>' % (
        segs_d(cr_segments(fp, closed=True)) + 'Z', C['forest_tint']))
for mname, mp in marsh_polys.items():
    P.append('<path d="%s" fill="%s"/>' % (segs_d(cr_segments(mp, closed=True)) + 'Z', C['marsh_tint']))
lib = borders['Liberty of Holmstow']['pts']
P.append('<path d="%s" fill="#e6d7ef" opacity="0.55"/>' % (segs_d(cr_segments(lib[:-1], closed=True)) + 'Z'))
# frontier band and debatable land
fb = D['frontier_band']['pts']
P.append('<path d="%s" fill="url(#hatch)"/>' % (segs_d(cr_segments(fb[:19])) + 'L' +
                                                 segs_d(cr_segments(fb[19:]))[1:] + 'Z'))
dl = D['debatable_land']['pts']
P.append('<path d="%s" fill="url(#stripes)" stroke="%s" stroke-width="0.7" stroke-dasharray="%s"/>' % (
    poly_d(dl), C['border'], DISPUTE_DASH))
P.append('</g>')

# village texture and terrain glyphs
P.append('<path d="%s" stroke="#8f7a5c" stroke-width="1.25" stroke-linecap="round" opacity="0.55"/>' % ''.join(vill))
P.append('<path d="%s" stroke="%s" stroke-width="1.2" stroke-linecap="round" opacity="0.8"/>' % (
    ''.join(heath_svg), C['heath_dot']))
P.append('<g>%s</g>' % ''.join(hills_svg))
P.append('<g>%s</g>' % ''.join(marsh_svg))
P.append('<g>%s</g>' % ''.join(trees_svg))
P.append('<g>%s</g>' % ''.join(terrain))

# Kingswood Chase legal boundary
rf = D['royal_forest_boundary']['pts']
P.append('<path d="%s" fill="none" stroke="#4d7a3a" stroke-width="1.0" stroke-dasharray="%s"/>' %
         (segs_d(cr_segments(rf, closed=True)) + 'Z', FOREST_DASH))

# sea + water lining
P.append('<path d="%s" fill="%s"/>' % (SEA_D, C['sea']))
P.append('<g clip-path="url(#seaopen)" fill="none">')
for wdt, col in ((26, C['sea_line']), (24.8, C['sea']), (15, C['sea_line']), (13.8, C['sea']), (6.5, C['sea_line']),
                 (5.4, C['sea'])):
    P.append('<path d="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (OUTER_COAST_D, col, f1(wdt)))
P.append('</g>')
P.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.1" stroke-linejoin="round"/>' % (
    segs_d(coast_segs), C['coast']))

# sea lanes
for sr in D['sea_routes']:
    segs = cr_segments(sr['pts'])
    P.append('<path d="%s" fill="none" stroke="#5d93ab" stroke-width="1.1" stroke-dasharray="0.1 2.4" '
             'stroke-linecap="round"/>' % segs_d(segs))

# rivers
for rv in rivers:
    name = rv['name']
    segs, pts = river_geo[name]
    if name == 'Ambre':
        # navigable (thick) from Cheapford down; thinner above Cheapford
        k = [tuple(p) for p in rv['pts']].index((380, 438))
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-linecap="round"/>' % (
            segs_d(segs[:k]), C['river']))
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.7" stroke-linecap="round"/>' % (
            segs_d(segs[k:]), C['river']))
    elif name == 'Lisk':
        k = [tuple(p) for p in rv['pts']].index((430, 292))
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.1" stroke-linecap="round"/>' % (
            segs_d(segs[:k]), C['river']))
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.1" stroke-linecap="round"/>' % (
            segs_d(segs[k:]), C['river']))
    elif name in ('Brim', 'Wend'):
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round"/>' % (
            segs_d(segs), C['river']))
    elif name == 'Skel':
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-linecap="round"/>' % (
            segs_d(segs), C['river']))
    else:
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.85" stroke-linecap="round"/>' % (
            segs_d(segs), C['river']))

# Thelling Dyke (old earthwork)
dyke = [r_ for r_ in D['ruins_and_old_layers'] if 'pts' in r_][0]
dsegs = cr_segments(dyke['pts'])
P.append(dyke_svg(dyke_pts))

# borders
for b in D['borders']:
    segs, pts = border_geo[b['name']]
    cls = b['class']
    if cls == 'realm':
        P.append('<path d="%s" fill="none" stroke="#fbf3df" stroke-width="3.6" opacity="0.7"/>' % segs_d(segs))
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="%s"/>' % (
            segs_d(segs), C['border'], REALM_DASH))
    elif cls == 'great_fief':
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.1" stroke-dasharray="%s" opacity="0.85"/>' % (
            segs_d(segs), C['border'], FIEF_DASH))
    else:
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.9" stroke-dasharray="%s"/>' % (
            segs_d(segs), C['purple'], LIBERTY_DASH))

# roads
for rd in roads:
    segs, pts = road_geo[rd['name']]
    d = segs_d(segs) if segs else poly_d(pts, closed=False)
    cls = rd['class']
    if cls == 'regional_road':
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.9" stroke-linejoin="round"/>' % (d, C['road2']))
for rd in roads:
    segs, pts = road_geo[rd['name']]
    d = segs_d(segs) if segs else poly_d(pts, closed=False)
    cls = rd['class']
    if cls == 'old_road_in_use':
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-linejoin="round"/>' % (d, OLD_ROAD))
    elif cls == 'pilgrim_road':
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.9" stroke-linejoin="round"/>' % (d, C['road2']))
        L_ = path_len(pts)
        dd = 9.0
        while dd < L_ - 6:
            (sx_, sy_), _ = point_at(pts, dd)
            P.append(g_scallop(sx_, sy_ - 1.2, 0.62))
            dd += 17.0
for rd in roads:
    segs, pts = road_geo[rd['name']]
    d = segs_d(segs) if segs else poly_d(pts, closed=False)
    if rd['class'] == 'royal_highway':
        P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.1" stroke-linejoin="round" stroke-linecap="round"/>' % (
            d, C['road']))
# mule path over the Carrow Gap
P.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.1" stroke-dasharray="0.1 2.1" stroke-linecap="round"/>' % (
    segs_d(cr_segments(D['passes'][1]['path'])), C['road2']))

# zoom box
P.append('<rect x="%s" y="%s" width="%s" height="%s" fill="none" stroke="%s" stroke-width="0.8"/>' % (
    ZOOM[0], ZOOM[1], ZOOM[2] - ZOOM[0], ZOOM[3] - ZOOM[1], C['ink']))

# symbols and labels
P.append('<g>%s</g>' % ''.join(svg_sym))
P.append('<g>%s</g>' % ''.join(svg_lab))

# ----- title cartouche
tx0, ty0, tx1, ty1 = TITLE_BOX
P.append('<g data-nocheck="1">')
P.append('<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="#fbf6e9" stroke="%s" stroke-width="0.9"/>' % (
    tx0, ty0, tx1 - tx0, ty1 - ty0, C['mtn_line']))
P.append('<rect x="%s" y="%s" width="%s" height="%s" rx="2" fill="none" stroke="%s" stroke-width="0.4"/>' % (
    tx0 + 2, ty0 + 2, tx1 - tx0 - 4, ty1 - ty0 - 4, C['mtn_line']))
P.append('<text x="%s" y="%s" font-size="14" font-weight="bold" letter-spacing="1.6" fill="%s">THE KINGDOM OF DARAVEL</text>' % (
    tx0 + 9, ty0 + 19, C['ink']))
P.append('<text x="%s" y="%s" font-size="7.6" font-style="italic" fill="%s">c. 1300 · schematic map of the worked example (chapter 12)</text>' % (
    tx0 + 9, ty0 + 31, C['ink2']))
P.append('<text x="%s" y="%s" font-size="6.8" fill="%s">Shown: the capital, 3 cities, all 38 towns and 26 of the ~180</text>' % (
    tx0 + 9, ty0 + 42, C['ink2']))
P.append('<text x="%s" y="%s" font-size="6.8" fill="%s">market towns; the ~7,700 villages appear only as texture.</text>' % (
    tx0 + 9, ty0 + 51, C['ink2']))
P.append('</g>')

# ----- legends
leg1, y_end1 = legend_panel(LEG_TOP, PANEL_TOP[0], PANEL_TOP[1], PANEL_TOP[2], 'KEY')
P.append('<g data-nocheck="1">%s</g>' % leg1)

# ----- scale bar
sx0, sy0, sx1, sy1 = SCALE_BOX
P.append('<g data-nocheck="1">')
P.append('<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="#fbf6e9" stroke="%s" stroke-width="0.9"/>' % (
    sx0, sy0, sx1 - sx0, sy1 - sy0, C['mtn_line']))
bx = sx0 + 14
by = sy0 + 15
# km bar: 0-100 km = 200 units
for i in range(5):
    P.append('<rect x="%s" y="%s" width="40" height="3.2" fill="%s" stroke="%s" stroke-width="0.5"/>' % (
        f1(bx + i * 40), f1(by), C['ink'] if i % 2 == 0 else '#fffaf0', C['ink']))
for i, v in enumerate([0, 20, 40, 60, 80, 100]):
    P.append('<text x="%s" y="%s" font-size="6.4" text-anchor="middle" fill="%s">%s</text>' % (
        f1(bx + i * 40), f1(by - 2.5), C['ink'], v))
P.append('<text x="%s" y="%s" font-size="6.6" fill="%s">km</text>' % (f1(bx + 206), f1(by + 3.2), C['ink']))
# mile bar: 0-60 mi; 1 mi = 3.22 units
mi = D['canvas']['units_per_mile']
mby = by + 7.5
for i in range(6):
    P.append('<rect x="%s" y="%s" width="%s" height="3.2" fill="%s" stroke="%s" stroke-width="0.5"/>' % (
        f1(bx + i * 10 * mi), f1(mby), f1(10 * mi), C['ink'] if i % 2 == 1 else '#fffaf0', C['ink']))
for i, v in enumerate([0, 10, 20, 30, 40, 50, 60]):
    P.append('<text x="%s" y="%s" font-size="6.4" text-anchor="middle" fill="%s">%s</text>' % (
        f1(bx + i * 10 * mi), f1(mby + 10.5), C['ink'], v))
P.append('<text x="%s" y="%s" font-size="6.6" fill="%s">miles</text>' % (f1(bx + 206), f1(mby + 3.2), C['ink']))
P.append('<text x="%s" y="%s" font-size="6.2" font-style="italic" fill="%s">2 units = 1 km</text>' % (
    f1(bx + 232), f1(by + 10), C['ink2']))
P.append('</g>')

# ----- compass
cx, cy, cr = COMPASS
P.append('<g data-nocheck="1">')
P.append(circ(cx, cy, cr * 0.62, 'none', C['mtn_line'], 0.6))
P.append('<path d="M%s,%sL%s,%sL%s,%sZ" fill="%s"/>' % (f1(cx), f1(cy - cr), f1(cx + 4.5), f1(cy), f1(cx - 4.5), f1(cy),
                                                         C['ink']))
P.append('<path d="M%s,%sL%s,%sL%s,%sZ" fill="#fffaf0" stroke="%s" stroke-width="0.7"/>' % (
    f1(cx), f1(cy + cr), f1(cx + 4.5), f1(cy), f1(cx - 4.5), f1(cy), C['ink']))
P.append('<path d="M%s,%sL%s,%sL%s,%sZ" fill="#fffaf0" stroke="%s" stroke-width="0.7"/>' % (
    f1(cx - cr * 0.75), f1(cy), f1(cx), f1(cy - 3.5), f1(cx), f1(cy + 3.5), C['ink']))
P.append('<path d="M%s,%sL%s,%sL%s,%sZ" fill="%s"/>' % (
    f1(cx + cr * 0.75), f1(cy), f1(cx), f1(cy - 3.5), f1(cx), f1(cy + 3.5), C['ink']))
P.append('<text x="%s" y="%s" font-size="10" font-weight="bold" text-anchor="middle" fill="%s" stroke="%s" '
         'stroke-width="2.4" paint-order="stroke">N</text>' % (f1(cx), f1(cy - cr - 3), C['ink'], C['sea']))
P.append('</g>')

P.append('</svg>')

svg = '\n'.join(P)
leg2, y_end2 = legend_panel(LEG_BOT, PANEL_BOT[0], PANEL_BOT[1], PANEL_BOT[2])
leg2_y0 = PANEL_BOT[1]
leg3, y_end3 = legend_panel(LEG_SEA, PANEL_SEA[0], PANEL_SEA[1], PANEL_SEA[2])
svg = svg.replace('</svg>', '<g data-nocheck="1">%s%s</g>\n</svg>' % (leg2, leg3))
open(OUT, 'w').write(svg)
sys.stderr.write('top legend ends at %.1f; bottom legend %.1f-%.1f\n' % (y_end1, leg2_y0, y_end2))
sys.stderr.write('FAILED: %s\n' % failed)
sys.stderr.write('size %d bytes; mountains %d hills %d trees %d marsh %d villages %d\n' % (
    len(svg), len(mtns), len(hills_svg), len(trees_svg), len(marsh_svg), len(vill)))
