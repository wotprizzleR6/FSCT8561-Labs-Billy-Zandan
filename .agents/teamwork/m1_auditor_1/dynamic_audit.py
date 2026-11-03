"""
Dynamic Execution, Mutation, and Stress-Testing for metadata_scanner.py
"""

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, PngImagePlugin

workspace_dir = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_auditor_1")
scanner_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py")
report_csv_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv")
original_images_dir = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images")

temp_dir = workspace_dir / "audit_temp"
if temp_dir.exists():
    shutil.rmtree(temp_dir)
temp_dir.mkdir(parents=True, exist_ok=True)

test_results = {}

print("=== 1. Execution on Original Images and Comparison with metadata_report.csv ===")
fresh_csv = temp_dir / "fresh_report.csv"
cmd = [sys.executable, str(scanner_path), "-i", str(original_images_dir), "-o", str(fresh_csv), "-q"]
proc = subprocess.run(cmd, capture_output=True, text=True)
print(f"Return code: {proc.returncode}")
if proc.stderr:
    print(f"Stderr: {proc.stderr}")

with open(report_csv_path, "r", encoding="utf-8") as f:
    existing_rows = list(csv.DictReader(f))

with open(fresh_csv, "r", encoding="utf-8") as f:
    fresh_rows = list(csv.DictReader(f))

print(f"Existing rows count: {len(existing_rows)}")
print(f"Fresh rows count: {len(fresh_rows)}")

differences = []
for idx, (ex, fr) in enumerate(zip(existing_rows, fresh_rows)):
    for k in ex:
        if ex[k] != fr[k]:
            differences.append((idx, k, ex[k], fr[k]))

if not differences and len(existing_rows) == len(fresh_rows):
    print("MATCH: Generated report matches existing metadata_report.csv EXACTLY.")
    test_results["fresh_run_match"] = "PASS"
else:
    print(f"MISMATCH: Found differences: {differences}")
    test_results["fresh_run_match"] = "FAIL"


print("\n=== 2. Mutation Testing: Renamed Original Images ===")
# Copy all 6 original images to a new directory with completely randomized names
renamed_dir = temp_dir / "renamed_images"
renamed_dir.mkdir(parents=True, exist_ok=True)

name_mapping = {
    "Activation.png": "mutant_01_alpha.png",
    "Brain-Channel.png": "sample_beta_999.png",
    "Brain.png": "charlie_anonymous.png",
    "Chemicals.png": "delta_test_x.png",
    "Dopamine.png": "echo_random_payload.png",
    "Music.png": "foxtrot_unknown_img.png",
}

for orig_name, new_name in name_mapping.items():
    shutil.copy2(original_images_dir / orig_name, renamed_dir / new_name)

renamed_csv = temp_dir / "renamed_report.csv"
cmd = [sys.executable, str(scanner_path), "-i", str(renamed_dir), "-o", str(renamed_csv), "-q"]
proc = subprocess.run(cmd, capture_output=True, text=True)
print(f"Renamed scan return code: {proc.returncode}")

with open(renamed_csv, "r", encoding="utf-8") as f:
    renamed_rows = {r["filename"]: r for r in csv.DictReader(f)}

mutation_passed = True
for orig_name, new_name in name_mapping.items():
    matching_orig = next(r for r in fresh_rows if r["filename"] == orig_name)
    renamed_row = renamed_rows.get(new_name)
    if not renamed_row:
        print(f"ERROR: Missing row for {new_name}")
        mutation_passed = False
        continue
    # Compare suspected_field, encoding, risk_score
    for field in ["suspected_field", "encoding", "risk_score"]:
        if matching_orig[field] != renamed_row[field]:
            print(f"FAIL on {new_name} ({orig_name}) for {field}: expected {matching_orig[field]}, got {renamed_row[field]}")
            mutation_passed = False

if mutation_passed:
    print("PASS: Metadata extraction and risk scoring are 100% independent of filename!")
    test_results["filename_mutation"] = "PASS"
else:
    print("FAIL: Filename mutation produced discrepancies!")
    test_results["filename_mutation"] = "FAIL"


print("\n=== 3. Adversarial / Synthetic Images Testing ===")
synthetic_dir = temp_dir / "synthetic_images"
synthetic_dir.mkdir(parents=True, exist_ok=True)

# 3.1 Blank image - no metadata
blank_img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
blank_path = synthetic_dir / "clean_blank.png"
blank_img.save(blank_path)

# 3.2 Benign image - legitimate non-covert metadata
benign_path = synthetic_dir / "clean_benign.png"
png_info = PngImagePlugin.PngInfo()
png_info.add_text("Software", "Adobe Photoshop 2024")
png_info.add_text("Author", "Alice Analyst")
png_info.add_text("Description", "This is a scenic photo taken on vacation.")
blank_img.save(benign_path, pnginfo=png_info)

