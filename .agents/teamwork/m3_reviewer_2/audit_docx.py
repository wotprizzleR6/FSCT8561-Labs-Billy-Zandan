"""
Adversarial Quality & Integrity Audit for Lab 6 Word Document Deliverable.
Path: Lab6/Lab6-Billy-Zandan-A01371854.docx
"""

import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import docx

def run_audit():
    docx_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6-Billy-Zandan-A01371854.docx")
    assert docx_path.exists(), f"File does not exist: {docx_path}"
    
    print(f"[*] Auditing {docx_path} ({docx_path.stat().st_size} bytes)")
    
    # 1. Zip package inspection
    with zipfile.ZipFile(docx_path, 'r') as z:
        namelist = z.namelist()
        print(f"[+] Total files in zip package: {len(namelist)}")
        assert "word/document.xml" in namelist, "word/document.xml missing"
        
        media_files = [n for n in namelist if n.startswith("word/media/")]
        print(f"[+] Embedded media files count: {len(media_files)}")
        for m in media_files:
            info = z.getinfo(m)
            print(f"    - {m}: {info.file_size} bytes")
            
        doc_xml_bytes = z.read("word/document.xml")
        root = ET.fromstring(doc_xml_bytes)
        
        # Check XML styling tags
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        shd_elems = root.findall('.//w:shd', namespaces)
        tcMar_elems = root.findall('.//w:tcMar', namespaces)
        tcBorders_elems = root.findall('.//w:tcBorders', namespaces)
        tblHeader_elems = root.findall('.//w:tblHeader', namespaces)
        cantSplit_elems = root.findall('.//w:cantSplit', namespaces)
        pBdr_elems = root.findall('.//w:pBdr', namespaces)
        
        print(f"[+] OOXML Style Elements Found:")
        print(f"    - w:shd (cell shading): {len(shd_elems)}")
        print(f"    - w:tcMar (cell margins/padding): {len(tcMar_elems)}")
        print(f"    - w:tcBorders (cell borders): {len(tcBorders_elems)}")
        print(f"    - w:tblHeader (header repeat): {len(tblHeader_elems)}")
        print(f"    - w:cantSplit (prevent row splitting): {len(cantSplit_elems)}")
        print(f"    - w:pBdr (paragraph borders for code blocks): {len(pBdr_elems)}")

    # 2. Document object analysis via python-docx
    doc = docx.Document(str(docx_path))
    
    paragraphs = doc.paragraphs
    tables = doc.tables
    print(f"[+] python-docx Parsed Paragraphs: {len(paragraphs)}")
    print(f"[+] python-docx Parsed Tables: {len(tables)}")
    
    # Check student metadata in body paragraphs
    para_text_all = "\n".join(p.text for p in paragraphs)
    name_found = "Billy Zandan" in para_text_all
    id_found = "A01371854" in para_text_all
    print(f"[+] Student Name 'Billy Zandan' in body paragraphs: {name_found}")
    print(f"[+] Student ID 'A01371854' in body paragraphs: {id_found}")
    
    # Check words
    words = para_text_all.split()
    print(f"[+] Total word count in body paragraphs: {len(words)}")
    
    # Check section headings
    headings = [p.text for p in paragraphs if p.text.startswith("Section ") or p.text.startswith("Executive Summary")]
    print(f"[+] Section headings detected ({len(headings)}):")
    for h in headings:
        print(f"    - {h}")
        
    # Check figure captions
    captions = [p.text for p in paragraphs if p.text.startswith("Figure ")]
    print(f"[+] Figure captions detected ({len(captions)}):")
    for c in captions:
        print(f"    - {c}")
        
    # Check table structure
    for i, t in enumerate(tables, 1):
        print(f"[+] Table {i}: {len(t.rows)} rows x {len(t.columns)} cols")
        hdr = [cell.text.replace("\n", " ") for cell in t.rows[0].cells]
        print(f"    Header: {hdr}")
        for r_idx, r in enumerate(t.rows[1:], 1):
            row_vals = [cell.text.replace("\n", " ")[:30] for cell in r.cells]
            print(f"    Row {r_idx}: {row_vals}")
            
    # Check the 6 image carrier names and secrets
    expected_data = {
        "Brain.png": ("RECON: Perform DNS harvesting and Subdomain enumeration.", "Stage 1"),
        "Activation.png": ("VULN: Identify unpatched CVE-2024-XXXX in web gateway.", "Stage 2"),
        "Chemicals.png": ("EXPLOIT: Deploy SQL Injection payload to bypass WAF.", "Stage 3"),
        "Dopamine.png": ("PERSIST: Establish reverse shell via obfuscated cron job.", "Stage 4"),
        "Brain-Channel.png": ("LATERAL: Pivot to internal Domain Controller using Mimikatz.", "Stage 5"),
        "Music.png": ("EXFIL: Tunnel compressed database dump via DNS Covert Channel.", "Stage 6")
    }
    
    print("\n[*] Verifying 6 image carrier names and recovered secrets:")
    full_doc_text = para_text_all + "\n" + "\n".join(" | ".join(cell.text for cell in r.cells) for t in tables for r in t.rows)
    for img_name, (secret, stage) in expected_data.items():
        in_para = img_name in para_text_all and secret in para_text_all
        in_table = any(img_name in " ".join(c.text for c in r.cells) and secret in " ".join(c.text for c in r.cells) for t in tables for r in t.rows)
        print(f"    - {img_name}: In Body Paragraphs={in_para}, In Tables={in_table}")
        assert in_para, f"Missing {img_name} or secret in paragraphs!"
        assert in_table, f"Missing {img_name} or secret in tables!"
        
    # Check reflection questions depth and citations
    print("\n[*] Checking reflection questions depth & citations:")
    ortega_refs = [
        "Ortega",
        "Chapter 13",
        "Chapter 14",
        "getexif",
        "Base64",
        "hashlib",
        "ISO/IEC 27037",
        "Mimikatz",
        "cron",
        "DNS Covert Channel"
    ]
    for ref in ortega_refs:
        count = para_text_all.count(ref)
        print(f"    - '{ref}': found {count} times in body paragraphs")
        assert count > 0, f"Keyword '{ref}' missing from report!"
        
    print("\n[+] ALL DOCX AUDIT CHECKS COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    run_audit()
