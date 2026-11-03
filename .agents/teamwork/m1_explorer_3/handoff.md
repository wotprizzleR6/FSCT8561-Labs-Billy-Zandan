# Handoff Report: Milestone 1 — CSV Validation, CLI Usability, Robustness, and Test Criteria

**Author:** Teamwork Explorer Agent 3 (`m1_explorer_3`)  
**Date:** 2026-11-02  
**Target:** Milestone 1 (`Lab6/metadata_scanner.py` and `Lab6/metadata_report.csv`)  
**Working Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_explorer_3`  
**Parent Conversation ID:** `4454555e-8e94-46d7-b2c6-e12b4f18de76`  
**Handoff Type:** Hard (Task Complete)  

---

## 1. Observation

1. **CLI Invocation Requirements**:
   - `ORIGINAL_REQUEST.md` line 37 requires: "An automated metadata scanner executes against all six images in `Images/` without errors."
   - Dispatch message specifies exact invocations: `python metadata_scanner.py` and `python metadata_scanner.py --images Images --output metadata_report.csv`.
   - `Lab6.ipynb` cell 421 uses `sorted(image_dir.glob("*.png"))` where `image_dir = Path("Images")`.

2. **CSV Schema & Formatting Requirements**:
   - `PROJECT.md` lines 31–36 require:
     - Output path: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv`
     - Required CSV header: `filename,format,metadata_fields,suspected_field,encoding,risk_score,reason`
     - Exactly 6 data rows, one per image (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`).
     - Format: UTF-8 encoded CSV.
   - `Lab6.ipynb` cell 446 specifies `"metadata_fields": ", ".join(img.info.keys())` which introduces commas into the field value.
   - Direct execution probe with Python `csv.writer` confirmed:
     `Raw line: 'Activation.png,PNG,"srgb, gamma, dpi",UserComment,Plain text,15,Reason\r\n'`
     `Read fields: 7`
     Naive `line.split(',')` returned 9 tokens, confirming that RFC 4180 double-quoting (`"..."`) is strictly necessary for `metadata_fields` and compound `reason` text.

3. **XMP Packet Unicode BOM on Windows Console**:
   - Direct inspection of `Lab6/Images/Dopamine.png` showed:
     `Type of XML:com.adobe.xmp: <class 'PIL.PngImagePlugin.iTXt'>`
     `First 100 repr: "<?xpacket begin='\ufeff' id='W5M0MpCehiHzreSzNTczkc9d'?>..."`
   - Testing console encoding without UTF-8 reconfigure under Windows CP1252 produced verbatim error:
     `UnicodeEncodeError: 'charmap' codec can't encode character '\ufeff' in position 17: character maps to <undefined>`
   - `defusedxml.ElementTree.fromstring(xmp)` parsed cleanly without error and located `{http://ns.adobe.com/exif/1.0/}MakerNote`.

4. **EXIF UserComment 8-Byte ASCII Header**:
   - Direct inspection of `Lab6/Images/Activation.png` Sub-IFD tag 37510 showed:
     `UserComment (37510): bytes = b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in...'`
   - Naive string conversion `str(val)` leaves raw Python byte representation `b'ASCII\\x00...'` unless sliced `[8:]` and decoded as UTF-8.

5. **Evidence Image SHA-256 Hashes**:
   - Verification tool run confirmed the baseline SHA-256 hashes of all 6 raw images in `Lab6/Images/`:
     - `Activation.png`: `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904`
     - `Brain-Channel.png`: `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359`
     - `Brain.png`: `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e`
     - `Chemicals.png`: `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a`
     - `Dopamine.png`: `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472`
     - `Music.png`: `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370`

---

## 2. Logic Chain

1. **From CLI Requirements (Obs. 1) to Parser Architecture**:
   Because the script must support both `python metadata_scanner.py` (zero-args) and `python metadata_scanner.py --images Images --output metadata_report.csv` (explicit flags), as well as possible execution from either `Lab6/` or the repository root, `argparse` with fallback auto-detection must be implemented. Supplying aliases (`-i`/`--images`/`--image-dir` and `-o`/`--output`/`--output-csv`) guarantees compatibility with both Lab 6 test harnesses and Lab 5 conventions.

2. **From Embedded Delimiters (Obs. 2) to CSV Quoting Rules**:
   Because `metadata_fields` concatenates multiple tag names with commas (e.g., `"srgb, gamma, dpi, exif, Make, Model"`), naive string splitting or unquoted CSV generation causes column count inflation (from 7 to 9+ fields). Therefore, generating output strictly through `csv.DictWriter(f, fieldnames=..., quoting=csv.QUOTE_MINIMAL)` and opening files with `newline=""` is required to ensure full RFC 4180 compliance across all parsers (Python `csv`, `pandas`, Excel).

3. **From Console Unicode Errors (Obs. 3) to Console Hardening**:
   Because `Dopamine.png` embeds `\ufeff` in its XMP header, executing the scanner with `--verbose` or printing logs on standard Windows CP1252 consoles will trigger fatal `UnicodeEncodeError` exceptions unless standard streams are explicitly reconfigured to UTF-8 (`sys.stdout.reconfigure(encoding='utf-8')`).

4. **From Binary EXIF Headers (Obs. 4) to Decoding Cleanliness**:
   Because `Activation.png` encapsulates its secret behind `b'ASCII\x00\x00\x00'`, the extraction engine must inspect for this 8-byte prefix and slice it prior to decoding; otherwise, the CSV report will store polluted byte strings.

5. **From Cryptographic Baseline (Obs. 5) to Forensic Auditability**:
   Because digital forensics requires non-spoliation of original evidence, verification commands must confirm that running `metadata_scanner.py` never writes to, modifies, or recalculates CRC checksums on the raw image files in `Images/`.

---

## 3. Caveats

1. **Jupyter Notebook Execution in Milestone 2**:
   This handoff specifies testing and verification for the standalone CLI tool `metadata_scanner.py`. In Milestone 2, Cell 463 of `Lab6.ipynb` will incorporate this scanning logic. The logic formulated here is directly portable into the notebook cell.
2. **Third-Party Libraries**:
   The verification strategy relies exclusively on Python standard library modules (`argparse`, `csv`, `pathlib`, `sys`, `xml.etree.ElementTree`, `base64`, `hashlib`) and pre-installed `Pillow` (12.3.0) and `defusedxml` (0.7.1). No additional external package installation is required.

---

## 4. Conclusion

Milestone 1's validation criteria, robustness requirements, and verification commands are completely defined:
1. **CLI Invocation**: `metadata_scanner.py` must support zero-arg defaults, explicit `--images`/`--output` flags, `-h`/`--help`, and exit code 0 on success vs code 1 on invalid paths.
2. **CSV Contract**: `metadata_report.csv` must be UTF-8 encoded with exactly 7 columns (`filename,format,metadata_fields,suspected_field,encoding,risk_score,reason`), exactly 6 data rows, and RFC 4180 quoting for fields containing commas or semicolons.
3. **Robustness**: The script must include stream encoding reconfiguration (`utf-8`), non-existent directory validation with stderr reporting, per-file try-except guards for corrupted images, zero-metadata image handling (score 0), and 8-byte ASCII header stripping.
4. **Verification Suites**: Concrete commands are ready for Reviewers, Challengers, and Forensic Auditors to verify M1 immediately upon worker implementation.

Detailed documentation is available in `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_explorer_3\analysis.md`.

---

## 5. Verification Method

To independently verify Milestone 1 after `metadata_scanner.py` is implemented:

### Command 1: Standard Reviewer Happy Path
```powershell
cd c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6
python metadata_scanner.py
python -c "import csv; r = list(csv.reader(open('metadata_report.csv', encoding='utf-8'))); assert len(r) == 7; assert r[0] == ['filename','format','metadata_fields','suspected_field','encoding','risk_score','reason']; print('M1 REVIEW PASS: 7 rows, valid headers.')"
```

### Command 2: Parameterized Invocation & Quoting Validation
```powershell
python metadata_scanner.py --images Images --output custom_report.csv
python -c "import csv; r = list(csv.reader(open('custom_report.csv', encoding='utf-8'))); assert all(len(row) == 7 for row in r); print('M1 RFC 4180 PASS: Exactly 7 fields per row.')"
Remove-Item custom_report.csv -Force
```

### Command 3: Challenger Adversarial Directory Test
```powershell
python metadata_scanner.py --images InvalidDirectoryXYZ --output test.csv
if ($LASTEXITCODE -ne 0) { Write-Host "M1 CHALLENGER PASS: Exited non-zero on bad directory." } else { Write-Error "FAIL" }
```

### Command 4: Forensic Chain of Custody Audit
```powershell
python -c "
import hashlib, sys
from pathlib import Path

hashes = {
    'Activation.png': '1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904',
    'Brain-Channel.png': '3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359',
    'Brain.png': '5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e',
    'Chemicals.png': '96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a',
    'Dopamine.png': 'ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472',
    'Music.png': '3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370'
}
for name, exp in hashes.items():
    act = hashlib.sha256((Path('Images') / name).read_bytes()).hexdigest()
    assert act == exp, f'Hash mismatch: {name}'
print('M1 AUDIT PASS: Evidence files untampered.')
"
```

### Invalidation Conditions
- Any output CSV where `csv.reader` does not parse exactly 7 fields on every row.
- Failure of `python metadata_scanner.py` with zero arguments when run inside `Lab6/`.
- Unhandled `UnicodeEncodeError` when running on Windows PowerShell without explicit UTF-8 code page.
- Modification of any PNG file's SHA-256 hash in `Lab6/Images/`.
