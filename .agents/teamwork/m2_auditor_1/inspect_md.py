import json
from pathlib import Path

nb_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print("=== Checking Markdown Cells for Placeholders ===")
placeholders = ["TODO", "TBD", "__________", "FIXME", "XXX", "fill here", "your answer here"]
found_placeholders = []

for idx, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") == "markdown":
        src = "".join(cell.get("source", []))
        for ph in placeholders:
            if ph.lower() in src.lower():
                found_placeholders.append((idx, ph, src[:80]))

print(f"Placeholders found: {len(found_placeholders)}")
for p in found_placeholders:
    print(f"  Cell {p[0]}: found '{p[1]}' in {repr(p[2])}")

# Let's inspect reflection questions (Cell 40)
cell_40 = "".join(nb["cells"][40].get("source", []))
print(f"\nCell 40 word count: {len(cell_40.split())}")
print(f"Cell 40 preview: {repr(cell_40[:150])}")

# Let's inspect Evidence table (Cell 20)
cell_20 = "".join(nb["cells"][20].get("source", []))
print(f"\nCell 20 preview:\n{cell_20[:400]}")

# Let's inspect Reconstructed Secret (Cell 33)
cell_33 = "".join(nb["cells"][33].get("source", []))
print(f"\nCell 33 preview:\n{cell_33[:400]}")
