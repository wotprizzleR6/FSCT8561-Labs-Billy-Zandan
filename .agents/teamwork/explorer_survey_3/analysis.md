# Lab 6 Tooling & Environment Exploration Report

**Explorer**: Tooling & Environment Explorer  
**Date**: November 2, 2026  
**Target Project**: Lab 6 (Covert Channels in Image Metadata)  
**Location**: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6`

---

## Executive Summary

A comprehensive investigation of the Python execution environment, headless notebook execution capabilities, document generation tooling, metadata extraction libraries, and automated scanner architecture was conducted for Lab 6.

Key findings:
1. **Python Environments**: System Python is **Python 3.14.8** (`C:\Users\BillyZ\AppData\Local\Programs\Python\Python314\python.exe`) with `pillow` (12.3.0), `python-docx` (1.2.0), `pandas` (3.0.6), and `defusedxml` (0.7.1) pre-installed. In addition, **Anaconda Python 3.13.9** (`C:\Users\BillyZ\anaconda3\python.exe`) has a complete Jupyter environment (`jupyter`, `nbformat` 5.10.4, `nbconvert` 7.16.6, `ipykernel` 6.31.0, `pillow` 12.0.0, `defusedxml` 0.7.1, `pandas` 2.3.3) ready for immediate headless execution.
2. **Headless Execution**: Verified working using `C:\Users\BillyZ\anaconda3\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace Lab6.ipynb`. Execution was experimentally verified on a test notebook, executing code and preserving rich outputs in-place without GUI intervention.
3. **Report Generation**: Verified working using `python-docx` (1.2.0) under Python 3.14, generating valid `.docx` files with structured formatting, styled headers, and data tables matching the 100-point rubric.
4. **Tooling & Extraction**: The CLI tool `exiftool` is **not** present in `PATH`. However, pure-Python extraction using standard libraries (`PIL.Image`, `PIL.ExifTags`, `defusedxml` / `xml.etree.ElementTree`, and `base64`) was tested and verified across **all six images**, extracting 100% of the covert fragments without any external dependencies.
5. **Scanner & Risk Model**: Designed an automated, explainable risk-scoring architecture adhering strictly to the rubric's suggested scoring model (+10 confirmed covert message, +5 suspicious encoding, +5 additional unusual indicator). A prototype scanner was implemented and verified, yielding consistent, deterministic scores and clear narrative justifications.

---

## 1. Python Environment & Package Survey

### 1.1 Available Python Interpreters

| Interpreter Path | Python Version | Role / Suitability |
|---|---|---|
| `C:\Users\BillyZ\AppData\Local\Programs\Python\Python314\python.exe` | 3.14.8 (64-bit) | System default `python`. Contains `python-docx`, `pillow`, `pandas`, `defusedxml`. Ideal for script execution and Word document generation. |
| `C:\Users\BillyZ\anaconda3\python.exe` | 3.13.9 (64-bit) | Anaconda base. Contains `jupyter`, `nbformat`, `nbconvert`, `ipykernel`, `pillow`, `pandas`. Ideal for headless notebook execution. |
| `C:\Users\BillyZ\miniconda3\python.exe` | 3.13.5 (64-bit) | Minimal installation without data science or jupyter packages. |
| `C:\Users\BillyZ\miniconda3\envs\whisper-env\python.exe` | 3.10.19 (64-bit) | Specialized audio transcription environment; not required for Lab 6. |

### 1.2 Target Package Availability Matrix

| Package Requested | System Python 3.14 | Anaconda Python 3.13 | Notes & Resolution |
|---|---|---|---|
| **PIL / Pillow** | **12.3.0** (Installed) | **12.0.0** (Installed) | Available in both environments; handles EXIF, PNG chunks, and raw metadata buffers. |
| **exifread** | Not Installed | Not Installed | Not needed; Pillow's `img.getexif()` and `exif.get_ifd()` provide all required tag access. |
| **piexif** | Not Installed | Not Installed | Not needed; Pillow handles PNG and EXIF parsing natively. |
| **exiftool / PyExifTool** | Not Installed | Not Installed | Not needed; pure-Python extraction extracts all six secrets successfully. |
| **xmltodict** | Not Installed | Not Installed | Not needed; standard `defusedxml.ElementTree` and `xml.etree.ElementTree` parse XMP XML seamlessly. |
| **defusedxml** | **0.7.1** (Installed) | **0.7.1** (Installed) | Available in both; safe XML parsing against entity expansion attacks. |
| **python-docx** | **1.2.0** (Installed) | Not Installed | Available in Python 3.14; generates `Lab6_Report.docx` programmatically. |
| **pandas** | **3.0.6** (Installed) | **2.3.3** (Installed) | Available in both; can load and display `metadata_report.csv`. |
| **jupyter** | Not Installed | **Installed** | Full Jupyter suite available via Anaconda. |
| **nbformat** | Not Installed | **5.10.4** (Installed) | Used for programmatic notebook manipulation. |
| **nbconvert** | Not Installed | **7.16.6** (Installed) | Used for CLI and API headless notebook execution. |
| **ipykernel** | Not Installed | **6.31.0** (Installed) | Jupyter execution kernel (`base` environment). |

---

## 2. Headless Notebook Execution Strategy

### 2.1 Execution Mechanism Options

Two reliable headless execution paths were evaluated and verified:

#### Option A: CLI Headless Execution via Anaconda `jupyter nbconvert` (Recommended)
Command:
```powershell
Set-Location "c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6"
C:\Users\BillyZ\anaconda3\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace Lab6.ipynb
```
- **Execution Mode**: Executes all code cells sequentially, records stdout/stderr, updates cell execution counters, and saves the executed notebook in place.
- **Working Directory Requirement**: Must be run with the current working directory set to `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6` so that `Path("Images")` and `metadata_report.csv` resolve to the correct relative paths.
- **Verification Result**: Tested on `test_nb.ipynb`. Executed in 7.2 seconds; cell outputs and execution metadata were correctly saved.

#### Option B: Programmatic Headless Execution via Python API
If programmatic execution from a Python wrapper script is preferred:
```python
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

