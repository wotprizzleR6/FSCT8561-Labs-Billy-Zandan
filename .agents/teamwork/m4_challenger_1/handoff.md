# Handoff Report: Adversarial Coverage Hardening (Tier 5 White-Box Testing)

**Agent ID:** `m4_challenger_1`  
**Working Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m4_challenger_1`  
**Target Files:** `Lab6/metadata_scanner.py`, `Lab6/metadata_report.csv`, `Lab6/test_e2e_lab6.py`, `Lab6/Images/`  
**Date:** 2026-11-02  
**Verdict:** **APPROVE**

---

## 1. Observation

### 1.1 Strict Baseline E2E Test Suite Execution
- **Command:** `cmd /c "set STRICT_E2E=1 && pytest Lab6/test_e2e_lab6.py -v"`
- **Result:**
  ```text
  platform win32 -- Python 3.14.8, pytest-9.2.0, pluggy-1.7.0
  rootdir: C:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan
  collected 82 items

  Lab6/test_e2e_lab6.py::TestTier1FeatureCoverage::test_t1_f1_01_exif_primary_extraction PASSED [  1%]
  ...
  Lab6/test_e2e_lab6.py::TestTier4RealWorldScenarios::test_t4_82_scenario_5_academic_forensic_report_delivery_audit PASSED [100%]
  ============================= 82 passed in 2.11s ==============================
  ```
- **Observations:** All 82 tests across Tier 1 (Feature Coverage), Tier 2 (Boundary & Corner Cases), Tier 3 (Cross-Feature Combinations), and Tier 4 (Real-World Incident Scenarios) passed with zero skips and zero failures under strict enforcement (`STRICT_E2E=1`).

### 1.2 White-Box Source Code Analysis of `Lab6/metadata_scanner.py`
1. **Multi-Layer Extraction Handlers:**
   - EXIF IFD0 inspected via `img.getexif()` (`collect_metadata_field_names:160`, `extract_metadata_candidates:226`).
   - EXIF Sub-IFD (`ExifOffset` tag `0x8769`) and GPS Sub-IFD (`0x8825`) traversed safely using `exif.get_ifd()` (`extract_metadata_candidates:238-249`).
   - Native PNG chunks extracted via `img.info` (`collect_metadata_field_names:157`, `extract_metadata_candidates:199`).
   - Adobe XMP XML packets parsed safely using `defusedxml.ElementTree` with standard `xml.etree.ElementTree` fallback (`metadata_scanner.py:51-56`).
   - Unhandled XML parse errors gracefully fall back to regex `r"<exif:MakerNote>(.*?)</exif:MakerNote>"` (`extract_metadata_candidates:217-219`).
2. **De-Obfuscation & Detection:**
   - Standard 8-byte EXIF ASCII header `b"ASCII\x00\x00\x00"` stripped cleanly (`analyze_and_deobfuscate:271-275`).
   - RFC 4648 Base64 payloads validated with length `>= 16`, `% 4 == 0`, regex alphabet check, `base64.b64decode(..., validate=True)`, and a printable character ratio guard `> 0.85` (`analyze_and_deobfuscate:277-287`).
   - Threat keywords matched case-insensitively across `THREAT_KEYWORDS` and `LIFECYCLE_STAGE_PREFIXES` (`analyze_and_deobfuscate:308-310`).
3. **Risk Scoring Engine:**
   - Base confirmed message: `+10` (`calculate_risk_score:338`).
   - Obfuscated Base64 encoding requiring computation: `+5` (`calculate_risk_score:342-344`).
   - Anomalous container indicators: Camera hardware and GPS on digital graphic: `+5` (`calculate_risk_score:347-349`).
   - Unusual container / embedded XMP: `+5` (`calculate_risk_score:351-353`).
   - Double-counting prevention: Mutually exclusive `elif` structure enforces that score additions are capped at a single `+5` addition, preventing unbounded accumulation (`calculate_risk_score:342-353`).
4. **Exception Handling & Directory Scanning:**
   - `scan_directory` wraps each single-image scan in a `try...except Exception as e:` block (`metadata_scanner.py:441-456`), logging errors to `sys.stderr` and proceeding with remaining files rather than terminating prematurely.
   - Output CSV path creation automatically creates non-existent parent directories via `out_path.parent.mkdir(parents=True, exist_ok=True)` (`metadata_scanner.py:462`).

### 1.3 Adversarial Test Harness Construction & Execution
- **Harness Path:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m4_challenger_1\test_adversarial_hardening.py`
- **Total Test Cases:** 40 adversarial tests across 8 categories:
  - Category 1: Malformed & Corrupted Image Headers (corrupted PNG magic bytes, truncated PNG files, 0-byte PNG files, truncated EXIF UserComments, malformed XMP XML with regex fallback, malformed XMP without MakerNote).
  - Category 2: Directory & Filesystem Edge Cases (non-existent directory, empty directory, mixed non-PNG files `.txt`/`.csv`/`.docx`/`.jpg`, clean PNG with zero metadata, directory and output paths containing spaces and symbols).
  - Category 3: CLI Parameter Boundaries & Unknown Flags (exit code 1 on missing directory, `--help` exit code 0, `--quiet` stdout suppression, `--verbose` secret preview, `--strict` unrecognized argument handling, `--input-dir` unrecognized argument handling, nested auto-created output directory).
  - Category 4: Obfuscation, Decoding & Payload Boundaries (binary Base64 rejection via printable threshold, short Base64 rejection, valid Base64 decoding, case-insensitive threat keyword matching, UTF-8 non-ASCII characters, 500KB payload handling, integer/tuple raw EXIF value handling).
  - Category 5: Risk Scoring Logic & Double-Counting Protections (plain message score 10, Base64 score 15, camera+GPS score 15, XMP score 15, double-counting cap test confirming 15, benign metadata score 0).
  - Category 6: CSV Schema, Escaping & RFC 4180 Compliance (quotes and commas escaping, exact 7-column schema verification, UTF-8 integrity).
  - Category 7: Idempotency, Determinism & State Isolation (5 consecutive runs yielding byte-for-byte identical output, immediate file descriptor release after scan, immutability of global constants).
  - Category 8: Path Resolution Flexibility (absolute paths, relative `Images` default string, direct script execution).
