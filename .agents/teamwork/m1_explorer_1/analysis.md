# Technical Design & Architecture Specification: Lab 6 Metadata Scanner (`metadata_scanner.py`)

**Document ID:** `M1-ARCH-METADATA-SCANNER`  
**Author:** Teamwork Explorer Agent (`m1_explorer_1`)  
**Target Milestone:** Milestone 1 — Automated Scanner Architecture & Multi-Layer Extraction Flow  
**Target File:** `Lab6/metadata_scanner.py`  
**Associated Deliverables:** `Lab6/metadata_report.csv`, `Lab6/Lab6.ipynb` (Cells 34-39), `Lab6/Lab6-Billy-Zandan-A01371854.docx`

---

## 1. Executive Summary & Purpose

The objective of Milestone 1 is to formulate the technical architecture, data structures, multi-layer extraction pipeline, heuristic detection engine, and risk scoring logic for `Lab6/metadata_scanner.py`. 

In Lab 6 (*Covert Channels in Image Metadata*), six PNG images (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`) conceal fragments of a fictional cybersecurity incident narrative. These fragments are distributed across heterogeneous metadata layers (standard EXIF IFD0, nested EXIF Sub-IFDs, PNG text chunks, and embedded Adobe XMP XML packets) and obfuscated using varied techniques (raw strings, 8-byte ASCII headers, XML encapsulation, and RFC 4648 Base64).

`metadata_scanner.py` serves as the core automated audit engine for Lab 6. It must operate both as a standalone Command Line Interface (CLI) tool and as an importable Python module for notebook execution (`Lab6.ipynb`) and automated test suites. The scanner must inspect every image, uncover covert metadata, identify suspected fields and encodings, assign consistent, explainable heuristic risk scores without hardcoding, and output a compliant 7-column CSV report to `Lab6/metadata_report.csv`.

---

## 2. CLI Interface & Execution Specification

### 2.1 Command-Line Arguments

The CLI must provide a user-friendly interface using Python’s standard `argparse` module, supporting both flags and sensible default paths tailored to the Lab 6 project directory structure:

| Argument | Short Flag | Type | Default | Description |
|---|:---:|:---:|---|---|
| `--image-dir` | `-d` | `Path` / `str` | `Images` | Directory containing target PNG images. The script resolves this relative to the script location (`Lab6/Images`) or current working directory. |
| `--output-csv` | `-o` | `Path` / `str` | `metadata_report.csv` | Output file path for the CSV report (defaults to `metadata_report.csv` in the same directory as the script or current directory). |
| `--verbose` | `-v` | `bool` (flag) | `False` | Enables detailed stdout diagnostic output per image (listing all discovered fields, extracted payloads, and scoring rationale). |
| `--quiet` | `-q` | `bool` (flag) | `False` | Suppresses stdout summary table, displaying only fatal errors. |

### 2.2 Path Resolution Strategy

To ensure seamless execution whether invoked from the repository root (`python Lab6/metadata_scanner.py`), from within the `Lab6` directory (`python metadata_scanner.py`), or from a Jupyter notebook kernel:

```python
script_dir = Path(__file__).resolve().parent
# If default 'Images' directory doesn't exist relative to cwd, check relative to script_dir:
if not image_dir.exists() and (script_dir / image_dir).exists():
    image_dir = script_dir / image_dir

if not output_csv.is_absolute() and not output_csv.parent.exists():
    output_csv = script_dir / output_csv.name
```

### 2.3 Terminal & Environment Compatibility

Windows PowerShell and `cmd.exe` historically default to legacy code pages (e.g. `cp1252`), which can crash with `UnicodeEncodeError` when printing characters such as `→`, `\ufeff`, or degree symbols (`°`). The scanner must enforce UTF-8 stdout reconfiguration:

```python
import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
```

---

## 3. Multi-Layer Metadata Extraction Pipeline

Forensic analysis demonstrated that single-mechanism metadata extraction fails catastrophically on modern image sets (see Section 6 on EXIF limitations). `metadata_scanner.py` must implement a unified multi-layer pipeline:

```
                          ┌───────────────────────────┐
                          │    Target Image (.png)    │
                          └─────────────┬─────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
│     Layer 1 & 2:      │   │       Layer 3:        │   │       Layer 4:        │
│   EXIF Multi-IFD      │   │    PNG Text Chunks    │   │    Adobe XMP XML      │
│  (Pillow getexif /    │   │      (img.info)       │   │  (XML:com.adobe.xmp / │
│   exif.get_ifd())     │   │                       │   │   xmp in img.info)    │
└──────────┬────────────┘   └───────────┬───────────┘   └───────────┬───────────┘
           │                            │                           │
           │ • IFD0 Tags (270, 33432)   │ • tEXt / zTXt / iTXt      │ • Defused XML parsing
           │ • Exif Sub-IFD (0x8769)    │ • 'Software', 'Copyright' │ • Element iteration
           │   -> Tag 37510 UserComment │ • 'ImageDescription'      │ • Tag text extraction
           │ • GPS Sub-IFD (0x8825)     │                           │   (e.g. MakerNote)
           └────────────────────────────┼───────────────────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │   Consolidated Metadata Dict  │
                        │ & Field Inventory Collection  │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │   Heuristic Detection &       │
                        │   De-Obfuscation Engine       │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │   Explainable Risk Scoring    │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │   CSV Export & Summary Print  │
                        └───────────────────────────────┘
```

### Layer 1: EXIF Primary IFD0
- **Extraction API:** `img.getexif()`
- **Tag Translation:** `PIL.ExifTags.TAGS.get(tag_id, str(tag_id))`
- **Target Fields:**
  - Tag 270 (`ImageDescription`): Stores plaintext in `Brain-Channel.png`.
  - Tag 33432 (`Copyright`): Stores Base64 string in `Music.png`.
  - Tag 271 (`Make`), Tag 272 (`Model`), Tag 305 (`Software`), Tag 306 (`DateTime`), Tag 34665 (`ExifOffset`), Tag 34853 (`GPSInfo`).

### Layer 2: EXIF Sub-IFDs (Exif Sub-IFD & GPS IFD)
- **Extraction API:** `exif.get_ifd(0x8769)` (Exif Sub-IFD) and `exif.get_ifd(0x8825)` (GPS Sub-IFD).
- **Fallback for Legacy Pillow / Environments:** If `get_ifd` is unavailable or returns empty, check `img._getexif()` which returns a flattened tag dictionary containing sub-IFD entries.
- **Target Fields:**
  - Tag 37510 (`UserComment` / `0x9286`): Located inside `0x8769` in `Activation.png`. Holds `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`.
  - GPS IFD (`0x8825`): Holds GPS latitude, longitude, and reference tags in `Activation.png`.

### Layer 3: PNG Textual Metadata Chunks (`tEXt`, `zTXt`, `iTXt`)
- **Extraction API:** `img.info`
- **Data Filtering:** Non-string items (such as raw binary chunks under `'exif'`, integer color spaces, or resolution tuples under `'dpi'`) must be filtered safely:
  - Strings: directly inspected.
  - Bytes: checked for text or decoded safely.
- **Target Fields:**
  - `img.info['Software']`: Stores plaintext in `Brain.png` (`RECON: Perform DNS harvesting and Subdomain enumeration.`).
  - `img.info['ImageDescription']`: Stores plaintext in `Chemicals.png` (`EXPLOIT: Deploy SQL Injection payload to bypass WAF.`).
  - `img.info['Copyright']`: Stores Base64 string in `Music.png`.

### Layer 4: Adobe XMP XML Packets
- **Extraction API:** `img.info.get("XML:com.adobe.xmp")` or `img.info.get("xmp")`.
- **Parsing Strategy:**
  - If raw `bytes`, decode to UTF-8 with `errors="replace"`.
  - Parse using `defusedxml.ElementTree` (falling back to standard `xml.etree.ElementTree`).
  - Traverse all elements via `root.iter()`.
  - Strip RDF namespace URIs (e.g., `{http://ns.adobe.com/exif/1.0/}MakerNote` -> `MakerNote`).
  - Extract inner text for every non-empty XML node.
  - Regex fallback: `re.findall(r'<([^:>]+:)?([^>]+)>([^<]+)</', xmp_str)` to safeguard against malformed XML structures.
- **Target Fields:**
  - `<exif:MakerNote>`: Stores plaintext in `Dopamine.png` (`PERSIST: Establish reverse shell via obfuscated cron job.`).

---

## 4. De-Obfuscation & Heuristic Detection Engine

The detection engine examines all collected key-value pairs across the three containers to locate covert-channel indicators without hardcoding static filenames or pre-baked answers.

### 4.1 Threat Signature & Attack Lifecycle Keywords
A value (or decoded value) is classified as a confirmed covert-channel payload if it contains:
1. **Stage Marker Prefixes:** `RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`.
2. **Threat Activity Keywords:** `CVE-`, `Mimikatz`, `SQL Injection`, `WAF`, `cron job`, `DNS Covert Channel`, `DNS harvesting`, `Subdomain enumeration`, `reverse shell`, `Domain Controller`.

### 4.2 De-Obfuscation Handlers

#### 1. EXIF UserComment Header Stripping
- Standard EXIF specification mandates an 8-byte character identification code for tag 37510:
  - `b'ASCII\x00\x00\x00'` (ASCII)
  - `b'UNICODE\x00'` (Unicode)
  - `b'JIS\x00\x00\x00\x00\x00'` (JIS)
- **Heuristic:** If value starts with `b'ASCII\x00\x00\x00'`, strip the 8-byte prefix and decode the remaining bytes as UTF-8.
- **Detected Encoding:** `EXIF ASCII header / plain text` (or `ASCII (null-prefixed)`).

#### 2. RFC 4648 Base64 Detection & Decoding
- **Candidate Filter:**
  - Length >= 16 and divisible by 4.
  - Matches regex `^[A-Za-z0-9+/]+={0,2}$`.
  - Non-trivial ASCII distribution (Shannon entropy > 3.5 or valid text characteristics).
- **Verification:**
  - Call `base64.b64decode(candidate, validate=True)`.
  - Check whether decoded payload decodes cleanly as UTF-8.
  - Check whether decoded string is printable and contains threat keywords or word spaces.
- **Detected Encoding:** `Base64`.

#### 3. XML Encapsulation
- **Candidate Filter:** Value was extracted from an Adobe XMP XML tree (e.g. `XML:com.adobe.xmp`).
- **Detected Encoding:** `XML encapsulation / plain text` (or `XML element`).

#### 4. Plain Text
- Value requires no structural stripping or algorithmic decoding to read.
- **Detected Encoding:** `None (plain text)` (or `Plain text`).

---

## 5. Explainable Risk Scoring Engine & Ground Truth Model

### 5.1 Rubric Scoring Rules

Per `Lab6.ipynb` (Cell 409) and the grading rubric, risk scores must be calculated using consistent, explainable heuristics:

1. **Rule 1 — Confirmed Covert Message (+10 points):**  
   Assigned when a field contains verified incident narrative tokens (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`) or operational threat signatures.
2. **Rule 2 — Encoded/Obfuscated Payload (+5 points):**  
   Assigned when the payload was disguised using Base64 encoding or structural headers (EXIF ASCII null-prefixed header) requiring computational decoding.
3. **Rule 3 — Anomalous Metadata Indicator (+5 points):**  
   Assigned when metadata exhibits anomalous carrier behavior supported by evidence:
   - Hardware camera metadata (Nikon D750, Olympus OM-D) and GPS coordinates embedded inside a non-photographic graphic or diagram.
   - Attack instructions stored in non-standard descriptive fields (`Software`, `MakerNote`).
   - XMP packet present without standard EXIF tables.
4. **Non-Double-Counting Guard:**  
   An encoded payload must NOT be penalized twice (as both an encoded indicator and an additional unusual indicator). The maximum score for an individual image under these rules is 15.

### 5.2 Ground Truth Mapping Table (`metadata_report.csv`)

| Filename | Format | Discovered Metadata Fields | Suspected Field | Detected Encoding | Risk Score | Score Rationale (`reason`) |
|---|:---:|---|---|---|:---:|---|
| `Activation.png` | PNG | `srgb, gamma, dpi, exif, Make, Model, Software, create-date, UserComment, GPSInfo` | `UserComment` | `EXIF ASCII header / plain text` | **15** | Confirmed covert message in EXIF UserComment (+10); camera and GPS tags embedded in graphic (+5). |
| `Brain-Channel.png` | PNG | `srgb, gamma, dpi, exif, ImageDescription` | `ImageDescription` | `None (plain text)` | **10** | Confirmed covert message in EXIF ImageDescription (+10). |
| `Brain.png` | PNG | `srgb, gamma, dpi, Software` | `Software` | `None (plain text)` | **10** | Confirmed covert message in PNG text Software chunk (+10). |
| `Chemicals.png` | PNG | `ImageDescription` | `ImageDescription` | `None (plain text)` | **10** | Confirmed covert message in PNG text ImageDescription chunk (+10). |
| `Dopamine.png` | PNG | `srgb, gamma, dpi, xmp, XML:com.adobe.xmp` | `XML:com.adobe.xmp (exif:MakerNote)` | `XML encapsulation / plain text` | **10** | Confirmed covert message inside XMP MakerNote element (+10). |
| `Music.png` | PNG | `srgb, gamma, dpi, Copyright, Make, Model, create-date, exif` | `Copyright` | `Base64` | **15** | Confirmed covert message (+10) obfuscated with Base64 encoding requiring decoding (+5). |

*Note on Heuristic Variations:* If an evaluator classifies the abuse of `Software` in `Brain.png` or `MakerNote` in `Dopamine.png` as an anomalous carrier (+5), those scores become 15. The scanner's reason field must explicitly itemize every applied point addition (e.g. `Confirmed covert message (+10); ... (+5)`), ensuring total transparency.

---

## 6. Detailed Data Models & Function Specifications for Worker

To ensure clean code organization, maintainability, and testability, the Worker should structure `Lab6/metadata_scanner.py` into distinct modular functions:

```python
# Outline of modules and data models
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Dict, List, Tuple
```

### 6.1 Data Model: `ImageScanResult`

```python
@dataclass
class ImageScanResult:
    filename: str
    format: str
    metadata_fields: str      # Comma-separated list of field names
    suspected_field: str      # Identified covert field
    encoding: str             # Detected encoding
    risk_score: int           # Computed score (0, 5, 10, 15)
    reason: str               # Justification text
    raw_value: str = ""       # For diagnostic / evidence logging
    decoded_value: str = ""   # Recovered message snippet

    def to_csv_dict(self) -> Dict[str, Any]:
        """Return exactly the 7 CSV columns mandated by interface contract."""
        return {
            "filename": self.filename,
            "format": self.format,
            "metadata_fields": self.metadata_fields,
            "suspected_field": self.suspected_field,
            "encoding": self.encoding,
            "risk_score": self.risk_score,
            "reason": self.reason,
        }
```

### 6.2 Function Specifications

#### 1. `extract_exif_metadata(img: Image.Image) -> Tuple[Dict[str, Any], List[str]]`
- **Purpose:** Extracts top-level IFD0 tags, Exif Sub-IFD (`0x8769`), and GPS Sub-IFD (`0x8825`).
- **Logic:**
  1. Initialize `exif_dict = {}` and `tag_names = []`.
  2. Call `exif = img.getexif()`. If empty or `None`, return `({}, [])`.
  3. Iterate `(tag_id, value)` in `exif.items()`. Map `tag_id` using `ExifTags.TAGS.get(tag_id, str(tag_id))`. Store in `exif_dict` and record tag name.
  4. Query `exif.get_ifd(0x8769)`. For each sub-IFD tag, map name and store in `exif_dict` under `ExifTags.TAGS.get(sub_tag, f"SubIFD_{sub_tag}")`. Add name to `tag_names`.
  5. Query `exif.get_ifd(0x8825)`. If present and non-empty, record `"GPSInfo"` in `tag_names`.
  6. Return `(exif_dict, tag_names)`.

#### 2. `extract_png_info(img: Image.Image) -> Tuple[Dict[str, Any], List[str]]`
- **Purpose:** Inspects native PNG textual chunks exposed via `img.info`.
- **Logic:**
  1. Initialize `info_dict = {}` and `keys = list(img.info.keys())`.
  2. For key, value in `img.info.items()`:
     - If key in `("exif", "xmp")`: record key name in `keys`, but do not treat raw binary as string.
     - If `isinstance(value, str)`: store `info_dict[key] = value`.
     - If `isinstance(value, bytes)`: attempt safe UTF-8 decoding; if printable, store in `info_dict[key]`.
  3. Return `(info_dict, keys)`.

#### 3. `extract_xmp_metadata(img: Image.Image) -> Tuple[Dict[str, str], List[str]]`
- **Purpose:** Parses Adobe XMP XML packets embedded in PNG `iTXt` chunks.
- **Logic:**
  1. Retrieve raw XMP packet via `img.info.get("XML:com.adobe.xmp")` or `img.info.get("xmp")`.
  2. If absent, return `({}, [])`.
  3. Decode bytes to UTF-8 with `errors="replace"`.
  4. Parse XML with `defusedxml.ElementTree` or `xml.etree.ElementTree`.
  5. Traverse elements with `root.iter()`. Strip `{namespace}` from `elem.tag`.
  6. If `elem.text` is non-empty, store `xmp_dict[f"XMP:{local_tag}"] = elem.text.strip()`.
  7. Return `(xmp_dict, [f"XMP:{t}" for t in xmp_dict.keys()])`.

#### 4. `decode_candidate_value(raw_val: Any) -> Tuple[str, str, bool, bool]`
- **Purpose:** Tests a value for encoding and checks for covert narrative indicators.
- **Returns:** `(cleaned_or_decoded_str, encoding_label, is_covert, is_encoded)`
- **Logic:**
  1. If `isinstance(raw_val, bytes)`:
     - Check if starts with `b"ASCII\x00\x00\x00"`: slice `[8:]`, decode UTF-8. Set `encoding = "EXIF ASCII header / plain text"`, `is_encoded = True`.
     - Else: decode with UTF-8 `errors="replace"`.
  2. If string resembles Base64 (length % 4 == 0, regex match, length >= 16):
     - Try `decoded_bytes = base64.b64decode(raw_val, validate=True)`.
     - If decodes to printable UTF-8:
       - Set `cleaned_str = decoded_bytes.decode("utf-8")`.
       - Set `encoding = "Base64"`, `is_encoded = True`.
  3. Check `cleaned_str` for incident stage prefixes (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`) or security keywords (`CVE-`, `Mimikatz`, `SQL Injection`, `WAF`, `cron job`, `DNS Covert Channel`).
  4. If match found: `is_covert = True`.
  5. Return `(cleaned_str, encoding, is_covert, is_encoded)`.

#### 5. `evaluate_risk(filename: str, suspected_field: str, encoding: str, is_covert: bool, is_encoded: bool, has_gps_camera: bool, is_xmp_only: bool) -> Tuple[int, str]`
- **Purpose:** Applies the explainable classroom heuristic scoring rules.
- **Returns:** `(risk_score, reason)`
- **Logic:**
  1. Base score = 0. Reasons list = `[]`.
  2. If `is_covert`:
     - Score += 10.
     - Reasons.append(f"Confirmed covert message in {suspected_field} (+10)")
  3. If `is_encoded`:
     - Score += 5.
     - Reasons.append(f"Obfuscated with {encoding} requiring decoding (+5)")
  4. If not `is_encoded` and `has_gps_camera`:
     - Score += 5.
     - Reasons.append("Camera hardware and GPS tags embedded in graphic (+5)")
  5. Return `(score, "; ".join(Reasons) + ".")`.

#### 6. `scan_single_image(image_path: Path) -> ImageScanResult`
- **Purpose:** Runs the multi-layer pipeline on a single image and produces an `ImageScanResult`.

#### 7. `scan_directory(image_dir: Path, output_csv: Optional[Path] = None, verbose: bool = False) -> List[Dict[str, Any]]`
- **Purpose:** Discovers all `*.png` images in `image_dir`, sorts them by filename, runs `scan_single_image`, writes to `output_csv` if supplied, and returns the list of result dictionaries.

#### 8. `main() -> None`
- **Purpose:** CLI entry point, parses arguments, runs `scan_directory`, and prints a formatted terminal summary table.

---

## 7. Error Handling & Robustness Matrix

| Scenario / Edge Case | Failure Mode Without Robust Design | Architectural Mitigation in Scanner |
|---|---|---|
| **EXIF tags in Sub-IFD (`Activation.png`)** | Naive `getexif()` returns only 10 tags, skipping tag 37510. | Call `exif.get_ifd(0x8769)` or fallback to `_getexif()`. |
| **8-byte charset header in UserComment** | String displays as `ASCII\x00\x00\x00...` or fails UTF-8 decode. | Check `startswith(b"ASCII\x00\x00\x00")` and slice `[8:]`. |
| **Non-string objects in `img.info`** | Calling string methods on integer or raw tuple causes `AttributeError`. | Type guard with `isinstance(val, str)` / `isinstance(val, bytes)`. |
| **Raw EXIF chunk in `img.info['exif']`** | Trying to decode raw binary TIFF header causes `UnicodeDecodeError`. | Explicitly skip key `'exif'` in string scan. |
| **XMP XML namespaces & prefixes** | Exact tag match fails due to RDF namespaces (`{http://...}MakerNote`). | Strip namespace URIs using `split('}')[-1]` on element tags. |
| **Windows Console CP1252 crash** | Outputting arrows (`→`) or UTF-8 BOM causes `UnicodeEncodeError`. | Reconfigure `sys.stdout` to UTF-8 on Windows. |
| **Missing output directory** | CSV export fails with `FileNotFoundError` if parent dir absent. | Use `output_path.parent.mkdir(parents=True, exist_ok=True)`. |
| **Non-PNG files or subdirectories in target** | Attempting to open non-image files crashes script. | Filter strictly by `image_path.is_file()` and suffix `*.png`. |

---

## 8. Verification & Testing Guidance for the Worker

The implementer should verify `Lab6/metadata_scanner.py` using the following verification steps:

1. **CLI Execution Test:**
   ```powershell
   python Lab6/metadata_scanner.py --verbose
   ```
   *Expected:* Scans all 6 images, logs field details, and saves `Lab6/metadata_report.csv` without unhandled exceptions.

2. **CSV Schema & Row Count Validation:**
   ```powershell
   python -c "
   import csv
   with open('Lab6/metadata_report.csv', encoding='utf-8') as f:
       rows = list(csv.DictReader(f))
   assert len(rows) == 6, f'Expected 6 rows, got {len(rows)}'
   expected_headers = ['filename', 'format', 'metadata_fields', 'suspected_field', 'encoding', 'risk_score', 'reason']
   assert list(rows[0].keys()) == expected_headers, f'Headers mismatch: {rows[0].keys()}'
   for r in rows:
       assert int(r['risk_score']) in (10, 15), f'Unexpected score: {r}'
   print('CSV Schema and Row Validation Passed!')
   "
   ```

3. **Importable Module Test:**
   ```powershell
   python -c "
   from Lab6.metadata_scanner import scan_directory
   results = scan_directory('Lab6/Images')
   assert len(results) == 6
   print('Module import test passed!')
   "
   ```
