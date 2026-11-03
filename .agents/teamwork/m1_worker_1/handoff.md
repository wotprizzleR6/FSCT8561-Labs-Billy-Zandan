# Milestone 1 Handoff Report: Automated Scanner & CSV Engine

**Agent:** Teamwork Worker (`m1_worker_1`)  
**Parent Conversation ID:** `4454555e-8e94-46d7-b2c6-e12b4f18de76`  
**Target Milestone:** Milestone 1 — Automated Scanner & CSV Engine (`metadata_scanner.py` & `metadata_report.csv`)  
**Date:** 2026-11-02  
**Handoff Type:** Hard (Task Complete)  

---

## 1. Observation

1. **Target Deliverables Created:**
   - Source File: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py` (20,942 bytes)
   - CSV Report: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv` (1,172 bytes, 8 lines: 1 header + 6 data rows + trailing newline)

2. **Generated CSV Report Content (`metadata_report.csv`):**
   ```csv
   filename,format,metadata_fields,suspected_field,encoding,risk_score,reason
   Activation.png,PNG,"srgb, gamma, dpi, exif, Make, Model, Software, create-date, UserComment, GPSInfo",UserComment,EXIF ASCII header / plain text,15,Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5).
   Brain-Channel.png,PNG,"srgb, gamma, dpi, exif, ImageDescription",ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
   Brain.png,PNG,"srgb, gamma, dpi, Software",Software,None (plain text),10,Confirmed covert message in Software (+10).
   Chemicals.png,PNG,ImageDescription,ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
   Dopamine.png,PNG,"srgb, gamma, dpi, xmp, XML:com.adobe.xmp",XML:com.adobe.xmp (exif:MakerNote),XML encapsulation / plain text,15,Confirmed covert message in XML:com.adobe.xmp (exif:MakerNote) (+10); unusual container / embedded XMP packet (+5).
   Music.png,PNG,"srgb, gamma, dpi, Copyright, Make, Model, create-date, exif",Copyright,Base64,15,Confirmed covert message in Copyright (+10); obfuscated with Base64 encoding requiring decoding (+5).
   ```

3. **E2E Test Execution (`Lab6/test_e2e_lab6.py`):**
   - Command: `python Lab6/test_e2e_lab6.py` and `pytest Lab6/test_e2e_lab6.py -v`
   - Result:
     ```
     Ran 82 tests in 1.572s
     OK (skipped=22)
     ======================= 60 passed, 22 skipped in 1.74s ========================
     ```
   - 60 passed tests cover all Milestone 1 features:
     - F1 (Multi-Layer Metadata Extraction): EXIF IFD0, Sub-IFD UserComment, PNG chunks, XMP packets, readability.
     - F2 (De-obfuscation & Decoding): RFC 4648 Base64 decoding, 8-byte ASCII prefix stripping, XMP MakerNote XML parsing, plaintext fidelity.
     - F3 (Narrative Reconstruction Logic): Stage labels, sequencing, Cyber Kill Chain alignment.
     - F4 (Automated Scanner CLI): Script existence, CLI zero return code, CSV file generation, iteration over all 6 images, stdout progress feedback, idempotency, clean file locks, timeout limits.
     - F5 (CSV Schema & Risk Scoring): Exact 7 columns, 6 data rows, valid filename set, scores between 10 and 20, reason lengths > 10, RFC 4180 quoting, no double counting, UTF-8 integrity, suspected field names matching tags, PNG format uniformity.
     - Tier 3 Cross-feature combinations (71, 72, 73, 74) and Tier 4 real-world incident scenarios (78, 79, 80).
   - 22 skipped tests correspond to Milestone 2 (`Lab6.ipynb` execution) and Milestone 3 (`Lab6-Billy-Zandan-A01371854.docx` generation), as expected.

4. **Forensic Custody Integrity:**
   - SHA-256 hashes for all six evidence files in `Lab6/Images/` were independently computed and verified identical to original baselines:
     - `Activation.png`: `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904`
     - `Brain-Channel.png`: `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359`
     - `Brain.png`: `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e`
     - `Chemicals.png`: `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a`
     - `Dopamine.png`: `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472`
     - `Music.png`: `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370`

---

## 2. Logic Chain

1. **Multi-Layer Architecture (from Obs. 1 & 2):**  
   Because `Brain.png`, `Chemicals.png`, and `Dopamine.png` have 0 EXIF IFD0 tags, while `Brain-Channel.png` stores its payload in EXIF IFD0 tag 270 (which does not appear in `img.info`), querying only one layer fails. The implementation in `metadata_scanner.py` queries `img.info`, `img.getexif()`, `exif.get_ifd(ExifTags.IFD.Exif)`, `exif.get_ifd(ExifTags.IFD.GPSInfo)`, and parses XMP XML packets (`XML:com.adobe.xmp`), discovering 100% of candidate metadata fields.

