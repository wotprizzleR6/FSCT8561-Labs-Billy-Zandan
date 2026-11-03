import json
import os
import sys
import tempfile
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

REPO_ROOT = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
LAB6_DIR = REPO_ROOT / "Lab6"
ORIGINAL_NB_PATH = LAB6_DIR / "Lab6.ipynb"
WORK_DIR = REPO_ROOT / ".agents" / "teamwork" / "m2_auditor_1"
TEMP_DIR = WORK_DIR / "temp_exec"
TEMP_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_NB_PATH = TEMP_DIR / "clean_copy.ipynb"
EXECUTED_NB_PATH = TEMP_DIR / "freshly_executed.ipynb"

print(f"Reading original notebook: {ORIGINAL_NB_PATH}")
with open(ORIGINAL_NB_PATH, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

# Create a stripped copy (remove outputs and execution counts)
for cell in nb.cells:
    if cell.cell_type == "code":
        cell.outputs = []
        cell.execution_count = None

with open(CLEAN_NB_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"Executing stripped copy in: {LAB6_DIR}")
ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

try:
    ep.preprocess(nb, {"metadata": {"path": str(LAB6_DIR)}})
    print("[PASS] Independent execution succeeded with 0 errors!")
    with open(EXECUTED_NB_PATH, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    exec_success = True
except Exception as e:
    print(f"[FAIL] Independent execution raised exception: {e}")
    exec_success = False
    sys.exit(1)

# Now compare freshly executed outputs vs original saved outputs
print("\n=== Comparing Fresh Execution Outputs vs Original Saved Outputs ===")
with open(ORIGINAL_NB_PATH, "r", encoding="utf-8") as f:
    orig_nb = json.load(f)

with open(EXECUTED_NB_PATH, "r", encoding="utf-8") as f:
    fresh_nb = json.load(f)

orig_code_cells = [c for c in orig_nb["cells"] if c["cell_type"] == "code"]
fresh_code_cells = [c for c in fresh_nb["cells"] if c["cell_type"] == "code"]

assert len(orig_code_cells) == len(fresh_code_cells), "Code cell count mismatch"

diff_count = 0
for idx, (orig_c, fresh_c) in enumerate(zip(orig_code_cells, fresh_code_cells)):
    orig_outs = orig_c.get("outputs", [])
    fresh_outs = fresh_c.get("outputs", [])
    
    orig_text = "".join(["".join(o.get("text", [])) for o in orig_outs if o.get("output_type") == "stream"])
    fresh_text = "".join(["".join(o.get("text", [])) for o in fresh_outs if o.get("output_type") == "stream"])
    
    # Strip carriage returns and extra whitespace
    orig_clean = orig_text.replace("\r\n", "\n").strip()
    fresh_clean = fresh_text.replace("\r\n", "\n").strip()
    
    if orig_clean == fresh_clean:
        print(f"[PASS] Code Cell {idx+1} (exec_count {fresh_c.get('execution_count')}): Outputs match identically.")
    else:
        # Check if the difference is trivial (like timestamps or memory addresses or pip notices)
        print(f"[DIFF] Code Cell {idx+1} output diff:")
        print(f"  ORIGINAL:\n{orig_clean[:200]}...")
        print(f"  FRESH:\n{fresh_clean[:200]}...")
        diff_count += 1

print(f"\nTotal differences found: {diff_count}")
