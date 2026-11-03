import json
import os
import sys
import io
import contextlib
from pathlib import Path

REPO_ROOT = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
LAB6_DIR = REPO_ROOT / "Lab6"
NOTEBOOK_PATH = LAB6_DIR / "Lab6.ipynb"

print(f"Loading notebook: {NOTEBOOK_PATH}")
with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Change current working directory to LAB6_DIR as Jupyter kernel does
os.chdir(LAB6_DIR)
print(f"Current working dir set to: {os.getcwd()}")

# Execution environment
kernel_globals = {
    "__name__": "__main__",
    "__file__": str(NOTEBOOK_PATH),
}

code_cells = [c for c in nb["cells"] if c.get("cell_type") == "code"]
print(f"Found {len(code_cells)} code cells to execute.\n")

mismatches = []
execution_results = []

for idx, cell in enumerate(code_cells):
    ec = cell.get("execution_count")
    source_lines = cell.get("source", [])
    source_text = "".join(source_lines)
    
    # Filter out IPython magics (e.g. %pip)
    executable_lines = []
    for line in source_lines:
        stripped = line.strip()
        if stripped.startswith("%") or stripped.startswith("!"):
            # Note: IPython magic
            continue
        executable_lines.append(line)
    executable_code = "".join(executable_lines)
    
    saved_stream_outs = []
    for out in cell.get("outputs", []):
        if out.get("output_type") == "stream":
            saved_stream_outs.append("".join(out.get("text", [])))
    saved_stdout = "".join(saved_stream_outs).replace("\r\n", "\n").strip()
    
    captured_stdout = io.StringIO()
    error_occurred = None
    
    with contextlib.redirect_stdout(captured_stdout):
        try:
            if executable_code.strip():
                exec(executable_code, kernel_globals)
        except Exception as e:
            error_occurred = f"{type(e).__name__}: {e}"
            
    fresh_stdout = captured_stdout.getvalue().replace("\r\n", "\n").strip()
    
    print(f"--- Code Cell {idx+1} [Execution Count: {ec}] ---")
    if error_occurred:
        print(f"  [EXEC ERROR]: {error_occurred}")
        mismatches.append((idx+1, "Execution Error", error_occurred))
    else:
        # Check comparison (ignoring cell 1 if it had %pip)
        if idx == 0:
            print("  [Cell 1 is %pip install Pillow -> skipped execution]")
            continue
            
        print(f"  Fresh stdout length: {len(fresh_stdout)} chars")
        print(f"  Saved stdout length: {len(saved_stdout)} chars")
        
        # Compare
        if fresh_stdout == saved_stdout:
            print("  [VERIFIED] Fresh output EXACTLY matches saved output.")
        else:
            # Let's inspect diff
            print("  [DIFF NOTED]")
            print(f"    Saved: {repr(saved_stdout[:100])}")
            print(f"    Fresh: {repr(fresh_stdout[:100])}")
            mismatches.append((idx+1, saved_stdout, fresh_stdout))

print("\n" + "="*50)
print(f"Execution Verification Summary: {len(code_cells)-1-len(mismatches)}/{len(code_cells)-1} cells exactly matched.")
if mismatches:
    print(f"Mismatches / Errors count: {len(mismatches)}")
    for m in mismatches:
        print(f"  Cell {m[0]}")
else:
    print("ALL CODE CELLS EXECUTED AUTHENTICALLY WITH IDENTICAL OUTPUTS!")
