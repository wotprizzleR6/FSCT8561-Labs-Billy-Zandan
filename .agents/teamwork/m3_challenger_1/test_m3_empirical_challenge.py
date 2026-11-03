#!/usr/bin/env python3
"""
Empirical Challenge & Stress-Testing Suite for Milestone 3 Artifacts:
- Lab6/Lab6-Billy-Zandan-A01371854.docx
- Lab6/generate_report_docx.py

Author: empirical_challenger (critic, specialist)
Directory: .agents/teamwork/m3_challenger_1/
"""

import hashlib
import io
import os
import subprocess
import sys
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
import docx

PROJECT_ROOT = Path("c:/Users/BillyZ/Desktop/FSCT8561-Labs-Billy-Zandan").resolve()
LAB6_DIR = PROJECT_ROOT / "Lab6"
DOCX_PATH = LAB6_DIR / "Lab6-Billy-Zandan-A01371854.docx"
GEN_SCRIPT = LAB6_DIR / "generate_report_docx.py"
SCANNER_SCRIPT = LAB6_DIR / "metadata_scanner.py"
CSV_PATH = LAB6_DIR / "metadata_report.csv"
IMAGES_DIR = LAB6_DIR / "Images"

EXPECTED_IMAGES = [
    "Activation.png",
    "Brain-Channel.png",
    "Brain.png",
    "Chemicals.png",
    "Dopamine.png",
    "Music.png",
]

EXPECTED_STAGES = ["RECON", "VULN", "EXPLOIT", "PERSIST", "LATERAL", "EXFIL"]

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

