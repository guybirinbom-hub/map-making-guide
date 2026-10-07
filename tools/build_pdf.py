#!/usr/bin/env python3
"""Build map-making-guide.pdf: every chapter in guide/ combined into one book.

Usage:  python3 tools/build_pdf.py [--only 00,05] [--html-only]
Needs:  pip install weasyprint markdown-it-py mdit-py-plugins linkify-it-py beautifulsoup4
        node + Playwright/Chromium (only to make tools/build/map.png the first time)

Layout: A4, two text columns, tables and figures across the full width,
a clickable "Chapters" page with page numbers, and PDF bookmarks.

WeasyPrint drops content when a `column-span: all` element sits inside a
multi-column box at a page break, so nothing spans columns here: each chapter
is cut into separate blocks (two-column text runs, full-width headings,
tables and figures). check_pdf() fails the build if a heading goes missing.
"""
import html
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "guide"
TOOLS = ROOT / "tools"
BUILD = TOOLS / "build"
FONTS = TOOLS / "fonts"
OUT_PDF = ROOT / "map-making-guide.pdf"
REPO_URL = "https://github.com/guybirinbom-hub/map-making-guide/blob/HEAD/"

# GitHub-style heading slugs, shared with the link checker
_spec = importlib.util.spec_from_file_location("check_links", TOOLS / "check_links.py")
_cl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cl)
slug = _cl.slug

CALLOUTS = {
    "Map tip:": "maptip",
    "Rule of thumb:": "rule",
    "Later era (1500s+):": "later",
    "Fantasy twist:": "fantasy",
}
WIDE = {"h2", "figure", "section"}          # always full width
WIDE_CLASSES = {"table-wrap", "summary"}
SHORT_TABLE_ROWS = 4                       # tables this short never split

md = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True}).enable(
    ["table", "strikethrough", "linkify", "smartquotes"])
md.use(tasklists_plugin)


def chapter_files(only=None):
    files = sorted(GUIDE.glob("[0-9][0-9]-*.md"))
    if only:
        files = [f for f in files if f.name[:2] in only]
    return files


def chapter_label(num):
    return "Chapter %d" % int(num)


def rewrite_href(href, num):
    """Turn a Markdown link target into an in-PDF anchor (or a web link)."""
    if re.match(r"^[a-z]+:", href):
        return href
    if href.startswith("#"):
        return "#c%s-%s" % (num, href[1:])
    path, _, frag = href.partition("#")
    m = re.match(r"^(?:\./)?(\d\d)-[^/]+\.md$", path)
    if m:
        return "#c%s-%s" % (m.group(1), frag) if frag else "#c%s" % m.group(1)
    if path.startswith("../"):
        return REPO_URL + path[3:] + ("#" + frag if frag else "")
    return REPO_URL + "guide/" + href


def nbsp_last(text):
    """Keep the last two words of a title together."""
    return re.sub(r" (\S+)$", " \\1", text.strip())


