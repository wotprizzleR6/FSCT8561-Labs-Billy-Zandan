import json
from pathlib import Path

nb_path = Path("Lab6/Lab6.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print("Total cells in notebook:", len(nb["cells"]))
code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
print("Total code cells:", len(code_cells))

has_errors = False
exec_counts = []
for idx, c in enumerate(code_cells, 1):
    ec = c.get("execution_count")
    exec_counts.append(ec)
    outputs = c.get("outputs", [])
    errs = [o for o in outputs if o.get("output_type") == "error"]
    if errs:
        print(f"Error in code cell {idx}: {errs[0].get('ename')}: {errs[0].get('evalue')}")
        has_errors = True
    print(f"Code cell {idx}: exec_count={ec}, outputs={len(outputs)}")

print("Execution counts:", exec_counts)
if not has_errors:
    print("ALL CODE CELLS EXECUTED WITH 0 ERRORS.")

# Inspect markdown answers
print("\n--- Inspecting Key Markdown Cells ---")
cell_4 = "".join(nb["cells"][4]["source"])
print("Cell 4 (Evidence Table preview):", cell_4[:300], "...\n")
cell_33 = "".join(nb["cells"][33]["source"])
print("Cell 33 (Reconstructed secret preview):", cell_33[:300], "...\n")
cell_40 = "".join(nb["cells"][40]["source"])
print(f"Cell 40 length: {len(cell_40)} chars, {len(cell_40.split())} words")
print("Cell 40 preview:", cell_40[:300], "...\n")