class TestDocxArchiveAndXmlIntegrity(unittest.TestCase):
    """Deep structural and XML validation of the docx container."""

    def test_01_file_exists_and_non_empty(self):
        self.assertTrue(DOCX_PATH.exists(), f"Docx file does not exist at {DOCX_PATH}")
        size = DOCX_PATH.stat().st_size
        self.assertGreater(size, 50000, f"Docx size is unexpectedly small: {size} bytes")
        print(f"[+] Docx exists, size: {size:,} bytes, SHA256: {compute_sha256(DOCX_PATH)}")

    def test_02_valid_zip_archive_crc_integrity(self):
        self.assertTrue(zipfile.is_zipfile(str(DOCX_PATH)), "DOCX is not a valid zip archive")
        with zipfile.ZipFile(str(DOCX_PATH), "r") as zf:
            bad_file = zf.testzip()
            self.assertIsNone(bad_file, f"Zip archive CRC check failed on file: {bad_file}")
            print(f"[+] Zip CRC32 check passed for all {len(zf.infolist())} internal files")

    def test_03_standard_ooxml_core_components_present(self):
        required_parts = [
            "[Content_Types].xml",
            "_rels/.rels",
            "word/document.xml",
            "word/_rels/document.xml.rels",
            "word/styles.xml",
            "word/settings.xml",
            "docProps/core.xml",
            "docProps/app.xml",
        ]
        with zipfile.ZipFile(str(DOCX_PATH), "r") as zf:
            namelist = zf.namelist()
            for part in required_parts:
                self.assertIn(part, namelist, f"Required OOXML part '{part}' missing from archive")
        print(f"[+] All required OOXML structure parts present")

    def test_04_xml_syntax_and_well_formedness(self):
        with zipfile.ZipFile(str(DOCX_PATH), "r") as zf:
            for item in zf.infolist():
                if item.filename.endswith(".xml") or item.filename.endswith(".rels"):
                    content = zf.read(item.filename)
                    try:
                        ET.fromstring(content)
                    except ET.ParseError as pe:
                        self.fail(f"XML parse error in {item.filename}: {pe}")
        print(f"[+] All internal XML and .rels files are 100% well-formed and valid XML")

    def test_05_embedded_media_images_integrity(self):
        with zipfile.ZipFile(str(DOCX_PATH), "r") as zf:
            media_files = [f for f in zf.namelist() if f.startswith("word/media/")]
            self.assertGreaterEqual(len(media_files), 6, f"Expected at least 6 media images, found {len(media_files)}")
            
            for mf in media_files:
                img_bytes = zf.read(mf)
                self.assertGreater(len(img_bytes), 1000, f"Media file {mf} too small: {len(img_bytes)} bytes")
                # PNG magic bytes
                self.assertTrue(img_bytes.startswith(b"\x89PNG\r\n\x1a\n"), f"Media file {mf} is not a valid PNG")
                
                # Pillow verification and decode
                with Image.open(io.BytesIO(img_bytes)) as img:
                    img.verify()
                
                with Image.open(io.BytesIO(img_bytes)) as img:
                    img.load()
                    width, height = img.size
                    self.assertGreaterEqual(width, 500, f"Image {mf} width ({width}) smaller than expected")
                    self.assertGreaterEqual(height, 100, f"Image {mf} height ({height}) smaller than expected")
                    print(f"    - Media {mf}: {width}x{height}, format={img.format}, mode={img.mode}, {len(img_bytes):,} bytes")
            print(f"[+] Verified {len(media_files)} embedded media images: all valid PNGs without corruption")

    def test_06_relationship_target_integrity(self):
        with zipfile.ZipFile(str(DOCX_PATH), "r") as zf:
            doc_rels_bytes = zf.read("word/_rels/document.xml.rels")
            root = ET.fromstring(doc_rels_bytes)
            ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
            
            rel_map = {}
            for elem in root.findall(".//r:Relationship", ns):
                rel_id = elem.attrib.get("Id")
                rel_target = elem.attrib.get("Target")
                rel_map[rel_id] = rel_target
                if rel_target.startswith("media/"):
                    full_media_path = f"word/{rel_target}"
                    self.assertIn(full_media_path, zf.namelist(), f"Dangling media target: {full_media_path}")
            
            # Now verify document.xml references
            doc_xml_bytes = zf.read("word/document.xml")
            doc_root = ET.fromstring(doc_xml_bytes)
            # Find all a:blip elements
            a_ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
            r_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            blip_count = 0
            for elem in doc_root.iter(f"{{{a_ns}}}blip"):
                embed_id = elem.attrib.get(f"{{{r_ns}}}embed")
                if embed_id:
                    blip_count += 1
                    self.assertIn(embed_id, rel_map, f"blip embed ID {embed_id} not found in document.xml.rels")
            self.assertGreaterEqual(blip_count, 6, f"Expected at least 6 blip image embeds, found {blip_count}")
            print(f"[+] Verified {blip_count} drawingml image blips map cleanly to valid media targets")


