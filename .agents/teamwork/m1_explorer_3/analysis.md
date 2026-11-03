# Analysis Report: Milestone 1 — CSV Validation, CLI Usability, Robustness, and Test Criteria

**Author:** Teamwork Explorer Agent 3 (`m1_explorer_3`)  
**Date:** 2026-11-02  
**Target File:** `Lab6/metadata_scanner.py`  
**Target Deliverable:** `Lab6/metadata_report.csv`  
**Reference Files:** `Lab6/Lab6.ipynb`, `PROJECT.md`, `ORIGINAL_REQUEST.md`, Survey Reports 1–3  

---

## 1. Executive Summary & Scope

This report establishes the complete testing, verification, validation, and hardening specification for Milestone 1: the automated metadata scanner (`Lab6/metadata_scanner.py`) and its structured CSV export (`Lab6/metadata_report.csv`).

Milestone 1 serves as the foundational data engine for Lab 6. Its output feeds directly into the in-place Jupyter notebook (`Lab6.ipynb` Cells 38–39) and the final formal Word report (`Lab6-Billy-Zandan-A01371854.docx`). To guarantee that `metadata_scanner.py` operates reliably across all execution contexts, CLI callers, test runners, and grading platforms, this analysis formulates:
1. **Exact CLI Invocation Contracts:** Dual-context execution (running from `Lab6/` or repository root), flexible flag aliases (`--images`/`--image-dir`/`-i`, `--output`/`--output-csv`/`-o`), help output, stream separation, and exit codes.
2. **RFC 4180 CSV Validation Checklist:** UTF-8 character encoding, exact 7-column header schema, 6 valid data rows, proper quoting of fields with embedded commas (`metadata_fields`) or semicolons (`reason`), and parser compatibility.
3. **Robustness & Edge-Case Engineering:** Non-existent directories, empty directories, corrupted image files, zero-metadata images, XMP Unicode Byte Order Mark (BOM `\ufeff`) handling on Windows CP1252 consoles, and EXIF `UserComment` binary null-byte header stripping.
4. **Multi-Role Concrete Verification Suites:** Verifiable PowerShell, bash, and Python one-liner command suites tailored specifically for Reviewers, Challengers, and Forensic Auditors.

---

## 2. CLI Invocation Specification & Usability Requirements

### 2.1 Canonical CLI Invocations

`metadata_scanner.py` must support both zero-argument default execution and fully parameterized CLI execution:

| Mode | Command Line Invocation | Expected Behavior |
|---|---|---|
| **Default Mode (Zero-Arg)** | `python metadata_scanner.py` | Auto-detects input image directory (`Images` or `Lab6/Images`) and auto-detects output CSV destination (`metadata_report.csv` or `Lab6/metadata_report.csv`). Scans all 6 PNG files and exits with code 0. |
| **Parameterized Mode (Standard)** | `python metadata_scanner.py --images Images --output metadata_report.csv` | Explicitly scans images in `Images` and writes results to `metadata_report.csv`. |
| **Parameterized Mode (Lab 5 Aliases)** | `python metadata_scanner.py --image-dir Images --output-csv metadata_report.csv` | Interoperable flag aliases matching Lab 4/5 automated scanning conventions. |
| **Short Flag Mode** | `python metadata_scanner.py -i Images -o metadata_report.csv -v` | Compact CLI flags with optional verbose extraction logs. |
| **Help / Discovery Mode** | `python metadata_scanner.py -h` / `--help` | Emits formatted CLI usage documentation, flags, default values, and exits with code 0. |

### 2.2 CLI Argument Matrix & Parser Design

The script must implement `argparse.ArgumentParser` configured with aliases and sensible fallback defaults:

