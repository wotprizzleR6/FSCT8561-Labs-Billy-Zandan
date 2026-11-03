# Milestone 1 Review & Adversarial Challenge Report

**Reviewer / Adversarial Critic Agent:** `m1_reviewer_2`  
**Parent Conversation ID:** `4454555e-8e94-46d7-b2c6-e12b4f18de76`  
**Target Milestone:** Milestone 1 — Automated Scanner & CSV Engine  
**Artifacts Reviewed:**
- `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py`
- `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv`
- `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\test_e2e_lab6.py`
- `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_worker_1\handoff.md`

**Verdict:** **APPROVE**  
**Integrity Status:** **VERIFIED (Zero integrity violations, zero facades, zero hardcoded shortcuts)**

---

## 1. Observation

1. **Automated E2E Test Suite Execution:**
   - Ran `python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\test_e2e_lab6.py` and `pytest Lab6/test_e2e_lab6.py -v`.
   - Result: 60 passed, 22 skipped (corresponding to M2 and M3 pending deliverables), 0 failed in 1.73s.
   - All M1 features (F1 Multi-layer Extraction, F2 De-obfuscation, F3 Narrative Logic, F4 Automated Scanner CLI, F5 Metadata CSV Schema & Scoring, pairwise combinations, and real-world incident scenarios) passed.

2. **Source Code & Integrity Audit of `Lab6/metadata_scanner.py` (588 lines):**
   - Exact file size: 20,942 bytes.
   - Checked for integrity violations:
     - No hardcoded target image filenames (`Activation.png`, `Brain.png`, etc.) exist anywhere in `metadata_scanner.py`. The file was checked via ripgrep (`grep_search`), returning 0 matches.
     - No hardcoded secret narrative messages exist in source code.
     - All extractions use genuine PIL and XML parsers (`Image.open`, `img.info`, `img.getexif()`, `sub_ifd`, `gps_ifd`, `ET.fromstring`).
     - De-obfuscation algorithms (EXIF 8-byte ASCII prefix stripping, RFC 4648 Base64 decoding, XMP XML namespace handling) perform real algorithmic transformations with printable distribution checks (>0.85).

3. **CSV Schema, RFC 4180 Quoting, and Parser Verification:**
   - Evaluated `Lab6/metadata_report.csv` with standard `csv.reader` and `pandas.read_csv`.
   - Exactly 7 lines total: 1 header + 6 data rows.
   - Exact line endings: strictly 7 `\r\n` (CRLF) line terminators, 0 lone `\n` line terminators, strictly compliant with RFC 4180 §2.1.
   - Fields containing commas (e.g. `metadata_fields`) are enclosed in double quotes per RFC 4180 §2.6.
   - `pandas.read_csv` loaded a 6x7 DataFrame with 0 null/NaN entries and matching column types (`int64` for `risk_score`, `object` for strings).

