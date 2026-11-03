import json
import sys

# Ensure UTF-8 output even on Windows console
sys.stdout.reconfigure(encoding="utf-8")

with open("Lab6/Lab6.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

code_cells = [(i, c) for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"]
print(f"Total cells: {len(nb['cells'])}")
print(f"Total code cells: {len(code_cells)}")

for idx, (cell_i, cell) in enumerate(code_cells):
    src = "".join(cell.get("source", []))
    exec_c = cell.get("execution_count")
    outs = cell.get("outputs", [])
    print(f"\n==================================================")
    print(f"CODE CELL {idx+1} [nb index {cell_i}] execution_count: {exec_c}")
    print(f"==================================================")
    print("--- SOURCE ---")
    print(src.strip())
    print("--- OUTPUTS ---")
    if not outs:
        print("(No output)")
    for out in outs:
        otype = out.get("output_type")
        if otype == "stream":
            print(f"[{out.get('name', 'stream')}]: {''.join(out.get('text', [])).strip()}")
        elif otype == "error":
            print(f"[ERROR]: {out.get('ename')}: {out.get('evalue')}")
        elif otype == "execute_result":
            print(f"[EXECUTE_RESULT]: {out.get('data', {})}")
        else:
            print(f"[{otype}]: {out}")
