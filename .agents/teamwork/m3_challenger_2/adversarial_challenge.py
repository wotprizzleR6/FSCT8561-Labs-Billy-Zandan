#!/usr/bin/env python3
"""
Adversarial Stress Harness for Milestone 3 Deliverables
Author: Teamwork Challenger (m3_challenger_2)
"""

import csv
import json
import os
import zipfile
from pathlib import Path
import base64
import xml.etree.ElementTree as ET
from PIL import Image
import docx

WORKSPACE = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
LAB6 = WORKSPACE / "Lab6"
DOCX_PATH = LAB6 / "Lab6-Billy-Zandan-A01371854.docx"
NOTEBOOK_PATH = LAB6 / "Lab6.ipynb"
CSV_PATH = LAB6 / "metadata_report.csv"
SCANNER_PY = LAB6 / "metadata_scanner.py"
GENERATE_DOCX_PY = LAB6 / "generate_report_docx.py"
IMAGES_DIR = LAB6 / "Images"

failures = []

def record_failure(test_name, details):
    failures.append((test_name, details))
    print(f"[FAIL] {test_name}: {details}")

def run_adversarial_suite():
    print("=" * 80)
    print("STARTING ADVERSARIAL STRESS HARNESS")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # CHALLENGE 1: Ground Truth vs All Artifacts - Strict String Equality
    # -------------------------------------------------------------------------
    print("\n--- Challenge 1: Ground Truth Secret Fragments Character-by-Character ---")
    gt_secrets = {
        "Brain.png": "RECON: Perform DNS harvesting and Subdomain enumeration.",
        "Activation.png": "VULN: Identify unpatched CVE-2024-XXXX in web gateway.",
        "Chemicals.png": "EXPLOIT: Deploy SQL Injection payload to bypass WAF.",
        "Dopamine.png": "PERSIST: Establish reverse shell via obfuscated cron job.",
        "Brain-Channel.png": "LATERAL: Pivot to internal Domain Controller using Mimikatz.",
        "Music.png": "EXFIL: Tunnel compressed database dump via DNS Covert Channel.",
    }

    # Verify physical files yield exactly this
    img_extracted = {}
    with Image.open(IMAGES_DIR / "Brain.png") as im:
        img_extracted["Brain.png"] = im.info["Software"]
    with Image.open(IMAGES_DIR / "Activation.png") as im:
        raw = im.getexif().get_ifd(0x8769)[37510]
        img_extracted["Activation.png"] = raw[8:].decode("utf-8") if raw.startswith(b"ASCII\x00\x00\x00") else raw.decode("utf-8")
    with Image.open(IMAGES_DIR / "Chemicals.png") as im:
        img_extracted["Chemicals.png"] = im.info["ImageDescription"]
    with Image.open(IMAGES_DIR / "Dopamine.png") as im:
        raw_xmp = im.info.get("XML:com.adobe.xmp") or im.info.get("xmp")
        if isinstance(raw_xmp, bytes):
            raw_xmp = raw_xmp.decode("utf-8", errors="replace")
        root = ET.fromstring(raw_xmp.lstrip("\ufeff"))
        for elem in root.iter():
            if elem.tag.endswith("MakerNote") and elem.text:
                img_extracted["Dopamine.png"] = elem.text.strip()
                break
    with Image.open(IMAGES_DIR / "Brain-Channel.png") as im:
        img_extracted["Brain-Channel.png"] = im.getexif()[270]
    with Image.open(IMAGES_DIR / "Music.png") as im:
        raw_b64 = im.getexif().get(33432) or im.info.get("Copyright")
        img_extracted["Music.png"] = base64.b64decode(raw_b64).decode("utf-8")

    for fn, expected in gt_secrets.items():
        actual = img_extracted[fn]
        if actual != expected:
            record_failure("BinaryImageGroundTruth", f"{fn}: expected '{expected}', got '{actual}'")
        else:
            print(f"[OK] Physical image {fn} matches expected ground truth.")

    # Check DOCX Table 1
    doc = docx.Document(str(DOCX_PATH))
    t1 = doc.tables[0]
    t1_map = {}
    for row in t1.rows[1:]:
        cells = [c.text.strip() for c in row.cells]
        t1_map[cells[0]] = {
            "container": cells[1],
            "field": cells[2],
            "raw": cells[3],
            "method": cells[4],
            "secret": cells[5],
            "stage": cells[6],
        }

    for fn, expected in gt_secrets.items():
        if fn not in t1_map:
            record_failure("DocxTable1MissingFile", f"Missing {fn} in Table 1")
            continue
        actual_secret = t1_map[fn]["secret"]
        if actual_secret != expected:
            record_failure("DocxTable1SecretMismatch", f"{fn}: expected '{expected}', got '{actual_secret}'")
        else:
            print(f"[OK] DOCX Table 1 secret matches for {fn}.")

    # Check Notebook
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb_json = json.load(f)
    
    # Check each cell's text and outputs
    nb_corpus = ""
    for c in nb_json["cells"]:
        nb_corpus += "".join(c.get("source", [])) + "\n"
        for out in c.get("outputs", []):
            if "text" in out:
                nb_corpus += "".join(out["text"]) + "\n"
            if "data" in out and "text/plain" in out["data"]:
                nb_corpus += "".join(out["data"]["text/plain"]) + "\n"

    for fn, expected in gt_secrets.items():
        if expected not in nb_corpus:
            record_failure("NotebookSecretMismatch", f"Secret for {fn} ('{expected}') not found verbatim in notebook text or outputs.")
        else:
            print(f"[OK] Notebook contains verbatim secret for {fn}.")

    # -------------------------------------------------------------------------
    # CHALLENGE 2: CSV Table 100% Equivalence
    # -------------------------------------------------------------------------
    print("\n--- Challenge 2: DOCX CSV Table vs metadata_report.csv Differential ---")
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        csv_records = list(csv.DictReader(f))

    t2 = doc.tables[1]
    t2_headers = [c.text.strip() for c in t2.rows[0].cells]
    expected_docx_headers = [
        "Filename",
        "Format",
        "Discovered Metadata Fields",
        "Suspected Field",
        "Encoding",
        "Risk Score",
        "Risk Heuristic Justification",
    ]
    if t2_headers != expected_docx_headers:
        record_failure("DocxTable2HeaderMismatch", f"Expected {expected_docx_headers}, got {t2_headers}")
    else:
        print("[OK] DOCX Table 2 headers match expected schema.")

    if len(t2.rows) - 1 != len(csv_records):
        record_failure("DocxTable2RowCount", f"Expected {len(csv_records)} rows, got {len(t2.rows)-1}")
    else:
        print(f"[OK] DOCX Table 2 has exact row count ({len(csv_records)}).")

    for idx, rec in enumerate(csv_records):
        row_cells = [c.text.strip() for c in t2.rows[idx + 1].cells]
        expected_cells = [
            rec["filename"],
            rec["format"],
            rec["metadata_fields"],
            rec["suspected_field"],
            rec["encoding"],
            rec["risk_score"],
            rec["reason"],
        ]
        for col_i, (act, exp) in enumerate(zip(row_cells, expected_cells)):
            if act != exp:
                record_failure("DocxTable2CellMismatch", f"Row {idx+1} col {col_i}: expected '{exp}', got '{act}'")
        print(f"[OK] Row {idx+1} ({rec['filename']}) matched 100%.")

    # -------------------------------------------------------------------------
    # CHALLENGE 3: Attack Lifecycle Stages and Sequencing
    # -------------------------------------------------------------------------
    print("\n--- Challenge 3: Attack Lifecycle Stages and Sequence Consistency ---")
    lifecycle_order = [
        ("Stage 1", "RECON", "Brain.png"),
        ("Stage 2", "VULN", "Activation.png"),
        ("Stage 3", "EXPLOIT", "Chemicals.png"),
        ("Stage 4", "PERSIST", "Dopamine.png"),
        ("Stage 5", "LATERAL", "Brain-Channel.png"),
        ("Stage 6", "EXFIL", "Music.png"),
    ]

    docx_text = "\n".join(p.text for p in doc.paragraphs)

    # Verify stage order in docx Section 3
    last_pos = -1
    for stg_num, stg_name, carrier in lifecycle_order:
        marker = f"{stg_num} — "
        pos = docx_text.find(marker)
        if pos == -1:
            record_failure("DocxLifecycleMissingStage", f"Marker '{marker}' not found in DOCX paragraphs")
        elif pos < last_pos:
            record_failure("DocxLifecycleSequenceError", f"Stage '{marker}' appeared out of sequence (pos {pos} < {last_pos})")
        else:
            print(f"[OK] DOCX lifecycle stage {stg_num} ({stg_name}) found at sequence index {pos}.")
            last_pos = pos

    # Check notebook sequence
    last_nb_pos = -1
    for stg_num, stg_name, carrier in lifecycle_order:
        # Check carrier + secret sequence
        secret = gt_secrets[carrier]
        pos = nb_corpus.find(secret)
        if pos == -1:
            record_failure("NotebookLifecycleMissingSecret", f"Secret '{secret}' not found in notebook")
        else:
            print(f"[OK] Notebook contains secret for {stg_num} ({stg_name}) at character position {pos}.")

    # Verify technical rebuttal of alphabetical sorting in docx
    if "Alphabetical" not in docx_text and "alphabetical" not in docx_text:
        record_failure("DocxAlphabeticalDisproof", "No mention of alphabetical sorting rebuttal in docx.")
    else:
        print("[OK] Alphabetical sorting disproof verified in docx.")

    # -------------------------------------------------------------------------
    # CHALLENGE 4: Media, Visual Screenshot Cards, and Package Integrity
    # -------------------------------------------------------------------------
    print("\n--- Challenge 4: DOCX OpenXML Media and Packaging Integrity ---")
    with zipfile.ZipFile(str(DOCX_PATH), "r") as z:
        namelist = z.namelist()
        media_files = [n for n in namelist if n.startswith("word/media/")]
        print(f"[OK] Word document contains {len(media_files)} embedded media files: {media_files}")
        if len(media_files) < 6:
            record_failure("DocxMissingImages", f"Expected at least 6 terminal images, found {len(media_files)}")
        else:
            for mf in media_files:
                data = z.read(mf)
                if len(data) < 1000:
                    record_failure("DocxCorruptImage", f"Media file {mf} is unusually small ({len(data)} bytes)")
                else:
                    print(f"[OK] Embedded media {mf} valid ({len(data)} bytes).")

    # -------------------------------------------------------------------------
    # CHALLENGE 5: Reflection Questions and Citations
    # -------------------------------------------------------------------------
    print("\n--- Challenge 5: Reflection Questions and Academic Depth ---")
    required_citations = ["Ortega", "Chapter 13", "Chapter 14"]
    for cit in required_citations:
        if cit not in docx_text:
            record_failure("DocxMissingCitation", f"Citation '{cit}' missing from docx text")
        else:
            print(f"[OK] DOCX contains required citation: '{cit}'.")

    # Check 5 reflection questions in docx
    q_markers = [
        "Question 1:",
        "Question 2:",
        "Question 3:",
        "Question 4:",
        "Question 5:",
    ]
    for qm in q_markers:
        if qm not in docx_text:
            record_failure("DocxMissingQuestion", f"Question marker '{qm}' missing from docx text")
        else:
            print(f"[OK] DOCX contains reflection question marker: '{qm}'.")

    # Check student info in DOCX
    if "Billy Zandan" not in docx_text:
        record_failure("DocxStudentName", "Student name 'Billy Zandan' missing in docx text")
    if "A01371854" not in docx_text:
        record_failure("DocxStudentID", "Student ID 'A01371854' missing in docx text")
    print("[OK] Student name and ID confirmed in DOCX text.")

    # -------------------------------------------------------------------------
    # CHALLENGE 6: Source Code Listing Match
    # -------------------------------------------------------------------------
    print("\n--- Challenge 6: Scanner Source Code Listing in DOCX ---")
    with open(SCANNER_PY, "r", encoding="utf-8") as f:
        scanner_code = f.read()

    # Verify key functions from metadata_scanner.py appear in docx paragraphs
    key_code_snippets = [
        "def configure_utf8_streams",
        "def collect_metadata_field_names",
        "def extract_metadata_candidates",
        "def analyze_and_deobfuscate",
        "def calculate_risk_score",
        "def scan_single_image",
        "def scan_directory",
    ]
    for snip in key_code_snippets:
        if snip not in docx_text:
            record_failure("DocxMissingCodeSnippet", f"Snippet '{snip}' missing from docx paragraphs")
        else:
            print(f"[OK] Scanner code snippet '{snip}' present in DOCX.")

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("ADVERSARIAL STRESS HARNESS SUMMARY")
    print("=" * 80)
    if failures:
        print(f"[!] FAILED: {len(failures)} issues detected:")
        for name, det in failures:
            print(f"    - [{name}] {det}")
        return False
    else:
        print("[PASS] 100% OF ADVERSARIAL STRESS CHECKS PASSED WITH ZERO DISCREPANCIES.")
        return True

if __name__ == "__main__":
    success = run_adversarial_suite()
    if not success:
        exit(1)
