import os
import sys
import hashlib
import json
import csv
import re
import base64
import xml.etree.ElementTree as ET
from PIL import Image, ExifTags

def test_notebook_immutability():
    nb_path = "Lab6/Lab6.ipynb"
    assert os.path.exists(nb_path), "Lab6.ipynb not found"
    with open(nb_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    expected_hash = "86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9"
    assert actual_hash == expected_hash, f"Notebook hash mismatch: {actual_hash} != {expected_hash}"
    
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    assert len(nb["cells"]) == 42, f"Expected 42 cells, found {len(nb['cells'])}"
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) == 18, f"Expected 18 code cells, found {len(code_cells)}"
    executed = [c for c in code_cells if c.get("execution_count") is not None]
    assert len(executed) == 1, f"Expected exactly 1 pre-executed setup cell, found {len(executed)}"
    assert "%pip -q install Pillow" in executed[0]["source"][0], "Expected cell 1 to be pip install"
    print("[PASS] Test 1: Lab6.ipynb immutability & cell schema verified.")

def test_metadata_scanner_and_csv():
    csv_path = "Lab6/metadata_report.csv"
    scanner_path = "Lab6/metadata_scanner.py"
    assert os.path.exists(csv_path), "metadata_report.csv not found"
    assert os.path.exists(scanner_path), "metadata_scanner.py not found"
    
    # Verify CSV structure
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    expected_header = ["filename", "format", "metadata_fields", "suspected_field", "encoding", "risk_score", "reason"]
    assert rows[0] == expected_header, f"Header mismatch: {rows[0]} != {expected_header}"
    assert len(rows) == 7, f"Expected 7 rows (1 header + 6 data rows), found {len(rows)}"
    
    # Run scanner to temp file and diff
    tmp_csv = os.path.normpath(".agents/teamwork/victory_auditor/temp_dynamic_scan.csv")
    import subprocess
    res = subprocess.run([sys.executable, "Lab6/metadata_scanner.py", "-i", "Lab6/Images", "-o", tmp_csv, "-q"], capture_output=True, text=True)
    assert res.returncode == 0, f"Scanner execution failed with return code {res.returncode}: {res.stderr}"
    
    with open(csv_path, "rb") as f1, open(tmp_csv, "rb") as f2:
        h1 = hashlib.sha256(f1.read()).hexdigest()
        h2 = hashlib.sha256(f2.read()).hexdigest()
    
    if os.path.exists(tmp_csv):
        os.remove(tmp_csv)
        
    assert h1 == h2, f"Dynamic execution produced different CSV hash: {h1} != {h2}"
    print(f"[PASS] Test 2: metadata_scanner.py dynamic execution matches metadata_report.csv (SHA-256: {h1}).")

def test_image_forensics_and_kill_chain():
    img_dir = "Lab6/Images"
    expected_images = ["Activation.png", "Brain-Channel.png", "Brain.png", "Chemicals.png", "Dopamine.png", "Music.png"]
    found = sorted(os.listdir(img_dir))
    assert found == expected_images, f"Image list mismatch: {found} != {expected_images}"
    
    # 1. Brain.png
    im1 = Image.open(os.path.join(img_dir, "Brain.png"))
    s1 = im1.info.get("Software", "")
    assert s1 == "RECON: Perform DNS harvesting and Subdomain enumeration."
    
    # 2. Activation.png
    im2 = Image.open(os.path.join(img_dir, "Activation.png"))
    exif2 = im2.getexif()
    sub_ifd2 = exif2.get_ifd(34665)
    raw2 = sub_ifd2.get(37510)
    assert raw2.startswith(b"ASCII\x00\x00\x00")
    s2 = raw2[8:].decode("utf-8")
    assert s2 == "VULN: Identify unpatched CVE-2024-XXXX in web gateway."
    
    # 3. Chemicals.png
    im3 = Image.open(os.path.join(img_dir, "Chemicals.png"))
    s3 = im3.info.get("ImageDescription", "")
    assert s3 == "EXPLOIT: Deploy SQL Injection payload to bypass WAF."
    
    # 4. Dopamine.png
    im4 = Image.open(os.path.join(img_dir, "Dopamine.png"))
    xmp_raw4 = im4.info.get("XML:com.adobe.xmp", "").lstrip("\ufeff")
    root4 = ET.fromstring(xmp_raw4)
    maker_notes = [e.text.strip() for e in root4.iter() if e.tag.endswith("MakerNote")]
    assert len(maker_notes) == 1
    s4 = maker_notes[0]
    assert s4 == "PERSIST: Establish reverse shell via obfuscated cron job."
    
    # 5. Brain-Channel.png
    im5 = Image.open(os.path.join(img_dir, "Brain-Channel.png"))
    s5 = im5.getexif().get(270, "")
    assert s5 == "LATERAL: Pivot to internal Domain Controller using Mimikatz."
    
    # 6. Music.png
    im6 = Image.open(os.path.join(img_dir, "Music.png"))
    raw_b64 = im6.info.get("Copyright", "")
    assert raw_b64 == "RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="
    s6 = base64.b64decode(raw_b64, validate=True).decode("utf-8")
    assert s6 == "EXFIL: Tunnel compressed database dump via DNS Covert Channel."
    
    chain = [s1, s2, s3, s4, s5, s6]
    expected_prefixes = ["RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:"]
    for s, p in zip(chain, expected_prefixes):
        assert s.startswith(p)
    print("[PASS] Test 3: All 6 images independently verified across EXIF/PNG/XMP and 6-stage Kill Chain order confirmed.")

