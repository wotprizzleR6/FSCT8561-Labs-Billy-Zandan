"""
Verify prototype document against all 13 Docx test assertions from test_e2e_lab6.py.
"""

import csv
import unittest
import zipfile
from pathlib import Path
import docx

DOCX_PATH = Path(__file__).parent / "test_full_report.docx"
CSV_PATH = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv")
STUDENT_NAME = "Billy Zandan"
STUDENT_ID = "A01371854"

EXPECTED_IMAGES = [
    "Activation.png",
    "Brain-Channel.png",
    "Brain.png",
    "Chemicals.png",
    "Dopamine.png",
    "Music.png",
]

class TestPrototypeDocx(unittest.TestCase):

    def setUp(self):
        self.doc = docx.Document(str(DOCX_PATH))

    # Test 31
    def test_31_file_exists_and_valid(self):
        self.assertIsNotNone(self.doc)

    # Test 32
    def test_32_student_metadata(self):
        full_text = "\n".join(p.text for p in self.doc.paragraphs)
        for t in self.doc.tables:
            for row in t.rows:
                for c in row.cells:
                    full_text += "\n" + c.text
        self.assertIn(STUDENT_NAME, full_text)
        self.assertIn(STUDENT_ID, full_text)

    # Test 33
    def test_33_all_rubric_sections_present(self):
        full_text = "\n".join(p.text for p in self.doc.paragraphs).lower()
        rubric_keywords = ["evidence", "reconstructed", "scanner", "limitation", "reflection"]
        for kw in rubric_keywords:
            self.assertIn(kw, full_text)

    # Test 34
    def test_34_evidence_table_structure(self):
        self.assertGreaterEqual(len(self.doc.tables), 1)
        found_table = False
        for t in self.doc.tables:
            table_text = " ".join(c.text for row in t.rows for c in row.cells)
            if all(img in table_text for img in EXPECTED_IMAGES):
                found_table = True
                self.assertGreaterEqual(len(t.rows), 7)
                break
        self.assertTrue(found_table)

    # Test 35
    def test_35_limitations_and_reflections_addressed(self):
        full_text = "\n".join(p.text for p in self.doc.paragraphs)
        self.assertIn("EXIF", full_text)
        self.assertIn("Base64", full_text)
        self.assertIn("hash", full_text.lower())
        self.assertGreater(len(full_text.split()), 500)

    # Test 66
    def test_66_minimum_length_and_depth(self):
        self.assertGreaterEqual(len(self.doc.paragraphs), 15)

    # Test 67
    def test_67_evidence_table_column_count(self):
        found = False
        for t in self.doc.tables:
            if len(t.columns) >= 5:
                found = True
                break
        self.assertTrue(found)

    # Test 68
    def test_68_csv_results_table_present(self):
        found = False
        for t in self.doc.tables:
            header_text = " ".join(c.text.lower() for c in t.rows[0].cells)
            if "risk" in header_text or "suspected" in header_text:
                found = True
                break
        self.assertTrue(found)

    # Test 69
    def test_69_scanner_code_snippet_present(self):
        full_text = "\n".join(p.text for p in self.doc.paragraphs)
        self.assertTrue("import" in full_text and ("def " in full_text or "class " in full_text or "Image.open" in full_text))

    # Test 70
    def test_70_xml_package_validity(self):
        self.assertTrue(zipfile.is_zipfile(str(DOCX_PATH)))
        with zipfile.ZipFile(str(DOCX_PATH)) as zf:
            self.assertIn("word/document.xml", zf.namelist())

    # Test 76
    def test_76_csv_table_matches_metadata_report_csv(self):
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            csv_rows = list(csv.DictReader(f))
        doc_text = " ".join(c.text for t in self.doc.tables for row in t.rows for c in row.cells)
        for r in csv_rows:
            self.assertIn(r["filename"], doc_text)
            self.assertIn(str(r["risk_score"]), doc_text)

    # Test 77
    def test_77_reflections_match_notebook_answers(self):
        doc_text = "\n".join(p.text for p in self.doc.paragraphs)
        prompts = ["getexif", "Base64", "hash", "corroborat", "Lab"]
        for p in prompts:
            self.assertIn(p.lower(), doc_text.lower())

    # Scenario 5 deliverable check
    def test_82_scenario_5_table_count(self):
        self.assertGreaterEqual(len(self.doc.tables), 2)

if __name__ == "__main__":
    unittest.main()
