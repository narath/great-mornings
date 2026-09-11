"""Compare the phrases in BuiltInRecitation.swift with individual.md and index.html."""
import difflib
import os
import re
import sys

# A phrase in the Swift file is a line that is nothing but a quoted string.
# Movement names ("Arrive", 1, [) and keyed values (id: "individual") are not.
PHRASE = re.compile(r'^\s*"(.*)",\s*$')
CLOSING = re.compile(r'^\s*closing:\s*"(.*)"\s*$')
STANZA = re.compile(r'<p class="stanza">(.*?)</p>', re.S)
CLOSING_HTML = re.compile(r'<p class="closing">(.*?)</p>', re.S)


def from_swift(path):
    phrases, closing = [], None
    for line in open(path, encoding="utf-8"):
        if m := PHRASE.match(line):
            phrases.append(m.group(1))
        elif m := CLOSING.match(line):
            closing = m.group(1)
    if closing:
        phrases.append(closing)
    return phrases


def from_markdown(path):
    phrases = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip()          # drops the two-space hard break
        if not line:
            continue
        if line.startswith(("#", "*", "---", '"What makes')):
            continue                  # title, subtitle, rule, attribution
        phrases.append(line)
    return phrases


def from_html(path):
    html = open(path, encoding="utf-8").read()
    lines = []
    for block in STANZA.findall(html) + CLOSING_HTML.findall(html):
        for line in re.split(r"<br\s*/?>", block):
            line = re.sub(r"\s+", " ", line).strip()
            if line:
                lines.append(line)
    return lines


def report(want, got, name):
    """Return 0 and say so, or print a diff and return 1."""
    if want == got:
        print(f"check-text: {name} agrees ({len(got)} lines)")
        return 0
    print(f"check-text: {name} disagrees with the app.\n")
    print("\n".join(difflib.unified_diff(
        want, got, fromfile="BuiltInRecitation.swift",
        tofile=name, lineterm="")))
    return 1


def main():
    swift, markdown = sys.argv[1], sys.argv[2]
    page = os.path.join(os.path.dirname(os.path.dirname(markdown)), "index.html")
    want = from_swift(swift)
    status = report(want, from_markdown(markdown), "recitations/individual.md")
    if os.path.exists(page):
        status |= report(want, from_html(page), "index.html")
    return status


if __name__ == "__main__":
    sys.exit(main())
