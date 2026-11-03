# Analysis: Milestone 2 — In-Place Notebook Execution Pipeline & Output Validation

**Date**: 2026-11-02  
**Author**: Teamwork Explorer (Milestone 2)  
**Parent Conversation ID**: `4454555e-8e94-46d7-b2c6-e12b4f18de76`  
**Working Directory**: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_explorer_3`

---

## 1. Executive Summary

Milestone 2 requires populating all markdown and code responses within `Lab6/Lab6.ipynb`, executing the notebook in place so that all code cells complete with valid outputs, and confirming that the notebook satisfies all acceptance criteria tested by `test_e2e_lab6.py`.

Through technical investigation, empirical prototyping, and test verification in `.agents/teamwork/m2_explorer_3/`, we have established:
1. **Execution Pipeline**: Both CLI execution (`jupyter.exe nbconvert --to notebook --execute --inplace`) and programmatic Python execution via Anaconda's `nbconvert.preprocessors.ExecutePreprocessor` are verified to run deterministically.
2. **Working Directory Mandate**: Because `Lab6.ipynb` references `image_dir = Path("Images")`, execution MUST be rooted in `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6` (or explicitly passed via `resources['metadata']['path']`) to prevent `FileNotFoundError`.
3. **Notebook Population Scope**: Exactly 10 code cells require implementation or completion, 3 markdown cells require population (Evidence table in cell 20, Reconstructed secret narrative in cell 33, and Reflection questions in cell 40).
4. **Test Transition Verification**: When `Lab6.ipynb` is populated and executed in place, exactly 9 tests in `test_e2e_lab6.py` transition from `SKIPPED` to `PASSED`, raising the total test pass rate from 60/82 to 69/82 with 0 failures and 0 errors. The remaining 13 skipped tests are strictly downstream Milestone 3 / Milestone 4 deliverables (`Lab6-Billy-Zandan-A01371854.docx`).

---

## 2. In-Place Execution Pipeline Formulation

### 2.1 Primary CLI Execution Command

The primary method for executing `Lab6.ipynb` in place uses Anaconda Jupyter's `nbconvert` CLI:

```powershell
Set-Location "c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6"
& "C:\Users\BillyZ\anaconda3\Scripts\jupyter.exe" nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 Lab6.ipynb
```

#### CLI Command Arguments Breakdown:
- `--to notebook`: Preserves Jupyter Notebook JSON formatting (schema v4).
- `--execute`: Triggers the kernel execution pipeline across all code cells sequentially.
- `--inplace`: Overwrites `Lab6.ipynb` directly with execution counts, timing metadata, and output streams, eliminating intermediate temporary files.
- `--ExecutePreprocessor.timeout=600`: Overrides the default 30-second cell timeout to prevent timeouts during `%pip` dependency resolution or multi-file iteration.
- `Set-Location ...\Lab6`: Mandatory working directory configuration.

### 2.2 Programmatic Python Fallback Pipeline

In headless CI/CD environments or PowerShell sessions where console encoding or subprocess handling presents risks, the programmatic Python runner script provides a robust, zero-subprocess fallback.

```python
"""
Programmatic in-place notebook runner using Anaconda Python.
Guarantees execution context, eliminates event loop warnings, and preserves notebook JSON.
"""
import asyncio
import sys
from pathlib import Path

# On Windows, set WindowsSelectorEventLoopPolicy before pyzmq/tornado initialization
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

LAB6_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6")
NOTEBOOK_PATH = LAB6_DIR / "Lab6.ipynb"

# 1. Read existing notebook preserving structure
with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

# 2. Configure preprocessor
ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

# 3. Execute in-place with exact working directory context
ep.preprocess(nb, {"metadata": {"path": str(LAB6_DIR)}})