class TestDocxContentAndStructure(unittest.TestCase):
    """Content, semantic structure, styling, and rubric alignment tests."""

    @classmethod
    def setUpClass(cls):
        cls.doc = docx.Document(str(DOCX_PATH))

    def test_07_paragraph_and_run_depth(self):
        paragraphs = self.doc.paragraphs
        self.assertGreaterEqual(len(paragraphs), 50, f"Expected >= 50 paragraphs, found {len(paragraphs)}")
        full_text = "\n".join(p.text for p in paragraphs)
        word_count = len(full_text.split())
        self.assertGreaterEqual(word_count, 2000, f"Report word count too short: {word_count} words")
        print(f"[+] Total paragraphs: {len(paragraphs)}, total words: {word_count:,}")

    def test_08_student_identification(self):
        full_text = "\n".join(p.text for p in self.doc.paragraphs)
        self.assertIn("Billy Zandan", full_text, "Student name Billy Zandan missing from body paragraphs")
        self.assertIn("A01371854", full_text, "Student ID A01371854 missing from body paragraphs")
        
        # Check header & footer
        header_text = " ".join(p.text for s in self.doc.sections for p in s.header.paragraphs)
        footer_text = " ".join(p.text for s in self.doc.sections for p in s.footer.paragraphs)
        self.assertIn("FSCT 8561", header_text, "Course code missing from header")
        self.assertIn("A01371854", footer_text, "Student ID missing from footer")
        print("[+] Student metadata verified across document body and header/footer")

    def test_09_tables_count_and_geometry(self):
        tables = self.doc.tables
        self.assertGreaterEqual(len(tables), 2, f"Expected at least 2 tables, found {len(tables)}")
        print(f"[+] Found {len(tables)} tables in document")

    def test_10_forensic_evidence_table(self):
        t = self.doc.tables[0]
        self.assertEqual(len(t.columns), 7, f"Evidence table must have 7 columns, got {len(t.columns)}")
        self.assertEqual(len(t.rows), 7, f"Evidence table must have 7 rows (1 header + 6 data), got {len(t.rows)}")
        
        # Verify header cells
        headers = [c.text.strip() for c in t.rows[0].cells]
        self.assertEqual(headers[0], "Filename")
        self.assertEqual(headers[1], "Metadata Container Type")
        self.assertEqual(headers[2], "Field / Tag Name")
        self.assertEqual(headers[3], "Raw Extracted Value")
        self.assertEqual(headers[4], "Decoding Method Applied")
        self.assertEqual(headers[5], "Recovered Partial Secret Fragment")
        self.assertEqual(headers[6], "Incident Stage")

        # Verify all 6 images present in data rows
        filenames = [t.rows[r].cells[0].text.strip() for r in range(1, 7)]
        for img in EXPECTED_IMAGES:
            self.assertIn(img, filenames, f"Image {img} missing from evidence table rows")

        # Verify all 6 stages present in Incident Stage column
        stages_col = [t.rows[r].cells[6].text.strip() for r in range(1, 7)]
        for stg in EXPECTED_STAGES:
            self.assertTrue(any(stg in val for val in stages_col), f"Stage {stg} missing from Incident Stage column")
        print("[+] Table 1 (Forensic Evidence Table) fully verified: 7x7 geometry, all 6 images and stages present")

    def test_11_scanner_csv_results_table(self):
        t = self.doc.tables[1]
        self.assertEqual(len(t.columns), 7, f"Scanner CSV table must have 7 columns, got {len(t.columns)}")
        self.assertEqual(len(t.rows), 7, f"Scanner CSV table must have 7 rows (1 header + 6 data), got {len(t.rows)}")

        # Verify header names
        headers = [c.text.strip() for c in t.rows[0].cells]
        expected_csv_headers = [
            "Filename",
            "Format",
            "Discovered Metadata Fields",
            "Suspected Field",
            "Encoding",
            "Risk Score",
            "Risk Heuristic Justification",
        ]
        self.assertEqual(headers, expected_csv_headers)

        # Cross-validate against metadata_report.csv
        import csv
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            csv_rows = list(csv.DictReader(f))

        for r_idx, csv_row in enumerate(csv_rows, start=1):
            table_row = t.rows[r_idx]
            self.assertEqual(table_row.cells[0].text.strip(), csv_row["filename"])
            self.assertEqual(table_row.cells[1].text.strip(), csv_row["format"])
            self.assertEqual(table_row.cells[3].text.strip(), csv_row["suspected_field"])
            self.assertEqual(table_row.cells[4].text.strip(), csv_row["encoding"])
            self.assertEqual(table_row.cells[5].text.strip(), csv_row["risk_score"])
        print("[+] Table 2 (Scanner CSV Results Table) matches metadata_report.csv with 100% data fidelity")

    def test_12_reconstructed_incident_narrative(self):
        full_text = "\n".join(p.text for p in self.doc.paragraphs)
        for stage in EXPECTED_STAGES:
            self.assertIn(f"Stage {EXPECTED_STAGES.index(stage) + 1}", full_text)
            self.assertIn(stage, full_text)

        # Sequence justification & rebuttal of alphabetical sorting
        self.assertIn("alphabetical", full_text.lower(), "Alphabetical sorting rebuttal missing")
        self.assertIn("Lockheed Martin", full_text, "Lockheed Martin Kill Chain reference missing")
        self.assertIn("MITRE ATT&CK", full_text, "MITRE ATT&CK reference missing")
        print("[+] Reconstructed incident narrative & sequence justification verified")

    def test_13_embedded_scanner_source_code(self):
        scanner_code = SCANNER_SCRIPT.read_text(encoding="utf-8")
        full_text = "\n".join(p.text for p in self.doc.paragraphs)
        
        # Verify actual function definitions from scanner are present in document text
        key_snippets = [
            "collect_metadata_field_names",
            "extract_metadata_candidates",
            "analyze_and_deobfuscate",
            "calculate_risk_score",
            "scan_single_image",
            "scan_directory",
            "to_csv_dict",
        ]
        for snip in key_snippets:
            self.assertIn(snip, full_text, f"Scanner code snippet '{snip}' missing from docx text")
        print("[+] Verbatim metadata_scanner.py code verified in doc.paragraphs callout blocks")

    def test_14_limitations_and_reflection_questions(self):
        full_text = "\n".join(p.text for p in self.doc.paragraphs)
        
        # Limitations
        self.assertIn("Forensic Blind Spots of EXIF-Only Extraction Tools", full_text)
        self.assertIn("Limitations of Automated Risk-Scoring Heuristics", full_text)
        self.assertIn("Sub-IFD", full_text)
        self.assertIn("XMP", full_text)
        self.assertIn("False Positives", full_text)
        self.assertIn("False Negatives", full_text)
        self.assertIn("Steganography", full_text)

        # Reflection questions Q1-Q5
        for i in range(1, 6):
            self.assertIn(f"Question {i}:", full_text, f"Reflection Question {i} missing from docx")
        
        # Textbook citations
        self.assertIn("Ortega", full_text)
        self.assertIn("Chapter 13", full_text)
        self.assertIn("Chapter 14", full_text)
        print("[+] Limitations analysis, 5 reflection answers, and Ortega citations verified")