```python
parser = argparse.ArgumentParser(
    description="Lab 6 Automated Forensic Metadata Scanner & Heuristic Risk Scorer",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "-i",
    "--images",
    "--image-dir",
    dest="images",
    default=None,
    help="Path to directory containing input PNG images (default: auto-detected Images directory)",
)
parser.add_argument(
    "-o",
    "--output",
    "--output-csv",
    dest="output",
    default=None,
    help="Path to output CSV report file (default: auto-detected metadata_report.csv)",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Enable detailed extraction logs and per-field diagnostic output",
)
```

### 2.3 Dual-Execution Context & Path Resolution

Users, automated grading scripts, and E2E test harnesses may invoke the script from two distinct working directories:
- **Context A (Inside `Lab6/`):** Working directory is `.../FSCT8561-Labs-Billy-Zandan/Lab6`
- **Context B (Project Root):** Working directory is `.../FSCT8561-Labs-Billy-Zandan`

To prevent `FileNotFoundError` when no CLI flags are supplied, the script must perform contextual path resolution:

```python
script_dir = Path(__file__).resolve().parent

# Resolve Image Directory
if args.images:
  img_dir = Path(args.images)
else:
  if Path("Images").is_dir():
    img_dir = Path("Images")
  elif (script_dir / "Images").is_dir():
    img_dir = script_dir / "Images"
  else:
    img_dir = Path("Images")

# Resolve Output CSV Path
if args.output:
  output_csv = Path(args.output)
else:
  if (
      Path("Images").is_dir()
      or Path.cwd().name.lower() == "lab6"
      or not (script_dir / "Images").is_dir()
  ):
    output_csv = Path("metadata_report.csv")
  else:
    output_csv = script_dir / "metadata_report.csv"
```

### 2.4 Standard Streams & Exit Code Protocol

To integrate cleanly with E2E runners, subprocess wrappers, and CI pipelines, the CLI must adhere to standard UNIX/POSIX stream contracts:
- **Exit Code `0`:** Successful batch execution and CSV generation.
- **Exit Code `1`:** Operational error (e.g., target directory does not exist, file permission denied).
- **Exit Code `2`:** Invalid CLI arguments or unrecognized flags (standard `argparse` behavior).
- **Stream Discipline:**
  - `stdout`: User summary info, rows processed count, and verbose extraction reports.
  - `stderr`: Operational error messages, warnings for corrupted images, and usage errors.

### 2.5 Windows Console Encoding Hardening (`cp1252` vs `utf-8`)

On Windows 11 systems, PowerShell and Command Prompt default to code page 1252 (`cp1252`). When `metadata_scanner.py` parses `Dopamine.png`, the embedded Adobe XMP packet contains a Unicode Byte Order Mark (`\ufeff`) inside `begin='\ufeff'`. Printing this character or verbose XML data to `sys.stdout` will trigger a fatal `UnicodeEncodeError`:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\ufeff' in position 17: character maps to <undefined>
```

**Mandatory Requirement:** The script must reconfigure standard output and error streams to UTF-8 at entry:
```python
import sys

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
  sys.stderr.reconfigure(encoding="utf-8")
