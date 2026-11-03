# Milestone 3 Analysis: Docx Verification Checklist & E2E Test Assertion Mapping

**Author:** Milestone 3 Explorer 3 (`m3_explorer_3`)  
**Mission:** Docx test alignment, E2E test assertions, schema validation, and Word document verification checklist  
**Target Deliverable:** `Lab6/Lab6-Billy-Zandan-A01371854.docx`  
**Test Suite:** `Lab6/test_e2e_lab6.py` (82 total tests: 69 currently PASS, 13 currently SKIP)  
**Date:** 2026-11-02  

---

## 1. Executive Summary & Verification Objective

The objective of Milestone 3 is to generate the final Word document deliverable:
```
c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6-Billy-Zandan-A01371854.docx
```
Currently, the test harness `Lab6/test_e2e_lab6.py` executes 82 test cases across 4 tiers:
- **69 tests PASS** (covering Multi-Layer Extraction F1, Covert De-obfuscation F2, Narrative Assembly F3, Scanner CLI F4, CSV Schema & Scoring F5, and Notebook Execution F6).
- **13 tests SKIP** solely because `Lab6/Lab6-Billy-Zandan-A01371854.docx` has not yet been generated.
- **0 tests FAIL**.

When `Lab6-Billy-Zandan-A01371854.docx` is generated in full compliance with all 13 test assertions, all 13 skipped tests will immediately unlock and transition to PASS, achieving an unblemished **82 / 82 (100%) pass rate** both in progressive mode and under strict CI/CD mode (`STRICT_E2E=1`).

---

## 2. In-Depth Mapping of all 13 Skipped Tests in `Lab6/test_e2e_lab6.py`

Below is the definitive catalog of every test function currently skipped for Milestone 3, including exact line references, test inputs, evaluated objects, and exact assertion conditions.

