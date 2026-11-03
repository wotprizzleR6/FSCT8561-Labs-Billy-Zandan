"""
Comprehensive Independent Forensic Audit Script for Lab 6.
Author: m4_auditor_1 (Teamwork Forensic Auditor)
Target: Lab 6 full project deliverables
"""

import ast
import csv
import hashlib
import io
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Paths
ROOT_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
LAB6_DIR = ROOT_DIR / "Lab6"
IMAGES_DIR = LAB6_DIR / "Images"
SCANNER_PY = LAB6_DIR / "metadata_scanner.py"
SCANNER_CSV = LAB6_DIR / "metadata_report.csv"
NOTEBOOK = LAB6_DIR / "Lab6.ipynb"
DOCX_GEN = LAB6_DIR / "generate_report_docx.py"
DOCX_OUT = LAB6_DIR / "Lab6-Billy-Zandan-A01371854.docx"
TEST_SUITE = LAB6_DIR / "test_e2e_lab6.py"

BASELINE_IMAGE_HASHES = {
    "Activation.png": "1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904",
    "Brain-Channel.png": "3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359",
    "Brain.png": "5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e",
    "Chemicals.png": "96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a",
    "Dopamine.png": "ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472",
    "Music.png": "3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370",
}

EXPECTED_DELIVERABLE_HASHES = {
    "metadata_scanner.py": "5a2c5c649f7995ff18f9e0b1ebf0e76f8823ef3a6e4773285e13c4699acd1f5c",
    "metadata_report.csv": "11a671ebd807f466057c83adc03811e2e61553cbede793822c856072a93f2852",
    "Lab6.ipynb": "a54c3e5969eee409754ffd7f42ce1c80dd53706fd482cab88cb199895faefb7b",
    "generate_report_docx.py": "f157657806063c0467d10477c7cf968d7a7cf0e3c7150cf6dae19614623dab67",
    "Lab6-Billy-Zandan-A01371854.docx": "9ebd7524d6900ade090b1e49793b76ddf5b645a5e30cc87c08dbe36dfeab5173",
    "test_e2e_lab6.py": "fa262d86ad3819b62f42a651487d8f52f7579fa101edaa3fa1e6745529991efb",
}

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def check_image_custody():
    print("=== Check 1: Cryptographic Image Chain of Custody ===")
    all_match = True
    for img_name, expected_hash in BASELINE_IMAGE_HASHES.items():
        img_path = IMAGES_DIR / img_name
        if not img_path.exists():
            print(f"[FAIL] Missing image: {img_path}")
            all_match = False
            continue
        actual_hash = sha256_file(img_path)
        size = img_path.stat().st_size
        match = (actual_hash == expected_hash)
        status = "MATCH" if match else "MISMATCH"
        print(f"[{status}] {img_name:18s} ({size:,} B): {actual_hash}")
        if not match:
            print(f"       Expected: {expected_hash}")
            all_match = False
    return all_match

def check_deliverable_hashes():
    print("\n=== Check 1b: Production Deliverable Hashes ===")
    for fname, expected_hash in EXPECTED_DELIVERABLE_HASHES.items():
        fpath = LAB6_DIR / fname
        if not fpath.exists():
            print(f"[FAIL] Missing file: {fpath}")
            continue
        actual_hash = sha256_file(fpath)
        size = fpath.stat().st_size
        match = (actual_hash == expected_hash)
        status = "MATCH" if match else "MISMATCH"
        print(f"[{status}] {fname:32s} ({size:,} B): {actual_hash}")