def convert_chapter(path):
    num = path.name[:2]
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    tokens = md.parse(src)

    seen, title, sections = {}, None, []
    out_tokens = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == "heading_open":
            raw = lines[tok.map[0]].lstrip("#").strip()
            s = slug(raw)
            n = seen.get(s, 0)
            seen[s] = n + 1
            anchor = s if n == 0 else "%s-%d" % (s, n)
            if tok.tag == "h1":
                title = tokens[i + 1].content
                i += 3  # drop the h1; the chapter header replaces it
                continue
            tok.attrSet("id", "c%s-%s" % (num, anchor))
            if tok.tag == "h2":
                sections.append((tokens[i + 1].content, "c%s-%s" % (num, anchor)))
        elif tok.type == "hr":
            i += 1  # section rules come from the h2 itself
            continue
        elif tok.type == "blockquote_open":
            j = i + 1
            while j < len(tokens) and tokens[j].type != "inline":
                j += 1
            kids = [k for k in (tokens[j].children or []) if not (k.type == "text" and k.content == "")]
            if len(kids) > 1 and kids[0].type == "strong_open" and kids[1].content in CALLOUTS:
                tok.attrSet("class", "callout callout-" + CALLOUTS[kids[1].content])
                kids[1].content = kids[1].content.rstrip(":")
                if len(kids) > 3 and kids[3].type == "text":
                    kids[3].content = kids[3].content.lstrip()
        elif tok.type == "inline":
            kids = tok.children or []
            for k, child in enumerate(kids):
                if child.type != "link_open":
                    continue
                old = child.attrGet("href")
                new = rewrite_href(old, num)
                child.attrSet("href", new)
                if child.markup == "linkify":
                    child.attrSet("class", "url")
                # in the cheat sheet, say which chapter a source link points to
                m = re.match(r"^(?:\./)?(\d\d)-", old)
                if num == "13" and m and k + 1 < len(kids) and kids[k + 1].type == "text" \
                        and not re.match(r"^\d", kids[k + 1].content):
                    kids[k + 1].content = "%s %s" % (m.group(1), kids[k + 1].content)
        out_tokens.append(tok)
        i += 1

    body = md.renderer.render(out_tokens, md.options, {})
    return {"num": num, "title": title, "sections": sections, "body": body}


# ---------------------------------------------------------------- typography

ZWSP = "\u200b"


def break_url(text):
    """Allow line breaks after / _ - . = & in a printed URL (not inside https://)."""
    m = re.match(r"^(https?://)(.*)$", text)
    if not m:
        return text
    return m.group(1) + re.sub(r"([/_\-.=&?])(?=.)", "\\1" + ZWSP, m.group(2))


UNITS = r"km²|km|sq\u00a0mi|sq mi|mi|ha|kg|kcal|cm|mm|m|ft|t"


def typeset(html_text):
    """Non-breaking spaces and unbreakable spans in running text (never inside tags)."""
    def fix(m):
        t = m.group(1)
        t = t.replace("sq mi", "sq\u00a0mi")
        t = re.sub(r"(\d) (%s)(?![\w²])" % UNITS, "\\1\u00a0\\2", t)
        t = re.sub(r"\bc\. (?=\d)", "c.\u00a0", t)
        # number ranges like 8th–11th or 1,500–2,000 stay on one line
        t = re.sub(r"(?<![\w,.])(\d[\d,.]*(?:st|nd|rd|th|s)?–\d[\d,.]*(?:st|nd|rd|th|s)?%?)",
                   r'<span class="nw">\1</span>', t)
        # place-name endings like -ley or -thwaite never split after the hyphen
        t = re.sub(r"(?<=[\s(“‘/])(-[A-Za-zÀ-ž]{1,14})", r'<span class="nw">\1</span>', t)
        return ">" + t + "<"
    return re.sub(r">([^<]+)<", fix, html_text)


# ---------------------------------------------------------------- layout blocks

def classes(el):
    return set(el.get("class") or [])


def is_wide(el):
    return el.name in WIDE or bool(classes(el) & WIDE_CLASSES)


def is_lead_in(el):
    """A heading or a short 'colon' sentence that introduces the next table."""
    if el.name in ("h3", "h4"):
        return True
    if el.name == "p":
        text = el.get_text(" ", strip=True)
        return text.endswith(":") and len(text) < 260
    return False


CHUNK_CHARS = 2400   # WeasyPrint balances short two-column blocks reliably


def chunks(run):
    """Split a two-column run into blocks of about CHUNK_CHARS characters of text."""
    if not run:
        return []
    if kind_of_heading_only(run):
        return [run]
    out, cur, size = [], [], 0
    for e in run:
        n = len(e.get_text())
        if cur and e.name in ("h3", "h4"):  # each subheading starts its own block
            out.append(cur)
            cur, size = [], 0
        elif cur and size + n > CHUNK_CHARS and cur[-1].name not in ("h3", "h4"):
            out.append(cur)
            cur, size = [], 0
        cur.append(e)
        size += n
    if cur:
        out.append(cur)
    return out


def kind_of_heading_only(run):
    return len(run) <= 1


