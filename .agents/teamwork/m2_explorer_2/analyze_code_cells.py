import json
from pathlib import Path

nb_path = Path("Lab6/Lab6.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb.get("cells", [])
code_cells = []
markdown_cells = []

for idx, cell in enumerate(cells):
    ctype = cell.get("cell_type")
    src = "".join(cell.get("source", []))
    if ctype == "code":
        code_cells.append((idx, src))
    elif ctype == "markdown":
        markdown_cells.append((idx, src))

print(f"Total cells: {len(cells)}")
print(f"Code cells: {len(code_cells)}")
print(f"Markdown cells: {len(markdown_cells)}")
print()

for idx, src in code_cells:
    first_line = src.split('\n')[0] if src else "<EMPTY>"
    has_todo = "TODO" in src
    print(f"Code Cell {idx:02d}: lines={len(src.splitlines()):2d}, has_todo={str(has_todo):5s} | {first_line[:60]}")
