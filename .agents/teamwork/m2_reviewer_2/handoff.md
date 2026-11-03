# Milestone 2 Adversarial & Quality Review Report

**Agent:** `m2_reviewer_2` (Teamwork Reviewer & Adversarial Critic)  
**Parent Conversation ID:** `4454555e-8e94-46d7-b2c6-e12b4f18de76`  
**Date:** 2026-11-02T21:41:30Z  
**Target File Reviewed:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb`  
**Working Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_reviewer_2`  
**Verdict:** **APPROVE**  

---

## 1. Observation

### 1.1 Test Suite Execution
- Command executed: `python Lab6/test_e2e_lab6.py`
  - Output: `Ran 82 tests in 1.553s ... OK (skipped=13)`
- Command executed: `python -m pytest Lab6/test_e2e_lab6.py -v`
  - Output: `69 passed, 13 skipped in 1.67s` (Exit code: 0)
  - All Milestone 2 tests passed:
    - `test_t1_f6_26_notebook_valid_json` -> PASSED
    - `test_t1_f6_27_notebook_all_cells_executed` -> PASSED
    - `test_t1_f6_28_notebook_no_unhandled_exceptions` -> PASSED
    - `test_t1_f6_29_notebook_evidence_table_populated` -> PASSED
    - `test_t1_f6_30_notebook_reflection_questions_answered` -> PASSED
    - `test_t2_f6_61_notebook_kernelspec_validity` -> PASSED
    - `test_t2_f6_62_notebook_no_empty_code_cells` -> PASSED
    - `test_t2_f6_63_notebook_markdown_prompts_preserved` -> PASSED
    - `test_t2_f6_64_notebook_execution_count_positive_integers` -> PASSED
    - `test_t2_f6_65_notebook_cell_output_text_fidelity` -> PASSED
    - `test_t3_75_f3_f6_notebook_outputs_match_reconstructed_narrative` -> PASSED
    - `test_t4_81_scenario_4_notebook_headless_cicd_pipeline` -> PASSED
  - The remaining 13 skipped tests are strictly scoped to Milestone 3 (`Lab6-Billy-Zandan-A01371854.docx`).

### 1.2 In-Place Notebook Structure & Placeholder Elimination
- File: `Lab6/Lab6.ipynb` (67,209 bytes, valid Jupyter notebook `nbformat: 4.5`).
- Total cells: 42 (18 code cells, 24 markdown cells).
- Placeholder search across all 42 cells:
  - Underscore pattern `____`: 0 occurrences found.
  - Template strings (`TODO`, `TBD`, `[Your answer here]`, `[Insert ...]`, `FIXME`): 0 occurrences found.
