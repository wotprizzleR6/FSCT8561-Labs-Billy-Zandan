# Milestone 1 Review & Adversarial Challenge Report

**Reviewer Agent:** Teamwork Reviewer & Adversarial Critic (`m1_reviewer_1`)  
**Parent Conversation ID:** `4454555e-8e94-46d7-b2c6-e12b4f18de76`  
**Target Milestone:** Milestone 1 — Automated Scanner & CSV Engine (`metadata_scanner.py` & `metadata_report.csv`)  
**Date:** 2026-11-02  
**Verdict:** **APPROVE**  

---

## 1. Observation

1. **Target Deliverables Inspected:**
   - Source File: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py` (20,942 bytes, 588 lines)
   - CSV Report: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv` (1,172 bytes, 8 lines: 1 header + 6 data rows + trailing newline)

2. **Schema & Quoting Audit of `Lab6/metadata_report.csv`:**
   ```csv
   filename,format,metadata_fields,suspected_field,encoding,risk_score,reason
   Activation.png,PNG,"srgb, gamma, dpi, exif, Make, Model, Software, create-date, UserComment, GPSInfo",UserComment,EXIF ASCII header / plain text,15,Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5).
   Brain-Channel.png,PNG,"srgb, gamma, dpi, exif, ImageDescription",ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
   Brain.png,PNG,"srgb, gamma, dpi, Software",Software,None (plain text),10,Confirmed covert message in Software (+10).
   Chemicals.png,PNG,ImageDescription,ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
   Dopamine.png,PNG,"srgb, gamma, dpi, xmp, XML:com.adobe.xmp",XML:com.adobe.xmp (exif:MakerNote),XML encapsulation / plain text,15,Confirmed covert message in XML:com.adobe.xmp (exif:MakerNote) (+10); unusual container / embedded XMP packet (+5).
   Music.png,PNG,"srgb, gamma, dpi, Copyright, Make, Model, create-date, exif",Copyright,Base64,15,Confirmed covert message in Copyright (+10); obfuscated with Base64 encoding requiring decoding (+5).
   ```
   - Exact columns (7): `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`.
   - Number of data rows: exactly 6 rows matching all target files in `Lab6/Images/`.
   - Risk scores: `15`, `10`, `10`, `10`, `15`, `15` (all within the expected `[10, 15]` range).
   - Quoting: RFC 4180 compliant with quoted comma-separated field lists.

3. **Scanner CLI & Standalone Execution:**
   - Command: `python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py`
   - Exit code: `0`
   - Stdout feedback:
     ```
     Scanning directory: C:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images
     Found 6 PNG image(s) to inspect.

     [1/6] Scanned Activation.png
           Suspected Field : UserComment
           Encoding        : EXIF ASCII header / plain text
           Risk Score      : 15
           Reason          : Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5).
     [2/6] Scanned Brain-Channel.png ...
     ...
     Scan complete. Exported 6 record(s) to: C:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv
     ```
   - Additional CLI options tested: `--help`, `-v` (verbose), `-q` (quiet), custom `-o` output path. All options behaved as specified.

4. **Test Suite Execution (`Lab6/test_e2e_lab6.py`):**
   - Command 1: `python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\test_e2e_lab6.py`
     - Output: `Ran 82 tests in 1.580s | OK (skipped=22)`
   - Command 2: `pytest c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\test_e2e_lab6.py -v`
     - Output: `======================= 60 passed, 22 skipped in 1.72s ========================`
   - All 60 active tests passed (F1, F2, F3, F4, F5, cross-feature Tiers 3 & 4). The 22 skipped tests correspond to Milestone 2 (Notebook execution) and Milestone 3 (Word docx report), conforming to progressive testability.

5. **Integrity & Anti-Cheat Audit:**
   - Grep search for hardcoded image names (`Activation.png`, `Brain.png`, etc.) in `Lab6/metadata_scanner.py`: **0 matches**.
   - No mock dictionaries or hardcoded return mappings. Image analysis dynamically reads EXIF IFD0, Exif Sub-IFD, GPS Sub-IFD, PNG info chunks, and parses XML packets.
   - De-obfuscation performs real RFC 4648 Base64 decoding with printable character distribution ratio validation (>85%), byte slicing of standard EXIF ASCII headers, and XML element navigation.
   - Evidence file custody: SHA-256 hashes of all 6 files in `Lab6/Images/` verified identical to original hashes (no file modification).

