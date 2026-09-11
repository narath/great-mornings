"""recitations/individual.md -> plain text, or minimal HTML for textutil."""
import sys

HTML_MODE = "--html" in sys.argv
path = [a for a in sys.argv[1:] if not a.startswith("--")][0]

title = subtitle = None
blocks, current = [], []
for raw in open(path, encoding="utf-8"):
    line = raw.rstrip()
    if line.startswith("# "):
        title = line[2:]
    elif line.startswith("*") and line.endswith("*") and subtitle is None:
        subtitle = line.strip("*")
    elif line.startswith("---"):
        continue
    elif not line:
        if current:
            blocks.append(current)
            current = []
    else:
        current.append(line)
if current:
    blocks.append(current)

if HTML_MODE:
    print("<html><head><meta charset='utf-8'></head><body>")
    print(f"<h1>{title}</h1>")
    print(f"<p><i>{subtitle}</i></p>")
    for block in blocks:
        print("<p>" + "<br>".join(block) + "</p>")
    print("</body></html>")
else:
    print(title)
    print(subtitle)
    print()
    for block in blocks:
        print("\n".join(block))
        print()