# 4. Save executed notebook
with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"Successfully executed and saved {NOTEBOOK_PATH} in place.")
```

#### Programmatic Pipeline Advantages:
1. **Explicit CWD Guarantee**: `{"metadata": {"path": str(LAB6_DIR)}}` sets `os.getcwd()` for the kernel to `Lab6/`, ensuring `Path("Images")` always resolves to `Lab6/Images` regardless of the caller's working directory.
2. **Proactor Warning Suppression**: Python 3.8+ on Windows defaults to `ProactorEventLoop`, which lacks socket reader hooks needed by pyzmq. Injecting `WindowsSelectorEventLoopPolicy()` cleanly suppresses the `RuntimeWarning: Proactor event loop does not implement add_reader`.
3. **Fine-Grained Error Trapping**: Any cell failure raises `nbconvert.preprocessors.CellExecutionError`, exposing the exact cell index, offending code line, and stack trace.

---

## 3. Cell-by-Cell Content and Code Specification

The notebook contains 42 cells (index 0 to 41). The required changes are itemized below:

### 3.1 Code Cells

| Cell Index | ID | Purpose | Required Implementation / Replacement | Expected Output |
|---|---|---|---|---|
| Cell 2 | `373d32c9` | Environment setup | `%pip -q install Pillow` | `Note: you may need to restart...` |
| Cell 3 | `21e667ce` | Image discovery | Unchanged: verifies `image_dir = Path("Images")` | `Images found: 6` |
| Cell 6 | `cbd260f5` | Section 1 EXIF starter | Unchanged: extracts `Brain-Channel.png` EXIF | `ImageDescription : LATERAL: ...` |
| Cell 8 | `8e208ddf` | Section 1 EXIF student | Inspect `Activation.png` EXIF and Sub-IFD (tag 37510) | `Sub-IFD tags: 1`<br>`UserComment : b'ASCII\x00\x00\x00VULN: ...'` |
| Cell 10 | `a6fd6213` | Section 2 PNG starter | Unchanged: inspects `Brain.png` info dict | `Software : RECON: ...` |
| Cell 12 | `8d8e3b22` | Section 2 PNG student | Inspect `Chemicals.png` info dict | `ImageDescription : EXPLOIT: ...` |
| Cell 14 | `ecce3ffb` | Section 3 XMP starter | Unchanged: inspects `Dopamine.png` XMP packet | Raw XMP with `<exif:MakerNote>PERSIST: ...` |
| Cell 17 | `6c877333` | Section 4 Base64 starter | Unchanged: decodes example string | `Hello` |
| Cell 19 | `ba3acb4c` | Section 4 Base64 student | Decode `Music.png` Base64 Copyright tag | `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` |
| Cell 22 | `450aac19` | Inv. 1: Activation.png | Strip 8-byte ASCII prefix from Sub-IFD UserComment | `Recovered: VULN: Identify unpatched CVE-2024-XXXX in web gateway.` |
| Cell 24 | `c07cc67d` | Inv. 2: Brain-Channel.png| Extract tag 270 (ImageDescription) | `Recovered: LATERAL: Pivot to internal Domain Controller using Mimikatz.` |
| Cell 26 | `fd3dcade` | Inv. 3: Brain.png | Extract PNG text chunk `Software` | `Recovered: RECON: Perform DNS harvesting and Subdomain enumeration.` |
| Cell 28 | `d705ebdf` | Inv. 4: Chemicals.png | Extract PNG text chunk `ImageDescription` | `Recovered: EXPLOIT: Deploy SQL Injection payload to bypass WAF.` |
| Cell 30 | `a28bc2d3` | Inv. 5: Dopamine.png | Parse XML XMP packet and extract `MakerNote` text | `Recovered: PERSIST: Establish reverse shell via obfuscated cron job.` |
| Cell 32 | `d8df5cb3` | Inv. 6: Music.png | Base64 decode EXIF tag 33432 / Copyright | `Recovered: EXFIL: Tunnel compressed database dump via DNS Covert Channel.` |
| Cell 35 | `e97d9b27` | Step 7A starter loop | Unchanged: prints all image formats and field counts | 6 lines of `filename → PNG \| fields: N` |
| Cell 37 | `f983c05b` | Step 7B starter row | Unchanged: prints single dictionary row | `{'filename': 'Brain.png', ...}` |
| Cell 39 | `741a9382` | Step 7C complete scanner | Multi-layer scanner iterating 6 images, scoring risk, writing `metadata_report.csv` | `Saved 6 rows to metadata_report.csv`<br>Summary printout for each image |

### 3.2 Markdown Cells Requiring Completion

#### Cell 20 (ID `c655c95c`) — Evidence Table
Replace empty table cells with accurate metadata classifications:
```markdown
| Image | Metadata type / field | Decoding needed? | Partial secret recovered |
|---|---|---|---|
| Activation.png | EXIF Sub-IFD / UserComment (Tag 37510) | Yes (Strip 8-byte ASCII prefix `ASCII\x00\x00\x00`) | VULN: Identify unpatched CVE-2024-XXXX in web gateway. |
| Brain-Channel.png | EXIF Primary IFD0 / ImageDescription (Tag 270) | No (Plaintext ASCII) | LATERAL: Pivot to internal Domain Controller using Mimikatz. |
| Brain.png | PNG Native Chunk / `tEXt` (`Software` key) | No (Plaintext UTF-8 string) | RECON: Perform DNS harvesting and Subdomain enumeration. |
| Chemicals.png | PNG Native Chunk / `tEXt` (`ImageDescription` key) | No (Plaintext UTF-8 string) | EXPLOIT: Deploy SQL Injection payload to bypass WAF. |
| Dopamine.png | PNG Native Chunk / `iTXt` (XMP XML `<exif:MakerNote>`) | Yes (XML tag extraction / strip BOM) | PERSIST: Establish reverse shell via obfuscated cron job. |
| Music.png | EXIF Primary IFD0 & PNG `tEXt` / `Copyright` (Tag 33432) | Yes (RFC 4648 Base64 decoding) | EXFIL: Tunnel compressed database dump via DNS Covert Channel. |
```

#### Cell 33 (ID `86d441f0`) — Narrative Secret Reconstruction
Replace placeholder template `__________` with exact reconstructed stages and comprehensive Cyber Kill Chain ordering rationale:
1. `RECON: Perform DNS harvesting and Subdomain enumeration.` (Brain.png)
2. `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` (Activation.png)
3. `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` (Chemicals.png)
4. `PERSIST: Establish reverse shell via obfuscated cron job.` (Dopamine.png)
5. `LATERAL: Pivot to internal Domain Controller using Mimikatz.` (Brain-Channel.png)
6. `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` (Music.png)

*Reasoning must explain that the sequence strictly mirrors the Lockheed Martin Cyber Kill Chain and MITRE ATT&CK Enterprise lifecycle, and note that sorting by alphabetical image name produces an invalid sequence.*

#### Cell 40 (ID `a4a4d581`) — Reflection Questions
Append comprehensive, academic responses exceeding 150 words (currently tested at 1,093 words) covering:
1. Architectural reasons why `getexif()` returns 0 tags while metadata exists (PNG `tEXt`/`zTXt`/`iTXt` chunks, embedded XMP XML packets, and nested EXIF Sub-IFDs).
2. Theoretical and practical distinction between encoding (Base64 transport transformation without keys) and encryption (cryptographic confidentiality requiring keys).
3. Digital forensics principles regarding read-only evidence preservation, cryptographic hashing (SHA-256), and chain of custody compliance.
4. Evidentiary limitations of standalone metadata and the necessity of multi-source corroboration (network flow, WAF/web logs, EDR audit trails, and Active Directory event logs).
5. Methodological continuity with automated port scanning (Lab 4) and vulnerability scanner heuristic scoring (Lab 5).

---

## 4. Verification Check Formulation

To guarantee complete compliance with Milestone 2 acceptance criteria, the following 7-point verification suite must be executed against `Lab6/Lab6.ipynb`:

| Check ID | Verification Target | Assertion / Pass Condition | Invalidation Condition |
|---|---|---|---|
| **V1** | JSON Schema & Version | `nb_data["nbformat"] == 4`, `nbformat_minor >= 2` | Parse error, corrupted JSON, or non-v4 schema |
| **V2** | Execution Counts | For all non-empty code cells: `execution_count is not None` and `isinstance(execution_count, int)` and `execution_count > 0` | Any code cell has `null` execution count or missing count |
| **V3** | Zero Error Outputs | For all code cells: no output has `output_type == "error"` | Any traceback, unhandled exception (`ename` exists) |
| **V4** | Keyword Fidelity | Aggregate code cell outputs contain all 6 stage prefixes: `RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:` | Any missing attack stage keyword |
| **V5** | Placeholder Elimination | Substring `"__________"` does not appear anywhere in notebook JSON | Any remnant `__________` placeholder |
| **V6** | Evidence Documentation | Markdown cells contain all 6 image filenames (`Activation.png`, etc.) | Any image missing from evidence log |
| **V7** | Reflection Depth | Cell with `"Reflection questions"` has `len(content.split()) > 150` | Word count <= 150 or unanswered prompts |
| **V8** | E2E Pytest Suite | Run `pytest Lab6/test_e2e_lab6.py`: 69 tests pass, 0 fail, 0 errors, exactly 13 skipped (Docx only) | Less than 69 passing tests, or any failure |

---

## 5. Test Suite State Transition Matrix

| Test ID | Test Name | Pre-M2 Status | Post-M2 Status | Milestone Responsible |
|---|---|---|---|---|
| `test_t1_f6_27` | Notebook all cells executed | SKIPPED | **PASSED** | M2 |
| `test_t1_f6_28` | Notebook no unhandled exceptions | SKIPPED | **PASSED** | M2 |
| `test_t1_f6_29` | Notebook evidence table populated | SKIPPED | **PASSED** | M2 |
| `test_t1_f6_30` | Notebook reflection questions answered | SKIPPED | **PASSED** | M2 |
| `test_t2_f6_62` | Notebook no empty code cells | SKIPPED | **PASSED** | M2 |
| `test_t2_f6_64` | Notebook execution count positive integers | SKIPPED | **PASSED** | M2 |
| `test_t2_f6_65` | Notebook cell output text fidelity | SKIPPED | **PASSED** | M2 |
| `test_t3_75` | Notebook outputs match reconstructed narrative | SKIPPED | **PASSED** | M2 |
| `test_t4_81` | Notebook headless CI/CD pipeline | SKIPPED | **PASSED** | M2 |
| `test_t1_f7_31-35` | Word doc feature tests (5 tests) | SKIPPED | SKIPPED | M3 (Docx) |
| `test_t2_f7_66-70` | Word doc boundary tests (5 tests) | SKIPPED | SKIPPED | M3 (Docx) |
| `test_t3_76-77` | Word doc cross-feature tests (2 tests) | SKIPPED | SKIPPED | M3 (Docx) |
| `test_t4_82` | Full deliverable audit (1 test) | SKIPPED | SKIPPED | M4 (Final) |

**Total passing tests progression**: `60/82` (Pre-M2) → **`69/82`** (Post-M2).
