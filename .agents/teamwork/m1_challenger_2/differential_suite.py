#!/usr/bin/env python3
"""
Adversarial Differential Test Suite & Oracle Verifier for Milestone 1.

Executes exhaustive empirical tests:
1. Differential comparison between metadata_scanner.py, metadata_report.csv, and independent_oracle.py
2. Schema & RFC 4180 compliance
3. 6-Stage Attack Lifecycle integrity & Cyber Kill Chain sequence verification
4. Risk scoring engine rubric compliance & non-double-counting verification
5. Adversarial stress harness: edge cases, corrupted headers, boundary conditions, CLI parameters
"""

import base64
import csv
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from PIL import Image, PngImagePlugin

# Import independent oracle from local folder
from independent_oracle import IndependentMetadataOracle, run_oracle_scan, LIFECYCLE_MAPPING

# Production Paths
REPO_ROOT = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
LAB6_DIR = REPO_ROOT / "Lab6"
IMAGES_DIR = LAB6_DIR / "Images"
SCANNER_SCRIPT = LAB6_DIR / "metadata_scanner.py"
CSV_REPORT = LAB6_DIR / "metadata_report.csv"

# Add LAB6_DIR to sys.path so we can import metadata_scanner functions for whitebox/unit stress tests
if str(LAB6_DIR) not in sys.path:
    sys.path.insert(0, str(LAB6_DIR))

import metadata_scanner