def test_lab6_report_requirements():
    report_path = "Lab6/Lab6_Report.md"
    assert os.path.exists(report_path), "Lab6_Report.md not found"
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check 6 images in evidence table
    for img in ["Activation.png", "Brain-Channel.png", "Brain.png", "Chemicals.png", "Dopamine.png", "Music.png"]:
        assert img in content, f"Missing {img} in report"
    
    # Check 6 recovered secrets
    secrets = [
        "RECON: Perform DNS harvesting and Subdomain enumeration.",
        "VULN: Identify unpatched CVE-2024-XXXX in web gateway.",
        "EXPLOIT: Deploy SQL Injection payload to bypass WAF.",
        "PERSIST: Establish reverse shell via obfuscated cron job.",
        "LATERAL: Pivot to internal Domain Controller using Mimikatz.",
        "EXFIL: Tunnel compressed database dump via DNS Covert Channel."
    ]
    for s in secrets:
        assert s in content, f"Missing secret fragment: {s}"
    
    # Check reflection questions
    assert "Question 1: Why can an image contain a hidden message" in content
    assert "Question 2: How is encoding different from encryption" in content
    assert "Question 3: Why should investigators preserve the original files" in content
    assert "Question 4: Can metadata alone prove that an image was edited" in content
    assert "Question 5: How does this investigation connect to the automated evidence" in content
    
    # Check limitations
    assert "Limitations of EXIF-Only Metadata Extraction" in content
    assert "Limitations of Automated Risk Scoring" in content
    
    # Check textbook citations
    assert "Jose Manuel Ortega" in content
    assert "Fahad Ali Sarwar" in content
    
    # Check CSV table
    assert "metadata_report.csv" in content
    
    print("[PASS] Test 4: Lab6_Report.md satisfies all report criteria and rubric components.")

def test_lab6_instructions_requirements():
    inst_path = "Lab6/Lab6_Instructions.md"
    assert os.path.exists(inst_path), "Lab6_Instructions.md not found"
    with open(inst_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    required_sections = [
        "Objective & Prerequisites",
        "Environment Setup & Forensic Baseline",
        "EXIF Metadata Extraction",
        "PNG Text Chunk Extraction",
        "XMP Packet Extraction & XML Parsing",
        "Base64 Decoding Procedure",
        "Narrative Sequencing Rationale",
        "Automated Metadata Scanner Execution",
        "Forensic Evidence Verification"
    ]
    for sec in required_sections:
        assert sec in content, f"Missing section in instructions: {sec}"
        
    print("[PASS] Test 5: Lab6_Instructions.md satisfies all instructional criteria.")

if __name__ == "__main__":
    test_notebook_immutability()
    test_metadata_scanner_and_csv()
    test_image_forensics_and_kill_chain()
    test_lab6_report_requirements()
    test_lab6_instructions_requirements()
    print("\nALL AUDIT VERIFICATION TESTS PASSED SUCCESSFULLY!")
