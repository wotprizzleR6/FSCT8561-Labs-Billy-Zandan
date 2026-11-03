import json
import os
import sys
from pathlib import Path
from PIL import Image, ExifTags

sys.stdout.reconfigure(encoding='utf-8')

# Change directory to Lab6 to match notebook runtime environment
os.chdir("Lab6")

with open("Lab6.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']

print(f"Verifying {len(code_cells)} code cells against real execution in Lab6/...")

# Prepare execution environment
local_scope = {}
global_scope = {"__name__": "__main__"}

discrepancies = []

for idx, c in enumerate(code_cells):
    ec = c.get('execution_count')
    source = "".join(c.get('source', []))
    
    # Extract saved stream output from notebook
    saved_stream = ""
    for out in c.get('outputs', []):
        if out.get('output_type') == 'stream':
            saved_stream += "".join(out.get('text', []))
    
    # Skip %pip magic for python exec
    lines_to_exec = [line for line in source.splitlines() if not line.strip().startswith("%")]
    code_to_exec = "\n".join(lines_to_exec)
    
    if not code_to_exec.strip():
        print(f"Cell exec={ec} (magic only), skipped direct exec.")
        continue
    
    # Capture stdout
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    
    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(code_to_exec, global_scope, local_scope)
        actual_output = stdout_buf.getvalue()
        
        # Compare actual output with saved output
        # Normalize line endings and trailing whitespace
        norm_actual = "\n".join(l.rstrip() for l in actual_output.strip().splitlines())
        norm_saved = "\n".join(l.rstrip() for l in saved_stream.strip().splitlines())
        
        if norm_actual == norm_saved:
            print(f"Cell exec={ec}: Output EXACT MATCH with live execution.")
        else:
            # Check if differences are minor or substantial
            print(f"Cell exec={ec}: Output difference detected.")
            print(f"   Saved lines: {len(norm_saved.splitlines())}, Actual lines: {len(norm_actual.splitlines())}")
            # print diff
            import difflib
            diff = list(difflib.unified_diff(
                norm_saved.splitlines(),
                norm_actual.splitlines(),
                fromfile='saved_output',
                tofile='actual_output',
                lineterm=''
            ))
            for d in diff[:10]:
                print("   ", d)
            discrepancies.append((ec, diff))
    except Exception as exc:
        print(f"Cell exec={ec}: Execution RAISED EXCEPTION: {exc}")
        discrepancies.append((ec, str(exc)))

print(f"\nExecution verification complete. Discrepancies found: {len(discrepancies)}")
