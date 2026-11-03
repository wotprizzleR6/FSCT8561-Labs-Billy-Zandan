import hashlib
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import docx

PROJECT_ROOT = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
LAB6_DIR = PROJECT_ROOT / "Lab6"
IMAGES_DIR = LAB6_DIR / "Images"
AUDIT_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m3_auditor_1")

# Baseline hashes from M1 & M2 handoffs
BASELINE_IMAGE_HASHES = {
    "Activation.png": "1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904",
    "Brain-Channel.png": "3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359",
    "Brain.png": "5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e",
    "Chemicals.png": "96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a",
    "Dopamine.png": "ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472",
    "Music.png": "3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370"
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def test_image_hashes():
    print("=== CHECK 1: Cryptographic Baseline Hash Verification for Lab6/Images ===")
    all_match = True
    for img_name, expected_hash in BASELINE_IMAGE_HASHES.items():
        img_path = IMAGES_DIR / img_name
        if not img_path.exists():
            print(f"[FAIL] Missing image: {img_name}")
            all_match = False
            continue
        actual_hash = sha256_file(img_path)
        if actual_hash == expected_hash:
            print(f"[PASS] {img_name}: {actual_hash} (MATCH)")
        else:
            print(f"[FAIL] {img_name}: Expected {expected_hash}, got {actual_hash}")
            all_match = False
    return all_match

def test_static_generate_report_script():
    print("\n=== CHECK 2: Static Analysis of Lab6/generate_report_docx.py ===")
    script_path = LAB6_DIR / "generate_report_docx.py"
    if not script_path.exists():
        print(f"[FAIL] Script does not exist: {script_path}")
        return False
    
    code = script_path.read_text(encoding="utf-8")
    
    # Check for forbidden patterns
    forbidden_terms = [
        "shutil.copy", "copyfile", "copytree", "shutil.move", 
        "os.system('copy", 'os.system("copy', "subprocess.run(['copy",
        "subprocess.run([\"copy"
    ]
    violations = []
    for term in forbidden_terms:
        if term in code:
            violations.append(f"Found suspicious file copy pattern: {term}")
            
    # Check that it uses python-docx to construct document
    if "docx.Document(" not in code:
        violations.append("Missing docx.Document() invocation")
    if "doc.save(" not in code:
        violations.append("Missing doc.save() invocation")
    if "doc.add_table(" not in code:
        violations.append("Missing doc.add_table() invocation")
    if "doc.add_paragraph(" not in code:
        violations.append("Missing doc.add_paragraph() invocation")
        
    # Check dynamic reads
    if "scanner_script_path.read_text" not in code:
        violations.append("Missing dynamic read of metadata_scanner.py")
    if "csv.DictReader" not in code:
        violations.append("Missing dynamic read of metadata_report.csv")
        
    if violations:
        for v in violations:
            print(f"[FAIL] {v}")
        return False
    else:
        print("[PASS] No suspicious file copy operations detected.")
        print("[PASS] True python-docx programmatic construction verified.")
        print("[PASS] Dynamic reading of scanner source code and CSV report verified.")
        return True

def test_authentic_generation_and_docx_internals():
    print("\n=== CHECK 3: Authentic Generation and DOCX Inspection ===")
    # Import generate_report function from generate_report_docx
    sys.path.insert(0, str(LAB6_DIR))
    from generate_report_docx import generate_report
    
    audit_docx = AUDIT_DIR / "audit_output.docx"
    prod_docx = LAB6_DIR / "Lab6-Billy-Zandan-A01371854.docx"
    
    if not prod_docx.exists():
        print(f"[FAIL] Production deliverable does not exist: {prod_docx}")
        return False
        
    print(f"Production docx size: {prod_docx.stat().st_size} bytes")
    
    # Run generator to audit output path
    generate_report(
        output_docx_path=audit_docx,
        image_dir=IMAGES_DIR,
        scanner_script_path=LAB6_DIR / "metadata_scanner.py",
        csv_report_path=LAB6_DIR / "metadata_report.csv"
    )
    print(f"Audit generated docx size: {audit_docx.stat().st_size} bytes")
    
    # Verify both are valid zip archives
    with zipfile.ZipFile(prod_docx) as pz, zipfile.ZipFile(audit_docx) as az:
        p_namelist = set(pz.namelist())
        a_namelist = set(az.namelist())
        
        print(f"Production package items: {len(p_namelist)}")
        print(f"Audit package items:      {len(a_namelist)}")
        
        # Check required OOXML files
        required_parts = [
            "word/document.xml",
            "[Content_Types].xml",
            "word/_rels/document.xml.rels"
        ]
        for part in required_parts:
            if part not in p_namelist:
                print(f"[FAIL] Missing {part} in production docx")
                return False
            if part not in a_namelist:
                print(f"[FAIL] Missing {part} in audit docx")
                return False
        print("[PASS] Required OOXML package parts confirmed in both documents.")
        
        # Inspect embedded images
        media_files = [n for n in p_namelist if n.startswith("word/media/")]
        print(f"[PASS] Embedded media count: {len(media_files)} (expected 6 terminal cards)")
        if len(media_files) != 6:
            print(f"[FAIL] Expected 6 embedded media cards, found {len(media_files)}")
            return False

        # Parse document.xml
        p_xml = pz.read("word/document.xml")
        a_xml = az.read("word/document.xml")
        
        # Compare text content extracted from document.xml
        def extract_text_from_xml(xml_bytes):
            root = ET.fromstring(xml_bytes)
            texts = []
            for elem in root.iter():
                if elem.tag.endswith('}t'):
                    if elem.text:
                        texts.append(elem.text)
            return "".join(texts)
            
        p_text = extract_text_from_xml(p_xml)
        a_text = extract_text_from_xml(a_xml)
        
        print(f"Production document text length: {len(p_text)} chars")
        print(f"Audit document text length:      {len(a_text)} chars")
        
        if p_text == a_text:
            print("[PASS] Character-for-character identical text extracted from document.xml!")
        else:
            print("[FAIL] Mismatch between production docx and newly generated docx text!")
            return False
            
    # Check requirements using python-docx
    doc = docx.Document(str(prod_docx))
    full_paragraphs_text = "\n".join(p.text for p in doc.paragraphs)
    all_table_text = "\n".join(" ".join(cell.text for cell in row.cells) for t in doc.tables for row in t.rows)
    all_text = full_paragraphs_text + "\n" + all_table_text
    
    req_checks = [
        ("Student Name: Billy Zandan", "Billy Zandan" in full_paragraphs_text),
        ("Student ID: A01371854", "A01371854" in full_paragraphs_text),
        ("Table Count >= 2", len(doc.tables) >= 2),
        ("Evidence Table Rows >= 7", len(doc.tables[0].rows) >= 7),
        ("Scanner CSV Table Rows >= 7", len(doc.tables[1].rows) >= 7),
        ("Stage 1 RECON present", "RECON: Perform DNS harvesting and Subdomain enumeration." in all_text),
        ("Stage 2 VULN present", "VULN: Identify unpatched CVE-2024-XXXX in web gateway." in all_text),
        ("Stage 3 EXPLOIT present", "EXPLOIT: Deploy SQL Injection payload to bypass WAF." in all_text),
        ("Stage 4 PERSIST present", "PERSIST: Establish reverse shell via obfuscated cron job." in all_text),
        ("Stage 5 LATERAL present", "LATERAL: Pivot to internal Domain Controller using Mimikatz." in all_text),
        ("Stage 6 EXFIL present", "EXFIL: Tunnel compressed database dump via DNS Covert Channel." in all_text),
        ("Disproof of alphabetical ordering", "Forensic Absurdity" in full_paragraphs_text or "alphabetical" in full_paragraphs_text.lower()),
        ("Scanner source code embedded in paragraphs", "def collect_metadata_field_names" in full_paragraphs_text),
        ("Limitations: EXIF blind spots", "Forensic Blind Spots of EXIF-Only" in full_paragraphs_text),
        ("Limitations: Automated risk scoring", "Classroom Heuristics vs. Forensic Certainty" in full_paragraphs_text),
        ("Question 1 present", "Question 1: Hidden Metadata Beyond Primary EXIF" in full_paragraphs_text),
        ("Question 2 present", "Question 2: Encoding versus Encryption" in full_paragraphs_text),
        ("Question 3 present", "Question 3: Evidence Preservation" in full_paragraphs_text),
        ("Question 4 present", "Question 4: Evidentiary Weight of Metadata" in full_paragraphs_text),
        ("Question 5 present", "Question 5: Synthesis with Automated Security Scanners" in full_paragraphs_text),
        ("Citations: Ortega 2021", "Ortega" in full_paragraphs_text),
        ("Word Count > 3000 words", len(all_text.split()) > 3000)
    ]
    
    print(f"\nTotal words in report: {len(all_text.split())}")
    print(f"Total paragraphs: {len(doc.paragraphs)}")
    print(f"Total tables: {len(doc.tables)}")
    
    all_req_pass = True
    for desc, passed in req_checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {desc}")
        if not passed:
            all_req_pass = False
            
    return all_req_pass

if __name__ == "__main__":
    t1 = test_image_hashes()
    t2 = test_static_generate_report_script()
    t3 = test_authentic_generation_and_docx_internals()
    
    if t1 and t2 and t3:
        print("\n>>> OVERALL FORENSIC AUDIT: CLEAN <<<")
        sys.exit(0)
    else:
        print("\n>>> OVERALL FORENSIC AUDIT: INTEGRITY VIOLATION <<<")
        sys.exit(1)
