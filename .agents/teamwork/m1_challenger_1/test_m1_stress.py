#!/usr/bin/env python3
"""
Stress Test and Adversarial Verification Harness for Milestone 1.
Tests metadata_scanner.py and metadata_report.csv against rigorous failure modes,
CLI options, edge cases, and RFC 4180 compliance.

Owner: m1_challenger_1
"""

import csv
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[3]
LAB6_DIR = REPO_ROOT / "Lab6"
SCANNER_SCRIPT = LAB6_DIR / "metadata_scanner.py"
REPORT_CSV = LAB6_DIR / "metadata_report.csv"
IMAGES_DIR = LAB6_DIR / "Images"
CHALLENGER_DIR = Path(__file__).resolve().parent

EXPECTED_HEADERS = [
    "filename",
    "format",
    "metadata_fields",
    "suspected_field",
    "encoding",
    "risk_score",
    "reason",
]

EXPECTED_FILES = [
    "Activation.png",
    "Brain-Channel.png",
    "Brain.png",
    "Chemicals.png",
    "Dopamine.png",
    "Music.png",
]

EXPECTED_SCORES = {
    "Activation.png": 15,
    "Brain-Channel.png": 10,
    "Brain.png": 10,
    "Chemicals.png": 10,
    "Dopamine.png": 15,
    "Music.png": 15,
}

EXPECTED_SUSPECTED_FIELDS = {
    "Activation.png": "UserComment",
    "Brain-Channel.png": "ImageDescription",
    "Brain.png": "Software",
    "Chemicals.png": "ImageDescription",
    "Dopamine.png": "XML:com.adobe.xmp (exif:MakerNote)",
    "Music.png": "Copyright",
}

EXPECTED_ENCODINGS = {
    "Activation.png": "EXIF ASCII header / plain text",
    "Brain-Channel.png": "None (plain text)",
    "Brain.png": "None (plain text)",
    "Chemicals.png": "None (plain text)",
    "Dopamine.png": "XML encapsulation / plain text",
    "Music.png": "Base64",
}


def run_scanner(*args, cwd=None):
    """Helper to run metadata_scanner.py with specified arguments."""
    cmd = [sys.executable, str(SCANNER_SCRIPT)] + list(args)
    proc = subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc


