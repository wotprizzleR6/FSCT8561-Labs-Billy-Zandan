"""
Adversarial Coverage Hardening Test Suite (Tier 5 White-Box Testing)
Target: Lab6/metadata_scanner.py and Lab6/metadata_report.csv
Author: m4_challenger_1 (Empirical Challenger)
"""

import base64
import csv
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from PIL import Image, PngImagePlugin

# Import metadata_scanner directly for white-box unit testing
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LAB6_DIR = REPO_ROOT / "Lab6"
sys.path.insert(0, str(LAB6_DIR))

import metadata_scanner


class TestAdversarialCoverageHardening(unittest.TestCase):
    """Tier 5 White-Box Adversarial Hardening Suite."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="adv_test_"))
        cls.images_dir = LAB6_DIR / "Images"
        cls.scanner_script = LAB6_DIR / "metadata_scanner.py"
        cls.csv_report = LAB6_DIR / "metadata_report.csv"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    # ==========================================================================
    # CATEGORY 1: Malformed & Corrupted Image Headers
    # ==========================================================================

    def test_adv_01_corrupted_png_magic_bytes(self):
        """1.1 Corrupted PNG header (invalid magic bytes). Scanner should handle gracefully."""
        corrupt_png = self.temp_dir / "corrupt_magic.png"
        corrupt_png.write_bytes(b"\x89CORRUPT\r\n\x1a\n\x00\x00\x00\rIHDR...")
        # Direct single scan raises PIL.UnidentifiedImageError or OSError
        with self.assertRaises(Exception):
            metadata_scanner.scan_single_image(corrupt_png)

        # In directory scan, directory iteration catches exception and continues
        single_dir = self.temp_dir / "dir_corrupt_magic"
        single_dir.mkdir(exist_ok=True)
        shutil.copy(corrupt_png, single_dir / "corrupt_magic.png")
        rows = metadata_scanner.scan_directory(single_dir, quiet=True)
        self.assertEqual(len(rows), 0, "Corrupt image should be caught and skipped without crashing")

    def test_adv_02_truncated_png_file(self):
        """1.2 Truncated PNG (valid magic bytes, truncated mid-chunk)."""
        trunc_png = self.temp_dir / "truncated.png"
        # 8 bytes magic + 4 bytes length
        trunc_png.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR")
        single_dir = self.temp_dir / "dir_trunc"
        single_dir.mkdir(exist_ok=True)
        shutil.copy(trunc_png, single_dir / "truncated.png")
        rows = metadata_scanner.scan_directory(single_dir, quiet=True)
        self.assertEqual(len(rows), 0, "Truncated PNG must be handled without unhandled exception")

    def test_adv_03_zero_byte_png_file(self):
        """1.3 Zero-byte file with .png extension."""
        zero_png = self.temp_dir / "zero.png"
        zero_png.write_bytes(b"")
        single_dir = self.temp_dir / "dir_zero"
        single_dir.mkdir(exist_ok=True)
        shutil.copy(zero_png, single_dir / "zero.png")
        rows = metadata_scanner.scan_directory(single_dir, quiet=True)
        self.assertEqual(len(rows), 0)

    def test_adv_04_truncated_exif_usercomment(self):
        """1.4 EXIF UserComment shorter than 8 bytes."""
        short_bytes = b"ASCII"
        text, enc, is_covert, is_enc = metadata_scanner.analyze_and_deobfuscate("UserComment", short_bytes)
        self.assertEqual(text, "ASCII")
        self.assertEqual(enc, "None (plain text)")
        self.assertFalse(is_covert)
        self.assertFalse(is_enc)

    def test_adv_05_malformed_xmp_xml_fallback_to_regex(self):
        """1.5 Malformed XMP XML with syntax error triggers robust regex fallback."""
        malformed_xmp = (
            "<?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>\n"
            "<x:xmpmeta xmlns:x='adobe:ns:meta/'>\n"
            "<rdf:RDF>\n"
            "<UNCLOSED_TAG>\n"  # Syntax error: unclosed tag
            "<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>\n"
            "</rdf:RDF>\n"
        )
        img = Image.new("RGB", (10, 10), color="white")
        info = PngImagePlugin.PngInfo()
        info.add_text("XML:com.adobe.xmp", malformed_xmp)
        test_img_path = self.temp_dir / "xmp_malformed_test.png"
        img.save(test_img_path, pnginfo=info)

        res = metadata_scanner.scan_single_image(test_img_path)
        self.assertIn("MakerNote", res.suspected_field)
        self.assertIn("PERSIST", res.recovered_secret)
        self.assertEqual(res.risk_score, 15)

    def test_adv_06_malformed_xmp_without_makernote(self):
        """1.6 Malformed XMP XML without any MakerNote tag."""
        malformed_xmp = "<rdf:RDF><broken"
        img = Image.new("RGB", (10, 10), color="white")
        info = PngImagePlugin.PngInfo()
        info.add_text("XML:com.adobe.xmp", malformed_xmp)
        test_img_path = self.temp_dir / "xmp_no_tag.png"
        img.save(test_img_path, pnginfo=info)

        res = metadata_scanner.scan_single_image(test_img_path)
        self.assertEqual(res.risk_score, 0)
        self.assertEqual(res.suspected_field, "None")

    # ==========================================================================
    # CATEGORY 2: Directory & Filesystem Edge Cases
    # ==========================================================================

    def test_adv_07_nonexistent_directory(self):
        """2.1 Non-existent directory raises FileNotFoundError in scan_directory."""
        non_dir = self.temp_dir / "non_existent_folder_abc"
        with self.assertRaises(FileNotFoundError):
            metadata_scanner.scan_directory(non_dir)

    def test_adv_08_empty_directory(self):
        """2.2 Empty directory produces an empty report with headers only."""
        empty_dir = self.temp_dir / "empty_dir"
        empty_dir.mkdir(exist_ok=True)
        out_csv = empty_dir / "out.csv"
        rows = metadata_scanner.scan_directory(empty_dir, output_csv=out_csv, quiet=True)
        self.assertEqual(len(rows), 0)
        self.assertTrue(out_csv.exists())
        with open(out_csv, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)  # header only

    def test_adv_09_directory_with_non_png_files(self):
        """2.3 Directory containing non-PNG files (txt, csv, docx, jpg)."""
        mixed_dir = self.temp_dir / "mixed_dir"
        mixed_dir.mkdir(exist_ok=True)
        (mixed_dir / "test.txt").write_text("not an image")
        (mixed_dir / "report.csv").write_text("a,b,c")
        (mixed_dir / "doc.docx").write_bytes(b"PK\x03\x04")
        # Save a valid JPEG
        jpg_img = Image.new("RGB", (20, 20), color="blue")
        jpg_img.save(mixed_dir / "sample.jpg", "JPEG")

        rows = metadata_scanner.scan_directory(mixed_dir, quiet=True)
        self.assertEqual(len(rows), 0, "Non-PNG files must not be processed")

    def test_adv_10_benign_png_image_no_metadata(self):
        """2.4 Clean PNG with zero metadata receives risk score 0."""
        clean_img = Image.new("RGB", (20, 20), color="green")
        clean_path = self.temp_dir / "clean.png"
        clean_img.save(clean_path, "PNG")

        res = metadata_scanner.scan_single_image(clean_path)
        self.assertEqual(res.risk_score, 0)
        self.assertEqual(res.suspected_field, "None")
        self.assertEqual(res.encoding, "None")
        self.assertEqual(res.reason, "No covert metadata detected.")

    def test_adv_11_directory_and_output_path_with_spaces_and_symbols(self):
        """2.5 Directory paths with spaces and symbols."""
        spaced_dir = self.temp_dir / "Forensic Evidence #1 (Test)"
        spaced_dir.mkdir(exist_ok=True)
        # copy one valid image
        shutil.copy(self.images_dir / "Brain.png", spaced_dir / "Brain.png")
        out_csv = spaced_dir / "Report Output #1.csv"

        rows = metadata_scanner.scan_directory(spaced_dir, output_csv=out_csv, quiet=True)
        self.assertEqual(len(rows), 1)
        self.assertTrue(out_csv.exists())
        self.assertEqual(rows[0]["filename"], "Brain.png")

    # ==========================================================================
    # CATEGORY 3: CLI Parameter Boundaries & Unknown Flags
    # ==========================================================================

    def test_adv_12_cli_nonexistent_directory_exit_code_1(self):
        """3.1 CLI with non-existent directory exits with code 1."""
        res = subprocess.run(
            [sys.executable, str(self.scanner_script), "-i", "NonExistentFolder_12345"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 1)
        self.assertIn("not found", res.stderr)

    def test_adv_13_cli_help_flag_exit_code_0(self):
        """3.2 CLI -h / --help exits with code 0 and outputs usage."""
        for flag in ["-h", "--help"]:
            res = subprocess.run(
                [sys.executable, str(self.scanner_script), flag],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0)
            self.assertIn("Automated Image Metadata Covert Channel Scanner", res.stdout)

    def test_adv_14_cli_quiet_flag(self):
        """3.3 CLI -q / --quiet suppresses stdout."""
        out_csv = self.temp_dir / "cli_quiet.csv"
        res = subprocess.run(
            [
                sys.executable,
                str(self.scanner_script),
                "-i",
                str(self.images_dir),
                "-o",
                str(out_csv),
                "-q",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "", "Quiet flag must suppress stdout")

    def test_adv_15_cli_verbose_flag(self):
        """3.4 CLI -v / --verbose prints secret preview."""
        out_csv = self.temp_dir / "cli_verbose.csv"
        res = subprocess.run(
            [
                sys.executable,
                str(self.scanner_script),
                "-i",
                str(self.images_dir),
                "-o",
                str(out_csv),
                "-v",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Recovered Secret:", res.stdout)

    def test_adv_16_cli_unknown_strict_flag(self):
        """3.5 CLI unknown flag --strict raises unrecognized argument (exit code 2)."""
        res = subprocess.run(
            [sys.executable, str(self.scanner_script), "--strict"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 2)
        self.assertIn("unrecognized arguments: --strict", res.stderr)

    def test_adv_17_cli_unknown_input_dir_flag(self):
        """3.6 CLI unknown flag --input-dir raises unrecognized argument (exit code 2)."""
        res = subprocess.run(
            [sys.executable, str(self.scanner_script), "--input-dir", str(self.images_dir)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 2)
        self.assertIn("unrecognized arguments: --input-dir", res.stderr)

    def test_adv_18_cli_custom_output_creates_parent_directories(self):
        """3.7 CLI with nested non-existent directory creates parent directories."""
        nested_out = self.temp_dir / "nested" / "deep" / "dir" / "report.csv"
        res = subprocess.run(
            [
                sys.executable,
                str(self.scanner_script),
                "-i",
                str(self.images_dir),
                "-o",
                str(nested_out),
                "-q",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertTrue(nested_out.exists())

    # ==========================================================================
    # CATEGORY 4: Obfuscation, Decoding & Payload Boundaries
    # ==========================================================================

    def test_adv_19_base64_with_non_printable_bytes(self):
        """4.1 Base64 decoded to non-printable binary bytes (<85% printable)."""
        binary_data = bytes(range(128))
        raw_b64 = base64.b64encode(binary_data).decode("ascii")
        text, enc, is_covert, is_enc = metadata_scanner.analyze_and_deobfuscate("CustomTag", raw_b64)
        # Should not decode as covert Base64
        self.assertFalse(is_covert)
        self.assertEqual(enc, "None (plain text)")

    def test_adv_20_base64_short_string(self):
        """4.2 Base64 candidate shorter than 16 characters is not treated as Base64."""
        short_b64 = "UkVDT04="  # "RECON"
        text, enc, is_covert, is_enc = metadata_scanner.analyze_and_deobfuscate("CustomTag", short_b64)
        self.assertEqual(enc, "None (plain text)")
        self.assertFalse(is_enc)

    def test_adv_21_base64_valid_covert_stage(self):
        """4.3 Base64 payload encoding valid covert stage."""
        msg = "EXPLOIT: Deploy SQL Injection payload to bypass WAF."
        raw_b64 = base64.b64encode(msg.encode("utf-8")).decode("ascii")
        text, enc, is_covert, is_enc = metadata_scanner.analyze_and_deobfuscate("Copyright", raw_b64)
        self.assertEqual(text, msg)
        self.assertEqual(enc, "Base64")
        self.assertTrue(is_covert)
        self.assertTrue(is_enc)

    def test_adv_22_threat_keywords_case_insensitivity(self):
        """4.4 Threat keywords are recognized case-insensitively."""
        test_strings = [
            ("ImageDescription", "EXPLOIT: deploy reverse shell on port 4444"),
            ("Software", "recon: perform Dns Harvesting now"),
            ("UserComment", "lateral: move with MIMIKATZ to DC"),
            ("Copyright", "persist: setup CRON JOB persistence"),
        ]
        for field, s in test_strings:
            text, enc, is_covert, is_enc = metadata_scanner.analyze_and_deobfuscate(field, s)
            self.assertTrue(is_covert, f"Failed to match covert keywords in '{s}'")

    def test_adv_23_unicode_and_special_characters_handling(self):
        """4.5 Metadata containing Unicode (accents, Chinese, Cyrillic, emoji)."""
        unicode_str = "RECON: Обнаружение 扫描 DNS 🎯"
        text, enc, is_covert, is_enc = metadata_scanner.analyze_and_deobfuscate("Software", unicode_str)
        self.assertEqual(text, unicode_str)
        self.assertTrue(is_covert)
        self.assertEqual(enc, "None (plain text)")

    def test_adv_24_extreme_payload_size(self):
        """4.6 Extreme payload size (500KB string with covert prefix)."""
        large_payload = "RECON: " + "A" * 500_000
        text, enc, is_covert, is_enc = metadata_scanner.analyze_and_deobfuscate("Software", large_payload)
        self.assertTrue(is_covert)
        self.assertEqual(len(text), len(large_payload))

    def test_adv_25_raw_value_as_integer_or_tuple(self):
        """4.7 Raw EXIF values that are not string or bytes (e.g. int, tuple)."""
        text, enc, is_covert, is_enc = metadata_scanner.analyze_and_deobfuscate("ISOSpeedRatings", 400)
        self.assertEqual(text, "400")
        self.assertFalse(is_covert)

        text, enc, is_covert, is_enc = metadata_scanner.analyze_and_deobfuscate("Resolution", (300, 300))
        self.assertEqual(text, "(300, 300)")
        self.assertFalse(is_covert)

    # ==========================================================================
    # CATEGORY 5: Risk Scoring Logic & Double-Counting Protections
    # ==========================================================================

    def test_adv_26_risk_score_plain_covert_only(self):
        """5.1 Plain covert message without encoding or camera/GPS (+10)."""
        score, reason = metadata_scanner.calculate_risk_score(
            suspected_field="Software",
            encoding="None (plain text)",
            is_covert=True,
            is_encoded=False,
            context={"has_gps": False, "has_camera": False, "has_xmp": False},
        )
        self.assertEqual(score, 10)
        self.assertIn("Confirmed covert message in Software (+10)", reason)

    def test_adv_27_risk_score_base64_encoded(self):
        """5.2 Covert message + Base64 encoding (+10 + 5 = 15)."""
        score, reason = metadata_scanner.calculate_risk_score(
            suspected_field="Copyright",
            encoding="Base64",
            is_covert=True,
            is_encoded=True,
            context={"has_gps": False, "has_camera": False, "has_xmp": False},
        )
        self.assertEqual(score, 15)
        self.assertIn("Confirmed covert message in Copyright (+10)", reason)
        self.assertIn("obfuscated with Base64 encoding requiring decoding (+5)", reason)

    def test_adv_28_risk_score_camera_and_gps_anomalous_container(self):
        """5.3 Covert message + Camera hardware + GPS tags (+10 + 5 = 15)."""
        score, reason = metadata_scanner.calculate_risk_score(
            suspected_field="UserComment",
            encoding="EXIF ASCII header / plain text",
            is_covert=True,
            is_encoded=True,
            context={"has_gps": True, "has_camera": True, "has_xmp": False},
        )
        self.assertEqual(score, 15)
        self.assertIn("camera hardware and GPS tags embedded in graphic (+5)", reason)

    def test_adv_29_risk_score_xmp_container(self):
        """5.4 Covert message in XMP container (+10 + 5 = 15)."""
        score, reason = metadata_scanner.calculate_risk_score(
            suspected_field="XML:com.adobe.xmp (exif:MakerNote)",
            encoding="XML encapsulation / plain text",
            is_covert=True,
            is_encoded=False,
            context={"has_gps": False, "has_camera": False, "has_xmp": True},
        )
        self.assertEqual(score, 15)
        self.assertIn("unusual container / embedded XMP packet (+5)", reason)

    def test_adv_30_risk_score_double_counting_capped(self):
        """5.5 Covert message with Base64 AND Camera/GPS AND XMP -> score is capped at 15."""
        score, reason = metadata_scanner.calculate_risk_score(
            suspected_field="XML:com.adobe.xmp (exif:MakerNote)",
            encoding="Base64",
            is_covert=True,
            is_encoded=True,
            context={"has_gps": True, "has_camera": True, "has_xmp": True},
        )
        self.assertEqual(score, 15, "Score addition capped to prevent double-counting")

    def test_adv_31_risk_score_not_covert_returns_zero(self):
        """5.6 Non-covert metadata returns 0 even if camera/GPS or Base64 present."""
        score, reason = metadata_scanner.calculate_risk_score(
            suspected_field="None",
            encoding="Base64",
            is_covert=False,
            is_encoded=True,
            context={"has_gps": True, "has_camera": True, "has_xmp": True},
        )
        self.assertEqual(score, 0)
        self.assertEqual(reason, "No covert metadata detected.")

    # ==========================================================================
    # CATEGORY 6: CSV Schema, Escaping & RFC 4180 Compliance
    # ==========================================================================

    def test_adv_32_csv_escaping_with_quotes_and_commas(self):
        """6.1 CSV generation correctly escapes commas and quotes in reason field."""
        result = metadata_scanner.ImageScanResult(
            filename="test,comma.png",
            format="PNG",
            metadata_fields='field1, "quoted_field", field3',
            suspected_field="field1",
            encoding="None",
            risk_score=10,
            reason='Confirmed "covert, secret" message (+10).',
        )
        test_csv = self.temp_dir / "escaping_test.csv"
        with open(test_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=metadata_scanner.CSV_FIELDNAMES)
            writer.writeheader()
            writer.writerow(result.to_csv_dict())

        with open(test_csv, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["filename"], "test,comma.png")
        self.assertEqual(rows[0]["reason"], 'Confirmed "covert, secret" message (+10).')

    def test_adv_33_metadata_report_csv_exact_schema(self):
        """6.2 Verify current production metadata_report.csv conforms to strict RFC 4180."""
        self.assertTrue(self.csv_report.exists(), "Production metadata_report.csv must exist")
        with open(self.csv_report, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header, metadata_scanner.CSV_FIELDNAMES)
            rows = list(reader)
            self.assertEqual(len(rows), 6)
            for idx, r in enumerate(rows, 1):
                self.assertEqual(len(r), 7, f"Row {idx} has {len(r)} columns instead of 7")

    def test_adv_34_csv_output_encoding_is_utf8(self):
        """6.3 Verify CSV report is encoded in UTF-8 without replacement errors."""
        raw = self.csv_report.read_bytes()
        decoded = raw.decode("utf-8")
        self.assertGreater(len(decoded), 0)

    # ==========================================================================
    # CATEGORY 7: Idempotency, Determinism & State Isolation
    # ==========================================================================

    def test_adv_35_idempotent_csv_generation(self):
        """7.1 Running scanner 5 times produces byte-for-byte identical output."""
        runs = []
        for i in range(5):
            out_file = self.temp_dir / f"run_{i}.csv"
            metadata_scanner.scan_directory(self.images_dir, output_csv=out_file, quiet=True)
            runs.append(out_file.read_bytes())

        for i in range(1, 5):
            self.assertEqual(runs[0], runs[i], f"Run {i} differed from run 0")

    def test_adv_36_file_descriptor_release(self):
        """7.2 Scanned image files can be immediately opened/modified (no leak)."""
        temp_img_dir = self.temp_dir / "fd_test_dir"
        temp_img_dir.mkdir(exist_ok=True)
        sample_path = temp_img_dir / "sample.png"
        shutil.copy(self.images_dir / "Brain.png", sample_path)

        metadata_scanner.scan_directory(temp_img_dir, quiet=True)

        # File must not be locked
        with open(sample_path, "r+b") as f:
            f.seek(0)
            data = f.read(8)
            f.seek(0)
            f.write(data)

    def test_adv_37_immutable_constants(self):
        """7.3 Constants CSV_FIELDNAMES and LIFECYCLE_STAGE_PREFIXES are not mutated."""
        orig_fields = list(metadata_scanner.CSV_FIELDNAMES)
        orig_prefixes = tuple(metadata_scanner.LIFECYCLE_STAGE_PREFIXES)

        metadata_scanner.scan_directory(self.images_dir, quiet=True)

        self.assertEqual(metadata_scanner.CSV_FIELDNAMES, orig_fields)
        self.assertEqual(metadata_scanner.LIFECYCLE_STAGE_PREFIXES, orig_prefixes)

    # ==========================================================================
    # CATEGORY 8: Path Resolution Flexibility
    # ==========================================================================

    def test_adv_38_resolve_paths_absolute(self):
        """8.1 resolve_paths with absolute paths."""
        abs_img = self.images_dir.resolve()
        abs_out = (self.temp_dir / "test_out.csv").resolve()
        r_img, r_out = metadata_scanner.resolve_paths(str(abs_img), str(abs_out))
        self.assertEqual(r_img, abs_img)
        self.assertEqual(r_out, abs_out)

    def test_adv_39_resolve_paths_relative_images_arg(self):
        """8.2 resolve_paths with 'Images' default string."""
        r_img, r_out = metadata_scanner.resolve_paths("Images", "metadata_report.csv")
        self.assertTrue(r_img.exists())
        self.assertTrue(r_img.is_dir())

    def test_adv_40_main_entrypoint_execution(self):
        """8.3 Direct execution of metadata_scanner main() without args."""
        res = subprocess.run(
            [sys.executable, str(self.scanner_script)],
            cwd=str(LAB6_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Scan complete", res.stdout)


if __name__ == "__main__":
    unittest.main()