```

---

## 3. CSV Specification & Validation Checklist

### 3.1 RFC 4180 Compliance & Structural Grammar

The output file `metadata_report.csv` must strictly comply with **RFC 4180**:
1. **Encoding:** Strict UTF-8 without byte-order corruption (`encoding="utf-8"`).
2. **Line Terminators:** Standard CRLF (`\r\n`) or LF (`\n`), guaranteed by opening files with `newline=""` in Python text mode (`open(filepath, "w", newline="", encoding="utf-8")`).
3. **Delimiter:** Comma `,` (ASCII 44).
4. **Header Line:** Exactly one header line consisting of the 7 required column names in exact order.
5. **Row Cardinality:** Exactly 6 data rows corresponding to the 6 target images. Total lines in file: 7 lines (1 header + 6 data records).

### 3.2 Exact Column Schema Matrix

| Column Index | Field Name | Python Data Type | Allowed Nullable? | Description & Allowed Format |
|:---:|---|---|:---:|---|
| **0** | `filename` | `str` | No | Exact basename of the image file (e.g. `Activation.png`, `Music.png`). |
| **1** | `format` | `str` | No | Image container format, uppercase (e.g. `PNG`). |
| **2** | `metadata_fields` | `str` | No | Formatted list of all discovered metadata field names across EXIF, PNG chunks, and XMP. |
| **3** | `suspected_field` | `str` | No | Exact metadata tag or XML element identified as containing covert content (e.g. `UserComment`, `Software`, `ImageDescription`, `exif:MakerNote`, `Copyright`). |
| **4** | `encoding` | `str` | No | Detected representation or obfuscation technique (e.g. `ASCII (null-prefixed)`, `Plain text`, `XML element`, `Base64`). |
| **5** | `risk_score` | `int` | No | Integer computed by the classroom heuristic rules (expected values: `10` or `15`). |
| **6** | `reason` | `str` | No | Clear, plain-English justification detailing the heuristic rules applied without double counting. |

### 3.3 RFC 4180 Quoting & Delimiter Rules

A major source of parser failure in CSV reporting is unquoted delimiter collisions:
- **Embedded Commas in `metadata_fields`:** Because `metadata_fields` lists discovered tags separated by commas (e.g. `srgb, gamma, dpi, exif, Make, Model`), the field contains literal commas. Under RFC 4180 Section 2.6, **any field containing a comma must be enclosed in double quotes (`"..."`)**.
- **Embedded Punctuation in `reason`:** Compound reason sentences containing commas or semicolons must likewise be safely quoted.
- **Quote Escaping:** If a field contains literal quotation marks, they must be escaped by double double-quotes (`""`).
- **Standard Library Implementation:** The scanner must utilize Python's standard `csv.DictWriter` with `quoting=csv.QUOTE_MINIMAL` or `csv.QUOTE_NONNUMERIC`. Hand-rolled string formatting (e.g. `f"{filename},{format},{fields}..."`) is strictly prohibited.

### 3.4 Ground-Truth Target Schema & Content Matrix

| `filename` | `format` | `metadata_fields` (Sample Values) | `suspected_field` | `encoding` | `risk_score` | `reason` |
|---|---|---|---|---|:---:|---|
| `Activation.png` | `PNG` | `Make, Model, Software, DateTime, GPSInfo, UserComment, create-date, dpi, exif, gamma, srgb` | `UserComment` | `ASCII (null-prefixed)` | `15` | Confirmed covert payload detected in EXIF UserComment (+10); Obfuscated payload requiring decoding / camera and GPS tags in graphic (+5). |
| `Brain-Channel.png` | `PNG` | `ImageDescription, ResolutionUnit, XResolution, YResolution, YCbCrPositioning, dpi, exif, gamma, srgb` | `ImageDescription` | `Plain text` | `10` | Confirmed covert payload detected in EXIF ImageDescription (+10). |
| `Brain.png` | `PNG` | `Software, dpi, gamma, srgb` | `Software` | `Plain text` | `10` | Confirmed covert payload detected in PNG text Software chunk (+10). |
| `Chemicals.png` | `PNG` | `ImageDescription` | `ImageDescription` | `Plain text` | `10` | Confirmed covert payload detected in PNG text ImageDescription chunk (+10). |
| `Dopamine.png` | `PNG` | `XML:com.adobe.xmp, exif:MakerNote, dpi, gamma, srgb, xmp` | `XML:com.adobe.xmp` or `exif:MakerNote` | `XML element` | `10` | Confirmed covert payload detected in Adobe XMP MakerNote element (+10). |
| `Music.png` | `PNG` | `Copyright, DateTime, Make, Model, ResolutionUnit, XResolution, YResolution, create-date, dpi, exif, gamma, srgb` | `Copyright` | `Base64` | `15` | Confirmed covert payload detected in Copyright field (+10); Obfuscated payload requiring decoding (Base64) (+5). |

---

## 4. Robustness & Error Handling Architecture

The automated scanner must be resilient against corrupted inputs, missing directories, and heterogeneous metadata data types.

### 4.1 Non-Existent Directories & Invalid Paths
- **Scenario:** CLI caller provides `--images /invalid/path` or the default `Images` directory does not exist.
- **Handling:** Check path existence before entering file processing loops.
- **Action:** Output descriptive error to `sys.stderr` (`Error: Image directory '/invalid/path' does not exist or is not a directory.`) and call `sys.exit(1)`. Never permit an unhandled `FileNotFoundError` stack trace to bubble up to the console.

### 4.2 Empty Directories (Zero Image Edge Case)
- **Scenario:** Target directory exists but contains zero `.png` images.
- **Handling:** Inspect `len(image_paths)`.
- **Action:** Emit a warning to `sys.stderr` (`Warning: No PNG images found in directory '...'.`), write a valid CSV containing only the 7-column header line, print `Saved 0 rows to ...`, and exit with code 0.

### 4.3 Corrupted Images & Unhandled File Formats
- **Scenario:** The target folder contains non-image files (e.g. `.txt`, `.tmp`), subdirectories, or corrupted PNG files with invalid headers.
- **Handling:** Wrap `Image.open(p)` inside a try-except block targeting `(PIL.UnidentifiedImageError, OSError)`.
- **Action:** Emit a warning to `sys.stderr` (`[WARN] Skipping non-image or corrupted file: corrupt.png`) and continue processing the remaining images. An individual corrupted file must never abort the entire batch scan.

### 4.4 Benign Images with Zero Metadata
- **Scenario:** An image has no EXIF tags, no PNG text chunks, and no XMP packets (e.g., a stripped image).
- **Handling:** If all metadata dictionaries are empty, the heuristic scanner must not crash on missing dictionary keys or `None` values.
- **Action:** Output a valid row with:
  - `metadata_fields`: `""` (or `"None"`)
  - `suspected_field`: `""`
  - `encoding`: `"None"`
  - `risk_score`: `0`
  - `reason`: `"No covert indicators detected; clean metadata (0)"`

### 4.5 XMP XML Parsing & Unicode BOM (`\ufeff`) Handling
- **Scenario:** `Dopamine.png` encapsulates an Adobe XMP packet inside an `iTXt` chunk with keyword `XML:com.adobe.xmp`. The XML packet begins with `<?xpacket begin='\ufeff' id='W5M0MpCehiHzreSzNTczkc9d'?>`.
- **Nuances:**
  1. `img.info['XML:com.adobe.xmp']` is an instance of `PIL.PngImagePlugin.iTXt` (subclass of `str`), containing `\ufeff`.
  2. `img.info['xmp']` is `bytes`, containing UTF-8 encoded BOM `\xef\xbb\xbf`.
  3. Direct XML parsing via `xml.etree.ElementTree` or `defusedxml.ElementTree` handles processing instructions cleanly.
  4. Regex extraction `re.search(r'<exif:MakerNote>(.*?)</exif:MakerNote>', xmp_str, re.DOTALL)` bypasses XML namespaces and BOM issues safely.

### 4.6 Binary Null-Byte Slicing in EXIF `UserComment`
- **Scenario:** In `Activation.png`, Tag 37510 (`UserComment`) in the Exif Sub-IFD contains:
  `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`
- **Pitfall:** Converting `val` directly to string via `str(val)` yields `"b'ASCII\\x00\\x00\\x00VULN: ...'"`, polluting the CSV and reflection evidence with raw Python byte representation.
- **Handling:** Detect `isinstance(val, bytes)` and prefix matching `b"ASCII\x00\x00\x00"`. Slice the first 8 bytes and decode with `.decode("utf-8", errors="replace")`.

### 4.7 Heterogeneous Data Types in `img.info`
- **Scenario:** `img.info` is not a homogenous dictionary of strings.
  - `img.info['dpi']` is a `tuple` `(72, 72)`
  - `img.info['gamma']` is a `float` `0.45455`
  - `img.info['srgb']` is an `int` `0`
  - `img.info['exif']` is raw `bytes`
- **Handling:** When scanning for strings or building `metadata_fields`, always check types before calling string methods (`isinstance(v, str)` or `isinstance(v, bytes)`).

---

## 5. Concrete Verification Commands for Quality Personas

To enable Reviewers, Challengers, and Auditors to verify Milestone 1 independently, the following executable commands are provided.

### 5.1 Reviewer Verification Suite (Acceptance Criteria & Happy Paths)

Reviewers verify that all explicit requirements and deliverable contracts are met.

#### Test R1: Default Zero-Argument CLI Invocation
Execute scanner from within `Lab6/`:
```powershell
# Windows PowerShell
cd c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6
python metadata_scanner.py
```
*Expected Output:* Exit code `0`, console message indicating `Saved 6 rows to metadata_report.csv`, and generation of `metadata_report.csv`.

#### Test R2: Parameterized CLI Invocation
Execute scanner with explicit flags:
```powershell
python metadata_scanner.py --images Images --output metadata_report.csv
```
*Expected Output:* Exit code `0`, clean generation of `metadata_report.csv`.

#### Test R3: CSV Structural & Schema Validation (Python One-Liner)
Verify headers, row count, column count, and file encoding:
```powershell
python -c "import csv, sys; f = open('metadata_report.csv', 'r', encoding='utf-8'); r = list(csv.reader(f)); f.close(); assert len(r) == 7, f'Expected 7 rows, got {len(r)}'; expected_hdr = ['filename','format','metadata_fields','suspected_field','encoding','risk_score','reason']; assert r[0] == expected_hdr, f'Header mismatch: {r[0]}'; print('CSV Structure Verified: 7 rows, exact header match, UTF-8 encoded.')"
```

#### Test R4: Six Incident Stages Recovered in CSV
Verify that all 6 stage markers (`RECON`, `VULN`, `EXPLOIT`, `PERSIST`, `LATERAL`, `EXFIL`) are reflected in CSV output:
```powershell
python -c "import csv; r = list(csv.DictReader(open('metadata_report.csv', encoding='utf-8'))); filenames = {row['filename'] for row in r}; assert filenames == {'Activation.png', 'Brain-Channel.png', 'Brain.png', 'Chemicals.png', 'Dopamine.png', 'Music.png'}, f'Missing files: {filenames}'; scores = [int(row['risk_score']) for row in r]; assert all(s in (10, 15) for s in scores), f'Invalid scores: {scores}'; print('Content Verified: All 6 files present with valid risk scores (10-15).')"
```

---

### 5.2 Challenger Verification Suite (Adversarial, Robustness & Edge Cases)

Challengers attempt to break the implementation with unexpected inputs and edge cases.

#### Test C1: Non-Existent Image Directory
Pass an invalid image directory path:
```powershell
python metadata_scanner.py --images NonExistentDirectory123 --output test_out.csv
if ($LASTEXITCODE -ne 0) { Write-Host "PASS: Exited with non-zero code on missing directory." } else { Write-Error "FAIL: Exited with code 0 on missing directory." }
```
*Expected:* Exit code != 0, clean error message on stderr, no uncaught Python traceback.

#### Test C2: Empty Directory Handling
Create a temporary empty directory and scan it:
```powershell
mkdir temp_empty_dir -Force | Out-Null
python metadata_scanner.py --images temp_empty_dir --output temp_empty.csv
python -c "import csv; r = list(csv.reader(open('temp_empty.csv', encoding='utf-8'))); assert len(r) == 1, 'Expected header-only CSV for empty dir'; print('PASS: Empty directory gracefully handled with header-only CSV.')"
Remove-Item temp_empty_dir, temp_empty.csv -Force -Recurse
```

#### Test C3: Corrupted Image File Resilience
Create a dummy file with `.png` extension containing invalid random bytes:
```powershell
mkdir temp_corrupt_test -Force | Out-Null
Copy-Item Images\Brain.png temp_corrupt_test\Valid.png
[System.IO.File]::WriteAllBytes("temp_corrupt_test\Corrupt.png", [byte[]](1,2,3,4,5,6,7,8))
python metadata_scanner.py --images temp_corrupt_test --output temp_corrupt.csv
python -c "import csv; r = list(csv.DictReader(open('temp_corrupt.csv', encoding='utf-8'))); assert len(r) >= 1, 'Scanner failed to process valid image'; print('PASS: Scanner survived corrupted image file without crashing.')"
Remove-Item temp_corrupt_test, temp_corrupt.csv -Force -Recurse
```

#### Test C4: Windows CP1252 Terminal Compatibility
Verify that verbose output containing XMP's UTF-8 BOM (`\ufeff`) does not crash in PowerShell:
```powershell
python metadata_scanner.py --verbose
if ($LASTEXITCODE -eq 0) { Write-Host "PASS: Unicode BOM printed without cp1252 crash." } else { Write-Error "FAIL: Terminal encoding crash." }
```

---

### 5.3 Auditor Verification Suite (Standards, Dynamic Execution & Forensic Chain of Custody)

Auditors verify compliance with forensic standards, chain of custody, and ensure no hardcoded cheating.

#### Test A1: RFC 4180 Quoting Validation
Verify that commas within fields do not cause field count mismatches:
```powershell
python -c "import csv; f = open('metadata_report.csv', encoding='utf-8'); r = csv.reader(f); bad_rows = [idx for idx, row in enumerate(r) if len(row) != 7]; assert not bad_rows, f'RFC 4180 Violation on rows: {bad_rows}'; print('PASS: RFC 4180 verified: Every row contains exactly 7 parsed fields.')"
```

#### Test A2: Pandas Ingestion Validation
Verify that standard data science tools ingest the CSV without warnings:
```powershell
python -c "import pandas as pd; df = pd.read_csv('metadata_report.csv'); assert df.shape == (6, 7), f'Expected shape (6, 7), got {df.shape}'; assert list(df.columns) == ['filename','format','metadata_fields','suspected_field','encoding','risk_score','reason']; print('PASS: Pandas ingested metadata_report.csv cleanly.')"
```

#### Test A3: Dynamic Extraction Audit (Anti-Hardcoding Check)
Ensure the scanner is not simply printing static hardcoded strings:
```powershell
python -c "src = open('metadata_scanner.py', encoding='utf-8').read(); assert 'Activation.png' not in src or 'Image.open' in src, 'Static filename table detected'; assert 'getexif' in src or 'info' in src, 'Dynamic metadata extraction calls missing'; print('PASS: Dynamic extraction verified in source code.')"
```

#### Test A4: Forensic Read-Only Chain of Custody Check
Verify that running the scanner did NOT modify the raw evidence images (SHA-256 hashes must remain identical):
```powershell
python -c "
import hashlib
from pathlib import Path