def layout_chapter(ch, map_png):
    """Cut a chapter's HTML into full-width blocks and two-column runs."""
    soup = BeautifulSoup('<div id="root">%s</div>' % ch["body"], "html.parser")
    root = soup.find(id="root")

    # tables: wrapper, short ones kept whole
    for table in root.find_all("table"):
        rows = len(table.find_all("tr")) - 1
        wrap = soup.new_tag("div", attrs={"class": "table-wrap" + (" keep" if rows <= SHORT_TABLE_ROWS else "")})
        table.wrap(wrap)
    # printed URLs may break after slashes
    for a in root.find_all("a"):
        text = a.get_text()
        if text.startswith("http") and a.string is not None:
            a.string.replace_with(break_url(text))
            a["class"] = ["url"]
    # ordered lists that continue after a table keep their numbers
    for ol in root.find_all("ol", start=True):
        ol["style"] = "counter-reset: list-item %d" % (int(ol["start"]) - 1)
    # checklist boxes
    for box in root.select("input.task-list-item-checkbox"):
        box.replace_with(BeautifulSoup('<span class="tick"></span>', "html.parser"))

    items = [c for c in root.children if getattr(c, "name", None)]
    out, prelude = [], ""

    # "In this chapter" box
    for k, el in enumerate(items[:-1]):
        if el.name == "p" and el.get_text(strip=True) == "In this chapter:" and items[k + 1].name == "ul":
            nav = soup.new_tag("nav", attrs={"class": "intoc"})
            title = soup.new_tag("p", attrs={"class": "intoc-title"})
            title.string = "In this chapter"
            nav.append(title)
            nav.append(items[k + 1].extract())
            el.replace_with(nav)
            items[k:k + 2] = [nav]
            break

    # worked-example map: its own landscape page, with the italic caption under it
    for k, el in enumerate(items):
        img = el.find("img") if el.name == "p" else None
        if img is not None and "worked-example-kingdom" in img.get("src", ""):
            caption = ""
            if k + 1 < len(items) and items[k + 1].name == "p" and items[k + 1].find("em"):
                caption = items[k + 1].decode_contents()
                items.pop(k + 1)
            prelude = ('<section class="map-page"><figure><img src="%s" alt="Schematic map of Daravel">'
                       "<figcaption>%s</figcaption></figure></section>" % (map_png.as_uri(), caption))
            items.pop(k)
            break

    # quick summary and sources
    grouped, k = [], 0
    while k < len(items):
        el = items[k]
        hid = el.get("id", "") if el.name == "h2" else ""
        if hid.endswith("-quick-summary") and k + 1 < len(items) and items[k + 1].name == "ul":
            box = soup.new_tag("div", attrs={"class": "summary"})
            box.append(el)
            box.append(items[k + 1])
            grouped.append(box)
            k += 2
            continue
        if hid.endswith("-sources-and-further-reading"):
            el["class"] = ["sources-head"]
            grouped.append(el)
            grouped.append(("sources", items[k + 1:]))
            break
        grouped.append(el)
        k += 1

    run, opener_done = [], False

    def flush(kind="cols"):
        nonlocal run, opener_done
        if not run:
            return
        inner = "".join(str(e) for e in run)
        if not opener_done and kind == "cols":
            opener_done = True
            navs = [e for e in run if e.name == "nav"]
            if navs:
                rest = "".join(str(e) for e in run if e.name != "nav")
                out.append('<div class="opener"><div class="opener-text">%s</div>%s</div>' % (rest, str(navs[0])))
                run = []
                return
        notes = []
        if kind == "cols":
            while run and "callout" in classes(run[-1]) and len(notes) < 2:
                notes.insert(0, run.pop())
        cls = "cols" if kind == "cols" else "cols sources"
        for chunk in chunks(run):
            out.append('<div class="%s">%s</div>' % (cls, "".join(str(e) for e in chunk)))
        if notes:
            for e in notes:
                e["class"] = sorted(classes(e) | {"wide"})
                if len(notes) == 1:  # label on its own line above the two inner columns
                    first = e.find("p")
                    label = first.find("strong") if first else None
                    if label is not None and first.contents and first.contents[0] is label:
                        tag = BeautifulSoup('<p class="note-label"></p>', "html.parser").p
                        tag.string = label.get_text()
                        label.extract()
                        if len(e.get_text()) < 330:  # short: label left, text right
                            body = BeautifulSoup('<div class="note-body"></div>', "html.parser").div
                            for child in list(e.children):
                                body.append(child.extract())
                            e.append(tag)
                            e.append(body)
                            e["class"] = sorted(classes(e) | {"short"})
                        else:
                            e.insert(0, tag)
            out.append('<div class="note-row n%d">%s</div>' % (len(notes), "".join(str(e) for e in notes)))
        run = []

    for el in grouped:
        if isinstance(el, tuple):
            flush()
            run = list(el[1])
            flush("sources")
            continue
        if el.name == "h2":
            flush()
            opener_done = True
            out.append(str(el))
            continue
        if is_wide(el):
            if "table-wrap" in classes(el):
                leads = []
                while run and is_lead_in(run[-1]) and len(leads) < 2:
                    leads.insert(0, run.pop())
                if not leads and len(run) >= 2 and run[-2].name in ("h3", "h4") and run[-1].name == "p" \
                        and len(run[-1].get_text()) < 320:
                    leads = [run[-2], run[-1]]
                    del run[-2:]
                if leads:
                    lead = soup.new_tag("div", attrs={"class": "table-lead"})
                    for x in leads:
                        lead.append(x)
                    el.insert(0, lead)
            flush()
            out.append(str(el))
            continue
        if el.name == "h3" and run and opener_done:
            flush()
        run.append(el)
    flush()
    merged = []
    for block in out:
        if merged and merged[-1].startswith("<h2") and block.startswith('<div class="note-row'):
            merged[-1] = '<div class="keep-group">%s%s</div>' % (merged[-1], block)
        else:
            merged.append(block)
    return typeset("\n".join(merged)), prelude


