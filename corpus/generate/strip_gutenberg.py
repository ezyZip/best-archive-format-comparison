#!/usr/bin/env python3
"""Strip the Project Gutenberg header/footer boilerplate from an ebook text.

Removing the boilerplate (and with it the 'Project Gutenberg' trademark) lets
the plain public-domain text be redistributed in this corpus without invoking
the PG trademark license. See corpus/SOURCES.md.

Usage: strip_gutenberg.py <in.txt> <out.txt>
"""
import re
import sys

START = re.compile(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*")
END = re.compile(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*")


def main(src: str, dst: str) -> None:
    text = open(src, encoding="utf-8-sig").read()
    m_start = START.search(text)
    m_end = END.search(text)
    if not (m_start and m_end):
        sys.exit(f"boilerplate markers not found in {src}")
    body = text[m_start.end():m_end.start()].strip("\n") + "\n"
    # Normalize line endings to \n so the committed bytes are platform-stable.
    body = body.replace("\r\n", "\n")
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