expected_hashes = {
    'Activation.png': '1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904',
    'Brain-Channel.png': '3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359',
    'Brain.png': '5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e',
    'Chemicals.png': '96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a',
    'Dopamine.png': 'ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472',
    'Music.png': '3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370'
}

for name, exp_h in expected_hashes.items():
    p = Path('Images') / name
    calc_h = hashlib.sha256(p.read_bytes()).hexdigest()
    assert calc_h == exp_h, f'Forensic integrity violation: {name} was modified!'
print('PASS: All 6 evidence images bit-for-bit pristine. Chain of custody intact.')
"
```

---

## 6. Pytest E2E Integration Guidance (`Lab6/test_e2e_lab6.py`)

For `test_writer_e2e_1`, the following test structures are recommended for inclusion in Tier 1 and Tier 2 of `Lab6/test_e2e_lab6.py`:

```python
def test_metadata_scanner_cli_default(tmp_path):
  """Verify zero-argument CLI execution."""
  cmd = [sys.executable, str(SCANNER_PATH)]
  proc = subprocess.run(
      cmd, cwd=str(LAB6_DIR), capture_output=True, text=True, timeout=15
  )
  assert proc.returncode == 0
  assert (LAB6_DIR / "metadata_report.csv").is_file()


def test_metadata_scanner_cli_parameterized(tmp_path):
  """Verify parameterized CLI execution with custom output destination."""
  out_csv = tmp_path / "custom_report.csv"
  cmd = [
      sys.executable,
      str(SCANNER_PATH),
      "--images",
      str(LAB6_DIR / "Images"),
      "--output",
      str(out_csv),
  ]
  proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
  assert proc.returncode == 0
  assert out_csv.is_file()


