"""Compare the recitation in BuiltInRecitation.swift with individual.md and index.html.

Two invariants:

  1. The twenty phrases agree, word for word, in all three places.
  2. The app's closing line ("Go well.") appears in NONE of the published
     text. It belongs to the app, where it is spoken after the words; on
     paper and on the web the recitation ends at "I am ready."
"""
import difflib
import os
import re
import sys

# A phrase in the Swift file is a line that is nothing but a quoted string.
# Movement names ("Arrive", 1, [) and keyed values (id: "individual") are not.
PHRASE = re.compile(r'^\s*"(.*)",\s*$')
CLOSING = re.compile(r'^\s*closing:\s*"(.*)"\s*$')
STANZA = re.compile(r'<p class="stanza">(.*?)</p>', re.S)
LINE = re.compile(r'<span class="line">(.*?)</span>', re.S)


def from_swift(path):
    """(the twenty phrases, the app-only closing line)."""
    phrases, closing = [], None
    for line in open(path, encoding="utf-8"):
        if m := PHRASE.match(line):
            phrases.append(m.group(1))
        elif m := CLOSING.match(line):
            closing = m.group(1)
    return phrases, closing


def from_markdown(path):
    """Everything above the '---' rule. Below it is back matter."""
    phrases = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip()          # drops the two-space hard break
        if line.startswith("---"):
            break
        if not line or line.startswith(("#", "*")):
            continue                  # title, subtitle
        phrases.append(line)
    return phrases


def from_html(path):
    html = open(path, encoding="utf-8").read()
    lines = []
    for block in STANZA.findall(html):
        lines += [re.sub(r"\s+", " ", m).strip() for m in LINE.findall(block)]
    return [line for line in lines if line]


def report(want, got, name):
    if want == got:
        print(f"check-text: {name} agrees ({len(got)} phrases)")
        return 0
    print(f"check-text: {name} disagrees with the app.\n")
    print("\n".join(difflib.unified_diff(
        want, got, fromfile="BuiltInRecitation.swift",
        tofile=name, lineterm="")))
    return 1


def closing_is_absent(closing, paths):
    """The app's closing line must not appear in anything published."""
    status = 0
    for path in paths:
        if not os.path.exists(path):
            continue
        if closing and closing in open(path, encoding="utf-8").read():
            print(f"check-text: {os.path.basename(path)} contains the app's "
                  f"closing line {closing!r}. It belongs to the app only — "
                  f"the published text ends at the last phrase.")
            status = 1
    return status


def main():
    swift, markdown = sys.argv[1], sys.argv[2]
    root = os.path.dirname(os.path.dirname(markdown))
    page = os.path.join(root, "recitation", "index.html")

    want, closing = from_swift(swift)
    status = report(want, from_markdown(markdown), "recitations/individual.md")
    if os.path.exists(page):
        status |= report(want, from_html(page), "recitation/index.html")

    # Sources only. The downloads are derived from these, and
    # bin/build-downloads checks its own output after writing it — checking
    # them here would let a stale artefact block the rebuild that fixes it.
    sources = [markdown, page, os.path.join(root, "recitations/template.md")]
    status |= closing_is_absent(closing, sources)
    if not status:
        print(f"check-text: the app's closing line {closing!r} is absent from "
              f"the published text, as it should be")
    return status


if __name__ == "__main__":
    sys.exit(main())