6. **Adversarial Stress-Testing Experiments:**
   - **Scenario A (Benign Image with no metadata)**: Created a plain white PNG with no covert metadata. Result: `risk_score = 0`, `suspected_field = "None"`, `reason = "No covert metadata detected."`.
   - **Scenario B (Directory with mixed non-image files)**: Created `.txt` and `.bin` files alongside PNG. Result: scanner cleanly filtered only `.png` files without error.
   - **Scenario C (Corrupted PNG file)**: Placed invalid byte stream named `corrupt.png`. Result: scanner caught exception, printed warning to `sys.stderr`, and gracefully continued processing without crashing.
   - **Scenario D (Benign Base64 text)**: Created PNG containing Base64 string of innocuous English comment. Result: scanner decoded string, recognized no threat keywords or stage prefixes, and assigned `risk_score = 0`.

---

## 2. Logic Chain

1. **Extraction Completeness (from Obs. 1 & 4):**  
   The lab images store covert channels across distinct structures: `Brain-Channel.png` uses EXIF primary tag 270; `Activation.png` uses Exif Sub-IFD 37510; `Brain.png` and `Chemicals.png` use native PNG text chunks; `Dopamine.png` uses Adobe XMP XML packets; and `Music.png` uses EXIF Copyright tag 33432. `metadata_scanner.py` implements multi-layer inspection across all these vectors, ensuring that zero covert channels are overlooked.

2. **Heuristic Risk Scoring Correctness (from Obs. 2 & 6):**  
   The scoring engine establishes a baseline of +10 for confirmed covert messages (detected via stage prefix or threat keywords), +5 for computational decoding (Base64), +5 for anomalous carrier indicators (camera hardware + GPS tags in a synthetic graphic), and +5 for non-standard XML containers. Using `elif` branches for auxiliary scores strictly caps the maximum single-image addition to +5, enforcing the non-double-counting rule and yielding scores strictly within `{10, 15}`.

3. **CLI Design & Console Resilience (from Obs. 3):**  
   Path resolution logic dynamically handles invocation from either the repository root or the `Lab6` subdirectory. `configure_utf8_streams()` guards against Windows CP1252 stdout encoding exceptions during batch runs.

4. **Integrity Validation (from Obs. 5 & 6):**  
   The absence of hardcoded filenames, presence of real dynamic decoding algorithms, and resilience against adversarial inputs (benign Base64, corrupt files) prove this is an authentic, robust implementation without facades or shortcuts.

---

## 3. Caveats

1. **Single-Candidate Break in `scan_single_image`:**  
   The scanner breaks on the first confirmed covert candidate found in an image (`break` at line 398). In the current lab dataset, every image contains exactly one covert channel, so this is fully effective. In complex multi-payload threat scenarios, a multi-finding list aggregation would be necessary.
2. **Exclusion of Raster Steganography:**  
   The scanner intentionally inspects metadata structures (EXIF, PNG chunks, XMP) and does not analyze pixel raster data (`IDAT` chunks) for LSB steganography. This matches the scope of Lab 6 and is clearly documented.

---

## 4. Conclusion & Verdict

**Verdict: APPROVE**

Milestone 1 satisfies all functional, architectural, interface, adversarial, and integrity requirements:
- `Lab6/metadata_scanner.py` is well-structured, modular, fully typed, resilient, and non-trivial.
- `Lab6/metadata_report.csv` strictly obeys the 7-column schema, contains exactly 6 image rows, valid risk scores in `{10, 15}`, and clear heuristic explanations.
- All 60 relevant tests in `test_e2e_lab6.py` pass cleanly.
- Forensic custody of all evidence files is intact.
- No integrity violations or cheating shortcuts exist.

Proceed to Milestone 2 (Notebook In-Place Completion & Execution).

---

## 5. Verification Method

To independently verify this evaluation, execute:

1. **Run Scanner CLI:**
   ```powershell
   python Lab6/metadata_scanner.py
   ```
   *Expected:* Scans 6 images, outputs summary to stdout, exits with code 0.

2. **Verify CSV Schema & Rows:**
   ```powershell
   python -c "
   import csv
   with open('Lab6/metadata_report.csv', encoding='utf-8') as f:
       rows = list(csv.reader(f))
   assert len(rows) == 7
   assert rows[0] == ['filename', 'format', 'metadata_fields', 'suspected_field', 'encoding', 'risk_score', 'reason']
   for r in rows[1:]:
       assert len(r) == 7
       assert int(r[5]) in (10, 15)
   print('CSV Schema & Score Audit: PASSED')
   "
   ```

3. **Run Full Test Suite:**
   ```powershell
   python Lab6/test_e2e_lab6.py
   pytest Lab6/test_e2e_lab6.py -v
   ```
   *Expected:* 60 passed, 22 skipped, 0 failed.