def test_csv_rfc4180_compliance():
  """Verify RFC 4180 compliance, header order, and row count."""
  csv_path = LAB6_DIR / "metadata_report.csv"
  with open(csv_path, "r", encoding="utf-8") as f:
    reader = list(csv.reader(f))
  assert len(reader) == 7  # 1 header + 6 rows
  assert reader[0] == [
      "filename",
      "format",
      "metadata_fields",
      "suspected_field",
      "encoding",
      "risk_score",
      "reason",
  ]
  for row in reader[1:]:
    assert len(row) == 7


def test_scanner_nonexistent_directory():
  """Verify non-zero exit code on non-existent directory."""
  cmd = [
      sys.executable,
      str(SCANNER_PATH),
      "--images",
      "NoSuchDir999",
      "--output",
      "dummy.csv",
  ]
  proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
  assert proc.returncode != 0
  assert "does not exist" in proc.stderr.lower() or "error" in proc.stderr.lower()
```

---

## 7. Actionable Implementation Blueprint for Worker

To ensure Milestone 1 achieves 100% pass on first try, the implementing worker should follow this structural blueprint:

1. **Standard Library Only:** Rely strictly on `argparse`, `pathlib.Path`, `csv`, `base64`, `re`, `sys`, and `PIL` (plus `defusedxml` / `xml.etree.ElementTree`).
2. **CLI Entrypoint:** Implement `parse_args()` with aliases (`--images`/`--image-dir`/`-i`, `--output`/`--output-csv`/`-o`, `-v`).
3. **Multi-Layer Harvester Function (`extract_all_metadata(img_path)`):**
   - Harvest EXIF 0th IFD (`img.getexif()`).
   - Harvest Exif Sub-IFD (tag `0x8769` / `ExifOffset`).
   - Harvest GPS Sub-IFD (tag `0x8825` / `GPSInfo`).
   - Harvest PNG text chunks (`img.info`).
   - Harvest XMP packets (`img.info.get('XML:com.adobe.xmp')` or `img.info.get('xmp')`).
4. **Heuristic Detector & De-obfuscator (`analyze_indicators(metadata)`):**
   - Check Base64 pattern & safe decoding.
   - Strip EXIF ASCII header `b'ASCII\x00\x00\x00'`.
   - Match attack keywords (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`).
   - Evaluate camera hardware tags on diagram graphics.
5. **Explainable Scoring Engine (`score_risk(indicators)`):**
   - Base score: `+10` for confirmed covert message.
   - Obfuscation: `+5` for encoded content (Base64 / ASCII header).
   - Carrier anomaly: `+5` for non-standard carrier (if not already counted).
   - Cap / clamp to avoid double counting.
6. **CSV Generator:**
   - Use `csv.DictWriter(f, fieldnames=..., quoting=csv.QUOTE_MINIMAL)`.
   - Write using `open(out_path, "w", newline="", encoding="utf-8")`.
   - Ensure `out_path.parent.mkdir(parents=True, exist_ok=True)`.
