import json
import re
from pathlib import Path

nb_path = Path("Lab6/Lab6.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb['cells']

print("=== CHECK 1: Student Information Header ===")
c0 = "".join(cells[0]['source'])
print("Cell 0 snippet:\n", c0[:400])
has_student_name = "Billy Zandan" in c0
has_student_id = "A01371854" in c0
print(f"Student Name present: {has_student_name}")
print(f"Student ID present: {has_student_id}")

print("\n=== CHECK 2: Code Cells Sequential Execution Counts (1..18) ===")
code_cells = [c for c in cells if c['cell_type'] == 'code']
print(f"Total code cells: {len(code_cells)}")
exec_counts = [c.get('execution_count') for c in code_cells]
expected_counts = list(range(1, 19))
print(f"Execution counts: {exec_counts}")
print(f"Matches 1..18: {exec_counts == expected_counts}")

print("\n=== CHECK 3: Code Cells Outputs Valid, Non-Empty, Zero Tracebacks ===")
zero_tracebacks = True
all_non_empty = True
for idx, c in enumerate(code_cells):
    ec = c.get('execution_count')
    outputs = c.get('outputs', [])
    if len(outputs) == 0:
        all_non_empty = False
        print(f"WARNING: Code cell {idx+1} (exec {ec}) has no outputs!")
    for out in outputs:
        if out.get('output_type') == 'error':
            zero_tracebacks = False
            print(f"ERROR: Code cell {idx+1} (exec {ec}) has error traceback: {out.get('ename')}: {out.get('evalue')}")
print(f"All code cells have outputs: {all_non_empty}")
print(f"Zero error tracebacks: {zero_tracebacks}")

print("\n=== CHECK 4: Stage Markers in Code Outputs ===")
all_text_outputs = ""
for c in code_cells:
    for out in c.get('outputs', []):
        if out.get('output_type') == 'stream':
            all_text_outputs += "".join(out.get('text', []))
        elif out.get('output_type') in ('execute_result', 'display_data'):
            data = out.get('data', {})
            all_text_outputs += "".join(data.get('text/plain', []))

stages = ["RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:"]
for s in stages:
    present = s in all_text_outputs
    print(f"Stage '{s}': present = {present}")
    if present:
        # find matching line
        for line in all_text_outputs.splitlines():
            if s in line:
                print(f"   Sample output line: {line.strip()}")
                break

print("\n=== CHECK 5: Evidence Table in Cell 20 ===")
c20 = "".join(cells[20]['source'])
print(f"Cell 20 length: {len(c20)} chars")
print(f"Has table structure: {'|' in c20}")
images = ["Activation.png", "Brain-Channel.png", "Brain.png", "Chemicals.png", "Dopamine.png", "Music.png"]
for img in images:
    print(f"Image {img} in Cell 20: {img in c20}")
print("Cell 20 excerpt:\n", "\n".join([line for line in c20.splitlines() if any(img in line for img in images)]))

print("\n=== CHECK 6: Reconstructed Secret & Kill Chain in Cell 33 ===")
c33 = "".join(cells[33]['source'])
print(f"Cell 33 length: {len(c33)} chars")
has_placeholders_c33 = "__________" in c33
print(f"Placeholders '__________' remaining in Cell 33: {has_placeholders_c33}")
killchain_terms = ["Cyber Kill Chain", "MITRE ATT&CK", "Reconnaissance", "Exploitation", "Persistence", "Lateral Movement", "Exfiltration"]
for term in killchain_terms:
    print(f"Kill chain concept '{term}': {term.lower() in c33.lower()}")

print("\n=== CHECK 7: Reflection Questions in Cell 40 ===")
c40 = "".join(cells[40]['source'])
print(f"Cell 40 word count: {len(c40.split())} words")
for q_num in range(1, 6):
    pattern = rf"{q_num}\."
    has_q = bool(re.search(pattern, c40))
    print(f"Question {q_num} formatted/answered: {has_q}")

print("\n=== CHECK 8: Overall Placeholders in Entire Notebook ===")
any_placeholder = False
for idx, c in enumerate(cells):
    src = "".join(c.get('source', []))
    if "__________" in src:
        any_placeholder = True
        print(f"WARNING: Cell {idx} has '__________' placeholder!")
print(f"Any '__________' placeholders anywhere in notebook: {any_placeholder}")
