import json
from pathlib import Path

nb_path = Path("Lab6/Lab6.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")

for idx, cell in enumerate(nb['cells']):
    ctype = cell['cell_type']
    source = "".join(cell.get('source', []))
    preview = source.strip()[:100].replace('\n', ' ')
    if ctype == 'code':
        ec = cell.get('execution_count')
        out_cnt = len(cell.get('outputs', []))
        out_types = [o.get('output_type') for o in cell.get('outputs', [])]
        print(f"Cell {idx:02d} [CODE] exec={ec} outputs={out_cnt} {out_types} | {preview[:60]}")
    else:
        print(f"Cell {idx:02d} [MD] | {preview[:70]}")
