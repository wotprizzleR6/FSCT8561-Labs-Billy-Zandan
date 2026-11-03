#!/usr/bin/env python3
"""
Verification Script for Milestone 3 Word Document Deliverable.
Validates Lab6-Billy-Zandan-A01371854.docx against all 13 E2E test assertions
and rubric delivery requirements before running pytest.

Usage:
    python verify_docx.py [optional_path_to_docx]
"""

import csv
import os
from pathlib import Path
import sys
import zipfile
from typing import Dict, List, Tuple

try:
    import docx
    from docx import Document
except ImportError:
    print("ERROR: python-docx is not installed in the current environment.")
    print("Install via: pip install python-docx")
    sys.exit(1)


# Default paths
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
LAB6_DIR = REPO_ROOT / "Lab6"
DEFAULT_DOCX_PATH = LAB6_DIR / "Lab6-Billy-Zandan-A01371854.docx"
CSV_PATH = LAB6_DIR / "metadata_report.csv"

# Authoritative Constants matching test_e2e_lab6.py
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

RUBRIC_KEYWORDS = [
    "evidence",
    "reconstructed",
    "scanner",
    "limitation",
    "reflection",
]

REFLECTION_KEYWORDS = [
    "getexif",
    "base64",
    "hash",
    "corroborat",
    "lab",
]