| # | Test Function Name | Tier | Category | Lines | Evaluated Target | Exact Assertion Criteria |
|---|--------------------|:----:|:--------:|:-----:|:----------------:|:-------------------------|
| 1 | `test_t1_f7_31_docx_file_exists_and_valid` | Tier 1 | F7 | 452–456 | `DOCX_REPORT` | • File exists at `Lab6/Lab6-Billy-Zandan-A01371854.docx`<br>• `Document(str(DOCX_REPORT))` opens without raising an exception<br>• `doc is not None` |
| 2 | `test_t1_f7_32_docx_student_metadata` | Tier 1 | F7 | 457–467 | `doc.paragraphs` + `doc.tables` | • `"Billy Zandan"` in `full_text`<br>• `"A01371854"` in `full_text`<br>*(Checked across body paragraphs AND table cells)* |
| 3 | `test_t1_f7_33_docx_all_rubric_sections_present` | Tier 1 | F7 | 468–481 | `doc.paragraphs` (lower) | • `"evidence"` in `para_text`<br>• `"reconstructed"` in `para_text`<br>• `"scanner"` in `para_text`<br>• `"limitation"` in `para_text`<br>• `"reflection"` in `para_text`<br>*(Checked ONLY in body paragraphs!)* |
| 4 | `test_t1_f7_34_docx_evidence_table_structure` | Tier 1 | F7 | 482–495 | `doc.tables` | • `len(doc.tables) >= 1`<br>• At least 1 table contains all 6 image names: `Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`<br>• That table has `len(t.rows) >= 7` (1 header + 6 data rows) |
| 5 | `test_t1_f7_35_docx_limitations_and_reflections_addressed` | Tier 1 | F7 | 496–504 | `doc.paragraphs` | • `"EXIF"` in `para_text` (case-sensitive)<br>• `"Base64"` in `para_text` (case-sensitive)<br>• `"hash"` in `para_text.lower()` (case-insensitive)<br>• `len(para_text.split()) > 500` (>500 words in body paragraphs alone!) |
| 6 | `test_t2_f7_66_docx_minimum_length_and_depth` | Tier 2 | F7 | 792–796 | `doc.paragraphs` | • `len(doc.paragraphs) >= 15` (at least 15 paragraphs in document body) |
| 7 | `test_t2_f7_67_docx_evidence_table_column_count` | Tier 2 | F7 | 797–806 | `doc.tables` | • At least 1 table has `len(t.columns) >= 5` |
| 8 | `test_t2_f7_68_docx_csv_results_table_present` | Tier 2 | F7 | 807–817 | `doc.tables[...].rows[0]` | • At least 1 table whose first row (`t.rows[0].cells`) has `"risk"` or `"suspected"` (case-insensitive) in cell text |
| 9 | `test_t2_f7_69_docx_scanner_code_snippet_present` | Tier 2 | F7 | 818–825 | `doc.paragraphs` | • `"import"` in `para_text`<br>• AND (`"def "` in `para_text` OR `"class "` in `para_text` OR `"Image.open"` in `para_text`)<br>*(MUST be in body paragraphs, NOT table cells!)* |
| 10 | `test_t2_f7_70_docx_xml_package_validity` | Tier 2 | F7 | 826–833 | `zipfile` archive | • `zipfile.is_zipfile(str(DOCX_REPORT))` is True<br>• `"word/document.xml"` in archive `namelist()` |
| 11 | `test_t3_76_f5_f7_docx_csv_table_matches_metadata_report_csv` | Tier 3 | F5+F7 | 931–942 | `doc.tables` vs `CSV_REPORT` | • For each row in `metadata_report.csv`:<br>&nbsp;&nbsp;- `row["filename"]` in `table_text`<br>&nbsp;&nbsp;- `str(row["risk_score"])` in `table_text`<br>*(All 6 files and scores: Activation.png, 15; Brain-Channel.png, 10; Brain.png, 10; Chemicals.png, 10; Dopamine.png, 15; Music.png, 15)* |
| 12 | `test_t3_77_f6_f7_docx_reflections_match_notebook_answers` | Tier 3 | F6+F7 | 943–958 | `doc.paragraphs` (lower) | • `"getexif"` in `para_text.lower()` (Prompt 1)<br>• `"base64"` in `para_text.lower()` (Prompt 2)<br>• `"hash"` in `para_text.lower()` (Prompt 3)<br>• `"corroborat"` in `para_text.lower()` (Prompt 4)<br>• `"lab"` in `para_text.lower()` (Prompt 5) |
| 13 | `test_t4_82_scenario_5_academic_forensic_report_delivery_audit` | Tier 4 | Scenario 5 | 1060–1085 | Multi-artifact audit | • `metadata_scanner.py` exists<br>• `metadata_report.csv` has 6 rows<br>• `Lab6.ipynb` executed<br>• In `doc.paragraphs`: `"Billy Zandan"` and `"A01371854"`<br>• `len(doc.tables) >= 2` (both Evidence and CSV tables present) |

---

## 3. Forensic Gotchas & Architectural Pitfalls

During our deep-dive AST and execution analysis of `test_e2e_lab6.py`, we identified **four high-severity architectural traps** that could cause test failures even if a visually appealing Word document is produced. Implementers of `generate_report_docx.py` must adhere strictly to these rules:

### Gotcha 1: `doc.paragraphs` vs. `doc.tables` Isolation (The Callout Box Trap)
- **The Issue**: In `python-docx`, `doc.paragraphs` contains **ONLY** top-level paragraphs residing in the document body. Any paragraph placed inside a table cell (including 1x1 callout boxes or styled code containers) is stored in `cell.paragraphs` and is **completely invisible** to `doc.paragraphs`.
- **The Test Vulnerability**: `test_t2_f7_69_docx_scanner_code_snippet_present` inspects:
  ```python
  full_text = "\n".join(p.text for p in doc.paragraphs)
  self.assertTrue("import" in full_text and ("def " in full_text or "class " in full_text or "Image.open" in full_text))
  ```
  If the code block is rendered *only* inside a 1x1 table (as in `box_table = doc.add_table(1, 1)`), `doc.paragraphs` will NOT contain `"import"`, `"def "`, or `"Image.open"`, causing `test_t2_f7_69` to fail immediately!