- Evidence Table (Cell 20): All 6 images (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`) populated with verified metadata container types, field names, raw excerpts, decoding mechanisms, and recovered fragments.
- Incident Narrative (Cell 33): Reconstructed sequence fully populated in correct causal order (`Brain.png` [RECON] -> `Activation.png` [VULN] -> `Chemicals.png` [EXPLOIT] -> `Dopamine.png` [PERSIST] -> `Brain-Channel.png` [LATERAL] -> `Music.png` [EXFIL]) with comprehensive Cyber Kill Chain and MITRE ATT&CK justifications.

### 1.3 Reflection Questions Depth & Forensic Rigor (Cell 40)
- Word count: **1,093 words** (rubric requirement >150 words threshold).
- All 5 questions addressed with graduate-level depth:
  - **Q1 (Hidden metadata beyond primary EXIF):** Explains CIPA DC-008 standard, ISO/IEC 15948 PNG text chunks (`tEXt`/`zTXt`/`iTXt`), ISO 16684-1 Adobe XMP XML/RDF packets, and TIFF Sub-IFD pointer indirection (`ExifOffset` `0x8769`, `GPSInfo` `0x8825`).
  - **Q2 (Encoding vs Encryption):** Distinguishes RFC 4648 encoding from cryptographic confidentiality, Kerckhoffs's Principle, AES-256-GCM / ChaCha20-Poly1305, and details Base64 security through obscurity in `Music.png`.
  - **Q3 (Evidence preservation & hashing):** Spoliation prevention, bit-stream imaging, Federal Rules of Evidence (FRE 901/902), ISO/IEC 27037 standards, and SHA-256 baseline hashing.
  - **Q4 (Evidentiary weight & corroboration):** Details the unauthenticated, easily forged nature of image metadata headers, specifying required corroborating telemetry: Bro/Zeek DNS queries, WAF SQL injection logs, host EDR/cron audit logs, and Active Directory Mimikatz events.
  - **Q5 (Synthesis with Labs 4 & 5):** Bridges socket inspection / protocol parsing (Lab 4) to metadata container parsing, and vulnerability scanning / explainable heuristic risk scoring (Lab 5) to `metadata_scanner.py`.

### 1.4 Textbook Citations
- Textbook (*Mastering Python for Networking and Security*, 2nd Ed., by Jose Manuel Ortega) is explicitly cited in 3 notebook cells:
  - **Cell 4:** Cites Ortega Chapter 14 regarding ISO/IEC 27037 and cryptographic integrity baselines.
  - **Cell 7:** Cites Ortega Chapter 13 (*Extracting Geolocation and Metadata from Documents, Images, and Browsers*, pp. 784–812) regarding JEITA/CIPA EXIF standards and ISO/IEC 15948 PNG chunk specifications.
  - **Cell 41:** Cites Ortega Chapter 14 regarding LSB steganography and DCT frequency modulation limits.

### 1.5 Critical Limitations Analysis (Cell 41)
- Comprehensive analytical section covering:
  - **EXIF-Only Tool Blind Spots:** Format architectural omissions (PNG `tEXt`/`zTXt`/`iTXt` chunks, Adobe XMP packets, Sub-IFD pointers), and empirical impact demonstrating a 50% detection failure rate across the lab's evidence set (`Brain.png`, `Chemicals.png`, `Dopamine.png` returning 0 EXIF tags).
  - **Automated Risk-Scoring Heuristics:** Contrast between educational triage heuristics and mathematical certainty, false-positive vulnerabilities (benign Base64 thumbnails, ICC color profiles, authentic software/legal strings, synthetic graphic templates), and false-negative vulnerabilities (LSB pixel steganography, encrypted payloads without stage markers, numeric parameter modulation).

### 1.6 Code Cell Self-Containedness & Integrity Verification
- All 18 code cells contain executable Python code.
- Verification script executed independently confirmed:
  - Every snippet dynamically loads images from `image_dir` and parses real tags, chunks, XML trees, or Base64 streams.
  - Outputs are 100% genuine and reproducible; zero mocked objects or hardcoded bypasses.
  - Headless execution via `ExecutePreprocessor` on a fresh isolated kernel ran all 18 cells with 0 errors and produced identical execution counts `[1..18]`.
  - Scanner script `metadata_scanner.py` seamlessly executes in Cell 39 and outputs to `metadata_report.csv`.

---

## 2. Logic Chain

1. **Integrity & Authenticity Check (from Obs. 1.1, 1.6):**
   - No hardcoded test results, facade implementations, or fabricated outputs were detected. All 18 code cells dynamically query Pillow, ExifTags, ElementTree, and base64. All outputs match the bitstream content of the real image evidence files.
2. **Rubric Criteria Satisfaction (from Obs. 1.2, 1.3, 1.5):**
   - Zero `__________` placeholders remain; all markdown tables and narrative sections are fully fleshed out with defensible rationale.
   - Reflection questions contain 1,093 words of rigorous technical and forensic analysis, vastly exceeding the required minimums.
   - Cell 41 provides a thorough, graduate-level dissection of EXIF-only tool blind spots and automated heuristic risk scoring limitations.
3. **Execution Robustness (from Obs. 1.1, 1.6):**
   - Running both unit test runners (`pytest` and `python Lab6/test_e2e_lab6.py`) passes 69/69 currently applicable tests. Programmatic headless execution in an isolated kernel confirmed reproducible sequential execution without state leakage or path errors.
4. **Conclusion Support:**
   - Because all functional, structural, and academic requirements for Milestone 2 are met without integrity violations, the work product is ready for approval.

---

## 3. Findings & Observations

### Minor Finding 1: Ortega Citation Placement Consolidation
- **What:** The Ortega textbook is explicitly cited in Cell 4 (Chapter 14), Cell 7 (Chapter 13, pp. 784–812), and Cell 41 (Chapter 14). However, in Cell 40 (the reflection questions block), while the theoretical concepts from Chapters 13 and 14 are accurately utilized, the literal citation string "Ortega" is not repeated in Cell 40.
- **Where:** `Lab6/Lab6.ipynb`, Cell 40.
- **Impact:** Minor / Non-blocking. The notebook as a whole clearly and repeatedly references the required Ortega textbook, and all test assertions pass.
- **Suggestion for Milestone 3:** When compiling `Lab6-Billy-Zandan-A01371854.docx` in Milestone 3, incorporate explicit Ortega textbook citations into the reflection section of the final Word document.

---

## 4. Caveats

1. **Milestone 3 Deliverable Pending:** This review evaluates Milestone 2 (`Lab6/Lab6.ipynb`). The Microsoft Word deliverable (`Lab6-Billy-Zandan-A01371854.docx`) is planned for Milestone 3 and accounts for the 13 skipped tests in `test_e2e_lab6.py`.
2. **Python Environment for Headless Execution:** Headless re-execution of Jupyter notebooks via `ExecutePreprocessor` requires `nbformat` and `nbconvert`, which reside in the local Anaconda distribution (`C:\Users\BillyZ\anaconda3\python.exe`). Normal CLI scanner and E2E test runs execute cleanly under standard Python 3.14.

---

## 5. Conclusion

**Verdict: APPROVE**

Milestone 2 has successfully satisfied all rubric and test requirements:
1. `Lab6/Lab6.ipynb` is executed and saved in place with sequential execution counts 1..18 and zero errors.
2. All 5 reflection questions are comprehensively answered with 1,093 words and deep forensic rigor.
3. All `__________` placeholders have been completely eliminated.
4. Critical limitations analysis for EXIF-only tools and automated risk-scoring heuristics is thorough and well-reasoned.
5. Code cells are self-contained, reproducible, and dynamically extract metadata without shortcuts or facades.
6. Test suite stands at 69 passed, 13 skipped (100% of Milestone 1 and 2 tests).

---

## 6. Verification Method

To independently verify this review:

1. **Run Full Test Suite:**
   ```powershell
   python Lab6/test_e2e_lab6.py
   ```
   *Expected:* `Ran 82 tests ... OK (skipped=13)`.

2. **Run Pytest Runner:**
   ```powershell
   pytest Lab6/test_e2e_lab6.py -v
   ```
   *Expected:* `69 passed, 13 skipped`.

3. **Verify Zero Placeholders & Execution Integrity:**
   ```powershell
   python -c "import json; nb=json.load(open('Lab6/Lab6.ipynb', encoding='utf-8')); assert not any('__________' in ''.join(c.get('source', [])) for c in nb['cells']); assert len([c for c in nb['cells'] if c['cell_type']=='code']) == 18; assert all(c.get('execution_count') == i+1 for i, c in enumerate([c for c in nb['cells'] if c['cell_type']=='code'])); print('Verification PASSED')"
   ```
   *Expected:* `Verification PASSED`.