def check_static_ast():
    print("\n=== Check 2: Static AST & Anti-Cheating Analysis ===")
    # 2.1 metadata_scanner.py
    with open(SCANNER_PY, "r", encoding="utf-8") as f:
        src_scanner = f.read()
    tree_scanner = ast.parse(src_scanner, filename=str(SCANNER_PY))

    # Look for hardcoded filenames or dispatch dictionaries
    image_names = list(BASELINE_IMAGE_HASHES.keys())
    scanner_str_literals = [n.value for n in ast.walk(tree_scanner) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    found_image_literals = [s for s in scanner_str_literals if any(img in s for img in image_names)]
    print(f"[-] metadata_scanner.py image filename literals found: {found_image_literals}")

    # Check functions in scanner
    scanner_functions = [n for n in ast.walk(tree_scanner) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    print(f"[-] metadata_scanner.py defined functions: {len(scanner_functions)}")
    scanner_facades = []
    for fn in scanner_functions:
        body = fn.body
        # Check if function body is just a single return constant or pass
        if len(body) == 1:
            if isinstance(body[0], ast.Pass):
                scanner_facades.append((fn.name, "pass statement"))
            elif isinstance(body[0], ast.Raise) and isinstance(body[0].exc, ast.Name) and body[0].exc.id == "NotImplementedError":
                scanner_facades.append((fn.name, "NotImplementedError"))
            elif isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Constant):
                scanner_facades.append((fn.name, f"returns constant {body[0].value.value}"))
    print(f"[-] metadata_scanner.py facade functions detected: {scanner_facades}")

    # 2.2 generate_report_docx.py
    with open(DOCX_GEN, "r", encoding="utf-8") as f:
        src_docx_gen = f.read()
    tree_docx_gen = ast.parse(src_docx_gen, filename=str(DOCX_GEN))

    docx_functions = [n for n in ast.walk(tree_docx_gen) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    print(f"[-] generate_report_docx.py defined functions: {len(docx_functions)}")
    docx_facades = []
    for fn in docx_functions:
        body = fn.body
        if len(body) == 1:
            if isinstance(body[0], ast.Pass):
                docx_facades.append((fn.name, "pass statement"))
            elif isinstance(body[0], ast.Raise) and isinstance(body[0].exc, ast.Name) and body[0].exc.id == "NotImplementedError":
                docx_facades.append((fn.name, "NotImplementedError"))
            elif isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Constant):
                docx_facades.append((fn.name, f"returns constant {body[0].value.value}"))
    print(f"[-] generate_report_docx.py facade functions detected: {docx_facades}")

    # Check for forbidden file copy calls
    file_copy_calls = []
    for node in ast.walk(tree_docx_gen):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ("copy", "copyfile", "copytree", "move"):
                    file_copy_calls.append(node.func.attr)
    print(f"[-] generate_report_docx.py file copying calls: {file_copy_calls}")

    ast_clean = (len(found_image_literals) == 0 and len(scanner_facades) == 0 and len(docx_facades) == 0 and len(file_copy_calls) == 0)
    print(f"[AST Verdict]: {'PASS' if ast_clean else 'FAIL'}")
    return ast_clean

def check_notebook_authenticity():
    print("\n=== Check 3: Notebook Authenticity (Lab6.ipynb) ===")
    with open(NOTEBOOK, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    print(f"[-] Total notebook cells: {len(cells)}")

    code_cells = [c for c in cells if c.get("cell_type") == "code"]
    md_cells = [c for c in cells if c.get("cell_type") == "markdown"]
    print(f"[-] Code cells: {len(code_cells)}, Markdown cells: {len(md_cells)}")

    # Check execution counts
    exec_counts = [c.get("execution_count") for c in code_cells]
    print(f"[-] Code cell execution counts: {exec_counts}")
    sequential = (exec_counts == list(range(1, len(code_cells) + 1)))
    print(f"[-] Strictly sequential execution counts (1..{len(code_cells)}): {sequential}")

    # Check for cell errors
    errors_found = []
    for idx, c in enumerate(code_cells):
        for out in c.get("outputs", []):
            if out.get("output_type") == "error":
                errors_found.append((idx, out.get("ename"), out.get("evalue")))
    print(f"[-] Execution errors in cells: {errors_found}")

    # Check reflection questions
    all_nb_text = "\n".join("".join(c.get("source", [])) for c in cells)
    has_placeholders = "__________" in all_nb_text or "[TODO]" in all_nb_text or "FIXME" in all_nb_text
    print(f"[-] Unfilled placeholders found: {has_placeholders}")

    # Check reflection cells specifically (cells 40 and 41)
    q_cell_40 = "".join(cells[40].get("source", [])) if len(cells) > 40 else ""
    q_cell_41 = "".join(cells[41].get("source", [])) if len(cells) > 41 else ""
    word_count_40 = len(q_cell_40.split())
    word_count_41 = len(q_cell_41.split())
    has_ortega_cite = "Ortega" in all_nb_text
    print(f"[-] Cell 40 word count: {word_count_40}")
    print(f"[-] Cell 41 word count: {word_count_41}")
    print(f"[-] Citations to Ortega (2021) in notebook: {has_ortega_cite}")

    nb_clean = sequential and (len(errors_found) == 0) and (not has_placeholders) and has_ortega_cite and (word_count_40 > 100) and (word_count_41 > 100)
    print(f"[Notebook Verdict]: {'PASS' if nb_clean else 'FAIL'}")
    return nb_clean

def check_docx_package():
    print("\n=== Check 4: Word Document Package (Lab6-Billy-Zandan-A01371854.docx) ===")
    if not DOCX_OUT.exists():
        print(f"[FAIL] Deliverable docx does not exist: {DOCX_OUT}")
        return False

    with zipfile.ZipFile(DOCX_OUT, "r") as zf:
        namelist = zf.namelist()
        print(f"[-] OpenXML zip parts count: {len(namelist)}")
        expected_parts = ["word/document.xml", "[Content_Types].xml", "_rels/.rels", "word/_rels/document.xml.rels"]
        missing_parts = [p for p in expected_parts if p not in namelist]
        print(f"[-] Missing standard OpenXML parts: {missing_parts}")

        media_files = [f for f in namelist if f.startswith("word/media/")]
        print(f"[-] Embedded media images in docx: {len(media_files)} ({media_files})")

        doc_xml_bytes = zf.read("word/document.xml")
        root = ET.fromstring(doc_xml_bytes)

    # Extract all text from w:t elements
    namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    all_texts = [elem.text for elem in root.iter(f"{{{namespaces['w']}}}t") if elem.text]
    full_text = " ".join(all_texts)
    word_count = len(full_text.split())
    print(f"[-] Document word count: {word_count:,} words")
    print(f"[-] Document character count: {len(full_text):,} characters")

    # Tables count
    tables = root.findall(f".//{{{namespaces['w']}}}tbl")
    print(f"[-] Tables count in document: {len(tables)}")

    # Student metadata check
    has_student = "Billy Zandan" in full_text and "A01371854" in full_text
    print(f"[-] Student metadata (Billy Zandan, A01371854) verified: {has_student}")

    # Stages check
    stages = ["RECON", "VULN", "EXPLOIT", "PERSIST", "LATERAL", "EXFIL"]
    stages_present = all(s in full_text for s in stages)
    print(f"[-] All 6 Kill Chain stages present: {stages_present}")

    # Limitations & source code checks
    has_limitations = "Limitations" in full_text and "EXIF" in full_text and "Risk" in full_text
    has_scanner_code = "def scan_single_image" in full_text or "def calculate_risk_score" in full_text or "def extract_metadata_candidates" in full_text
    has_reflections = "Question 1" in full_text and "Question 5" in full_text
    has_ortega_cite = "Ortega (2021" in full_text

    print(f"[-] Limitations analysis present: {has_limitations}")
    print(f"[-] Full scanner source code embedded: {has_scanner_code}")
    print(f"[-] All 5 reflection questions answered: {has_reflections}")
    print(f"[-] Ortega (2021) textbook citations present: {has_ortega_cite}")

    docx_clean = (len(missing_parts) == 0 and len(media_files) >= 6 and len(tables) >= 2 and
                  has_student and stages_present and has_limitations and has_scanner_code and
                  has_reflections and has_ortega_cite)
    print(f"[Word Doc Verdict]: {'PASS' if docx_clean else 'FAIL'}")
    return docx_clean

def check_csv_report():
    print("\n=== Check 4b: Scanner CSV Report Authenticity ===")
    if not SCANNER_CSV.exists():
        print(f"[FAIL] Missing CSV report: {SCANNER_CSV}")
        return False

    with open(SCANNER_CSV, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    print(f"[-] CSV rows: {len(reader)}")
    expected_fields = ["filename", "format", "metadata_fields", "suspected_field", "encoding", "risk_score", "reason"]
    header_ok = list(reader[0].keys()) == expected_fields if reader else False
    print(f"[-] CSV headers match contract: {header_ok}")

    rows_match = True
    for row in reader:
        print(f"    - {row['filename']}: Risk={row['risk_score']}, Encoding={row['encoding']}, Field={row['suspected_field']}")
        if int(row["risk_score"]) < 10:
            rows_match = False

    csv_clean = (len(reader) == 6 and header_ok and rows_match)
    print(f"[CSV Report Verdict]: {'PASS' if csv_clean else 'FAIL'}")
    return csv_clean

if __name__ == "__main__":
    c1 = check_image_custody()
    check_deliverable_hashes()
    c2 = check_static_ast()
    c3 = check_notebook_authenticity()
    c4 = check_docx_package()
    c5 = check_csv_report()

    all_pass = c1 and c2 and c3 and c4 and c5
    print("\n==========================================")
    print(f"OVERALL PRE-TEST FORENSIC VERDICT: {'CLEAN' if all_pass else 'INTEGRITY VIOLATION'}")
    print("==========================================")
    sys.exit(0 if all_pass else 1)