class TestCLIRobustnessAndFlags(unittest.TestCase):
    """Stress tests covering CLI argument parsing, flags, and error exits."""

    def test_non_existent_images_directory(self):
        """Test scanning non-existent directory: exit code 1, graceful error message, no traceback."""
        bogus_dir = "non_existent_dir_987654321"
        proc = run_scanner("--images", bogus_dir)
        self.assertEqual(proc.returncode, 1, f"Expected returncode 1, got {proc.returncode}")
        self.assertIn("Error: Target image directory not found", proc.stderr)
        self.assertNotIn("Traceback (most recent call last):", proc.stderr, "Unhandled traceback leaked!")

    def test_custom_output_path_generation_and_cleanup(self):
        """Test --output custom path creates file and cleans up cleanly."""
        temp_csv = CHALLENGER_DIR / "test_custom_output.csv"
        if temp_csv.exists():
            temp_csv.unlink()

        try:
            proc = run_scanner("-i", str(IMAGES_DIR), "-o", str(temp_csv))
            self.assertEqual(proc.returncode, 0, f"Scanner failed with {proc.stderr}")
            self.assertTrue(temp_csv.exists(), "Custom CSV file was not created!")
            
            with open(temp_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 6, f"Expected 6 rows in custom CSV, got {len(rows)}")
                self.assertEqual(reader.fieldnames, EXPECTED_HEADERS)
        finally:
            if temp_csv.exists():
                temp_csv.unlink()

    def test_nested_directory_creation_for_output(self):
        """Test --output in non-existent nested directory creates parent dirs."""
        nested_csv = CHALLENGER_DIR / "nested" / "sub" / "output_report.csv"
        if nested_csv.parent.exists():
            shutil.rmtree(nested_csv.parent.parent)

        try:
            proc = run_scanner("-i", str(IMAGES_DIR), "-o", str(nested_csv))
            self.assertEqual(proc.returncode, 0, f"Scanner failed: {proc.stderr}")
            self.assertTrue(nested_csv.exists(), "Nested CSV not created!")
        finally:
            if nested_csv.parent.exists():
                shutil.rmtree(nested_csv.parent.parent)

    def test_verbose_flag_outputs_detailed_diagnostics(self):
        """Test --verbose flag prints recovered secrets and extra fields."""
        proc = run_scanner("-i", str(IMAGES_DIR), "-v")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Recovered Secret:", proc.stdout)
        self.assertIn("Suspected Field :", proc.stdout)
        self.assertIn("Risk Score      :", proc.stdout)
        self.assertIn("Reason          :", proc.stdout)
        # Check that individual secrets are printed
        self.assertIn("RECON:", proc.stdout)
        self.assertIn("VULN:", proc.stdout)
        self.assertIn("EXPLOIT:", proc.stdout)
        self.assertIn("PERSIST:", proc.stdout)
        self.assertIn("LATERAL:", proc.stdout)
        self.assertIn("EXFIL:", proc.stdout)

    def test_quiet_flag_suppresses_stdout(self):
        """Test --quiet flag suppresses standard console logs."""
        temp_csv = CHALLENGER_DIR / "quiet_test.csv"
        try:
            proc = run_scanner("-i", str(IMAGES_DIR), "-o", str(temp_csv), "-q")
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(proc.stdout.strip(), "", f"Expected empty stdout with --quiet, got:\n{proc.stdout}")
            self.assertEqual(proc.stderr.strip(), "")
            self.assertTrue(temp_csv.exists(), "CSV should still be written even in quiet mode")
        finally:
            if temp_csv.exists():
                temp_csv.unlink()

    def test_help_flag(self):
        """Test -h / --help prints usage and exits 0."""
        for flag in ["-h", "--help"]:
            proc = run_scanner(flag)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("Automated Image Metadata Covert Channel Scanner", proc.stdout)
            self.assertIn("--images", proc.stdout)
            self.assertIn("--output", proc.stdout)

    def test_cwd_resilience_from_lab6_directory(self):
        """Test running script from within Lab6 directory with default arguments."""
        proc = run_scanner(cwd=LAB6_DIR)
        self.assertEqual(proc.returncode, 0, f"Running from Lab6 failed: {proc.stderr}")
        self.assertIn("Found 6 PNG image(s)", proc.stdout)

    def test_cwd_resilience_from_repo_root(self):
        """Test running script from repo root without explicit -i."""
        proc = run_scanner(cwd=REPO_ROOT)
        self.assertEqual(proc.returncode, 0, f"Running from root failed: {proc.stderr}")
        self.assertIn("Found 6 PNG image(s)", proc.stdout)