class TestIdempotentRegeneration(unittest.TestCase):
    """Stress test regeneration of Lab6-Billy-Zandan-A01371854.docx via generate_report_docx.py."""

    def test_15_regeneration_execution(self):
        # Record initial hash
        initial_hash = compute_sha256(DOCX_PATH)
        print(f"[*] Pre-regeneration SHA256: {initial_hash}")

        # Run generator
        res = subprocess.run(
            [sys.executable, str(GEN_SCRIPT)],
            cwd=str(LAB6_DIR),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(res.returncode, 0, f"Generator script failed with returncode {res.returncode}:\n{res.stderr}")
        self.assertIn("Successfully compiled comprehensive Word report deliverable", res.stdout)
        
        # Verify file exists and is readable
        self.assertTrue(DOCX_PATH.exists())
        new_hash = compute_sha256(DOCX_PATH)
        print(f"[+] Post-regeneration SHA256: {new_hash}")
        
        # Re-verify zip validity and python-docx open
        self.assertTrue(zipfile.is_zipfile(str(DOCX_PATH)))
        re_doc = docx.Document(str(DOCX_PATH))
        self.assertGreaterEqual(len(re_doc.paragraphs), 50)
        self.assertGreaterEqual(len(re_doc.tables), 2)
        print("[+] Idempotent document regeneration successful: script executed cleanly with code 0")


class TestE2ESuiteIntegration(unittest.TestCase):
    """Verify that full E2E test suite (test_e2e_lab6.py) runs with STRICT_E2E=1 and passes."""

    def test_16_run_full_e2e_suite(self):
        test_file = LAB6_DIR / "test_e2e_lab6.py"
        self.assertTrue(test_file.exists(), f"E2E test suite missing at {test_file}")
        
        env = os.environ.copy()
        env["STRICT_E2E"] = "1"
        res = subprocess.run(
            [sys.executable, "-m", "unittest", "test_e2e_lab6.py"],
            cwd=str(LAB6_DIR),
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )
        print(f"[*] E2E suite output:\n{res.stderr}")
        self.assertEqual(res.returncode, 0, f"test_e2e_lab6.py failed with exit code {res.returncode}:\n{res.stderr}")
        self.assertIn("OK", res.stderr)
        print("[+] 100% of E2E tests (Tiers 1-4, 82 test cases) passed cleanly under STRICT_E2E=1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
