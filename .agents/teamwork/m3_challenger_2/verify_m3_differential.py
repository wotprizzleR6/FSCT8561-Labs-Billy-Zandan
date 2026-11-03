#!/usr/bin/env python3
"""
Differential Verification Test Suite for Lab 6 Deliverables
Empirical Challenger - Milestone 3
"""

import csv
import json
import os
from pathlib import Path
import base64
import xml.etree.ElementTree as ET
from PIL import Image, ExifTags
import docx

WORKSPACE = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
LAB6 = WORKSPACE / "Lab6"
DOCX_PATH = LAB6 / "Lab6-Billy-Zandan-A01371854.docx"
NOTEBOOK_PATH = LAB6 / "Lab6.ipynb"
CSV_PATH = LAB6 / "metadata_report.csv"
IMAGES_DIR = LAB6 / "Images"

def extract_ground_truth_secrets():
    secrets = {}
    
    # 1. Brain.png
    img = Image.open(IMAGES_DIR / "Brain.png")
    secrets["Brain.png"] = img.info.get("Software", "")
    
    # 2. Activation.png
    img = Image.open(IMAGES_DIR / "Activation.png")
    exif = img.getexif()
    sub_ifd = exif.get_ifd(0x8769)
    raw_user_comment = sub_ifd.get(0x9286) or sub_ifd.get(37510)
    # Strip 8-byte header
    if isinstance(raw_user_comment, bytes) and raw_user_comment.startswith(b"ASCII\x00\x00\x00"):
        secrets["Activation.png"] = raw_user_comment[8:].decode("utf-8")
    elif isinstance(raw_user_comment, str):
        secrets["Activation.png"] = raw_user_comment[8:] if raw_user_comment.startswith("ASCII\x00\x00\x00") else raw_user_comment
        
    # 3. Chemicals.png
    img = Image.open(IMAGES_DIR / "Chemicals.png")
    secrets["Chemicals.png"] = img.info.get("ImageDescription", "")
    
    # 4. Dopamine.png
    img = Image.open(IMAGES_DIR / "Dopamine.png")
    xmp_raw = img.info.get("XML:com.adobe.xmp", "")
    if isinstance(xmp_raw, bytes):
        xmp_str = xmp_raw.decode("utf-8", errors="ignore")
    else:
        xmp_str = xmp_raw
    xmp_clean = xmp_str.lstrip("\ufeff")
    root = ET.fromstring(xmp_clean)
    for elem in root.iter():
        if elem.tag.endswith("MakerNote") and elem.text:
            secrets["Dopamine.png"] = elem.text.strip()
            break
            
    # 5. Brain-Channel.png
    img = Image.open(IMAGES_DIR / "Brain-Channel.png")
    exif = img.getexif()
    secrets["Brain-Channel.png"] = exif.get(270) or exif.get(0x010e) or ""
    
    # 6. Music.png
    img = Image.open(IMAGES_DIR / "Music.png")
    exif = img.getexif()
    raw_copy = exif.get(33432) or img.info.get("Copyright", "")
    secrets["Music.png"] = base64.b64decode(raw_copy).decode("utf-8")
    
    return secrets