- **Execution Command:** `pytest .agents/teamwork/m4_challenger_1/test_adversarial_hardening.py -v`
- **Result:**
  ```text
  collected 40 items
  ...
  ============================= 40 passed in 1.57s ==============================
  ```

### 1.4 Combined Full-Suite Verification
- **Command:** `cmd /c "set STRICT_E2E=1 && pytest Lab6/test_e2e_lab6.py .agents/teamwork/m4_challenger_1/test_adversarial_hardening.py -v"`
- **Result:**
  ```text
  collected 122 items
  ============================= 122 passed in 3.57s =============================
  ```

---

## 2. Logic Chain

1. **Step 1: Baseline Integrity Verification**
   - The authoritative E2E test suite (`Lab6/test_e2e_lab6.py`) covers Features F1 through F7 in 4 tiers (82 tests).
   - Under `STRICT_E2E=1`, all 82 tests pass without regressions, confirming baseline conformance to `PROJECT.md` and `ORIGINAL_REQUEST.md`.

2. **Step 2: Analysis of White-Box Robustness**
   - In `metadata_scanner.py`, potentially fragile operations (image decoding, EXIF IFD traversal, XML parsing) are protected with explicit defensive guards:
     - Missing or empty IFDs (`sub_ifd`, `gps_ifd`) are checked for truthiness before tag enumeration.
     - Malformed XMP XML triggers a regex fallback targeting `<exif:MakerNote>`.
     - Non-string / non-bytes raw EXIF values are converted via `str(raw_val)`.
     - File handles are bounded within context managers (`with Image.open(...) as img:`, `with open(...) as f:`), preventing file descriptor exhaustion.

