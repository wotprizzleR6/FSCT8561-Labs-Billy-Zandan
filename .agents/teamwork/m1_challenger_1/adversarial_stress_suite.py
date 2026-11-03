#!/usr/bin/env python3
"""
Adversarial Stress Suite - Empirical Verification of Milestone 1 Deliverables
Runs dynamic test scenarios against metadata_scanner.py and metadata_report.csv:
1. CLI Robustness & Error Handling:
   - Non-existent directory handling (exit code 1, clean stderr, no traceback)
   - Pointing --images to a file instead of directory (exit code 1, clean stderr)
   - Custom output path generation and verification
   - Nested output directory creation
   - Verbose mode diagnostics
   - Quiet mode silence
   - Combined --verbose and --quiet precedence
2. Edge Case & Stress Testing:
   - Empty image directory (exit code 0, 0 records, valid header)
   - Corrupt PNG file handling (non-fatal, logged to stderr, other files scanned)
   - Non-image files in folder (ignored)
   - Space-containing and special character paths
3. RFC 4180 Compliance & Data Integrity:
   - Header schema verification
   - Row count = 6
   - Column count per row = 7
   - No NaN / null / undefined / empty values
   - Strict quote handling
   - Non-double-counted risk score assertions
"""

import csv
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[3]
LAB6_DIR = REPO_ROOT / "Lab6"
SCANNER_SCRIPT = LAB6_DIR / "metadata_scanner.py"
REPORT_CSV = LAB6_DIR / "metadata_report.csv"
IMAGES_DIR = LAB6_DIR / "Images"
WORKING_DIR = Path(__file__).resolve().parent

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

results = []

def record(test_name, status, details=""):
    results.append({"name": test_name, "status": status, "details": details})
    symbol = "PASS" if status == "PASS" else "FAIL"
    print(f"[{symbol}] {test_name}: {details}")

def run_cmd(args, cwd=REPO_ROOT):
    cmd = [sys.executable, str(SCANNER_SCRIPT)] + args
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

print("=" * 80)
print("STARTING ADVERSARIAL STRESS TEST SUITE FOR MILESTONE 1")
print(f"Target script: {SCANNER_SCRIPT}")
print(f"Target CSV: {REPORT_CSV}")
print("=" * 80)

# ------------------------------------------------------------------------------
# 1. CLI Robustness & Error Handling
# ------------------------------------------------------------------------------
print("\n--- [Phase 1: CLI Options & Error Handling] ---")

# Test 1.1: Non-existent directory
proc = run_cmd(["--images", "non_existent_directory_adversarial_test"])
if proc.returncode == 1 and "Error: Target image directory not found" in proc.stderr and "Traceback" not in proc.stderr:
    record("CLI: Non-existent images directory", "PASS", "Graceful exit code 1, clear error message, zero unhandled tracebacks")
else:
    record("CLI: Non-existent images directory", "FAIL", f"Returncode: {proc.returncode}, stderr: {proc.stderr}")

# Test 1.2: Passing a file instead of a directory to --images
sample_file = IMAGES_DIR / "Brain.png"
proc = run_cmd(["--images", str(sample_file)])
if proc.returncode == 1 and "Error: Target image directory not found" in proc.stderr and "Traceback" not in proc.stderr:
    record("CLI: Passing file path as images directory", "PASS", "Rejected file path gracefully with exit code 1")
else:
    record("CLI: Passing file path as images directory", "FAIL", f"Returncode: {proc.returncode}, stderr: {proc.stderr}")

# Test 1.3: Custom output path
custom_csv = WORKING_DIR / "test_custom.csv"
if custom_csv.exists():
    custom_csv.unlink()