2. **De-Obfuscation Routines (from Obs. 2):**  
   - `Activation.png`: Tag 37510 begins with `b'ASCII\x00\x00\x00'`. `analyze_and_deobfuscate` checks for this 8-byte prefix, slices it, and decodes clean UTF-8 text containing `VULN:`.
   - `Music.png`: Tag 33432 contains 84 base64 characters. The function validates length % 4 == 0, base64 character set, decodes via `base64.b64decode`, verifies printable character distribution (>85%), and extracts clean UTF-8 text containing `EXFIL:`.
   - `Dopamine.png`: The payload is encapsulated in `<exif:MakerNote>` inside `XML:com.adobe.xmp`. The XML parser extracts the element text, stripping namespaces.
   - `Brain.png`, `Brain-Channel.png`, `Chemicals.png`: Processed directly as plain text.

3. **Heuristic Risk Scoring & Non-Double-Counting Guard (from Obs. 2 & 3):**  
   - Base = 0.
   - Confirmed covert message prefix (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`) or offensive threat keywords: +10.
   - Suspicious encoding (Base64 in `Music.png`): +5 -> Score = 15.
   - Anomalous carrier indicator (camera hardware Nikon D750 + GPS coordinates embedded in synthetic diagram `Activation.png`): +5 -> Score = 15.
   - Isolated XMP packet without standard EXIF tables (`Dopamine.png`): +5 -> Score = 15.
   - Plain text without encoding or carrier anomalies (`Brain.png`, `Brain-Channel.png`, `Chemicals.png`): Score = 10.
   - Capping additions at +5 prevents double counting and guarantees scores in `{10, 15}`, satisfying both unit tests and scenario tests.

4. **Dynamic Path Resolution & CLI Usability (from Obs. 3):**  
   `resolve_paths()` inspects both `cwd` and `script_dir`, allowing zero-argument execution from either `c:\...\Lab6` or the repository root. `parse_arguments()` provides aliases (`--images`, `--image-dir`, `-i`, `-d`, `--output`, `--output-csv`, `-o`, `-v`, `-q`), while `configure_utf8_streams()` prevents CP1252 character encode crashes on Windows PowerShell.

---

## 3. Caveats

1. **Scope of Deliverables:**  
   Per Milestone 1 constraints, only `Lab6/metadata_scanner.py` and `Lab6/metadata_report.csv` were created. `Lab6.ipynb` (Milestone 2) and `Lab6-Billy-Zandan-A01371854.docx` (Milestone 3) have not been altered.
2. **Steganographic Invisibility:**  
   The scanner inspects metadata containers (EXIF, PNG chunks, XMP) and does not analyze pixel raster data (`IDAT` chunks) for LSB steganography or EOF overlays. This is by design per lab requirements and is documented in the code docstrings.

---

## 4. Conclusion

Milestone 1 is 100% complete, verified, and adheres to all project and integrity requirements:
- `Lab6/metadata_scanner.py` is fully implemented, syntactically clean, robust, and supports both CLI and importable module use.
- `Lab6/metadata_report.csv` is generated with 7 columns, RFC 4180 quoting, exactly 6 image rows, and explainable risk scores (10 and 15).
- All 60 relevant tests in `test_e2e_lab6.py` pass without error.
- Evidence files remain completely untampered.

---

## 5. Verification Method

Independent verification can be performed with the following commands:

1. **Verify E2E Test Suite (Milestone 1 Tests):**
   ```powershell
   python Lab6/test_e2e_lab6.py
   pytest Lab6/test_e2e_lab6.py -v
   ```
   *Expected:* 60 passed, 22 skipped, 0 failures.

2. **Verify CSV Schema & 7-Column Quoting:**
   ```powershell
   python -c "
   import csv
   with open('Lab6/metadata_report.csv', encoding='utf-8') as f:
       rows = list(csv.reader(f))
   assert len(rows) == 7, f'Expected 7 rows, got {len(rows)}'
   assert rows[0] == ['filename', 'format', 'metadata_fields', 'suspected_field', 'encoding', 'risk_score', 'reason']
   for r in rows:
       assert len(r) == 7, f'Invalid column count: {len(r)} in {r}'
   print('CSV Schema and RFC 4180 Verification Passed!')
   "
   ```

3. **Verify Parameterized CLI Invocation:**
   ```powershell
   python Lab6/metadata_scanner.py --images Lab6/Images --output Lab6/test_custom.csv -v
   python -c "import csv; assert len(list(csv.reader(open('Lab6/test_custom.csv', encoding='utf-8')))) == 7; print('Custom CSV Passed!')"
   Remove-Item Lab6/test_custom.csv -Force
   ```

4. **Verify Evidence Chain of Custody Integrity:**
   ```powershell
   python -c "
   import hashlib
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
       act = hashlib.sha256((Path('Lab6/Images') / name).read_bytes()).hexdigest()
       assert act == exp, f'Hash mismatch: {name}'
   print('Chain of Custody Audit: All evidence files intact!')
   "
   ```
