#!/usr/bin/env python3
"""
Inspect Lab6.ipynb cell execution and reflection answers in detail.
"""

import json
from pathlib import Path

NOTEBOOK_PATH = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb")

with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")

error_cells = []
code_cells = 0
for idx, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code":
        code_cells += 1
        for out in c.get("outputs", []):
            if out.get("output_type") == "error":
                error_cells.append((idx, out.get("ename"), out.get("evalue")))

print(f"Total code cells: {code_cells}")
print(f"Error cells: {error_cells}")

# Reflection question check
markdown_cells = [c for c in nb["cells"] if c["cell_type"] == "markdown"]
all_md = "\n".join("".join(c.get("source", [])) for c in markdown_cells)

for q in range(1, 6):
    print(f"Checking Question {q} in notebook...")
    assert f"Question {q}" in all_md or f"Q{q}" in all_md or f"question {q}" in all_md.lower()

print("All reflection questions confirmed in notebook!")
