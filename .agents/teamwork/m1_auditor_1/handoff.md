# Forensic Audit Handoff Report: Milestone 1 (Metadata Extraction and Risk Scoring)

## Forensic Audit Report

**Work Product**: `Lab6/metadata_scanner.py`, `Lab6/metadata_report.csv`  
**Profile**: General Project  
**Integrity Mode**: Development (per `ORIGINAL_REQUEST.md`, line 8)  
**Verdict**: **CLEAN** (No integrity violations or cheating detected)

### Phase Results
- [Phase 1: Hardcoded test results / filenames]: **PASS** — AST analysis verified 0 hardcoded image filenames and 0 hardcoded test output mappings in `metadata_scanner.py`.
- [Phase 1: Facade implementations]: **PASS** — All 11 functions in `metadata_scanner.py` implement genuine algorithmic logic without dummy returns, `pass`, or `NotImplementedError`.
- [Phase 1: Pre-populated / fabricated outputs]: **PASS** — Fresh dynamic scan of `Lab6/Images` reproduces `Lab6/metadata_report.csv` identically (6 rows, matching field-for-field).
- [Phase 2: Independent Metadata Extraction]: **PASS** — Direct binary inspection of all 6 image files confirms genuine embedded payloads across EXIF IFD0, Sub-IFD UserComment, PNG tEXt chunks, and Adobe XMP packets.
- [Phase 2: Mutation Testing (Filename Invariance)]: **PASS** — Scanning renamed mutant images (`mutant_01_alpha.png`, `sample_beta_999.png`, etc.) produced identical suspected fields, encodings, and risk scores.
- [Phase 2: Adversarial & Synthetic Testing]: **PASS** — Blank and benign images produced risk score 0 ("No covert metadata detected"); synthetic Base64 and XMP images dynamically scored 15.
- [Phase 2: E2E Test Suite Execution]: **PASS** — `pytest Lab6/test_e2e_lab6.py` passed all 60 applicable test cases (22 tests skipped pending Milestone 2/3).
- [Phase 2: Cryptographic Hash Integrity]: **PASS** — All file SHA-256 hashes cataloged and verified.

---

## 1. Observation

### 1.1 Static AST Analysis (`ast_audit.py`)
Static AST inspection of `Lab6/metadata_scanner.py` (20,942 bytes, 587 lines) yielded:
- Direct image filename literals found (`Activation.png`, `Brain.png`, etc.): **0**
- Hardcoded lookup dictionaries keyed by image filename: **0**
- Facade function check across all functions:
  * `configure_utf8_streams` (lines 136-143): 2 statements, Facade=False
  * `collect_metadata_field_names` (lines 150-180): 5 statements, Facade=False
  * `extract_metadata_candidates` (lines 183-249): 7 statements, Facade=False
  * `analyze_and_deobfuscate` (lines 256-312): 7 statements, Facade=False
  * `calculate_risk_score` (lines 319-356): 7 statements, Facade=False
  * `scan_single_image` (lines 363-409): 4 statements, Facade=False
  * `scan_directory` (lines 412-478): 10 statements, Facade=False
  * `resolve_paths` (lines 485-522): 8 statements, Facade=False
  * `parse_arguments` (lines 525-560): 7 statements, Facade=False
  * `main` (lines 563-583): 6 statements, Facade=False
  * `to_csv_dict` (lines 119-129): 2 statements, Facade=False

### 1.2 Ground-Truth Image Inspection (`independent_inspect.py`)
Direct extraction via independent script without importing `metadata_scanner.py` confirmed authentic payload presence in `Lab6/Images`:
1. `Activation.png`: EXIF IFD0 tag 34665 (ExifOffset) -> Sub-IFD tag 37510 (UserComment) containing `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`, GPS Sub-IFD (tag 34853), Make `'Nikon'`, Model `'D750'`.
2. `Brain-Channel.png`: Primary EXIF IFD0 tag 270 (ImageDescription) containing `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'`.
3. `Brain.png`: Native PNG tEXt chunk `Software` containing `'RECON: Perform DNS harvesting and Subdomain enumeration.'`.
4. `Chemicals.png`: Native PNG tEXt chunk `ImageDescription` containing `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'`.
5. `Dopamine.png`: Native PNG chunk `XML:com.adobe.xmp` containing `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>`.
6. `Music.png`: Native PNG chunk `Copyright` and EXIF tag 33432 containing Base64 string `RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4=` (decodes to `'EXFIL: Tunnel compressed database dump via DNS Covert Channel.'`).

### 1.3 Dynamic Execution & Mutation Testing (`dynamic_audit.py`)
1. **Report Regeneration**:
   Executing `python Lab6/metadata_scanner.py -i Lab6/Images -o fresh_report.csv -q` resulted in exit code 0 and generated an identical 6-row CSV matching `Lab6/metadata_report.csv` with 0 diffs.
2. **Filename Mutation**:
   All 6 images were copied to a temporary test folder and renamed to arbitrary identifiers (`mutant_01_alpha.png`, `sample_beta_999.png`, `charlie_anonymous.png`, `delta_test_x.png`, `echo_random_payload.png`, `foxtrot_unknown_img.png`). Scanning this directory yielded identical suspected fields, encodings, and risk scores.