def test_differential():
    print("================================================================================")
    print("EMPIRICAL DIFFERENTIAL TEST SUITE")
    print("================================================================================")
    
    # 1. Ground Truth Secrets
    gt_secrets = extract_ground_truth_secrets()
    print("[+] Extracted Ground Truth Secrets directly from binary images:")
    for k, v in gt_secrets.items():
        print(f"    {k}: {repr(v)}")
        
    # Expected sequence & stages
    expected_stages = [
        ("Stage 1", "Brain.png", "RECON: Perform DNS harvesting and Subdomain enumeration."),
        ("Stage 2", "Activation.png", "VULN: Identify unpatched CVE-2024-XXXX in web gateway."),
        ("Stage 3", "Chemicals.png", "EXPLOIT: Deploy SQL Injection payload to bypass WAF."),
        ("Stage 4", "Dopamine.png", "PERSIST: Establish reverse shell via obfuscated cron job."),
        ("Stage 5", "Brain-Channel.png", "LATERAL: Pivot to internal Domain Controller using Mimikatz."),
        ("Stage 6", "Music.png", "EXFIL: Tunnel compressed database dump via DNS Covert Channel."),
    ]
    
    for stage, fname, text in expected_stages:
        assert gt_secrets[fname] == text, f"Mismatch in ground truth for {fname}: got {gt_secrets[fname]} vs expected {text}"
    print("[PASS] Ground truth secrets match expected stage texts exactly.")
    
    # 2. Inspect DOCX Table 1 (Forensic Evidence Table)
    doc = docx.Document(str(DOCX_PATH))
    tables = doc.tables
    print(f"[+] Loaded DOCX: {len(tables)} tables, {len(doc.paragraphs)} paragraphs.")
    assert len(tables) >= 2, f"Expected at least 2 tables, found {len(tables)}"
    
    t_ev = tables[0]
    print(f"[+] Table 1: {len(t_ev.rows)} rows x {len(t_ev.columns)} columns.")
    ev_header = [c.text.strip() for c in t_ev.rows[0].cells]
    print(f"    Header: {ev_header}")
    
    # Check Table 1 contents
    docx_table1_secrets = {}
    for r_idx in range(1, len(t_ev.rows)):
        row_cells = [c.text.strip() for c in t_ev.rows[r_idx].cells]
        fname = row_cells[0]
        secret = row_cells[5]
        stage = row_cells[6]
        docx_table1_secrets[fname] = (secret, stage)
        print(f"    Row {r_idx} [{fname}]: Stage='{stage}', Secret='{secret}'")
        
    for stage, fname, text in expected_stages:
        assert fname in docx_table1_secrets, f"File {fname} not found in docx Table 1"
        extracted_secret, extracted_stage = docx_table1_secrets[fname]
        assert extracted_secret == text, f"Docx Table 1 secret mismatch for {fname}:\nGot:      '{extracted_secret}'\nExpected: '{text}'"
        assert stage in extracted_stage, f"Docx Table 1 stage mismatch for {fname}: {extracted_stage}"
    print("[PASS] DOCX Table 1 secret fragments and stages match ground truth character-for-character.")
    
    # 3. Inspect Section 3 Reconstructed Secret in DOCX text
    full_text = "\n".join(p.text for p in doc.paragraphs)
    for stage, fname, text in expected_stages:
        assert text in full_text, f"Reconstructed text '{text}' missing in docx paragraphs!"
    print("[PASS] Reconstructed narrative stages and secret fragments are present in DOCX paragraphs.")
    
    # Check full assembled secret string
    full_assembled_expected = (
        "RECON: Perform DNS harvesting and Subdomain enumeration. "
        "VULN: Identify unpatched CVE-2024-XXXX in web gateway. "
        "EXPLOIT: Deploy SQL Injection payload to bypass WAF. "
        "PERSIST: Establish reverse shell via obfuscated cron job. "
        "LATERAL: Pivot to internal Domain Controller using Mimikatz. "
        "EXFIL: Tunnel compressed database dump via DNS Covert Channel."
    )
    assert full_assembled_expected in full_text, "Full assembled operational directive mismatch in DOCX body!"
    print("[PASS] Full assembled operational directive in DOCX matches expected text 100%.")
    
    # 4. Compare CSV Table in DOCX with metadata_report.csv
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        csv_reader = list(csv.reader(f))
        
    csv_header_file = csv_reader[0]
    csv_rows_file = csv_reader[1:]
    
    t_csv = tables[1]
    print(f"[+] Table 2 (CSV Table in DOCX): {len(t_csv.rows)} rows x {len(t_csv.columns)} columns.")
    t_csv_header = [c.text.strip() for c in t_csv.rows[0].cells]
    print(f"    Header in docx Table 2: {t_csv_header}")
    
    assert len(t_csv.rows) - 1 == len(csv_rows_file), f"Row count mismatch: docx has {len(t_csv.rows)-1} rows, csv has {len(csv_rows_file)} rows"
    
    # Verify each cell matches
    for r_idx, csv_row in enumerate(csv_rows_file):
        docx_row = [c.text.strip() for c in t_csv.rows[r_idx + 1].cells]
        print(f"    Comparing row {r_idx+1} ({csv_row[0]}):")
        # CSV row: [filename, format, metadata_fields, suspected_field, encoding, risk_score, reason]
        for c_idx in range(len(csv_row)):
            val_csv = csv_row[c_idx].strip()
            val_docx = docx_row[c_idx].strip()
            assert val_csv == val_docx, f"Cell mismatch at row {r_idx+1}, col {c_idx} ({csv_header_file[c_idx]}):\nCSV:  '{val_csv}'\nDOCX: '{val_docx}'"
        print(f"      -> Exact match on all 7 columns.")
    print("[PASS] DOCX Table 2 matches metadata_report.csv 100% cell-for-cell.")
    
    # 5. Check Lab6.ipynb
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)
        
    print(f"[+] Loaded notebook: {len(nb.get('cells', []))} cells.")
    
    # Extract all text from notebook code outputs and markdown cells
    nb_full_text = ""
    for idx, cell in enumerate(nb.get("cells", [])):
        cell_type = cell.get("cell_type")
        source = "".join(cell.get("source", []))
        nb_full_text += f"\n--- CELL {idx} ({cell_type}) ---\n" + source
        
        # Check outputs of code cells
        outputs = cell.get("outputs", [])
        for out in outputs:
            if "text" in out:
                nb_full_text += "\n[OUTPUT TEXT]\n" + "".join(out["text"])
            if "data" in out:
                data = out["data"]
                if "text/plain" in data:
                    nb_full_text += "\n[OUTPUT PLAIN]\n" + "".join(data["text/plain"])
                    
    # Check that each secret fragment appears verbatim in notebook outputs / markdown
    for stage, fname, text in expected_stages:
        assert text in nb_full_text, f"Secret '{text}' for {fname} not found in notebook cells/outputs!"
        print(f"[PASS] Notebook contains secret for {fname}: '{text}'")
        
    # Check that the 6 attack lifecycle stages and sequence match in notebook
    for stage, fname, text in expected_stages:
        # Check that stage name and file name are linked
        assert fname in nb_full_text, f"{fname} missing in notebook!"
    assert "RECON" in nb_full_text and "VULN" in nb_full_text and "EXPLOIT" in nb_full_text and "PERSIST" in nb_full_text and "LATERAL" in nb_full_text and "EXFIL" in nb_full_text
    print("[PASS] All 6 stages (RECON, VULN, EXPLOIT, PERSIST, LATERAL, EXFIL) present in notebook.")
    
    # Check the full reconstructed narrative in notebook
    assert full_assembled_expected in nb_full_text or "RECON: Perform DNS harvesting and Subdomain enumeration. VULN: Identify unpatched CVE-2024-XXXX" in nb_full_text
    print("[PASS] Full narrative sequence matched in notebook.")
    
    print("\n================================================================================")
    print("ALL DIFFERENTIAL CHECKS PASSED PERFECTLY (100% MATCH)")
    print("================================================================================")

if __name__ == "__main__":
    test_differential()
