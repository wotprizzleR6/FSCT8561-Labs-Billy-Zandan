import json
from pathlib import Path

nb_path = Path("Lab6/Lab6.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

out_path = Path(".agents/teamwork/m2_explorer_2/notebook_dump.txt")
with open(out_path, "w", encoding="utf-8") as out:
    for idx, c in enumerate(nb.get("cells", [])):
        cell_type = c.get("cell_type")
        src = "".join(c.get("source", []))
        out.write(f"==================== CELL {idx:02d} [{cell_type}] ====================\n")
        out.write(src + "\n")
        outputs = c.get("outputs", [])
        if outputs:
            out.write(f"--- OUTPUTS ({len(outputs)}) ---\n")
            for o in outputs:
                out.write(json.dumps(o, indent=2)[:300] + "\n")
        out.write("\n")

print(f"Dumped {len(nb.get('cells', []))} cells to {out_path}")
