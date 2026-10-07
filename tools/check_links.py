#!/usr/bin/env python3
"""Check relative links and #anchors in the guide's Markdown files.

Usage: python3 tools/check_links.py
Exits with status 1 if any link points to a missing file or heading.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [ROOT / "README.md", ROOT / "PROGRESS.md", *sorted((ROOT / "guide").glob("*.md"))]

LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def slug(text):
    """GitHub-style heading anchor."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links -> text
    text = re.sub(r"[`*_~]", "", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path):
    found, seen, in_code = set(), {}, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        m = None if in_code else HEADING.match(line)
        if m:
            s = slug(m.group(2))
            n = seen.get(s, 0)
            found.add(s if n == 0 else f"{s}-{n}")
            seen[s] = n + 1
    return found


def main():
    cache, problems = {}, []
    for f in FILES:
        if not f.exists():
            continue
        in_code = False
        for no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
            if in_code:
                continue
            for target in LINK.findall(line):
                if re.match(r"^[a-z]+:", target):
                    continue  # external URL / mailto
                path_part, _, frag = target.partition("#")
                dest = (f.parent / path_part).resolve() if path_part else f
                if not dest.exists():
                    problems.append(f"{f.relative_to(ROOT)}:{no}: missing file {target}")
                    continue
                if frag and dest.suffix == ".md":
                    if dest not in cache:
                        cache[dest] = anchors(dest)
                    if frag not in cache[dest]:
                        problems.append(f"{f.relative_to(ROOT)}:{no}: missing anchor {target}")
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s) in {sum(1 for f in FILES if f.exists())} files")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