# ---------------------------------------------------------------- flowchart (chapter 0)

def flowchart_html(step_anchors):
    def box(label, step=None):
        href = step_anchors.get(step)
        inner = html.escape(label)
        if href:
            inner = '<a href="#%s">%s</a>' % (href, inner)
        return '<div class="fc-box">%s</div>' % inner

    parts = [
        ("Part A", "Continent and world", [(1, "Terrain and water check"), (2, "Good farmland"),
         (3, "Population budget"), (4, "Realms and borders"), (5, "Capitals"),
         (6, "Great cities and ports"), (7, "Trade routes and sea lanes")]),
        ("Part B", "Kingdom and region", [(8, "Regional cities and towns"), (9, "Market towns"),
         (10, "Castles and fortifications"), (11, "Roads and crossings"), (12, "Church geography"),
         (13, "Industry and resources")]),
        ("Part C", "Local area", [(14, "Villages"), (15, "Local features"), (16, "Ruins and older layers")]),
    ]
    cols = []
    for name, sub, steps in parts:
        boxes = '<div class="fc-arrow">↓</div>'.join(box("%d  %s" % (n, t), n) for n, t in steps)
        cols.append('<div class="fc-col"><p class="fc-part">%s<span>%s</span></p>%s</div>' % (name, sub, boxes))
    return (
        '<figure class="flowchart">'
        '<div class="fc-row">%s<div class="fc-side">→</div>%s</div>'
        '<div class="fc-down">↓</div>'
        '<div class="fc-cols">%s</div>'
        '<div class="fc-down">↓</div>'
        '<div class="fc-row">%s<div class="fc-side">→</div>%s</div>'
        '<figcaption>Work from big to small: Part A, then B, then C. If the final check fails, go back to Step 1.</figcaption>'
        "</figure>"
    ) % (
        box("0  Date, realm type, scale, magic", 0), box("What to draw at each scale", "scale"),
        '<div class="fc-sep">→</div>'.join(cols),
        box("17  Fantasy adjustments", 17), box("18  Final sanity check", 18),
    )