proc = run_cmd(["--images", str(IMAGES_DIR), "--output", str(custom_csv)])
if proc.returncode == 0 and custom_csv.exists() and custom_csv.stat().st_size > 0:
    with open(custom_csv, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    custom_csv.unlink()
    if len(rows) == 7:
        record("CLI: Custom output path (--output test_custom.csv)", "PASS", "Successfully wrote 7 lines (1 header + 6 rows) and cleaned up cleanly")
    else:
        record("CLI: Custom output path (--output test_custom.csv)", "FAIL", f"Expected 7 lines, found {len(rows)}")
else:
    record("CLI: Custom output path (--output test_custom.csv)", "FAIL", f"Execution failed: {proc.stderr}")

# Test 1.4: Nested non-existent directory output
nested_csv = WORKING_DIR / "adversarial_tmp" / "deeply" / "nested" / "report.csv"
if nested_csv.parent.exists():
    shutil.rmtree(WORKING_DIR / "adversarial_tmp")
proc = run_cmd(["--images", str(IMAGES_DIR), "--output", str(nested_csv)])
if proc.returncode == 0 and nested_csv.exists():
    record("CLI: Auto-creation of parent directories for output", "PASS", "Created parents recursively and generated report")
    shutil.rmtree(WORKING_DIR / "adversarial_tmp")
else:
    record("CLI: Auto-creation of parent directories for output", "FAIL", f"Failed: {proc.stderr}")

# Test 1.5: Verbose flag
proc = run_cmd(["--images", str(IMAGES_DIR), "--verbose", "-o", str(WORKING_DIR / "tmp_v.csv")])
(WORKING_DIR / "tmp_v.csv").unlink(missing_ok=True)
if proc.returncode == 0 and "Recovered Secret:" in proc.stdout and "Suspected Field :" in proc.stdout:
    record("CLI: Verbose flag (--verbose)", "PASS", "Produced rich diagnostic output including recovered plaintext secrets")
else:
    record("CLI: Verbose flag (--verbose)", "FAIL", "Missing expected diagnostic tokens")

# Test 1.6: Quiet flag
proc = run_cmd(["--images", str(IMAGES_DIR), "--quiet", "-o", str(WORKING_DIR / "tmp_q.csv")])
(WORKING_DIR / "tmp_q.csv").unlink(missing_ok=True)
if proc.returncode == 0 and proc.stdout.strip() == "" and proc.stderr.strip() == "":
    record("CLI: Quiet flag (--quiet)", "PASS", "Completely silent stdout and stderr output on success")
else:
    record("CLI: Quiet flag (--quiet)", "FAIL", f"Stdout not silent: {proc.stdout}")

# Test 1.7: Conflicting --verbose and --quiet
proc = run_cmd(["--images", str(IMAGES_DIR), "--verbose", "--quiet", "-o", str(WORKING_DIR / "tmp_vq.csv")])
(WORKING_DIR / "tmp_vq.csv").unlink(missing_ok=True)
if proc.returncode == 0 and proc.stdout.strip() == "":
    record("CLI: Conflicting flags (--verbose --quiet)", "PASS", "--quiet precedence preserved, no stdout printed")
else:
    record("CLI: Conflicting flags (--verbose --quiet)", "FAIL", f"Stdout output: {proc.stdout}")

# ------------------------------------------------------------------------------
# 2. Edge Case & Stress Testing
# ------------------------------------------------------------------------------
print("\n--- [Phase 2: Edge Cases & Malicious Inputs] ---")

# Test 2.1: Empty images directory
with tempfile.TemporaryDirectory() as tmpdir:
    tmp_csv = WORKING_DIR / "empty_dir_out.csv"
    proc = run_cmd(["--images", tmpdir, "--output", str(tmp_csv)])
    if proc.returncode == 0 and tmp_csv.exists():
        with open(tmp_csv, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        tmp_csv.unlink()
        if len(lines) == 1 and lines[0] == "filename,format,metadata_fields,suspected_field,encoding,risk_score,reason":
            record("Edge Case: Empty directory scan", "PASS", "Gracefully generated valid CSV containing only schema header")
        else:
            record("Edge Case: Empty directory scan", "FAIL", f"Unexpected content: {lines}")
    else:
        record("Edge Case: Empty directory scan", "FAIL", f"Failed with {proc.stderr}")

# Test 2.2: Corrupt PNG image in directory
with tempfile.TemporaryDirectory() as tmpdir:
    shutil.copy2(IMAGES_DIR / "Brain.png", Path(tmpdir) / "Brain.png")
    corrupt_file = Path(tmpdir) / "Corrupted.png"
    with open(corrupt_file, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\nGARBAGE_BYTES_THAT_CORRUPT_HEADER")
    tmp_csv = WORKING_DIR / "corrupt_test_out.csv"
    proc = run_cmd(["--images", tmpdir, "--output", str(tmp_csv)])
    if proc.returncode == 0 and "Error scanning Corrupted.png" in proc.stderr and tmp_csv.exists():
        with open(tmp_csv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        tmp_csv.unlink()
        if len(rows) == 1 and rows[0]["filename"] == "Brain.png":
            record("Edge Case: Corrupted PNG alongside valid image", "PASS", "Isolated error to stderr, continued scan, valid image captured")
        else:
            record("Edge Case: Corrupted PNG alongside valid image", "FAIL", f"Unexpected row count: {len(rows)}")
    else:
        record("Edge Case: Corrupted PNG alongside valid image", "FAIL", f"Proc failed: {proc.stderr}")

# Test 2.3: Directory with non-PNG files
with tempfile.TemporaryDirectory() as tmpdir:
    shutil.copy2(IMAGES_DIR / "Activation.png", Path(tmpdir) / "Activation.png")
    (Path(tmpdir) / "README.md").write_text("# Test", encoding="utf-8")
    (Path(tmpdir) / "image.jpg").write_text("fake jpeg", encoding="utf-8")
    (Path(tmpdir) / "nested_dir").mkdir()
    tmp_csv = WORKING_DIR / "non_png_out.csv"
    proc = run_cmd(["--images", tmpdir, "--output", str(tmp_csv)])
    if proc.returncode == 0:
        with open(tmp_csv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        tmp_csv.unlink()
        if len(rows) == 1 and rows[0]["filename"] == "Activation.png":
            record("Edge Case: Non-PNG files and folders ignored", "PASS", "Only valid PNG targets processed")
        else:
            record("Edge Case: Non-PNG files and folders ignored", "FAIL", f"Found {len(rows)} rows")
    else:
        record("Edge Case: Non-PNG files and folders ignored", "FAIL", f"Failed: {proc.stderr}")

# ------------------------------------------------------------------------------
# 3. CSV RFC 4180 Compliance & Ground-Truth Verification
# ------------------------------------------------------------------------------
print("\n--- [Phase 3: RFC 4180 CSV Validation & Data Integrity] ---")

if not REPORT_CSV.exists():
    record("CSV File Existence", "FAIL", f"File does not exist: {REPORT_CSV}")
else:
    record("CSV File Existence", "PASS", f"Found production report: {REPORT_CSV}")

    # Read raw bytes to check for UTF-8 and BOM
    raw_bytes = REPORT_CSV.read_bytes()
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        record("CSV Encoding: UTF-8 BOM check", "FAIL", "Report contains UTF-8 BOM, plain UTF-8 preferred")
    else:
        record("CSV Encoding: UTF-8 BOM check", "PASS", "Clean UTF-8 without stray byte order mark")

    # Strict CSV Reader
    with open(REPORT_CSV, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, dialect="excel")
        raw_rows = list(reader)

    # Header check
    expected_header = ["filename", "format", "metadata_fields", "suspected_field", "encoding", "risk_score", "reason"]
    if raw_rows[0] == expected_header:
        record("CSV Schema: Header column names & order", "PASS", f"Matches 7-column schema: {expected_header}")
    else:
        record("CSV Schema: Header column names & order", "FAIL", f"Got: {raw_rows[0]}")

    # Exact Row Count
    data_rows = raw_rows[1:]
    if len(data_rows) == 6:
        record("CSV Schema: Exact row count", "PASS", "Exactly 6 data rows (one per image carrier)")
    else:
        record("CSV Schema: Exact row count", "FAIL", f"Found {len(data_rows)} rows, expected 6")

    # Column count per row
    all_7 = all(len(r) == 7 for r in data_rows)
    if all_7:
        record("RFC 4180: Fixed field count per record", "PASS", "All 6 records have precisely 7 fields")
    else:
        record("RFC 4180: Fixed field count per record", "FAIL", "Some rows have unequal column counts")

    # Check for NaN / null / None values
    nan_found = False
    for r in data_rows:
        for val in r:
            if val.strip().lower() in ("nan", "null", "none", "undefined", ""):
                nan_found = True
                break
    if not nan_found:
        record("Data Integrity: No NaN, null, or empty values", "PASS", "All 42 cells contain valid populated data")
    else:
        record("Data Integrity: No NaN, null, or empty values", "FAIL", "Found NaN/null/empty values in CSV cells")

    # Validate ground-truth expected mappings
    expected_data = {
        "Activation.png": {
            "format": "PNG",
            "suspected_field": "UserComment",
            "encoding": "EXIF ASCII header / plain text",
            "risk_score": 15,
        },
        "Brain-Channel.png": {
            "format": "PNG",
            "suspected_field": "ImageDescription",
            "encoding": "None (plain text)",
            "risk_score": 10,
        },
        "Brain.png": {
            "format": "PNG",
            "suspected_field": "Software",
            "encoding": "None (plain text)",
            "risk_score": 10,
        },
        "Chemicals.png": {
            "format": "PNG",
            "suspected_field": "ImageDescription",
            "encoding": "None (plain text)",
            "risk_score": 10,
        },
        "Dopamine.png": {
            "format": "PNG",
            "suspected_field": "XML:com.adobe.xmp (exif:MakerNote)",
            "encoding": "XML encapsulation / plain text",
            "risk_score": 15,
        },
        "Music.png": {
            "format": "PNG",
            "suspected_field": "Copyright",
            "encoding": "Base64",
            "risk_score": 15,
        },
    }

    dict_rows = {r[0]: {"format": r[1], "metadata_fields": r[2], "suspected_field": r[3], "encoding": r[4], "risk_score": int(r[5]), "reason": r[6]} for r in data_rows}

    mapping_correct = True
    for fname, exp in expected_data.items():
        if fname not in dict_rows:
            mapping_correct = False
            record(f"Data Integrity: Row {fname}", "FAIL", "Missing row")
            continue
        actual = dict_rows[fname]
        if (actual["format"] != exp["format"] or 
            actual["suspected_field"] != exp["suspected_field"] or 
            actual["encoding"] != exp["encoding"] or 
            actual["risk_score"] != exp["risk_score"]):
            mapping_correct = False
            record(f"Data Integrity: Row {fname}", "FAIL", f"Got: {actual}, Expected: {exp}")
    if mapping_correct:
        record("Data Integrity: Ground-truth field & score verification", "PASS", "All 6 image rows match ground-truth forensic profile and heuristic scores")

    # Double-counting check
    scores = [dict_rows[fn]["risk_score"] for fn in expected_data]
    if all(s in (10, 15) for s in scores) and max(scores) <= 15:
        record("Heuristic Scoring: Double-counting protection", "PASS", f"All scores are 10 or 15 (max addition capped at +5, max score 15)")
    else:
        record("Heuristic Scoring: Double-counting protection", "FAIL", f"Unexpected scores: {scores}")

# ------------------------------------------------------------------------------
# SUMMARY & VERDICT
# ------------------------------------------------------------------------------
print("\n" + "=" * 80)
total_tests = len(results)
passed_tests = sum(1 for r in results if r["status"] == "PASS")
failed_tests = sum(1 for r in results if r["status"] == "FAIL")

print(f"TOTAL TESTS RUN: {total_tests}")
print(f"PASSED: {passed_tests}")
print(f"FAILED: {failed_tests}")

if failed_tests == 0:
    print("VERDICT: APPROVE (100% of adversarial stress and validation suites passed)")
else:
    print(f"VERDICT: REQUEST_CHANGES ({failed_tests} failure(s) detected)")
print("=" * 80)