3. **Step 3: Verification of Risk Scoring Model**
   - The rubric and spec define:
     - `+10`: Confirmed covert message
     - `+5`: Obfuscated / encoded payload requiring decoding
     - `+5`: Anomalous container / indicator (camera hardware and GPS on graphic, or isolated XMP packet)
     - Double-counting protection: Score additions are capped so that multiple anomaly indicators do not inflate scores beyond the rubric model.
   - Empirically, the scanner produces:
     - `Brain.png`: Score 10 (plain covert message in `Software`)
     - `Brain-Channel.png`: Score 10 (plain covert message in `ImageDescription`)
     - `Chemicals.png`: Score 10 (plain covert message in `ImageDescription`)
     - `Activation.png`: Score 15 (covert message in `UserComment` + camera/GPS on graphic)
     - `Dopamine.png`: Score 15 (covert message in `XML:com.adobe.xmp` + unusual XMP container)
     - `Music.png`: Score 15 (covert message in `Copyright` + Base64 encoding)
   - These scores match `metadata_report.csv` exactly and obey the additive model.

4. **Step 4: Adversarial Attack Stress-Testing**
   - The adversarial test harness subjected `metadata_scanner.py` to:
     - Corrupted/truncated PNG and EXIF headers (handled without crash; logged to stderr and skipped).
     - Empty directories and non-PNG files (gracefully processed).
     - Malformed XML and non-ASCII character sets (correctly parsed or regex-extracted).
     - CLI edge cases (unrecognized arguments exit with status 2; missing directory exits with status 1; valid arguments execute with status 0).
     - Repeated executions (100% deterministic and idempotent).
   - All 40 adversarial tests passed with zero failures.

---

## 3. Caveats

- **CLI Flag Alias Coverage:** The scanner supports `-i`, `--images`, `--image-dir`, `-d` for input directory, and `-o`, `--output`, `--output-csv` for output CSV. Flags `--input-dir` and `--strict` are not registered options in `argparse` and therefore intentionally cause `argparse` to report unrecognized arguments with exit code 2. This is standard POSIX CLI behavior.
- **Image Format Scope:** As specified by the lab scenario, `metadata_scanner.py` exclusively discovers and processes `.png` files. Non-PNG image formats (e.g., `.jpg`, `.bmp`) placed into the input directory are ignored.
- **Review Constraint Adherence:** Per challenger constraints, no production source files or production test suites were modified. All adversarial tests were authored and executed strictly within `.agents/teamwork/m4_challenger_1/`.

---

## 4. Conclusion

**Verdict:** **APPROVE**

No blocking gaps, unhandled exceptions, logic errors, or regression bugs were identified in `Lab6/metadata_scanner.py` or `Lab6/metadata_report.csv`. The scanner is robust against corrupted images, malformed XML, missing tags, and filesystem edge cases, while strictly honoring the 7-column CSV contract, RFC 4180 escaping, and non-double-counted heuristic risk scoring.

---

## 5. Verification Method

To independently reproduce and verify this assessment:

1. **Run Strict E2E Test Suite (82 tests):**
   ```powershell
   cmd /c "set STRICT_E2E=1 && pytest Lab6/test_e2e_lab6.py -v"
   ```
2. **Run White-Box Adversarial Hardening Suite (40 tests):**
   ```powershell
   pytest .agents/teamwork/m4_challenger_1/test_adversarial_hardening.py -v
   ```
3. **Run Full Combined Test Suite (122 tests):**
   ```powershell
   cmd /c "set STRICT_E2E=1 && pytest Lab6/test_e2e_lab6.py .agents/teamwork/m4_challenger_1/test_adversarial_hardening.py -v"
   ```
4. **Inspect Production Deliverables:**
   - CSV Report: `Lab6/metadata_report.csv`
   - Scanner CLI: `python Lab6/metadata_scanner.py --help`
   - Invalidation conditions: Any test failure in the 122-test suite, CSV column count deviation from 7, or crash on corrupted PNG input.