class TestEdgeCasesAndAdversarialInputs(unittest.TestCase):
    """Adversarial stress testing on empty folders, non-image files, corrupted images."""

    def test_empty_images_directory(self):
        """Empty images directory should output 0 records gracefully without crashing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_csv = CHALLENGER_DIR / "empty_dir_test.csv"
            try:
                proc = run_scanner("-i", tmpdir, "-o", str(temp_csv))
                self.assertEqual(proc.returncode, 0)
                self.assertIn("Found 0 PNG image(s)", proc.stdout)
                self.assertTrue(temp_csv.exists())
                with open(temp_csv, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    self.assertEqual(len(rows), 1, "Expected only header row for empty directory")
                    self.assertEqual(rows[0], EXPECTED_HEADERS)
            finally:
                if temp_csv.exists():
                    temp_csv.unlink()

    def test_corrupted_png_handling(self):
        """Corrupted PNG file should be logged to stderr without halting scan of valid images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Copy one valid image
            shutil.copy2(IMAGES_DIR / "Brain.png", tmppath / "Brain.png")
            # Write a corrupt image file with .png extension
            corrupt_png = tmppath / "Corrupted.png"
            with open(corrupt_png, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\xff" * 50)  # malformed chunk

            temp_csv = CHALLENGER_DIR / "corrupt_test.csv"
            try:
                proc = run_scanner("-i", str(tmppath), "-o", str(temp_csv))
                self.assertEqual(proc.returncode, 0, "Scanner should not crash completely on single corrupt file")
                self.assertIn("Error scanning Corrupted.png", proc.stderr)
                self.assertTrue(temp_csv.exists())
                with open(temp_csv, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    self.assertEqual(len(rows), 1, "Only valid image should be in results")
                    self.assertEqual(rows[0]["filename"], "Brain.png")
            finally:
                if temp_csv.exists():
                    temp_csv.unlink()

    def test_non_png_files_ignored(self):
        """Files with non-PNG extensions in images directory must be ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            shutil.copy2(IMAGES_DIR / "Chemicals.png", tmppath / "Chemicals.png")
            (tmppath / "notes.txt").write_text("Hello world", encoding="utf-8")
            (tmppath / "subfolder").mkdir()
            (tmppath / "data.csv").write_text("a,b,c", encoding="utf-8")

            temp_csv = CHALLENGER_DIR / "non_png_test.csv"
            try:
                proc = run_scanner("-i", str(tmppath), "-o", str(temp_csv))
                self.assertEqual(proc.returncode, 0)
                self.assertIn("Found 1 PNG image(s)", proc.stdout)
                with open(temp_csv, "r", encoding="utf-8") as f:
                    rows = list(csv.DictReader(f))
                    self.assertEqual(len(rows), 1)
                    self.assertEqual(rows[0]["filename"], "Chemicals.png")
            finally:
                if temp_csv.exists():
                    temp_csv.unlink()


class TestCSVComplianceAndDataIntegrity(unittest.TestCase):
    """Strict RFC 4180 parsing, schema verification, and heuristic score validation."""

    def setUp(self):
        self.assertTrue(REPORT_CSV.exists(), f"Report file not found: {REPORT_CSV}")
        with open(REPORT_CSV, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, dialect="excel")
            self.raw_rows = list(reader)

        with open(REPORT_CSV, "r", encoding="utf-8", newline="") as f:
            dict_reader = csv.DictReader(f)
            self.dict_rows = list(dict_reader)

    def test_exact_header_names_and_order(self):
        """Verify CSV header strictly matches the 7 required columns."""
        header = self.raw_rows[0]
        self.assertEqual(header, EXPECTED_HEADERS, f"Header mismatch: {header} vs {EXPECTED_HEADERS}")

    def test_exact_row_count(self):
        """Verify exactly 6 data rows (1 header + 6 data rows = 7 total)."""
        self.assertEqual(len(self.raw_rows), 7, f"Expected 7 lines total (1 header + 6 rows), got {len(self.raw_rows)}")
        self.assertEqual(len(self.dict_rows), 6, f"Expected 6 data rows, got {len(self.dict_rows)}")

    def test_all_rows_have_7_fields(self):
        """Verify every row has exactly 7 columns (RFC 4180 field count)."""
        for i, row in enumerate(self.raw_rows):
            self.assertEqual(len(row), 7, f"Row {i} has {len(row)} columns, expected 7. Content: {row}")

    def test_all_expected_images_present_and_unique(self):
        """Verify all 6 canonical images are present exactly once."""
        filenames = [r["filename"] for r in self.dict_rows]
        self.assertEqual(sorted(filenames), sorted(EXPECTED_FILES))
        self.assertEqual(len(filenames), len(set(filenames)), "Duplicate images detected in CSV!")

    def test_no_nan_or_null_or_empty_values(self):
        """Verify no NaN, null, None, or empty values in any field."""
        invalid_patterns = {"nan", "null", "none", "undefined", ""}
        for row_idx, row in enumerate(self.dict_rows, 1):
            for col in EXPECTED_HEADERS:
                val = row[col]
                self.assertIsNotNone(val, f"None value in row {row_idx}, column {col}")
                self.assertNotIn(
                    val.strip().lower(),
                    invalid_patterns,
                    f"Invalid or empty value '{val}' in row {row_idx}, column {col}",
                )

    def test_format_column_values(self):
        """Verify all format entries are 'PNG'."""
        for row in self.dict_rows:
            self.assertEqual(row["format"], "PNG", f"Unexpected format for {row['filename']}: {row['format']}")

    def test_suspected_fields_ground_truth(self):
        """Verify suspected_field matches ground truth for each image."""
        for row in self.dict_rows:
            fname = row["filename"]
            expected_field = EXPECTED_SUSPECTED_FIELDS[fname]
            self.assertEqual(
                row["suspected_field"],
                expected_field,
                f"Suspected field mismatch for {fname}: got '{row['suspected_field']}', expected '{expected_field}'",
            )

    def test_encodings_ground_truth(self):
        """Verify encoding matches ground truth for each image."""
        for row in self.dict_rows:
            fname = row["filename"]
            expected_enc = EXPECTED_ENCODINGS[fname]
            self.assertEqual(
                row["encoding"],
                expected_enc,
                f"Encoding mismatch for {fname}: got '{row['encoding']}', expected '{expected_enc}'",
            )

    def test_risk_scores_and_heuristic_reasons(self):
        """Verify risk scores match heuristic rules (10, 15) and reasons clearly document the additions."""
        for row in self.dict_rows:
            fname = row["filename"]
            score = int(row["risk_score"])
            expected_score = EXPECTED_SCORES[fname]
            self.assertEqual(score, expected_score, f"Risk score mismatch for {fname}: got {score}, expected {expected_score}")

            reason = row["reason"]
            self.assertIn("+10", reason, f"Reason for {fname} must mention +10 confirmed covert message")
            if score == 15:
                self.assertIn("+5", reason, f"Reason for {fname} with score 15 must document +5 addition")

    def test_rfc4180_quotes_and_commas(self):
        """Verify fields containing commas are properly escaped/quoted and parsed correctly."""
        for row in self.dict_rows:
            # Rows with multiple fields should contain commas parsed cleanly inside metadata_fields
            if row["filename"] != "Chemicals.png":
                self.assertIn(",", row["metadata_fields"], f"metadata_fields for {row['filename']} should contain commas")
            # If reason contains a semicolon or comma, verify it was parsed as a single field
            self.assertIn("+10", row["reason"])
            # Ensure the row did not get split into extra columns
            self.assertEqual(len(row), 7)


class TestNarrativeReconstructionAccuracy(unittest.TestCase):
    """Empirical verification of secret extraction and Kill Chain alignment."""

    def test_extraction_and_sequence(self):
        """Directly invoke scanner module functions to verify all 6 secret fragments."""
        sys.path.insert(0, str(LAB6_DIR))
        try:
            import metadata_scanner
        finally:
            if sys.path[0] == str(LAB6_DIR):
                sys.path.pop(0)

        secrets = {}
        for fname in EXPECTED_FILES:
            img_path = IMAGES_DIR / fname
            result = metadata_scanner.scan_single_image(img_path)
            secrets[fname] = result.recovered_secret

        # Verify Stage 1 RECON (Brain.png)
        self.assertTrue(secrets["Brain.png"].startswith("RECON:"), f"Brain.png mismatch: {secrets['Brain.png']}")
        self.assertIn("DNS harvesting and Subdomain enumeration", secrets["Brain.png"])

        # Verify Stage 2 VULN (Activation.png)
        self.assertTrue(secrets["Activation.png"].startswith("VULN:"), f"Activation.png mismatch: {secrets['Activation.png']}")
        self.assertIn("CVE-2024-", secrets["Activation.png"])

        # Verify Stage 3 EXPLOIT (Chemicals.png)
        self.assertTrue(secrets["Chemicals.png"].startswith("EXPLOIT:"), f"Chemicals.png mismatch: {secrets['Chemicals.png']}")
        self.assertIn("SQL Injection payload to bypass WAF", secrets["Chemicals.png"])

        # Verify Stage 4 PERSIST (Dopamine.png)
        self.assertTrue(secrets["Dopamine.png"].startswith("PERSIST:"), f"Dopamine.png mismatch: {secrets['Dopamine.png']}")
        self.assertIn("reverse shell via obfuscated cron job", secrets["Dopamine.png"])

        # Verify Stage 5 LATERAL (Brain-Channel.png)
        self.assertTrue(secrets["Brain-Channel.png"].startswith("LATERAL:"), f"Brain-Channel.png mismatch: {secrets['Brain-Channel.png']}")
        self.assertIn("internal Domain Controller using Mimikatz", secrets["Brain-Channel.png"])

        # Verify Stage 6 EXFIL (Music.png)
        self.assertTrue(secrets["Music.png"].startswith("EXFIL:"), f"Music.png mismatch: {secrets['Music.png']}")
        self.assertIn("DNS Covert Channel", secrets["Music.png"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
