# Milestone 3 Explorer Handoff Report

**Agent:** `m3_explorer_1` (Teamwork Explorer)  
**Parent Conversation ID:** `4454555e-8e94-46d7-b2c6-e12b4f18de76`  
**Date:** 2026-11-02  
**Scope:** Milestone 3 — Word Document Content, Rubric Mapping, and Academic Sections  
**Target File to Generate:** `Lab6/Lab6-Billy-Zandan-A01371854.docx`  
**Worker Implementation Script:** `Lab6/generate_report_docx.py`  

---

## 1. Observation

Direct observations from examining the codebase, lab artifacts, textbook, and test suites:

1. **Rubric & User Requirements (`ORIGINAL_REQUEST.md` §R4, lines 26–28, 46–55):**
   - The Word document must be saved at `Lab6/Lab6-Billy-Zandan-A01371854.docx`.
   - Must contain: Student Name (`Billy Zandan`), Student ID (`A01371854`), course metadata (`FSCT 8561`), complete evidence table for all 6 images, extraction output evidence, reconstructed six-stage secret with sequence reasoning, scanner source code and formatted CSV results table, explanation of limitations (EXIF-only and automated risk scoring), and comprehensive answers to all five reflection questions.

2. **Executed Notebook State (`Lab6/Lab6.ipynb`):**
   - All 42 cells (24 markdown, 18 code) have been executed with positive integer execution counts (1 through 18) and clean stdout outputs.
   - Cell 20 provides the evidence table.
   - Cells 21–32 contain image-by-image code and terminal outputs for `Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, and `Music.png`.
   - Cell 33 contains the reconstructed narrative and Cyber Kill Chain / MITRE ATT&CK justification, plus the technical disproof of filename ordering.
   - Cell 39 outputs the 6-row scan log and creates `metadata_report.csv`.
   - Cell 40 contains complete responses to reflection questions 1 through 5 and the limitations analysis.
   - Cell 41 details the 100-point grading rubric.

3. **CSV Ground Truth (`Lab6/metadata_report.csv`, lines 1–8):**
   - Exactly 7 columns: `filename,format,metadata_fields,suspected_field,encoding,risk_score,reason`.
   - Exactly 6 rows with risk scores 15 (`Activation.png`), 10 (`Brain-Channel.png`), 10 (`Brain.png`), 10 (`Chemicals.png`), 15 (`Dopamine.png`), and 15 (`Music.png`).

4. **Opaque-Box E2E Test Suite (`Lab6/test_e2e_lab6.py`):**
   - F7 tests explicitly verify docx deliverables:
     - `test_t1_f7_31_docx_file_exists_and_valid`: file opens via `docx.Document(DOCX_REPORT)`.
     - `test_t1_f7_32_docx_student_metadata`: full text must contain `"Billy Zandan"` and `"A01371854"`.
     - `test_t1_f7_33_docx_all_rubric_sections_present`: full text must contain lowercase keywords `"evidence"`, `"reconstructed"`, `"scanner"`, `"limitation"`, and `"reflection"`.
     - `test_t1_f7_34_docx_evidence_table_structure`: table containing all 6 image names with header + 6 rows (at least 7 rows total).
     - `test_t1_f7_35_docx_limitations_and_reflections_addressed`: contains `"EXIF"`, `"Base64"`, `"hash"`, and word count > 500 words.
     - `test_t2_f7_66_docx_minimum_length_and_depth`: document has at least 15 paragraphs.
     - `test_t2_f7_67_docx_evidence_table_column_count`: at least one table with >= 5 columns.
     - `test_t2_f7_68_docx_csv_results_table_present`: table with header containing `"risk"` or `"suspected"`.
     - `test_t2_f7_69_docx_scanner_code_snippet_present`: text contains `"import"` and (`"def "` or `"class "` or `"Image.open"`).
     - `test_t2_f7_70_docx_xml_package_validity`: valid OOXML zip archive containing `word/document.xml`.
     - `test_t3_76_f5_f7_docx_csv_table_matches_metadata_report_csv`: table contains every filename and its risk score from `metadata_report.csv`.
     - `test_t3_77_f6_f7_docx_reflections_match_notebook_answers`: contains `"getexif"`, `"base64"`, `"hash"`, `"corroborat"`, and `"lab"`.

5. **Authoritative Textbook (`Mastering Python for Networking and Security`, 2nd ed., Jose Manuel Ortega, 2021):**
   - **Chapter 13 (pp. 800–815):** "Extracting Geolocation and Metadata from Documents, Images, and Browsers" — `PIL.Image`, `_getexif()`, `ExifTags.TAGS`, tag 34853 (`GPSInfo`), camera hardware metadata (`Make`, `Model`, `Software`).
   - **Chapter 14 (pp. 853–870, 881–890):** "Cryptography and Steganography" — core distinction between encryption (confidentiality, secret keys, Kerckhoffs's principle) and encoding (open data representation, Base64 RFC 4648, zero security).
   - **Chapter 14 (pp. 892–905):** "Steganography techniques for hiding information in images" — LSB pixel steganography with `stepic` library, which bypasses metadata entirely (resulting in metadata risk score 0).
   - **Chapter 14 (pp. 906–915):** "Generating keys securely with the secrets and hashlib modules" — `hashlib.sha256()` and `hashlib.md5()` cryptographic digests for file integrity, non-repudiation, and chain of custody (ISO/IEC 27037).

---

## 2. Logic Chain

1. **From Observation 1 and 4 to Structure Design:**
   The Word document must satisfy all 5 rubric areas and all 12 E2E test assertions in `test_e2e_lab6.py`. Therefore, the document must be structured into 7 core sections:
   - Header & Document Metadata
   - Section 1: Executive Summary & Evidence Custody Inventory
   - Section 2: Complete Forensic Metadata Evidence Table (7 columns, 6 image rows)
   - Section 3: Detailed Image-by-Image Forensic Extraction Evidence (with code snippets and raw execution logs)
   - Section 4: Reconstructed Six-Stage Incident Secret Narrative (Cyber Kill Chain, MITRE ATT&CK, explicit technical disproof of filename ordering)
   - Section 5: Automated Metadata Scanner Architecture, Risk Scoring Heuristic Model, and Formatted CSV Audit Table
   - Section 6: Critical Forensic Limitations Analysis (EXIF-only blind spots and automated risk scoring limitations)
   - Section 7: Comprehensive Answers to Reflection Questions 1 to 5 (with explicit citations to Ortega Ch 13 & 14)

2. **From Observation 2 and 3 to Content Formulation:**
   The exact text, raw values, decoded strings, narrative order, and risk scores have been verified from the executed notebook (`Lab6.ipynb`) and CSV (`metadata_report.csv`). Re-transcribing these verbatim into the Word report guarantees 100% internal consistency across all lab deliverables.

3. **From Observation 5 to Academic Rigor:**
   Incorporating specific citations to Ortega (2021) Chapters 13 & 14 directly supports Questions 1, 2, 3, and the limitations analyses, ensuring full-credit marks under the 10-point presentation and interpretation rubric component.

4. **From Observation 4 to Worker Script Specification (`generate_report_docx.py`):**
   By providing a fully formulated Python script that uses `python-docx` to construct the document programmatically, the Worker agent in Milestone 3 can execute the script, generate `Lab6/Lab6-Billy-Zandan-A01371854.docx`, and verify it against `test_e2e_lab6.py` without guesswork or omissions.

---

## 3. Caveats

1. **PDF Conversion vs. Docx Deliverable:**
   The notebook markdown in Cell 41 mentions "Submit one PDF named `Lab6-FirstName-LastName-StudentNumber.pdf`", but `ORIGINAL_REQUEST.md` (§R4) and the project specification mandate generating `Lab6/Lab6-Billy-Zandan-A01371854.docx`. Word documents can be saved directly as `.docx`, and if a PDF is required in the future, Word or headless LibreOffice can convert it. The test suite specifically validates the `.docx` artifact.
2. **Double-Counting Heuristic:**
   In `metadata_scanner.py` and `metadata_report.csv`, `Music.png` and `Activation.png` are scored at 15 points (+10 covert keyword, +5 for Base64 in Music, +5 for GPS/camera in Activation). The rubric explicitly states: "Avoid double-counting an encoded message as both an encoded indicator and an additional unusual indicator." The document emphasizes this rule in both Section 5 and Section 6.

---

## 4. Conclusion

Milestone 3 analysis is complete. The structure, complete text, forensic tables, code listings, execution logs, narrative sequence justifications, technical disproofs, limitation essays, reflection answers with Ortega citations, and the Python generator blueprint have been thoroughly formulated and documented in:
`c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m3_explorer_1\analysis.md`

The Worker agent can proceed immediately to implement `Lab6/generate_report_docx.py`, execute it to produce `Lab6/Lab6-Billy-Zandan-A01371854.docx`, and run the test harness to confirm 100% test passage.

---

## 5. Verification Method

To independently verify this formulation and test the generated document:

1. **Inspect Analysis Specification:**
   - Path: `.agents/teamwork/m3_explorer_1/analysis.md`
   - Confirm all 7 sections, tables, and Ortega textbook citations are present.

2. **Execute Worker Document Generator (upon implementation):**
   ```powershell
   cd c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6
   python generate_report_docx.py
   ```

3. **Execute Opaque-Box E2E Test Suite:**
   ```powershell
   cd c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan
   pytest Lab6/test_e2e_lab6.py -v -k "docx"
   pytest Lab6/test_e2e_lab6.py -v
   ```

4. **Invalidation Conditions:**
   - Any failure in `test_t1_f7_*`, `test_t2_f7_*`, or `test_t3_76`/`test_t3_77`.
   - Word count of generated document under 500 words (the formulated specification exceeds 2,500 words).
   - Missing student identification (`Billy Zandan`, `A01371854`).
   - Missing any of the 6 images in the evidence table or CSV table.
