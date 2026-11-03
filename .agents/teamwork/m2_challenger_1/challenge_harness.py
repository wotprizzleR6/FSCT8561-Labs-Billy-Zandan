"""
Adversarial Stress-Testing and Verification Harness for Milestone 2: Lab6.ipynb
Executed by: m2_challenger_1 (Empirical Challenger)
"""

import sys
import os
import json
import hashlib
import re
import copy
from pathlib import Path

REPO_ROOT = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
LAB6_DIR = REPO_ROOT / "Lab6"
NOTEBOOK_PATH = LAB6_DIR / "Lab6.ipynb"
IMAGES_DIR = LAB6_DIR / "Images"
WORKING_DIR = REPO_ROOT / ".agents" / "teamwork" / "m2_challenger_1"
REEXEC_NOTEBOOK_PATH = WORKING_DIR / "test_reexec.ipynb"

class TestReport:
    def __init__(self):
        self.passes = []
        self.failures = []
        self.warnings = []

    def log_pass(self, test_name, detail=""):
        self.passes.append((test_name, detail))
        print(f"[PASS] {test_name}: {detail}")

    def log_fail(self, test_name, detail=""):
        self.failures.append((test_name, detail))
        print(f"[FAIL] {test_name}: {detail}")

    def log_warn(self, test_name, detail=""):
        self.warnings.append((test_name, detail))
        print(f"[WARN] {test_name}: {detail}")

report = TestReport()

print("=" * 70)
print("PHASE 1: NOTEBOOK JSON SCHEMA & STRUCTURE VALIDATION")
print("=" * 70)

# Check file exists and size
if not NOTEBOOK_PATH.exists():
    report.log_fail("Notebook Existence", f"{NOTEBOOK_PATH} does not exist!")
    sys.exit(1)
else:
    report.log_pass("Notebook Existence", f"Found {NOTEBOOK_PATH} ({NOTEBOOK_PATH.stat().st_size} bytes)")

# Parse JSON
try:
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb_json = json.load(f)
    report.log_pass("JSON Parsing", "Valid JSON syntax")
except Exception as e:
    report.log_fail("JSON Parsing", f"Failed to parse JSON: {e}")
    sys.exit(1)

# Validate nbformat v4
try:
    import nbformat
    from nbformat import validate
    nb_node = nbformat.from_dict(nb_json)
    validate(nb_node, version=4)
    report.log_pass("nbformat Validation", f"nbformat version={nb_node.nbformat}.{nb_node.nbformat_minor} conforms to schema")
except Exception as e:
    report.log_fail("nbformat Validation", f"nbformat validation failed: {e}")

cells = nb_json.get("cells", [])
code_cells = [c for c in cells if c.get("cell_type") == "code"]
markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]

print(f"Total cells: {len(cells)} (Code: {len(code_cells)}, Markdown: {len(markdown_cells)})")

if len(code_cells) == 18:
    report.log_pass("Code Cell Count", f"Exactly 18 code cells found (expected 18)")
else:
    report.log_fail("Code Cell Count", f"Found {len(code_cells)} code cells, expected 18")

print("\n" + "=" * 70)
print("PHASE 2: CODE CELL EXECUTION AUDIT (NON-NULL, SEQUENTIAL, OUTPUTS, NO ERRORS)")
print("=" * 70)

expected_counts = list(range(1, 19))
actual_counts = []
empty_code_cells = []
cells_missing_outputs = []
error_cells = []
hardcoded_path_cells = []

for idx, cell in enumerate(code_cells):
    c_num = idx + 1
    src = "".join(cell.get("source", []))
    exec_count = cell.get("execution_count")
    actual_counts.append(exec_count)
    outputs = cell.get("outputs", [])

    if not src.strip():
        empty_code_cells.append(c_num)

    # Check for non-empty outputs
    if len(outputs) == 0:
        cells_missing_outputs.append(c_num)

    # Check for error outputs
    for out in outputs:
        if out.get("output_type") == "error":
            error_cells.append((c_num, out.get("ename"), out.get("evalue")))

    # Check for hardcoded local absolute paths (anti-pattern)
    if "c:\\users" in src.lower() or "c:/users" in src.lower():
        hardcoded_path_cells.append(c_num)

if actual_counts == expected_counts:
    report.log_pass("Execution Counts", f"Strictly sequential 1 to 18: {actual_counts}")
else:
    report.log_fail("Execution Counts", f"Counts mismatch. Expected 1..18, got {actual_counts}")

if not empty_code_cells:
    report.log_pass("Non-Empty Code Cells", "All 18 code cells contain executable source code")