# 3.3 Synthetic Covert Base64 in PNG tEXt
covert_b64_path = synthetic_dir / "synthetic_b64.png"
png_info_b64 = PngImagePlugin.PngInfo()
# "RECON: Scanning subnet 192.168.1.0/24" -> Base64
b64_msg = "UkVDT046IFNjYW5uaW5nIHN1Ym5ldCAxOTIuMTY4LjEuMC8yNA=="
png_info_b64.add_text("Comment", b64_msg)
blank_img.save(covert_b64_path, pnginfo=png_info_b64)

# 3.4 Synthetic Covert Plaintext in XMP
covert_xmp_path = synthetic_dir / "synthetic_xmp.png"
png_info_xmp = PngImagePlugin.PngInfo()
xmp_packet = (
    '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
    '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
    '<rdf:Description xmlns:exif="http://ns.adobe.com/exif/1.0/">'
    '<exif:MakerNote>PERSIST: Install scheduled task backoor</exif:MakerNote>'
    '</rdf:Description></rdf:RDF></x:xmpmeta>'
)
png_info_xmp.add_text("XML:com.adobe.xmp", xmp_packet)
blank_img.save(covert_xmp_path, pnginfo=png_info_xmp)

synthetic_csv = temp_dir / "synthetic_report.csv"
cmd = [sys.executable, str(scanner_path), "-i", str(synthetic_dir), "-o", str(synthetic_csv), "-q"]
proc = subprocess.run(cmd, capture_output=True, text=True)
print(f"Synthetic scan return code: {proc.returncode}")

with open(synthetic_csv, "r", encoding="utf-8") as f:
    synth_rows = {r["filename"]: r for r in csv.DictReader(f)}

print("\nSynthetic Results:")
for fname, row in synth_rows.items():
    print(f"  {fname}: Risk={row['risk_score']}, Field={row['suspected_field']}, Enc={row['encoding']}, Reason={row['reason']}")

synth_passed = True
if int(synth_rows["clean_blank.png"]["risk_score"]) != 0:
    print("FAIL: clean_blank.png should have risk_score 0")
    synth_passed = False
if int(synth_rows["clean_benign.png"]["risk_score"]) != 0:
    print("FAIL: clean_benign.png should have risk_score 0")
    synth_passed = False
if int(synth_rows["synthetic_b64.png"]["risk_score"]) != 15 or synth_rows["synthetic_b64.png"]["encoding"] != "Base64":
    print("FAIL: synthetic_b64.png should have risk_score 15 and Base64")
    synth_passed = False
if int(synth_rows["synthetic_xmp.png"]["risk_score"]) != 15 or "MakerNote" not in synth_rows["synthetic_xmp.png"]["suspected_field"]:
    print("FAIL: synthetic_xmp.png should have risk_score 15 and MakerNote suspected_field")
    synth_passed = False

if synth_passed:
    print("PASS: Synthetic/adversarial testing verified dynamic detection and accurate risk scoring!")
    test_results["synthetic_adversarial"] = "PASS"
else:
    print("FAIL: Synthetic testing failed!")
    test_results["synthetic_adversarial"] = "FAIL"


print("\n=== 4. CLI Argument Hardening & Interface Compliance ===")
# Test invalid directory handling
proc_invalid = subprocess.run([sys.executable, str(scanner_path), "-i", str(temp_dir / "nonexistent")], capture_output=True, text=True)
cli_passed = (proc_invalid.returncode != 0)

# Test verbose mode
proc_verbose = subprocess.run([sys.executable, str(scanner_path), "-i", str(original_images_dir), "-v"], capture_output=True, text=True)
cli_passed = cli_passed and (proc_verbose.returncode == 0) and ("Recovered Secret" in proc_verbose.stdout)

if cli_passed:
    print("PASS: CLI handles arguments, verbose diagnostics, and missing directory errors correctly.")
    test_results["cli_interface"] = "PASS"
else:
    print("FAIL: CLI interface issue.")
    test_results["cli_interface"] = "FAIL"


print("\n=== 5. Cryptographic Hash & Chain of Custody Audit ===")
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("File Hashes (SHA-256):")
print(f"  metadata_scanner.py: {sha256_file(scanner_path)}")
print(f"  metadata_report.csv: {sha256_file(report_csv_path)}")
for img in sorted(original_images_dir.glob("*.png")):
    print(f"  Images/{img.name}: {sha256_file(img)}")

print(f"\nFinal Test Results Summary: {test_results}")
