import json
from pathlib import Path

nb_path = Path("Lab6/Lab6.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb.get('cells', []))}")
print(f"nbformat: {nb.get('nbformat')}.{nb.get('nbformat_minor')}")
print(f"metadata: {nb.get('metadata')}")

for idx, c in enumerate(nb.get("cells", [])):
    cell_type = c.get("cell_type")
    src = "".join(c.get("source", []))
    lines = src.strip().split("\n")
    first_line = lines[0] if lines else "<EMPTY>"
    exec_count = c.get("execution_count")
    num_outputs = len(c.get("outputs", []))
    print(f"Cell {idx:02d} [{cell_type:8s}] exec:{str(exec_count):4s} outputs:{num_outputs:2d} | {first_line[:65]}")
