import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

docx_path = Path("Lab6/Lab6-Billy-Zandan-A01371854.docx")
print("DOCX Path:", docx_path.resolve())
print("File exists:", docx_path.exists())
print("File size:", docx_path.stat().st_size, "bytes")

# Check zip structure
with zipfile.ZipFile(docx_path, "r") as z:
    file_list = z.namelist()
    print("Total files in docx zip:", len(file_list))
    media_files = [f for f in file_list if f.startswith("word/media/")]
    print(f"Media files embedded ({len(media_files)}):", media_files)
    
    # Read document.xml
    doc_xml_bytes = z.read("word/document.xml")
    root = ET.fromstring(doc_xml_bytes)
    
    # Extract all text
    namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = root.findall(".//w:p", namespaces)
    print("Total paragraphs:", len(paragraphs))
    
    tables = root.findall(".//w:tbl", namespaces)
    print("Total tables:", len(tables))
    
    # Get all text
    full_text = "".join(node.text for node in root.findall(".//w:t", namespaces) if node.text)
    print("Total text length:", len(full_text), "chars, ~", len(full_text.split()), "words")

# Check required elements
print("\n--- Content Audits ---")
reqs = {
    "Student Name 'Billy Zandan'": "Billy Zandan" in full_text,
    "Student ID 'A01371854'": "A01371854" in full_text,
    "Image: Activation.png": "Activation.png" in full_text,
    "Image: Brain-Channel.png": "Brain-Channel.png" in full_text,
    "Image: Brain.png": "Brain.png" in full_text,
    "Image: Chemicals.png": "Chemicals.png" in full_text,
    "Image: Dopamine.png": "Dopamine.png" in full_text,
    "Image: Music.png": "Music.png" in full_text,
    "Stage: RECON": "RECON" in full_text,
    "Stage: VULN": "VULN" in full_text,
    "Stage: EXPLOIT": "EXPLOIT" in full_text,
    "Stage: PERSIST": "PERSIST" in full_text,
    "Stage: LATERAL": "LATERAL" in full_text,
    "Stage: EXFIL": "EXFIL" in full_text,
    "Scanner source code present": "metadata_scanner.py" in full_text or "def scan_single_image" in full_text,
    "CSV table present": "metadata_report.csv" in full_text or "suspected_field" in full_text,
    "Limitations analysis present": "Limitations of EXIF-Only" in full_text or "Blind Spots" in full_text or "Risk-Scoring" in full_text,
    "Reflection Question 1": "Why can an image contain a hidden message" in full_text or "Question 1" in full_text,
    "Reflection Question 2": "How is encoding different from encryption" in full_text or "Question 2" in full_text,
    "Reflection Question 3": "Why should investigators preserve the original files" in full_text or "Question 3" in full_text,
    "Reflection Question 4": "Can metadata alone confirm that an incident occurred" in full_text or "Question 4" in full_text,
    "Reflection Question 5": "How would you defend against covert channels" in full_text or "Question 5" in full_text,
    "Citation Ortega (2021)": "Ortega" in full_text or "2021" in full_text,
}

all_passed = True
for k, v in reqs.items():
    print(f"[{'PASS' if v else 'FAIL'}] {k}")
    if not v:
        all_passed = False

print("\nAll docx checks passed:", all_passed)