lab6_dir = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6")
nb_path = lab6_dir / "Lab6.ipynb"

with open(nb_path, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
ep.preprocess(nb, {"metadata": {"path": str(lab6_dir)}})

with open(nb_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)
```
- **Verification Result**: Tested on `test_nb.ipynb` using `C:\Users\BillyZ\anaconda3\python.exe`. Execution completed with exit code 0.

---

## 3. Word Document (`Lab6_Report.docx`) Generation

### 3.1 Tooling Verification
- Library: `python-docx` 1.2.0 under Python 3.14.8.
- Tested: Headings, styled paragraphs, runs with formatting, table creation, cell alignment, margins, and document saving.
- Output: Valid Microsoft Word document generated cleanly without errors.

### 3.2 Required Document Architecture (Per Rubric & Requirements)
To earn full credit across all 100 points, the generated `Lab6_Report.docx` must contain:

1. **Title Page / Document Header**:
   - Course: FSCT 8561
   - Title: Lab 6: Covert Channels in Image Metadata Investigation Report
   - Author: Student name and ID metadata
   - Date and Version
2. **Executive Summary**:
   - Investigation objectives and scenario context.
   - High-level overview of findings: 6 images inspected, 6 attack narrative stages recovered.
3. **Forensic Evidence Summary Table (25 Points)**:
   - Complete table with columns: `Image Filename`, `Format`, `File Size / SHA-256 Hash`, `Metadata Layer`, `Field Name`, `Raw Value (or excerpt)`, `Decoding Applied`, `Recovered Secret Fragment`.
4. **Detailed Image-by-Image Forensic Analysis (25 Points)**:
   - Dedicated subsections for each of the six images:
     - Extraction methodology (EXIF vs. PNG text vs. XMP).
     - Verbatim raw metadata output and code snippet used.
     - Encoding analysis and decoding demonstration.
     - Forensic screenshot / textual representation of code execution output.
5. **Reconstructed Six-Stage Incident Secret Narrative (20 Points)**:
   - Ordered stages 1 through 6.
   - Comprehensive narrative justification mapping stages to the Cyber Kill Chain / MITRE ATT&CK framework (Reconnaissance -> Vulnerability Identification -> Exploitation -> Persistence -> Lateral Movement -> Exfiltration).
   - Explanation of why filename order is irrelevant.
6. **Automated Metadata Scanner Implementation (20 Points)**:
   - Architecture and design explanation of `metadata_scanner.py`.
   - Complete scanner source code.
   - CSV Results Table (`metadata_report.csv`) with columns: `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`.
   - Detailed justification for each risk score and heuristic decision.
7. **Forensic Limitations & Methodological Interpretation (10 Points)**:
   - *Limitation 1: EXIF-Only Extraction*: Explain why tools or scripts inspecting only EXIF (`getexif()`) miss PNG text chunks (tEXt/zTXt/iTXt) and XMP metadata (Brain.png, Chemicals.png, Dopamine.png).
   - *Limitation 2: Automated Risk Scoring*: Explain why heuristic scores are not forensic proof of malicious intent (risk of false positives on benign developer metadata, false negatives on steganographic LSB covert channels, reliance on known patterns).
8. **Comprehensive Reflection Questions (Lab 6 Notebook Questions)**:
   - Q1: Why images can contain hidden messages when `getexif()` returns 0 tags.
   - Q2: Encoding vs. Encryption, and why Base64 provides zero confidentiality.
   - Q3: The necessity of cryptographic hashing and evidence preservation in digital forensics.
   - Q4: Metadata limitations in proving unauthorized edits or incident occurrence, and required corroborating evidence (network logs, SIEM, disk forensics, host artifacts).
   - Q5: Integration and progression from Lab 4 (host artifact collection) and Lab 5 (network packet scanning/heuristics) to metadata analysis.

---

## 4. Pure-Python vs. ExifTool CLI Metadata Extraction

### 4.1 CLI Availability
`exiftool` CLI is **not present** on the system PATH.

### 4.2 Pure-Python Extraction Capabilities Across All 6 Images
Pure-Python extraction using Pillow (`PIL.Image`, `PIL.ExifTags`) and `defusedxml` / `xml.etree.ElementTree` is **100% effective and sufficient**. Every image's covert secret was inspected, verified, and extracted directly.

#### Summary of Image Extractions:

| Filename | Metadata Layer | Field Name | Raw Value / Format | Decoding Method | Recovered Secret Fragment |
|---|---|---|---|---|---|
| **Brain.png** | PNG Text Chunk | `Software` | `RECON: Perform DNS harvesting and Subdomain enumeration.` | Plain text | `RECON: Perform DNS harvesting and Subdomain enumeration.` |
| **Activation.png** | EXIF Sub-IFD (0x8769) | `UserComment` (Tag 37510) | `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'` | ASCII strip (remove 8-byte header `ASCII\x00\x00\x00`) | `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` |
| **Chemicals.png** | PNG Text Chunk | `ImageDescription` | `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` | Plain text | `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` |
| **Dopamine.png** | XMP Metadata (`XML:com.adobe.xmp`) | `exif:MakerNote` | XML element `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>` | XML ElementTree parse | `PERSIST: Establish reverse shell via obfuscated cron job.` |
| **Brain-Channel.png** | EXIF Primary IFD | `ImageDescription` (Tag 270) | `LATERAL: Pivot to internal Domain Controller using Mimikatz.` | Plain text | `LATERAL: Pivot to internal Domain Controller using Mimikatz.` |
| **Music.png** | EXIF (Tag 33432) & PNG Text | `Copyright` | `RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4=` | Base64 decode (`base64.b64decode`) | `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` |

### 4.3 Python Code Snippets for Each Layer

1. **PNG Text Chunks**:
   ```python
   with Image.open("Brain.png") as img:
       for key, val in img.info.items():
           if isinstance(val, str):
               print(f"{key}: {val}")
   ```
2. **EXIF Primary & Sub-IFD**:
   ```python
   with Image.open("Activation.png") as img:
       exif = img.getexif()
       # Sub-IFD 0x8769 contains UserComment
       sub_ifd = exif.get_ifd(0x8769)
       user_comment = sub_ifd.get(37510)  # tag 37510 = UserComment
       if isinstance(user_comment, bytes) and user_comment.startswith(b"ASCII\x00\x00\x00"):
           secret = user_comment[8:].decode("utf-8")
   ```
3. **XMP XML**:
   ```python
   import xml.etree.ElementTree as ET
   with Image.open("Dopamine.png") as img:
       xmp_data = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
       if isinstance(xmp_data, bytes):
           xmp_data = xmp_data.decode("utf-8")
       root = ET.fromstring(xmp_data.strip("\ufeff"))
       for elem in root.iter():
           if "MakerNote" in elem.tag:
               print("MakerNote secret:", elem.text)
   ```
4. **Base64 Decoding**:
   ```python
   import base64
   raw_b64 = "RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="
   decoded = base64.b64decode(raw_b64).decode("utf-8")
   ```

---

## 5. Automated Scanner Architecture & Risk Scoring Model

### 5.1 Design Principles
1. **Separation of Extraction and Detection**: The scanner first ingests metadata across all three physical formats (EXIF root/sub-IFDs, PNG text, XMP XML), then evaluates potential candidate strings against heuristic detection criteria.
2. **Defensive Decoding**: Strings are evaluated for Base64 characteristics (character set, padding, length, Shannon entropy, printable ratio) before attempting decoding, avoiding false positives on arbitrary strings.
3. **No Hard-Coded Secret Outputs**: Detection rules rely on pattern heuristics (stage prefixes like `RECON:`, `VULN:`, `EXPLOIT:`, security keywords like `CVE-`, `sql injection`, `mimikatz`, `reverse shell`, `dns covert channel`) rather than verbatim hard-coded secrets.
4. **Deterministic and Explainable Risk Scoring**: Built strictly upon the lab rubric's suggested scoring framework.

### 5.2 Classroom Risk Scoring Criteria

| Condition | Points | Forensic Justification |
|---|---|---|
| **Confirmed Covert Message** | **+10** | Metadata field contains operational attack stage indicator (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`) or explicit malicious payload/technique terminology. |
| **Suspicious Encoded Value** | **+5** | Field contains obfuscated/encoded content (such as valid Base64) requiring active decoding to extract readable information. |
| **Additional Unusual Metadata Indicator** | **+5** | Evidence of anomalous metadata structure, such as camera EXIF/GPS tags embedded on synthetic digital artwork screenshots, or camera `MakerNote` tags placed inside XMP on a PNG format image. (Double-counting avoided). |

### 5.3 Deterministic Scanner Results (`metadata_report.csv`)

| filename | format | metadata_fields | suspected_field | encoding | risk_score | reason |
|---|---|---|---|---|---|---|
| `Activation.png` | PNG | `srgb, gamma, dpi, exif, Make, Model, Software, create-date, EXIF:GPSInfo, EXIF:ResolutionUnit, EXIF:ExifOffset, EXIF:Make, EXIF:Model, EXIF:Software, EXIF:DateTime, EXIF:YCbCrPositioning, EXIF:XResolution, EXIF:YResolution` | `EXIF Sub-IFD:UserComment` | `ASCII (Null-prefixed)` | **15** | Confirmed covert incident narrative stage in EXIF Sub-IFD:UserComment ('VULN: Identify unpatched CVE-2024-XXXX in web gateway.'); GPS metadata present on synthetic screenshot asset |
| `Brain-Channel.png` | PNG | `srgb, gamma, dpi, exif, EXIF:ResolutionUnit, EXIF:ImageDescription, EXIF:YCbCrPositioning, EXIF:XResolution, EXIF:YResolution` | `EXIF:ImageDescription` | `Plain text` | **10** | Confirmed covert incident narrative stage in EXIF:ImageDescription ('LATERAL: Pivot to internal Domain Controller using Mimikatz.') |
| `Brain.png` | PNG | `srgb, gamma, dpi, Software` | `PNG:Software` | `Plain text` | **10** | Confirmed covert incident narrative stage in PNG:Software ('RECON: Perform DNS harvesting and Subdomain enumeration.') |
| `Chemicals.png` | PNG | `ImageDescription` | `PNG:ImageDescription` | `Plain text` | **10** | Confirmed covert incident narrative stage in PNG:ImageDescription ('EXPLOIT: Deploy SQL Injection payload to bypass WAF.') |
| `Dopamine.png` | PNG | `srgb, gamma, dpi, xmp, XML:com.adobe.xmp` | `XMP:MakerNote` | `Plain text` | **15** | Confirmed covert incident narrative stage in XMP:MakerNote ('PERSIST: Establish reverse shell via obfuscated cron job.'); Unusual metadata structure: MakerNote embedded in XMP on PNG format |
| `Music.png` | PNG | `srgb, gamma, dpi, Copyright, Make, Model, create-date, exif, EXIF:ResolutionUnit, EXIF:ExifOffset, EXIF:Make, EXIF:Model, EXIF:DateTime, EXIF:YCbCrPositioning, EXIF:Copyright, EXIF:XResolution, EXIF:YResolution` | `PNG:Copyright` | `Base64` | **15** | Confirmed covert message in Copyright encoded in Base64 (Decoded: 'EXFIL: Tunnel compressed database dump via DNS Covert Channel.') |

---

## 6. Recommendations for Downstream Agents

1. **For Implementer / Notebook Execution**:
   - Update `Lab6.ipynb` code cells to populate extraction snippets, secret outputs, answers to reflection questions, and the scanner implementation.
   - Run headless execution using:
     `C:\Users\BillyZ\anaconda3\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace Lab6.ipynb` from within `Lab6/`.
   - Verify that execution leaves no unfilled TODOs and generates `metadata_report.csv`.
2. **For Report Generation**:
   - Execute report generation using `C:\Users\BillyZ\AppData\Local\Programs\Python\Python314\python.exe` with `python-docx`.
   - Save the completed document to `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6_Report.docx`.
   - Ensure all sections from the 100-point rubric are thoroughly covered.