else:
    report.log_fail("Non-Empty Code Cells", f"Empty code cells: {empty_code_cells}")

if not cells_missing_outputs:
    report.log_pass("Cell Outputs Non-Empty", f"All 18 code cells have non-empty outputs list")
else:
    report.log_fail("Cell Outputs Non-Empty", f"Code cells missing outputs: {cells_missing_outputs}")

if not error_cells:
    report.log_pass("Zero Error Outputs", "No code cell contains output_type: 'error'")
else:
    report.log_fail("Zero Error Outputs", f"Errors found in code cells: {error_cells}")

if not hardcoded_path_cells:
    report.log_pass("Portability Check", "No hardcoded user absolute paths found in code cells")
else:
    report.log_warn("Portability Check", f"Hardcoded absolute paths in code cells: {hardcoded_path_cells}")

print("\n" + "=" * 70)
print("PHASE 3: MARKDOWN PLACEHOLDER & COMPLETENESS AUDIT")
print("=" * 70)

all_md_text = "\n".join("".join(c.get("source", [])) for c in markdown_cells)

# Check placeholders
placeholder_patterns = [
    (r"_{4,}", "Underscores placeholder (e.g. __________ )"),
    (r"\[Your answer here\]", "[Your answer here]"),
    (r"\[Insert.*?\]", "[Insert ...]"),
    (r"TODO:", "TODO markers"),
    (r"FIXME:", "FIXME markers")
]

for pat, desc in placeholder_patterns:
    matches = re.findall(pat, all_md_text, flags=re.IGNORECASE)
    if matches:
        report.log_fail("Placeholder Check", f"Found {len(matches)} unpopulated placeholder(s) matching '{desc}'")
    else:
        report.log_pass("Placeholder Check", f"Zero matches for '{desc}'")

# Check student metadata
if "Billy Zandan" in all_md_text and "A01371854" in all_md_text:
    report.log_pass("Student Metadata", "Contains 'Billy Zandan' and 'A01371854'")
else:
    report.log_fail("Student Metadata", "Missing student name or student ID in markdown cells")

# Check Evidence Table
evidence_table_found = False
for c in markdown_cells:
    txt = "".join(c.get("source", []))
    if "| Image" in txt and "Brain.png" in txt and "Activation.png" in txt:
        evidence_table_found = True
        # Verify all 6 images in table
        for img in ["Brain.png", "Activation.png", "Chemicals.png", "Dopamine.png", "Brain-Channel.png", "Music.png"]:
            if img in txt:
                report.log_pass(f"Evidence Table Row ({img})", "Present in evidence table")
            else:
                report.log_fail(f"Evidence Table Row ({img})", "MISSING from evidence table")
        break

if not evidence_table_found:
    report.log_fail("Evidence Table", "Complete evidence table not found in markdown cells")

# Check Narrative Reconstruction
narrative_stages = ["RECON", "VULN", "EXPLOIT", "PERSIST", "LATERAL", "EXFIL"]
narrative_found = all(stage in all_md_text for stage in narrative_stages) and "Stage 1" in all_md_text and "Stage 6" in all_md_text
if narrative_found:
    report.log_pass("Narrative Reconstruction", "All 6 stages (RECON..EXFIL) present and sequenced")
else:
    report.log_fail("Narrative Reconstruction", "Missing one or more narrative stages in markdown")

# Check Reflection Questions
reflections_ok = True
for q in ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]:
    if q in all_md_text:
        report.log_pass(f"Reflection {q}", "Found prompt/answer")
    else:
        report.log_fail(f"Reflection {q}", f"Missing {q}")
        reflections_ok = False

# Reflection length check
for c in markdown_cells:
    txt = "".join(c.get("source", []))
    if "Reflection & Analytical Questions" in txt or "Question 1:" in txt:
        word_count = len(txt.split())
        if word_count > 500:
            report.log_pass("Reflection Word Count", f"{word_count} words in reflection response cell (>500 words)")
        else:
            report.log_fail("Reflection Word Count", f"Only {word_count} words in reflection response cell")
        break

# Limitations analysis check
if "Limitations" in all_md_text and "EXIF" in all_md_text and "risk" in all_md_text.lower():
    report.log_pass("Limitations Analysis", "EXIF-only and automated risk scoring limitations analyzed")
else:
    report.log_fail("Limitations Analysis", "Missing comprehensive limitations analysis")

print("\n" + "=" * 70)
print("PHASE 4: CRYPTOGRAPHIC SHA-256 HASH VERIFICATION")
print("=" * 70)