4. **CLI Resilience & Multi-Directory Path Resolution:**
   - Execution from repository root (`c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan`): default zero-argument invocation resolved paths to `Lab6/Images` and `Lab6/metadata_report.csv` with exit code 0.
   - Execution from inside `Lab6/`: zero-argument invocation succeeded with exit code 0.
   - Execution from outside the repo (`C:\` root): zero-argument invocation succeeded with exit code 0 due to `script_dir` fallback in `resolve_paths()`.
   - CLI flags: `-h` displays standard help; `-q` suppresses output while generating CSV; `-v` provides verbose diagnostic output; non-existent directories exit code 1 with stderr diagnostic; unknown options exit code 2.

5. **Module Importability & Programmatic API:**
   - Successfully imported `metadata_scanner` into Python without side effects or unintentional CLI execution.
   - Tested public classes and functions: `ImageScanResult`, `collect_metadata_field_names`, `extract_metadata_candidates`, `analyze_and_deobfuscate`, `calculate_risk_score`, `scan_single_image`, `scan_directory`. All behaved deterministically.

6. **Adversarial Stress Testing:**
   - Benign image test: Created synthetic image with standard Photoshop/GIMP metadata; scanner returned `risk_score = 0`, `suspected_field = "None"`, `reason = "No covert metadata detected."`.
   - Batch corruption resilience: Placed 0-byte and truncated PNG files alongside valid images; `scan_directory` caught exceptions per image, logged to stderr, and successfully processed the valid images without terminating early.
   - Base64 noise rejection: Random binary Base64 strings were rejected by printable ratio heuristics (>85%), preventing false-positive decodes.
   - Malformed XMP XML: Truncated/unclosed XML fell back to regex pattern extraction cleanly.
   - Unicode/Emoji stream resilience: `configure_utf8_streams()` prevented Windows CP1252 `UnicodeEncodeError` exceptions.

7. **Chain of Custody Hash Audit:**
   - SHA-256 hashes of all 6 evidence files in `Lab6/Images/` verified identical to original baseline hashes:
     - `Activation.png`: `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904`
     - `Brain-Channel.png`: `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359`
     - `Brain.png`: `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e`
     - `Chemicals.png`: `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a`
     - `Dopamine.png`: `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472`
     - `Music.png`: `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370`

---

## 2. Logic Chain

1. **Integrity Validation (from Obs. 2 & 7):**
   The source code contains no hardcoded inputs or facade outputs. It genuinely inspects and extracts metadata layers from disk images. The evidence files remain completely unmodified, verifying chain-of-custody integrity.
2. **Schema & Quoting Conformance (from Obs. 3):**
   RFC 4180 requires CRLF line breaks, consistent column counts, and quotation of strings containing commas. The output `metadata_report.csv` satisfies all conditions, loading seamlessly across both built-in `csv.reader` and high-performance `pandas.read_csv`.
3. **Execution Robustness & Portability (from Obs. 4 & 5):**
   By inspecting both `cwd` and `script_dir`, `resolve_paths()` enables the script to run seamlessly from any working directory. Wrapping entry points in `if __name__ == "__main__":` ensures the scanner can be imported as a library for subsequent milestones (M2 notebook execution and M3 report generation).
4. **Adversarial Resilience (from Obs. 6):**
   Edge case testing proved that the scanner is not brittle: it rejects non-covert metadata (score 0), survives corrupted files in batch directories, falls back to regex for malformed XMP XML, avoids decoding random binary Base64, and protects against Windows console character map crashes via `configure_utf8_streams()`.
5. **E2E Test Alignment (from Obs. 1):**
   All 60 test cases for Milestone 1 pass cleanly in `test_e2e_lab6.py`. The 22 skipped tests belong strictly to downstream milestones M2 and M3.

---

## 3. Caveats

1. **Downstream Deliverables Not Yet Built:**
   `Lab6.ipynb` (Milestone 2) and `Lab6-Billy-Zandan-A01371854.docx` (Milestone 3) are intentionally unexecuted/unbuilt at this stage, accounting for the 22 skipped tests in the E2E suite.
2. **Steganographic Scope:**
   As intended by the lab specification, the scanner analyzes metadata containers (EXIF, PNG text chunks, Adobe XMP packets) and does not perform LSB raster image steganography detection on pixel `IDAT` blocks.

---

## 4. Conclusion

**Verdict: APPROVE**

Milestone 1 satisfies all functional, architectural, adversarial, and integrity requirements:
- `metadata_scanner.py` is production-ready, fully importable, robust against edge cases, and cross-directory compatible.
- `metadata_report.csv` is fully compliant with RFC 4180 and parses flawlessly with `csv.reader` and `pandas`.
- All 60 applicable unit and integration tests pass without error.
- No integrity violations, facades, or shortcuts exist.
- Milestone 1 is approved to proceed to Milestone 2 (`Lab6.ipynb` in-place execution).

---

## 5. Verification Method

To independently verify this assessment:

1. **Run full E2E test suite:**
   ```powershell
   python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\test_e2e_lab6.py
   pytest c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\test_e2e_lab6.py -v
   ```
   *Expected:* 60 passed, 22 skipped, 0 failures.

2. **Verify RFC 4180 and CSV parsing:**
   ```powershell
   python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_reviewer_2\test_csv_rfc4180.py
   ```
   *Expected:* Clean pass with 7 CRLF line terminators and zero lone LF.

3. **Verify module importability & programmatic API:**
   ```powershell
   python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_reviewer_2\test_import_module.py
   ```
   *Expected:* All programmatic calls pass cleanly.

4. **Verify adversarial stress resilience:**
   ```powershell
   python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_reviewer_2\test_adversarial_scanner.py
   ```
   *Expected:* All 6 adversarial stress tests pass cleanly.

5. **Verify zero hardcoded shortcuts in source code:**
   ```powershell
   python -c "
   from pathlib import Path
   src = Path('Lab6/metadata_scanner.py').read_text()
   for name in ['Activation', 'Brain', 'Chemicals', 'Dopamine', 'Music']:
       assert name not in src, f'Found hardcoded image name: {name}'
   print('Zero hardcoded filenames confirmed.')
   "
   ```
