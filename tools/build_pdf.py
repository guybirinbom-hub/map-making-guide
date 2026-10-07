#!/usr/bin/env python3
"""Build map-making-guide.pdf: every chapter in guide/ combined into one book.

Usage:  python3 tools/build_pdf.py [--only 00,05] [--html-only]
Needs:  pip install weasyprint markdown-it-py mdit-py-plugins
        tools/build/map.png (made here with tools/render_svg.js if missing)

Layout: A4, two text columns, tables and figures across the full width,
a clickable "Chapters" page with page numbers, and PDF bookmarks.
"""
import html
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

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

md = MarkdownIt("commonmark", {"html": False}).enable("table").enable("strikethrough")
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
    path = path.lstrip("./") if path.startswith("./") else path
    m = re.match(r"^(\d\d)-[^/]+\.md$", path)
    if m:
        return "#c%s-%s" % (m.group(1), frag) if frag else "#c%s" % m.group(1)
    if path.startswith("../"):
        return REPO_URL + path[3:] + ("#" + frag if frag else "")
    return REPO_URL + "guide/" + href


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
            for child in tok.children or []:
                if child.type == "link_open":
                    child.attrSet("href", rewrite_href(child.attrGet("href"), num))
        out_tokens.append(tok)
        i += 1

    body = md.renderer.render(out_tokens, md.options, {})
    body = post_process(body, num)
    return {"num": num, "title": title, "sections": sections, "body": body}


def post_process(body, num):
    # tables run across both columns
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    # task-list checkboxes become drawn boxes
    body = re.sub(r'<input class="task-list-item-checkbox"[^>]*>', '<span class="tick"></span>', body)
    # "In this chapter" lists become a small contents box
    body = re.sub(
        r"<p><strong>In this chapter:</strong></p>\s*<ul>(.*?)</ul>",
        r'<nav class="intoc"><p class="intoc-title">In this chapter</p><ul>\1</ul></nav>',
        body, count=1, flags=re.S)
    # quick summary and sources get their own styles
    body = re.sub(r'(<h2 id="c%s-quick-summary">.*?</h2>\s*)(<ul>.*?</ul>)' % num,
                  r'<div class="summary">\1\2</div>', body, count=1, flags=re.S)
    m = re.search(r'<h2 id="c%s-sources-and-further-reading">' % num, body)
    if m:
        body = body[:m.start()] + '<div class="sources">' + body[m.start():] + "</div>"
    # the Mermaid flowchart becomes a drawn, linked diagram
    body = re.sub(r'<pre><code class="language-mermaid">.*?</code></pre>', lambda _: flowchart_html(), body, flags=re.S)
    # the worked-example map gets its own landscape page (inserted before chapter 12)
    body = re.sub(r'<p><img src="images/worked-example-kingdom\.svg"[^>]*></p>', "", body)
    return body


STEP_ANCHORS = {}


def flowchart_html():
    def box(label, step=None):
        href = STEP_ANCHORS.get(step)
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


def find_step_anchors(ch00):
    for text, anchor in ch00["sections"]:
        m = re.match(r"Step (\d+)", text)
        if m:
            STEP_ANCHORS[int(m.group(1))] = anchor
        if text.lower().startswith("what to draw at each scale"):
            STEP_ANCHORS["scale"] = anchor


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
            '<li class="toc-ch"><a href="#c%s"><span class="toc-num">%s</span>%s</a><ul>%s</ul></li>'
            % (ch["num"], chapter_label(ch["num"]), inline(ch["title"]), secs))
    return (
        '<section class="contents" id="contents"><h1 class="front-title">Chapters</h1>'
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
    <li><strong>Check your map</strong> against <a href="#c11">Chapter 11: Common Mistakes</a> when you are done.</li>
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
    faces = []
    for f in sorted(FONTS.glob("*.ttf")):
        m = re.match(r"([A-Za-z]+?)(SC)?-(\d+)(i?)\.ttf", f.name)
        fam = {"Alegreya": "Alegreya", "AlegreyaSans": "Alegreya Sans", "IMFellEnglish": "IM Fell English"}[m.group(1)]
        if m.group(2):
            fam += " SC"
        faces.append("@font-face { font-family: '%s'; src: url('%s'); font-weight: %s; font-style: %s; }"
                     % (fam, f.as_uri(), m.group(3), "italic" if m.group(4) else "normal"))
    return "\n".join(faces)


def build(only=None, html_only=False):
    BUILD.mkdir(exist_ok=True)
    map_png = BUILD / "map.png"
    if not map_png.exists():
        subprocess.run(["node", str(TOOLS / "render_svg.js"), str(GUIDE / "images/worked-example-kingdom.svg"),
                        str(map_png), "3"], check=True, stdout=subprocess.DEVNULL)
    chapters = [convert_chapter(f) for f in chapter_files(only)]
    ch00 = next((c for c in chapters if c["num"] == "00"), None)
    if ch00:
        find_step_anchors(ch00)
        ch00["body"] = re.sub(r'<figure class="flowchart">.*?</figure>', lambda _: flowchart_html(),
                              ch00["body"], flags=re.S)

    parts = [cover_html(map_png.as_uri()), howto_html(), contents_html(chapters)]
    for ch in chapters:
        if ch["num"] == "12":
            parts.append(
                '<section class="map-page"><figure><img src="%s" alt="Schematic map of Daravel">'
                '<figcaption>The kingdom of Daravel, c. 1300: the worked example of Chapter 12, drawn with the '
                'master legend of Chapter 13.</figcaption></figure></section>' % map_png.as_uri())
        parts.append(
            '<section class="chapter" id="c%s"><header class="chapter-head"><p class="chapter-num">%s</p>'
            '<h1>%s</h1></header><div class="cols">%s</div></section>'
            % (ch["num"], chapter_label(ch["num"]), inline(ch["title"]), ch["body"]))

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


if __name__ == "__main__":
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")
    build(only, "--html-only" in sys.argv)