class DocxVerifier:
    def __init__(self, docx_path: Path, csv_path: Path = CSV_PATH):
        self.docx_path = docx_path
        self.csv_path = csv_path
        self.checks: List[Tuple[str, str, bool, str]] = []  # (test_id, name, passed, details)

    def record(self, test_id: str, name: str, passed: bool, details: str):
        self.checks.append((test_id, name, passed, details))

    def run_all_checks(self) -> bool:
        print(f"================================================================================")
        print(f"VERIFYING DOCX DELIVERABLE: {self.docx_path.name}")
        print(f"Target Path: {self.docx_path}")
        print(f"================================================================================")

        # 1. File existence
        if not self.docx_path.exists():
            self.record(
                "test_t1_f7_31",
                "File Existence",
                False,
                f"File not found at: {self.docx_path}"
            )
            self._print_summary()
            return False

        file_size_kb = self.docx_path.stat().st_size / 1024
        print(f"[*] File exists ({file_size_kb:.1f} KB)")

        # 2. Package / Zip validity (test_t2_f7_70)
        is_zip = zipfile.is_zipfile(str(self.docx_path))
        has_doc_xml = False
        if is_zip:
            try:
                with zipfile.ZipFile(str(self.docx_path)) as zf:
                    has_doc_xml = "word/document.xml" in zf.namelist()
            except Exception as e:
                is_zip = False
        self.record(
            "test_t2_f7_70",
            "OOXML Zip Package Validity",
            is_zip and has_doc_xml,
            f"Valid zip: {is_zip}, contains word/document.xml: {has_doc_xml}"
        )

        # 3. Load with python-docx (test_t1_f7_31)
        doc = None
        try:
            doc = Document(str(self.docx_path))
            self.record(
                "test_t1_f7_31",
                "Docx Parser Load Success",
                True,
                "Document opened cleanly with python-docx"
            )
        except Exception as e:
            self.record(
                "test_t1_f7_31",
                "Docx Parser Load Success",
                False,
                f"Failed to parse document: {e}"
            )
            self._print_summary()
            return False

        # Extract texts
        body_paragraphs = [p.text for p in doc.paragraphs]
        para_text = "\n".join(body_paragraphs)
        para_text_lower = para_text.lower()
        word_count = len(para_text.split())

        # Collect table texts
        table_cells_text = []
        for t in doc.tables:
            for row in t.rows:
                for c in row.cells:
                    table_cells_text.append(c.text)
        all_table_text = " ".join(table_cells_text)
        combined_text = para_text + "\n" + all_table_text

        # 4. Student Metadata in paragraph/table text (test_t1_f7_32)
        has_name = STUDENT_NAME in combined_text
        has_id = STUDENT_ID in combined_text
        self.record(
            "test_t1_f7_32",
            "Student Metadata (Global)",
            has_name and has_id,
            f"Name '{STUDENT_NAME}': {has_name}, ID '{STUDENT_ID}': {has_id}"
        )

        # 5. Rubric Section Headings in Paragraph Text (test_t1_f7_33)
        missing_rubric = [kw for kw in RUBRIC_KEYWORDS if kw not in para_text_lower]
        self.record(
            "test_t1_f7_33",
            "Rubric Section Headings (Paragraphs)",
            len(missing_rubric) == 0,
            f"Checked: {RUBRIC_KEYWORDS}; Missing: {missing_rubric}"
        )

        # 6. Evidence Table Structure (test_t1_f7_34)
        found_ev_table = False
        ev_table_rows = 0
        for t in doc.tables:
            t_text = " ".join(c.text for row in t.rows for c in row.cells)
            if all(img in t_text for img in EXPECTED_IMAGES):
                found_ev_table = True
                ev_table_rows = len(t.rows)
                break
        self.record(
            "test_t1_f7_34",
            "Evidence Table Structure (6 Images, >=7 rows)",
            found_ev_table and ev_table_rows >= 7,
            f"Found table: {found_ev_table}, Row count: {ev_table_rows} (min 7 required)"
        )

        # 7. Limitations & Reflection Substantive Text (test_t1_f7_35)
        has_exif = "EXIF" in para_text
        has_base64 = "Base64" in para_text
        has_hash = "hash" in para_text_lower
        word_count_ok = word_count > 500
        self.record(
            "test_t1_f7_35",
            "Limitations & Substantive Text (>500 words, EXIF, Base64, hash)",
            has_exif and has_base64 and has_hash and word_count_ok,
            f"Words: {word_count} (>500), EXIF: {has_exif}, Base64: {has_base64}, hash: {has_hash}"
        )

        # 8. Minimum Paragraph Count (test_t2_f7_66)
        para_count = len(doc.paragraphs)
        self.record(
            "test_t2_f7_66",
            "Paragraph Count (>=15 paragraphs)",
            para_count >= 15,
            f"Paragraphs: {para_count} (min 15 required)"
        )

        # 9. Evidence Table Column Count (test_t2_f7_67)
        max_cols = max((len(t.columns) for t in doc.tables), default=0)
        self.record(
            "test_t2_f7_67",
            "Table Column Count (>=5 columns)",
            max_cols >= 5,
            f"Max table columns found: {max_cols} (min 5 required)"
        )

        # 10. CSV Results Table Present (test_t2_f7_68)
        found_csv_table = False
        for t in doc.tables:
            if len(t.rows) > 0:
                header_text = " ".join(c.text.lower() for c in t.rows[0].cells)
                if "risk" in header_text or "suspected" in header_text:
                    found_csv_table = True
                    break
        self.record(
            "test_t2_f7_68",
            "CSV Results Table Header ('risk' or 'suspected')",
            found_csv_table,
            f"CSV header found in doc.tables: {found_csv_table}"
        )

        # 11. Scanner Source Code in Paragraphs (test_t2_f7_69)
        # MUST reside in doc.paragraphs!
        has_import = "import" in para_text
        has_code_element = ("def " in para_text) or ("class " in para_text) or ("Image.open" in para_text)
        self.record(
            "test_t2_f7_69",
            "Scanner Source Code Snippet in Body Paragraphs",
            has_import and has_code_element,
            f"'import': {has_import}, 'def '/'class '/'Image.open': {has_code_element}"
        )

        # 12. CSV Table Data Consistency with metadata_report.csv (test_t3_76)
        csv_consistent = True
        csv_details = []
        if self.csv_path.exists():
            with open(self.csv_path, "r", encoding="utf-8") as f:
                csv_rows = list(csv.DictReader(f))
            for r in csv_rows:
                fn = r["filename"]
                score = str(r["risk_score"])
                if fn not in all_table_text or score not in all_table_text:
                    csv_consistent = False
                    csv_details.append(f"Missing {fn} or score {score}")
            details_str = "All 6 filenames and risk scores found in tables" if csv_consistent else "; ".join(csv_details)
        else:
            csv_consistent = False
            details_str = f"CSV report not found at: {self.csv_path}"
        self.record(
            "test_t3_76",
            "CSV Table Matches metadata_report.csv Content",
            csv_consistent,
            details_str
        )

        # 13. Reflection Prompts Addressed in Paragraphs (test_t3_77)
        missing_prompts = [p for p in REFLECTION_KEYWORDS if p not in para_text_lower]
        self.record(
            "test_t3_77",
            "Reflection Prompts Addressed in Paragraphs",
            len(missing_prompts) == 0,
            f"Checked: {REFLECTION_KEYWORDS}; Missing: {missing_prompts}"
        )

        # 14. Scenario 5 Delivery Audit (test_t4_82)
        # Note: requires STUDENT_NAME and STUDENT_ID in doc.paragraphs directly!
        name_in_para = STUDENT_NAME in para_text
        id_in_para = STUDENT_ID in para_text
        table_count = len(doc.tables)
        scenario_ok = name_in_para and id_in_para and (table_count >= 2)
        self.record(
            "test_t4_82",
            "Scenario 5 Audit (Name & ID in Paragraphs + >=2 Tables)",
            scenario_ok,
            f"Name in para: {name_in_para}, ID in para: {id_in_para}, Tables: {table_count} (min 2)"
        )

        self._print_summary()
        return all(p for _, _, p, _ in self.checks)

    def _print_summary(self):
        print(f"\n================================================================================")
        print(f"VERIFICATION RESULTS SUMMARY")
        print(f"================================================================================")
        passed_count = sum(1 for _, _, p, _ in self.checks if p)
        total_count = len(self.checks)

        for test_id, name, passed, details in self.checks:
            status = "PASS" if passed else "FAIL"
            marker = "[+]" if passed else "[X]"
            print(f"{marker} {status:<4} | {test_id:<14} | {name}")
            print(f"          Details: {details}")

        print(f"--------------------------------------------------------------------------------")
        print(f"TOTAL: {passed_count}/{total_count} assertions passed.")
        if passed_count == total_count:
            print("STATUS: ALL DOCX VERIFICATION CHECKS PASSED (100% READY FOR M4 VERIFICATION)!")
        else:
            print("STATUS: VERIFICATION DEFICIENCIES DETECTED — REMEDIATION REQUIRED.")
        print(f"================================================================================\n")


def main():
    target_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DOCX_PATH
    verifier = DocxVerifier(target_path)
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