3. **Synthetic / Adversarial Verification**:
   - `clean_blank.png` (blank RGBA image): Risk Score = 0, Reason = `"No covert metadata detected."`
   - `clean_benign.png` (PNG with legitimate `Software`, `Author`, `Description` tags): Risk Score = 0, Reason = `"No covert metadata detected."`
   - `synthetic_b64.png` (PNG with synthetic Base64 covert payload in `Comment` chunk): Risk Score = 15, Encoding = `"Base64"`, Suspected Field = `"Comment"`
   - `synthetic_xmp.png` (PNG with synthetic XMP packet containing `<exif:MakerNote>PERSIST: Install scheduled task backdoor</exif:MakerNote>`): Risk Score = 15, Encoding = `"XML encapsulation / plain text"`, Suspected Field = `"XML:com.adobe.xmp (exif:MakerNote)"`

### 1.4 Test Suite Execution
Running `pytest Lab6/test_e2e_lab6.py -v`:
- Total collected: 82 test cases
- Passed: 60 test cases (100% of applicable tests for M1)
- Skipped: 22 test cases (M2 notebook in-place execution and M3 docx generation, which are planned for subsequent milestones)
- Failed: 0

### 1.5 Cryptographic Chain of Custody (SHA-256)
- `metadata_scanner.py`: `5a2c5c649f7995ff18f9e0b1ebf0e76f8823ef3a6e4773285e13c4699acd1f5c`
- `metadata_report.csv`: `11a671ebd807f466057c83adc03811e2e61553cbede793822c856072a93f2852`
- `Images/Activation.png`: `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904`
- `Images/Brain-Channel.png`: `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359`
- `Images/Brain.png`: `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e`
- `Images/Chemicals.png`: `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a`
- `Images/Dopamine.png`: `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472`
- `Images/Music.png`: `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370`

---

## 2. Logic Chain

1. **Step 1 (Static AST Inspection)**: As observed in Section 1.1, AST walking revealed zero hardcoded filename strings, zero hardcoded dictionary lookup tables, and zero facade/placeholder functions. Therefore, `metadata_scanner.py` does not contain hardcoded results or facade implementations.
2. **Step 2 (Empirical Data Verification)**: As observed in Section 1.2, independent inspection of the binary image files confirmed that all covert channel strings (DNS harvesting, CVE-2024-XXXX, SQL injection, cron job reverse shell, Mimikatz pivot, DNS exfiltration) physically reside within the image containers across 4 different metadata mechanisms (EXIF IFD0, EXIF Sub-IFD, PNG tEXt, Adobe XMP). Therefore, the extraction logic addresses authentic forensic artifacts.
3. **Step 3 (Dynamic Execution & Invariance)**: As observed in Section 1.3, running the scanner against mutated filenames yielded identical results, and running against blank/benign/synthetic images proved that scoring and detection vary strictly based on image payload properties (+10 confirmed covert, +5 Base64, +5 GPS/camera hardware or XMP). Therefore, the scanner computes results dynamically and authentically.
4. **Step 4 (Test Harness Conformance)**: As observed in Section 1.4, all 60 test cases covering Milestone 1 features pass without regression.
5. **Conclusion**: Because all static, dynamic, mutation, synthetic, and forensic checks passed with empirical evidence, the work product is authentic and free of integrity violations.

---

## 3. Caveats

- **Scope boundary**: This audit specifically covered Milestone 1 (`metadata_scanner.py` and `metadata_report.csv`). The remaining 22 tests in `test_e2e_lab6.py` relate to Milestone 2 (`Lab6.ipynb` in-place execution) and Milestone 3 (`Lab6-Billy-Zandan-A01371854.docx` document generation), which are scheduled in subsequent milestones.
- No other caveats.

---

## 4. Conclusion

**Verdict: CLEAN.**
Milestone 1 work products (`Lab6/metadata_scanner.py` and `Lab6/metadata_report.csv`) fully satisfy all integrity and forensic criteria:
- Genuine multi-layer metadata extraction across EXIF, PNG chunks, and Adobe XMP.
- True dynamic de-obfuscation (Base64 decoding, EXIF ASCII header stripping, XML extraction).
- Transparent, heuristic risk scoring without filename hardcoding or double-counting.
- Full RFC 4180 CSV contract compliance.

Milestone 1 is certified as CLEAN and ready to proceed to Milestone 2.

---

## 5. Verification Method

To independently reproduce this forensic audit:
1. **Static AST Analysis**:
   ```powershell
   python .agents\teamwork\m1_auditor_1\ast_audit.py
   ```
2. **Dynamic Mutation & Adversarial Fuzzing**:
   ```powershell
   python .agents\teamwork\m1_auditor_1\dynamic_audit.py
   ```
3. **E2E Test Suite**:
   ```powershell
   python -m pytest Lab6/test_e2e_lab6.py -v
   ```
   Expected: 60 passed, 22 skipped (M2/M3).