- **Mandatory Solution**: 
  - Render code snippets as genuine body paragraphs (`doc.add_paragraph()`) formatted with the Consolas font, or include code snippets in body text alongside any callout box.

### Gotcha 2: Header / Footer Isolation for Student Metadata
- **The Issue**: In `python-docx`, `section.header.paragraphs` and `section.footer.paragraphs` are disjoint from `doc.paragraphs`.
- **The Test Vulnerability**: In `test_t4_82_scenario_5_academic_forensic_report_delivery_audit`:
  ```python
  full_text = "\n".join(p.text for p in doc.paragraphs)
  self.assertIn(STUDENT_NAME, full_text)
  self.assertIn(STUDENT_ID, full_text)
  ```
  Notice that unlike `test_t1_f7_32` (which checks paragraphs + table cells), Scenario 5 checks **ONLY** `doc.paragraphs`!
- **Mandatory Solution**: 
  - The student's full name (`Billy Zandan`) and student ID (`A01371854`) **MUST** be explicitly rendered in document body paragraphs (e.g., in the Title / Subtitle / Author metadata block at the top of page 1), in addition to any running header/footer.

### Gotcha 3: Exact Case-Sensitivity on Technical Keywords
- **The Issue**: `test_t1_f7_35` checks:
  ```python
  self.assertIn("EXIF", full_text)
  self.assertIn("Base64", full_text)
  self.assertIn("hash", full_text.lower())
  ```
- **Mandatory Solution**:
  - `"EXIF"` must be all uppercase.
  - `"Base64"` must have a capital 'B' and lowercase 'ase64'.
  - `"hash"` can be any case.

### Gotcha 4: Table Header Identification for CSV Results Table
- **The Issue**: `test_t2_f7_68` searches for a table where:
  ```python
  header_text = " ".join(c.text.lower() for c in t.rows[0].cells)
  if "risk" in header_text or "suspected" in header_text: ...
  ```
- **Mandatory Solution**:
  - The first row (`t.rows[0]`) of the CSV results table must contain column headers including words like `"Risk Score"` or `"Suspected Field"`.

---

## 4. Complete Milestone 3 Word Document Verification Checklist

To ensure 100% compliance prior to running tests, the document generator must satisfy every item on this checklist:

### A. Document File & Package Schema
- [ ] Document is saved to exact path: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6-Billy-Zandan-A01371854.docx`.
- [ ] File is a valid OOXML zip archive (`zipfile.is_zipfile` is True).
- [ ] Archive contains `word/document.xml`.
- [ ] File size is realistic for an academic deliverable (>25 KB).

### B. Student Identity & Author Metadata
- [ ] Student Name `"Billy Zandan"` is present in body paragraph text (`doc.paragraphs`).
- [ ] Student ID `"A01371854"` is present in body paragraph text (`doc.paragraphs`).
- [ ] Header / Footer metadata includes student name and course information.

### C. Paragraph Content, Headings & Word Count
- [ ] Document has at least 15 paragraphs in `doc.paragraphs` (`len(doc.paragraphs) >= 15`).
- [ ] Total word count in body paragraphs exceeds 500 words (`len(full_text.split()) > 500`).
- [ ] Rubric keywords appear in body paragraph text (case-insensitively):
  - [ ] `"evidence"`
  - [ ] `"reconstructed"`
  - [ ] `"scanner"`
  - [ ] `"limitation"`
  - [ ] `"reflection"`
- [ ] Case-sensitive technical terms appear in body paragraphs:
  - [ ] `"EXIF"` (exact match)
  - [ ] `"Base64"` (exact match)
  - [ ] `"hash"` (case-insensitive)
- [ ] Reflection question keywords appear in body paragraphs (case-insensitively):
  - [ ] `"getexif"` (Prompt 1)
  - [ ] `"base64"` (Prompt 2)
  - [ ] `"hash"` (Prompt 3)
  - [ ] `"corroborat"` (Prompt 4)
  - [ ] `"lab"` (Prompt 5)

### D. Python Scanner Code Snippet
- [ ] Python source code snippet is included in body paragraph text (`doc.paragraphs`).
- [ ] Code text contains `"import"`.
- [ ] Code text contains at least one of: `"def "`, `"class "`, or `"Image.open"`.

### E. Table 1: Metadata Evidence Table
- [ ] Table has at least 5 columns (`len(t.columns) >= 5`), e.g., Image Name, Metadata Layer/Type, Suspected Field, Raw Value / Decoding, Recovered Secret / Stage.
- [ ] Table has at least 7 rows (`len(t.rows) >= 7`): 1 header row + 6 image rows.
- [ ] Table cell text contains all 6 image filenames:
  - [ ] `Activation.png`
  - [ ] `Brain-Channel.png`
  - [ ] `Brain.png`
  - [ ] `Chemicals.png`
  - [ ] `Dopamine.png`
  - [ ] `Music.png`
- [ ] Recovered secret fragments match ground truth for all 6 images.

### F. Table 2: Scanner CSV Results Table
- [ ] Table has at least 2 tables in document (`len(doc.tables) >= 2`).
- [ ] First row header (`t.rows[0].cells`) contains `"risk"` or `"suspected"` (e.g. `Suspected Field`, `Risk Score`).
- [ ] Table reproduces all 6 rows from `Lab6/metadata_report.csv`:
  - [ ] `Activation.png` and score `15`
  - [ ] `Brain-Channel.png` and score `10`
  - [ ] `Brain.png` and score `10`
  - [ ] `Chemicals.png` and score `10`
  - [ ] `Dopamine.png` and score `15`
  - [ ] `Music.png` and score `15`

---

## 5. Standalone Verification Tool: `verify_docx.py`

To eliminate guesswork, `m3_explorer_3` created an automated verification tool in this working directory:
```
c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m3_explorer_3\verify_docx.py
```

### Tool Architecture & Features
1. **Direct AST/python-docx inspection**: Programmatically parses `doc.paragraphs`, `doc.tables`, table cells, headers, and zip structures.
2. **Exact Test Mapping**: Directly evaluates the precise conditions of all 13 skipped E2E tests:
   - `test_t1_f7_31` (Load success)
   - `test_t1_f7_32` (Student metadata)
   - `test_t1_f7_33` (Rubric headings)
   - `test_t1_f7_34` (Evidence table structure)
   - `test_t1_f7_35` (Limitations & word count > 500)
   - `test_t2_f7_66` (Paragraph count >= 15)
   - `test_t2_f7_67` (Column count >= 5)
   - `test_t2_f7_68` (CSV results table header)
   - `test_t2_f7_69` (Code snippet in paragraphs)
   - `test_t2_f7_70` (OOXML zip validity)
   - `test_t3_76` (CSV report table parity)
   - `test_t3_77` (Reflection prompts in paragraphs)
   - `test_t4_82` (Scenario 5 comprehensive deliverable audit)
3. **Exit Code Semantics**: Returns `0` if and only if all 13 assertions pass; returns `1` with itemized diagnostics if any assertion fails.

### Running the Verification Tool
```powershell
python .agents/teamwork/m3_explorer_3/verify_docx.py [optional_path_to_docx]
```
If no path is specified, it targets `Lab6/Lab6-Billy-Zandan-A01371854.docx`.

---

## 6. Official Test Commands for Milestone 3 & M4

Once `Lab6-Billy-Zandan-A01371854.docx` is generated:

### 1. Pre-Flight Verification
Run the verification script:
```powershell
python .agents/teamwork/m3_explorer_3/verify_docx.py
```

### 2. Standard E2E Test Execution (Milestone 3 Validation)
```powershell
python -m pytest Lab6/test_e2e_lab6.py -v
```
Expected output:
```
======================= 82 passed in 1.85s =======================
```

### 3. Strict CI/CD Mode Verification (Milestone 4 Readiness)
```powershell
cmd /c "set STRICT_E2E=1 && python -m pytest Lab6/test_e2e_lab6.py -v"
```
Expected output:
```
======================= 82 passed in 1.85s =======================
```
Zero skipped, zero failed.