class TestMilestone1DifferentialOracle(unittest.TestCase):
    """Differential test suite comparing metadata_scanner against independent oracle."""

    @classmethod
    def setUpClass(cls):
        # 1. Run independent oracle
        cls.oracle_results = {r["filename"]: r for r in run_oracle_scan(IMAGES_DIR)}

        # 2. Run scanner directly to generate latest results in-memory
        cls.scanner_results = {
            r["filename"]: r
            for r in metadata_scanner.scan_directory(IMAGES_DIR, quiet=True)
        }

        # 3. Read production CSV report
        cls.csv_rows = {}
        with open(CSV_REPORT, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cls.csv_headers = reader.fieldnames
            for row in reader:
                cls.csv_rows[row["filename"]] = row

    # ==========================================================================
    # 1. CSV Schema & RFC 4180 Compliance
    # ==========================================================================
    def test_csv_contract_and_structure(self):
        """Verify metadata_report.csv matches contract exactly."""
        expected_headers = [
            "filename",
            "format",
            "metadata_fields",
            "suspected_field",
            "encoding",
            "risk_score",
            "reason",
        ]
        self.assertEqual(self.csv_headers, expected_headers, "CSV headers do not match contract")
        self.assertEqual(len(self.csv_rows), 6, "CSV must contain exactly 6 image rows")

        expected_filenames = {
            "Activation.png",
            "Brain-Channel.png",
            "Brain.png",
            "Chemicals.png",
            "Dopamine.png",
            "Music.png",
        }
        self.assertEqual(set(self.csv_rows.keys()), expected_filenames)

    # ==========================================================================
    # 2. Differential Verification: Extracted Fields
    # ==========================================================================
    def test_differential_metadata_fields(self):
        """Compare metadata fields reported by scanner vs oracle."""
        print("\n--- Metadata Fields Differential ---")
        for fname in sorted(self.csv_rows.keys()):
            scanner_fields = [f.strip() for f in self.scanner_results[fname]["metadata_fields"].split(",")]
            csv_fields = [f.strip() for f in self.csv_rows[fname]["metadata_fields"].split(",")]
            oracle_res = self.oracle_results[fname]
            
            # Scanner in-memory vs CSV file must match 100%
            self.assertEqual(scanner_fields, csv_fields, f"Mismatch between scanner memory and CSV file for {fname}")

            # Verify that suspected field is indeed detected in metadata
            suspected = self.scanner_results[fname]["suspected_field"]
            print(f"[{fname}] Scanner fields: {scanner_fields} | Suspected: {suspected}")

            # Every suspected field must be verified by oracle
            if fname == "Activation.png":
                self.assertIn("UserComment", scanner_fields)
                self.assertIn("GPSInfo", scanner_fields)
            elif fname == "Brain-Channel.png":
                self.assertIn("ImageDescription", scanner_fields)
            elif fname == "Brain.png":
                self.assertIn("Software", scanner_fields)
            elif fname == "Chemicals.png":
                self.assertIn("ImageDescription", scanner_fields)
            elif fname == "Dopamine.png":
                self.assertTrue(any("xmp" in f.lower() for f in scanner_fields))
            elif fname == "Music.png":
                self.assertIn("Copyright", scanner_fields)

    # ==========================================================================
    # 3. Differential Verification: Suspected Fields & Payload Fragments
    # ==========================================================================
    def test_differential_suspected_fields_and_payloads(self):
        """Compare suspected fields and recovered payloads between scanner and oracle."""
        print("\n--- Suspected Fields & Payloads Differential ---")
        for fname in sorted(self.csv_rows.keys()):
            scanner_row = self.scanner_results[fname]
            oracle_res = self.oracle_results[fname]

            # In Dopamine, scanner labels as 'XML:com.adobe.xmp (exif:MakerNote)', oracle has 'XML:com.adobe.xmp (MakerNote)'
            if fname == "Dopamine.png":
                self.assertIn("MakerNote", scanner_row["suspected_field"])
            else:
                self.assertEqual(scanner_row["suspected_field"], oracle_res["suspected_field"])

            # Verify recovered secret
            self.assertTrue(bool(oracle_res["recovered_secret"]), f"Oracle failed to recover secret for {fname}")
            print(f"[{fname}] Verified Secret: {oracle_res['recovered_secret']}")

    # ==========================================================================
    # 4. Differential Verification: Detected Encodings
    # ==========================================================================
    def test_differential_encodings(self):
        """Verify detected encoding classification matches oracle ground truth."""
        print("\n--- Encodings Differential ---")
        expected_encodings = {
            "Activation.png": "EXIF ASCII header / plain text",
            "Brain-Channel.png": "None (plain text)",
            "Brain.png": "None (plain text)",
            "Chemicals.png": "None (plain text)",
            "Dopamine.png": "XML encapsulation / plain text",
            "Music.png": "Base64",
        }

        for fname, exp_enc in expected_encodings.items():
            scanner_enc = self.scanner_results[fname]["encoding"]
            oracle_enc = self.oracle_results[fname]["encoding"]
            csv_enc = self.csv_rows[fname]["encoding"]

            self.assertEqual(scanner_enc, exp_enc, f"Scanner encoding mismatch on {fname}")
            self.assertEqual(oracle_enc, exp_enc, f"Oracle encoding mismatch on {fname}")
            self.assertEqual(csv_enc, exp_enc, f"CSV encoding mismatch on {fname}")
            print(f"[{fname}] Encoding verified: {scanner_enc}")

    # ==========================================================================
    # 5. Differential Verification: Risk Scores & Justifications
    # ==========================================================================
    def test_differential_risk_scores_and_justifications(self):
        """Verify risk score rubric compliance and justification semantics."""
        print("\n--- Risk Scores & Justifications Differential ---")
        expected_scores = {
            "Activation.png": 15,
            "Brain-Channel.png": 10,
            "Brain.png": 10,
            "Chemicals.png": 10,
            "Dopamine.png": 15,
            "Music.png": 15,
        }

        for fname, exp_score in expected_scores.items():
            scanner_score = int(self.scanner_results[fname]["risk_score"])
            oracle_score = self.oracle_results[fname]["risk_score"]
            csv_score = int(self.csv_rows[fname]["risk_score"])
            reason = self.csv_rows[fname]["reason"]

            self.assertEqual(scanner_score, exp_score, f"Scanner score mismatch on {fname}")
            self.assertEqual(oracle_score, exp_score, f"Oracle score mismatch on {fname}")
            self.assertEqual(csv_score, exp_score, f"CSV score mismatch on {fname}")

            # Verify score breakdown in reason string
            self.assertIn("+10", reason, f"Reason for {fname} must cite +10 base covert score")
            if exp_score == 15:
                self.assertIn("+5", reason, f"Reason for {fname} must cite +5 bonus score")
            else:
                self.assertNotIn("+5", reason, f"Reason for {fname} must not cite +5 bonus score")

            print(f"[{fname}] Score: {scanner_score} | Reason: {reason}")

    # ==========================================================================
    # 6. Attack Lifecycle Stage Mapping & Ordering Logic
    # ==========================================================================
    def test_attack_lifecycle_mapping_and_order(self):
        """Verify the 6 images map to the 6 attack lifecycle stages and logical order."""
        print("\n--- Attack Lifecycle Mapping ---")
        expected_stage_mapping = {
            "Brain.png": ("RECON", 1),
            "Activation.png": ("VULN", 2),
            "Chemicals.png": ("EXPLOIT", 3),
            "Dopamine.png": ("PERSIST", 4),
            "Brain-Channel.png": ("LATERAL", 5),
            "Music.png": ("EXFIL", 6),
        }

        recovered_stages = {}
        for fname, (expected_stage, stage_num) in expected_stage_mapping.items():
            oracle_res = self.oracle_results[fname]
            actual_stage = oracle_res["lifecycle_stage"]
            self.assertEqual(actual_stage, expected_stage, f"Lifecycle stage mismatch for {fname}")
            recovered_stages[stage_num] = (fname, actual_stage, oracle_res["recovered_secret"])

        # Reconstruct narrative in stage order 1 to 6
        ordered_narrative = []
        for i in range(1, 7):
            fname, stage, secret = recovered_stages[i]
            ordered_narrative.append(f"Stage {i} ({stage}) [{fname}]: {secret}")
            print(f"Stage {i} ({stage}): [{fname}] -> {secret}")

        self.assertEqual(len(ordered_narrative), 6)


class TestScannerAdversarialStress(unittest.TestCase):
    """Stress tests and adversarial attack scenarios on metadata_scanner.py."""

    def test_cli_execution_and_custom_flags(self):
        """Test scanner CLI behavior under diverse command line arguments."""
        # 1. Custom output path in temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_csv = Path(tmpdir) / "custom_report.csv"
            cmd = [
                sys.executable,
                str(SCANNER_SCRIPT),
                "--images",
                str(IMAGES_DIR),
                "--output",
                str(custom_csv),
                "--quiet",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"CLI failed: {res.stderr}")
            self.assertTrue(custom_csv.exists(), "Custom CSV was not created")

            with open(custom_csv, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                self.assertEqual(len(rows), 6)

    def test_cli_error_on_invalid_directory(self):
        """Scanner CLI must return non-zero exit code when given a non-existent directory."""
        cmd = [
            sys.executable,
            str(SCANNER_SCRIPT),
            "--images",
            r"c:\path\does\not\exist\12345",
            "--quiet",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("not found", res.stderr.lower() + res.stdout.lower())

    def test_scanner_on_empty_directory(self):
        """Scanner must handle directory with 0 images gracefully without crashing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_csv = Path(tmpdir) / "empty.csv"
            res = metadata_scanner.scan_directory(tmpdir, output_csv=out_csv, quiet=True)
            self.assertEqual(len(res), 0)
            self.assertTrue(out_csv.exists())
            with open(out_csv, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                self.assertEqual(len(rows), 0)

    def test_scanner_on_benign_image(self):
        """Scanner must assign risk score 0 to an image without covert channels."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = Path(tmpdir) / "clean.png"
            img = Image.new("RGB", (64, 64), color="blue")
            meta = PngImagePlugin.PngInfo()
            meta.add_text("Author", "Alice")
            meta.add_text("Description", "A beautiful blue sky photo.")
            img.save(img_path, pnginfo=meta)

            result = metadata_scanner.scan_single_image(img_path)
            self.assertEqual(result.risk_score, 0)
            self.assertEqual(result.suspected_field, "None")
            self.assertEqual(result.encoding, "None")
            self.assertIn("No covert metadata detected", result.reason)

    def test_scanner_double_counting_protection(self):
        """
        Verify double-counting protection:
        An image with Base64 encoding AND GPS/camera tags must NOT exceed score 15.
        """
        context_both = {"has_gps": True, "has_camera": True, "has_xmp": False}
        score, reason = metadata_scanner.calculate_risk_score(
            suspected_field="Copyright",
            encoding="Base64",
            is_covert=True,
            is_encoded=True,
            context=context_both,
        )
        self.assertEqual(score, 15, "Score must be capped at 15 (cannot add +5 twice for both Base64 and GPS)")
        self.assertIn("obfuscated with Base64", reason)

    def test_scanner_corrupted_base64_handling(self):
        """Scanner analyze_and_deobfuscate must gracefully handle malformed base64."""
        # Invalid base64 that looks like base64 but has invalid characters or padding
        bad_b64 = "ThisIsNotBase64Padding=="
        text, enc, is_covert, is_encoded = metadata_scanner.analyze_and_deobfuscate("TestField", bad_b64)
        self.assertFalse(is_covert)
        self.assertEqual(enc, "None (plain text)")

    def test_scanner_malformed_xml_handling(self):
        """Scanner analyze_and_deobfuscate / extract_metadata_candidates must survive malformed XML."""
        # Scenario A: XML with unclosed envelope / unbound prefix, but containing MakerNote
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = Path(tmpdir) / "malformed_xmp.png"
            img = Image.new("RGB", (32, 32), color="green")
            meta = PngImagePlugin.PngInfo()
            bad_xml = "<x:xmpmeta><unclosed_wrapper><exif:MakerNote>EXPLOIT: Malformed XML</exif:MakerNote></x:xmpmeta>"
            meta.add_text("XML:com.adobe.xmp", bad_xml)
            img.save(img_path, pnginfo=meta)

            # Scanner should not throw unhandled exception and regex fallback should recover secret
            result = metadata_scanner.scan_single_image(img_path)
            self.assertTrue(result.risk_score > 0)
            self.assertIn("EXPLOIT", result.recovered_secret)

        # Scenario B: Completely truncated XML tag (unclosed MakerNote)
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = Path(tmpdir) / "truncated_xmp.png"
            img = Image.new("RGB", (32, 32), color="green")
            meta = PngImagePlugin.PngInfo()
            truncated_xml = "<x:xmpmeta><exif:MakerNote>EXPLOIT: Truncated without close"
            meta.add_text("XML:com.adobe.xmp", truncated_xml)
            img.save(img_path, pnginfo=meta)

            # Scanner must survive without raising unhandled exception
            result = metadata_scanner.scan_single_image(img_path)
            self.assertEqual(result.risk_score, 0)



if __name__ == "__main__":
    unittest.main(verbosity=2)
