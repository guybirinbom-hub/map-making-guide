#!/usr/bin/env python3
"""Report section headings (h2/h3) left at the foot of a page with no text below them.

Usage: python3 tools/find_stranded.py map-making-guide.pdf
"""
import sys

import pdfplumber

pdf = pdfplumber.open(sys.argv[1])
found = 0
for n, page in enumerate(pdf.pages, 1):
    words = page.extract_words(extra_attrs=["size", "fontname"])
    body = [w for w in words if w["top"] < page.height - 50]          # ignore the footer
    heads = [w for w in body if ("Bold" in w["fontname"] and w["size"] > 10.2)]
    for h in heads:
        below = [w for w in body if w["top"] > h["bottom"] + 2]
        if h["top"] > page.height * 0.6 and len(below) < 8:
            line = " ".join(w["text"] for w in body if abs(w["top"] - h["top"]) < 2)
            print("p%d  y=%.0f  %s" % (n, h["top"], line[:70]))
            found += 1
            break
print("%d stranded heading(s)" % found)
