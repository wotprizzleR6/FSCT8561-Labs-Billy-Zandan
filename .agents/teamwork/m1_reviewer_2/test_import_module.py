import sys
from pathlib import Path

# Add repo root and Lab6 to sys.path
repo_root = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
sys.path.insert(0, str(repo_root / "Lab6"))

# Test 1: Direct module import
import metadata_scanner

print("Successfully imported metadata_scanner directly!")

# Test 2: Check exposed functions and classes
expected_attributes = [
    "ImageScanResult",
    "collect_metadata_field_names",
    "extract_metadata_candidates",
    "analyze_and_deobfuscate",
    "calculate_risk_score",
    "scan_single_image",
    "scan_directory",
    "resolve_paths",
    "parse_arguments",
    "main",
    "configure_utf8_streams",
]

for attr in expected_attributes:
    assert hasattr(metadata_scanner, attr), f"Missing expected attribute: {attr}"
    print(f"Verified attribute: {attr} -> {type(getattr(metadata_scanner, attr))}")

# Test 3: Programmatic call of scan_single_image
img_path = repo_root / "Lab6" / "Images" / "Activation.png"
result = metadata_scanner.scan_single_image(img_path)
print(f"Programmatic scan result for Activation.png: {result}")
assert isinstance(result, metadata_scanner.ImageScanResult)
assert result.filename == "Activation.png"
assert result.suspected_field == "UserComment"
assert result.risk_score == 15
assert "VULN:" in result.recovered_secret

# Test 4: Programmatic call of scan_directory without writing to disk
rows = metadata_scanner.scan_directory(repo_root / "Lab6" / "Images", output_csv=None, quiet=True)
print(f"Programmatic scan_directory returned {len(rows)} rows.")
assert len(rows) == 6

# Test 5: Check analyze_and_deobfuscate standalone
raw_usercomment = b"ASCII\x00\x00\x00VULN: Test secret message"
cleaned, enc, is_cov, is_enc = metadata_scanner.analyze_and_deobfuscate("UserComment", raw_usercomment)
assert cleaned == "VULN: Test secret message"
assert enc == "EXIF ASCII header / plain text"
assert is_cov is True
assert is_enc is True
print("analyze_and_deobfuscate UserComment verified!")

# Test 6: Check analyze_and_deobfuscate Base64
import base64
b64_payload = base64.b64encode(b"EXFIL: Target data exfiltrated through covert metadata").decode("ascii")
cleaned_b64, enc_b64, is_cov_b64, is_enc_b64 = metadata_scanner.analyze_and_deobfuscate("Copyright", b64_payload)
assert cleaned_b64 == "EXFIL: Target data exfiltrated through covert metadata"
assert enc_b64 == "Base64"
assert is_cov_b64 is True
assert is_enc_b64 is True
print("analyze_and_deobfuscate Base64 verified!")

print("\nALL MODULE IMPORT AND PROGRAMMATIC TESTS PASSED!")
