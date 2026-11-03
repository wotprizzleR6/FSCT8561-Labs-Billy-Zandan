import io
import sys
import tempfile
from pathlib import Path
from PIL import Image, PngImagePlugin

repo_root = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
sys.path.insert(0, str(repo_root / "Lab6"))
import metadata_scanner
metadata_scanner.configure_utf8_streams()

def test_benign_image():
    """Verify that a benign image with normal metadata is NOT flagged as covert."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_img = Path(tmpdir) / "benign.png"
        img = Image.new("RGB", (50, 50), color="white")
        meta = PngImagePlugin.PngInfo()
        meta.add_text("Author", "Alice")
        meta.add_text("Software", "GIMP 2.10.30")
        meta.add_text("Comment", "Standard benign vacation photo")
        img.save(tmp_img, pnginfo=meta)

        res = metadata_scanner.scan_single_image(tmp_img)
        print("Benign image test:", res)
        assert res.risk_score == 0, f"Expected 0 risk score, got {res.risk_score}"
        assert res.suspected_field == "None"
        assert res.encoding == "None"
        assert res.reason == "No covert metadata detected."
        assert res.recovered_secret == ""
    print("PASS: Benign image test")

def test_corrupt_file_in_batch():
    """Verify that corrupt files in a directory do not halt batch scanning."""
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        # Create 1 valid image
        valid_img = d / "valid.png"
        img = Image.new("RGB", (20, 20), color="blue")
        img.save(valid_img)

        # Create 1 corrupt 0-byte PNG
        corrupt_zero = d / "corrupt_zero.png"
        corrupt_zero.write_bytes(b"")

        # Create 1 corrupt junk PNG
        corrupt_junk = d / "corrupt_junk.png"
        corrupt_junk.write_bytes(b"\x89PNG\r\n\x1a\nJUNKDATA" * 5)

        # Scan directory
        out_csv = d / "out.csv"
        rows = metadata_scanner.scan_directory(d, output_csv=out_csv, quiet=True)
        print(f"Batch with corrupt files returned {len(rows)} valid records.")
        # Exactly 1 valid image should be processed
        assert len(rows) == 1
        assert rows[0]["filename"] == "valid.png"
    print("PASS: Corrupt file batch resilience")

def test_base64_binary_noise_rejection():
    """Verify that random base64 strings that decode to non-printable binary are rejected."""
    # 32 chars of valid base64 encoding random binary bytes
    import os
    random_bytes = os.urandom(24)
    import base64
    b64_junk = base64.b64encode(random_bytes).decode("ascii")
    
    cleaned, enc, is_cov, is_enc = metadata_scanner.analyze_and_deobfuscate("Copyright", b64_junk)
    print("Base64 binary noise test:", enc, is_cov, is_enc)
    # Because printable_ratio < 0.85, it shouldn't be decoded as valid Base64 text
    assert enc == "None (plain text)" or not is_cov
    assert is_cov is False
    print("PASS: Base64 binary noise rejection")

def test_malformed_xmp_fallback():
    """Verify fallback regex parsing on malformed XMP XML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_img = Path(tmpdir) / "malformed_xmp.png"
        img = Image.new("RGB", (20, 20), color="green")
        meta = PngImagePlugin.PngInfo()
        # Malformed XML missing closing tag or bad syntax, but containing MakerNote
        bad_xmp = "<x:xmpmeta><rdf:RDF><exif:MakerNote>EXPLOIT: Reverse shell injected</exif:MakerNote><broken></x:xmpmeta>"
        meta.add_text("XML:com.adobe.xmp", bad_xmp)
        img.save(tmp_img, pnginfo=meta)

        res = metadata_scanner.scan_single_image(tmp_img)
        print("Malformed XMP test:", res)
        assert res.risk_score == 15
        assert "exif:MakerNote" in res.suspected_field
        assert "EXPLOIT:" in res.recovered_secret
    print("PASS: Malformed XMP regex fallback")

def test_utf8_special_characters():
    """Verify handling of Unicode, accents, and emojis in metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_img = Path(tmpdir) / "unicode.png"
        img = Image.new("RGB", (20, 20), color="yellow")
        meta = PngImagePlugin.PngInfo()
        meta.add_text("ImageDescription", "RECON: DNS harvesting on subdomains \U0001F600 café ñ 日本語")
        img.save(tmp_img, pnginfo=meta)

        res = metadata_scanner.scan_single_image(tmp_img)
        print("Unicode metadata test:", res)
        assert res.risk_score == 10
        assert "RECON:" in res.recovered_secret
        assert "café" in res.recovered_secret
    print("PASS: Unicode special characters")

def test_empty_directory():
    """Verify behavior on an empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_csv = Path(tmpdir) / "empty.csv"
        rows = metadata_scanner.scan_directory(tmpdir, output_csv=out_csv, quiet=True)
        assert len(rows) == 0
        import csv
        with open(out_csv, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            assert len(reader) == 1 # Just header
            assert reader[0] == metadata_scanner.CSV_FIELDNAMES
    print("PASS: Empty directory scan")

if __name__ == "__main__":
    test_benign_image()
    test_corrupt_file_in_batch()
    test_base64_binary_noise_rejection()
    test_malformed_xmp_fallback()
    test_utf8_special_characters()
    test_empty_directory()
    print("\nALL ADVERSARIAL STRESS TESTS COMPLETED SUCCESSFULLY!")