def step_anchors(ch00):
    anchors = {}
    for text, anchor in ch00["sections"]:
        m = re.match(r"Step (\d+)", text)
        if m:
            anchors[int(m.group(1))] = anchor
        if text.lower().startswith("what to draw at each scale"):
            anchors["scale"] = anchor
    return anchors


# ---------------------------------------------------------------- front matter

def inline(text):
    """Render a heading's inline Markdown without links."""
    out = md.renderInline(text)
    return re.sub(r"</?a[^>]*>", "", out)


def contents_html(chapters):
    skip = {"Quick summary", "Sources and further reading"}
    items = []
    for ch in chapters:
        secs = "".join(
            '<li><a href="#%s">%s</a></li>' % (a, inline(t)) for t, a in ch["sections"] if t not in skip)
        items.append(
            '<li class="toc-ch"><a class="toc-num" href="#c%s">%s</a>'
            '<a class="toc-title" href="#c%s">%s</a><ul>%s</ul></li>'
            % (ch["num"], chapter_label(ch["num"]), ch["num"], inline(ch["title"]), secs))
    return ('<section class="contents" id="contents"><h1 class="front-title">Chapters</h1>'
            '<ul class="toc">%s</ul></section>' % "".join(items))


def cover_html(map_uri):
    return """
<section class="cover">
  <p class="cover-kicker">A field guide for fantasy cartographers</p>
  <h1 class="cover-title">Map-Making Guide</h1>
  <p class="cover-sub">Everything human-made: where settlements go, how big they are, and where to put
  capitals, castles, roads, borders, farms, mines, churches and ruins.</p>
  <img class="cover-map" src="%s" alt="Schematic map of the example kingdom of Daravel">
  <p class="cover-foot">Based on real history, c. 1000–1500, with notes to 1650 · continent, kingdom and local maps</p>
</section>""" % map_uri


def howto_html():
    return """
<section class="howto">
  <h1 class="front-title">How to use this guide</h1>
  <ol class="howto-list">
    <li><strong>Start with <a href="#c00">Chapter 0: Step by Step</a>.</strong> It tells you what to draw, in order,
    from a blank continent down to a single valley. Each step links to the chapter that explains it.</li>
    <li><strong>Keep <a href="#c13">Chapter 13: Quick Reference</a> open while you draw.</strong> It has every key
    number and the master legend of map symbols.</li>
    <li><strong>Read Chapters 1–11 when you want the reasons</strong>, the real-world examples and the fine detail.</li>
    <li><strong>See it done in <a href="#c12">Chapter 12: Worked Example</a></strong>, which builds a whole kingdom with
    the guide's numbers and shows the finished map.</li>
    <li><strong>Check your map against <a href="#c11">Chapter 11: Common Mistakes</a></strong> when you are done.</li>
  </ol>
  <div class="howto-key">
    <p class="howto-key-title">The four kinds of note box</p>
    <blockquote class="callout callout-maptip"><p><strong>Map tip</strong>What to draw, where, and which symbol to use.</p></blockquote>
    <blockquote class="callout callout-rule"><p><strong>Rule of thumb</strong>A short rule you can remember while drawing.</p></blockquote>
    <blockquote class="callout callout-later"><p><strong>Later era (1500s+)</strong>What changes after the Middle Ages.</p></blockquote>
    <blockquote class="callout callout-fantasy"><p><strong>Fantasy twist</strong>How magic, monsters or other races change the rule.</p></blockquote>
  </div>
  <p class="howto-note">Distances are given in kilometres and miles. Populations are ranges, because historians'
  estimates differ. Blue text is a link: click it to jump to that chapter or section.</p>
</section>"""


def font_faces():
    names = {"Alegreya": "Alegreya", "AlegreyaSans": "Alegreya Sans", "IMFellEnglish": "IM Fell English"}
    faces = []
    for f in sorted(FONTS.glob("*.ttf")):
        m = re.match(r"([A-Za-z]+?)(SC)?-(\d+)(i?)\.ttf", f.name)
        fam = names[m.group(1)] + (" SC" if m.group(2) else "")
        faces.append("@font-face { font-family: '%s'; src: url('%s'); font-weight: %s; font-style: %s; }"
                     % (fam, f.as_uri(), m.group(3), "italic" if m.group(4) else "normal"))
    return "\n".join(faces)