# Calculate real SHA-256 for all images
real_hashes = {}
for img_name in ["Activation.png", "Brain-Channel.png", "Brain.png", "Chemicals.png", "Dopamine.png", "Music.png"]:
    p = IMAGES_DIR / img_name
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    real_hashes[img_name] = h
    print(f"{img_name}: {h}")

# Check if notebook cell 4 mentions these exact hashes
cell4_txt = "".join(cells[4].get("source", []))
for img_name, h in real_hashes.items():
    if h in cell4_txt:
        report.log_pass(f"Hash Integrity ({img_name})", f"SHA-256 {h[:12]}... matches file on disk")
    else:
        report.log_warn(f"Hash Integrity ({img_name})", f"SHA-256 {h} not found verbatim in baseline cell")

print("\n" + "=" * 70)
print("PHASE 5: HEADLESS RE-EXECUTION TEST")
print("=" * 70)

try:
    from nbconvert.preprocessors import ExecutePreprocessor
    print("Testing programmatic execution of Lab6.ipynb in a fresh kernel...")
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    
    # Read notebook
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb_to_run = nbformat.read(f, as_version=4)

    # Clear outputs before re-executing
    for c in nb_to_run.cells:
        if c.cell_type == "code":
            c.outputs = []
            c.execution_count = None

    # Execute in Lab6 working directory
    ep.preprocess(nb_to_run, {"metadata": {"path": str(LAB6_DIR)}})
    
    # Save executed notebook to working dir (NOT modifying production file)
    with open(REEXEC_NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbformat.write(nb_to_run, f)

    report.log_pass("Headless Execution", f"Successfully executed all 18 cells in fresh kernel, wrote copy to {REEXEC_NOTEBOOK_PATH.name}")

    # Inspect re-executed notebook
    reexec_errors = []
    reexec_counts = []
    for idx, c in enumerate(nb_to_run.cells):
        if c.cell_type == "code":
            reexec_counts.append(c.execution_count)
            for out in c.get("outputs", []):
                if out.get("output_type") == "error":
                    reexec_errors.append((idx, out.get("ename"), out.get("evalue")))

    if not reexec_errors:
        report.log_pass("Re-execution Zero Errors", "All cells ran with 0 errors in fresh headless execution")
    else:
        report.log_fail("Re-execution Zero Errors", f"Errors during re-execution: {reexec_errors}")

    if reexec_counts == expected_counts:
        report.log_pass("Re-execution Counts", f"Sequential 1..18: {reexec_counts}")
    else:
        report.log_fail("Re-execution Counts", f"Counts: {reexec_counts}")

except Exception as e:
    report.log_fail("Headless Execution", f"Exception during execution: {e}")

print("\n" + "=" * 70)
print("PHASE 6: ADVERSARIAL STRESS-TESTING & EDGE CASES")
print("=" * 70)

# Check 1: Output token fidelity
# Ensure outputs contain exact stage strings
output_tokens = ["RECON", "VULN", "EXPLOIT", "PERSIST", "LATERAL", "EXFIL"]
all_output_text = ""
for c in code_cells:
    for out in c.get("outputs", []):
        t = out.get("text", "")
        if isinstance(t, list):
            all_output_text += "".join(t)
        elif isinstance(t, str):
            all_output_text += t
        data = out.get("data", {})
        if "text/plain" in data:
            dp = data["text/plain"]
            if isinstance(dp, list):
                all_output_text += "".join(dp)
            elif isinstance(dp, str):
                all_output_text += dp

for tok in output_tokens:
    if tok in all_output_text:
        report.log_pass(f"Output Token ({tok})", f"Token found in code cell outputs")
    else:
        report.log_fail(f"Output Token ({tok})", f"Token MISSING from code cell outputs")

# Check 2: Cell 39 scanner output check
cell39_src = "".join(cells[39].get("source", []))
cell39_outs = "".join(str(o) for o in cells[39].get("outputs", []))
if "metadata_scanner" in cell39_src:
    report.log_pass("Cell 39 Scanner Integration", "Cell 39 invokes metadata_scanner")
    if "metadata_report.csv" in cell39_outs or "Activation.png" in cell39_outs or "Successfully saved" in cell39_outs:
        report.log_pass("Cell 39 Scanner Output", "Scanner output displayed in cell 39")
    else:
        report.log_warn("Cell 39 Scanner Output", "Scanner output summary might be concise")

# Summary
print("\n" + "=" * 70)
print(f"STRESS TEST SUMMARY: {len(report.passes)} PASSES, {len(report.failures)} FAILURES, {len(report.warnings)} WARNINGS")
print("=" * 70)

if report.failures:
    print("VERDICT: REQUEST_CHANGES")
    sys.exit(1)
else:
    print("VERDICT: APPROVE")
    sys.exit(0)