# ---------------------------------------------------------------- build and check

def _norm(text):
    import unicodedata
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"[\s\u00ad\u00a0\u200b\u2010\u2011-]+", "", text).lower()


def check_pdf(pdf, chapters, doc):
    """Fail if any heading, paragraph, list item or table cell is missing from the PDF."""
    text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
    flat = _norm(text)
    soup = BeautifulSoup(doc, "html.parser")
    # note labels are set in a small-caps face that text extraction cannot read; they are drawn, not lost
    labels = {k.rstrip(":") for k in CALLOUTS}
    for lab in soup.select(".callout p:first-child > strong:first-child, .note-label"):
        if lab.get_text().strip() in labels:
            lab.decompose()
    blocks = soup.select("section.chapter h2, section.chapter h3, section.chapter p, section.chapter li, section.chapter td")
    missing = []
    for el in blocks:
        if el.name == "li" and el.find(["ul", "ol"]):
            el = BeautifulSoup(str(el), "html.parser")  # compare the item's own text, not its sub-list
            for sub in el.find_all(["ul", "ol"]):
                sub.decompose()
        key = _norm(el.get_text())[:40]
        if len(key) >= 8 and key not in flat:
            missing.append(el.get_text()[:90])
    zero = re.findall(r"\.{3,}\s*0\s*$", text, re.M)
    if missing or zero:
        print("CHECK FAILED: %d of %d text blocks missing, %d contents entries with page 0"
              % (len(missing), len(blocks), len(zero)))
        for m in missing[:30]:
            print("  missing:", m)
        sys.exit(1)
    print("check passed: all %d text blocks found in the PDF" % len(blocks))


def build(only=None, html_only=False):
    BUILD.mkdir(exist_ok=True)
    map_png = BUILD / "map.png"
    if not map_png.exists():
        subprocess.run(["node", str(TOOLS / "render_svg.js"), str(GUIDE / "images/worked-example-kingdom.svg"),
                        str(map_png), "3"], check=True, stdout=subprocess.DEVNULL)
    chapters = [convert_chapter(f) for f in chapter_files(only)]
    for ch in chapters:
        if ch["num"] == "00":
            fc = flowchart_html(step_anchors(ch))
            ch["body"] = re.sub(r'<pre><code class="language-mermaid">.*?</code></pre>', lambda _: fc,
                                ch["body"], flags=re.S)

    parts = [cover_html(map_png.as_uri()), howto_html(), contents_html(chapters)]
    for ch in chapters:
        body, prelude = layout_chapter(ch, map_png)
        if prelude:
            parts.append(prelude)
        parts.append(
            '<section class="chapter" id="c%s"><header class="chapter-head"><p class="chapter-num">%s</p>'
            "<h1>%s</h1></header>%s</section>"
            % (ch["num"], chapter_label(ch["num"]), nbsp_last(inline(ch["title"])), body))

    css = font_faces() + "\n" + (TOOLS / "guide.css").read_text(encoding="utf-8")
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Map-Making Guide</title>'
           '<meta name="description" content="Where to put settlements, castles, roads, borders and every other '
           'human-made feature on a fantasy map, based on real medieval history.">'
           "<style>%s</style></head><body>%s</body></html>" % (css, "\n".join(parts)))
    (BUILD / "guide.html").write_text(doc, encoding="utf-8")
    if html_only:
        return
    import weasyprint
    out = OUT_PDF if not only else BUILD / ("preview-%s.pdf" % "-".join(only))
    weasyprint.HTML(string=doc, base_url=str(ROOT)).write_pdf(out)
    print("wrote", out)
    check_pdf(out, chapters, doc)


if __name__ == "__main__":
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")
    build(only, "--html-only" in sys.argv)
