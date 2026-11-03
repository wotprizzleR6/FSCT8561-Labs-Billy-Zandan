# Survey Report: Environment, Metadata Scanner Architecture, Notebook Execution, and Report Generation

**Date**: 2026-11-02  
**Investigator**: Teamwork Explorer (Survey 3)  
**Target Lab**: Lab 6 — Covert Channels in Image Metadata  
**Student Metadata**: Billy Zandan | A01371854 | BCIT FSCT 8561  

---

## Executive Summary

This survey provides a comprehensive technical investigation into the execution environment, metadata extraction mechanisms, automated scanner architecture, Jupyter notebook execution workflow, and Word document report generation for Lab 6.

### Key Highlights
1. **Python Environment**: Python 3.14.8 (64-bit AMD64) is installed with Pillow 12.3.0, python-docx 1.2.0, defusedxml 0.7.1, and pandas 3.0.6. Pip has working internet connectivity.
2. **Metadata Findings Across 6 Images**: All 6 covert channel payloads were located, extracted, and verified across three distinct metadata container formats (EXIF IFDs, PNG `tEXt` chunks, and Adobe XMP XML in PNG `iTXt` chunks).
3. **Attack Narrative Reconstruction**: The 6 fragments represent a complete Cyber Kill Chain progression:
   - Stage 1 `RECON` (`Brain.png`): "Perform DNS harvesting and Subdomain enumeration."
   - Stage 2 `VULN` (`Activation.png`): "Identify unpatched CVE-2024-XXXX in web gateway."
   - Stage 3 `EXPLOIT` (`Chemicals.png`): "Deploy SQL Injection payload to bypass WAF."
   - Stage 4 `PERSIST` (`Dopamine.png`): "Establish reverse shell via obfuscated cron job."
   - Stage 5 `LATERAL` (`Brain-Channel.png`): "Pivot to internal Domain Controller using Mimikatz."
   - Stage 6 `EXFIL` (`Music.png`): "Tunnel compressed database dump via DNS Covert Channel."
4. **Scanner Architecture**: Fully prototyped with multi-IFD EXIF parsing (including tag 37510 `UserComment`), PNG chunk inspection, XMP XML extraction, Base64 detection/decoding heuristics, and an explainable risk scoring model (+10 confirmed covert payload, +5 obfuscation/encoding, +5 anomalous carrier field).
5. **Notebook Execution Workflow**: Validated both zero-dependency deterministic JSON in-place execution and `nbclient`/`nbconvert` options.
6. **Word Document Generation**: Validated custom XML styling in `python-docx` for professional margins, tables, callout blocks, and high-fidelity rendered terminal console screenshot cards.

---

## 1. Python Environment & Package Ecosystem Survey

### 1.1 Python Interpreter & Runtime Details
- **Binary Path**: `C:\Users\BillyZ\AppData\Local\Programs\Python\Python314\python.exe`
- **Version**: Python 3.14.8 (tags/v3.14.8:8e6e75d, Sep 30 2026, 18:19:33) [MSC v.1944 64 bit (AMD64)]
- **Platform**: Windows 11 (PowerShell terminal encoding defaults to cp1252; Python scripts must configure `sys.stdout.reconfigure(encoding='utf-8')` when printing UTF-8/BOM characters like `\ufeff`).

### 1.2 Package Status Inventory

| Package Category | Package Name | Installed Version | Availability / Status | Forensic & Lab Relevance |
|---|---|---|---|---|
| **Image & Metadata** | `pillow` | 12.3.0 | Installed | Primary image parsing library (`PIL.Image`, `PIL.ExifTags`) |
| **Image & Metadata** | `defusedxml` | 0.7.1 | Installed | Secure XML parsing for Adobe XMP metadata packets |
| **Image & Metadata** | `lxml` | 6.1.3 | Installed | Advanced XML parsing & XPath navigation |
| **Document Generation** | `python-docx` | 1.2.0 | Installed | Direct generation of `.docx` forensic reports with tables & images |
| **Data Processing** | `pandas` | 3.0.6 | Installed | CSV data loading, tabular analysis, and summary generation |
| **PDF & Forensics** | `pypdf` | 6.21.2 | Installed | Used to inspect Ortega textbook and lab specifications |
| **PDF & Forensics** | `pdfplumber` | 0.11.10 | Installed | Secondary PDF inspection |
| **Document Export** | `reportlab` | 5.1.0 | Installed | PDF generation library |
| **Notebook Runtime** | `nbformat`, `nbclient`, `ipykernel` | Not installed in site-packages | Available via `pip` (wheels cached) | Notebook JSON execution engine |

### 1.3 Pip Network Connectivity
- `pip install --dry-run` succeeded without authentication errors.
- Internet connectivity is functional, allowing installation of `nbformat`, `nbclient`, or `ipykernel` if desired. However, zero-dependency script execution is also fully viable.

---

## 2. Forensic Image Analysis & Metadata Extraction Logic

### 2.1 File Hashes and Cryptographic Integrity

To satisfy forensic chain of custody and data integrity requirements (answering Reflection Question 3), SHA-256 and MD5 hashes were calculated for all original input artifacts:

| Filename | File Size | MD5 Hash | SHA-256 Cryptographic Hash |
|---|---|---|---|
| `Activation.png` | 259,975 B | `28a931ca770d9118a8286c0db414332c` | `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904` |
| `Brain-Channel.png` | 201,685 B | `8e8a9d7276707a9f18af7c2e09c70e3a` | `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359` |
| `Brain.png` | 2,354,330 B | `5d69dd3de9b5f8557ba26d8bcc644af4` | `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e` |
| `Chemicals.png` | 561,245 B | `694d3d3984e34b39a59e0305e837eb5f` | `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a` |
| `Dopamine.png` | 388,411 B | `22eedbe31ba01a541f29758f508d2a58` | `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472` |
| `Music.png` | 679,959 B | `5924abe517910c58798d5567ae27323d` | `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370` |

### 2.2 Low-Level PNG Chunk Structures

Direct binary chunk analysis was performed across all six PNG files:
1. `Activation.png`: Contains an `eXIf` chunk (510 bytes) and 4 `tEXt` chunks (`Make`, `Model`, `Software`, `create-date`).
2. `Brain-Channel.png`: Contains an `eXIf` chunk (152 bytes). No text chunks.
3. `Brain.png`: Contains a single `tEXt` chunk (65 bytes) for `Software`. No `eXIf` chunk.
4. `Chemicals.png`: Contains a single `tEXt` chunk (69 bytes) for `ImageDescription`. No `eXIf` chunk.
5. `Dopamine.png`: Contains an `iTXt` chunk (445 bytes) encapsulating Adobe XMP XML data. No `eXIf` chunk.
6. `Music.png`: Contains an `eXIf` chunk (382 bytes) and 4 `tEXt` chunks (`Copyright`, `Make`, `Model`, `create-date`).

### 2.3 Extraction Nuances & Forensic Gotchas
- **The Sub-IFD Blind Spot (`Activation.png`)**: Standard `img.getexif().items()` only iterates IFD0 (top-level tags). Tag 34665 (`ExifOffset`) points to the Exif sub-IFD. The covert payload in `Activation.png` is located inside tag 37510 (`UserComment`) within this sub-IFD. Calling `exif.get_ifd(ExifTags.IFD.Exif)` is mandatory to uncover it. Furthermore, EXIF `UserComment` begins with an 8-byte charset header (`ASCII\x00\x00\x00`) that must be stripped.
- **The PNG Text Chunk Blind Spot (`Brain.png`, `Chemicals.png`)**: `img.getexif()` returns 0 tags for both images. A naive investigator relying on EXIF tools will conclude "no metadata exists". However, `img.info` reveals uncompressed textual chunks containing plain-text covert instructions.
- **The XMP Namespace Blind Spot (`Dopamine.png`)**: `img.getexif()` returns 0 tags. The secret is embedded in an Adobe XMP XML packet (`XML:com.adobe.xmp` or `xmp`), specifically inside the `<exif:MakerNote>` element.
- **The Base64 Obfuscation Blind Spot (`Music.png`)**: The `Copyright` tag contains `RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4=`. Requires Base64 decoding to reveal the plain-text exfiltration command.

---

## 3. Automated Metadata Scanner Architecture

### 3.1 Architectural Design

The automated scanner (`metadata_scanner.py` / Step 7C in `Lab6.ipynb`) must be robust, modular, and non-hardcoded. It follows a multi-tier inspection pipeline:

```
                  ┌───────────────────────────────┐
                  │    Target Image (PNG File)    │
                  └──────────────┬────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       ┌───────────────────┐           ┌───────────────────┐
       │   EXIF Extractor  │           │   PNG & XMP Info  │
       └─────────┬─────────┘           └─────────┬─────────┘
                 │                               │
        ┌────────┴────────┐             ┌────────┴────────┐
        ▼                 ▼             ▼                 ▼
   IFD0 (Top)     Exif/GPS Sub-IFDs  tEXt Chunks     iTXt (XMP XML)
        │                 │             │                 │
        └────────┬────────┴─────────────┴────────┬────────┘
                 │                               │
                 ▼                               ▼
       ┌───────────────────────────────────────────────────┐
       │     Heuristic Detection & Decoding Pipeline       │
       │  - Base64 Regex & Safe UTF-8 Decode               │
       │  - ASCII Null-Header Strip (UserComment)          │
       │  - Attack Keyword & Pattern Matching              │
       └─────────────────────────┬─────────────────────────┘
                                 │
                                 ▼
       ┌───────────────────────────────────────────────────┐
       │          Explainable Risk Scoring Engine          │
       │  - Base Score: +10 (Confirmed Covert Payload)     │
       │  - Encoding Risk: +5 (Obfuscation / Base64/ASCII) │
       │  - Carrier Risk: +5 (Anomalous / Non-standard Tag)│
       └─────────────────────────┬─────────────────────────┘
                                 │
                                 ▼
       ┌───────────────────────────────────────────────────┐
       │             Export to metadata_report.csv         │
       └───────────────────────────────────────────────────┘
```

### 3.2 Heuristic Detection Engine
1. **Base64 Detection**:
   - String length >= 8 and divisible by 4.
   - Matches regex `^[A-Za-z0-9+/]+={0,2}$`.
   - Safely decodes using `base64.b64decode()`.
   - Verifies that decoded bytes are printable UTF-8 text containing forensic indicators.
2. **ASCII Header Detection**:
   - Detects `b'ASCII\x00\x00\x00'` prefix standard in EXIF `UserComment` fields.
   - Strips 8-byte prefix and decodes remaining payload.
3. **Covert Narrative Keywords**:
   - Matches attack lifecycle tokens: `RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`, or associated tool/CVE keywords (`Mimikatz`, `CVE-2024`, `SQL Injection`, `DNS Covert Channel`, `cron job`).

### 3.3 Risk Scoring Model & Justifications

To fulfill rubric requirements for an **explainable, consistent risk scoring model**, we implement the classroom heuristic model:
- **Base Score: +10** for a confirmed covert-message payload.
- **Encoding Score: +5** for obfuscated content requiring decoding (Base64, null-padded ASCII).
- **Anomalous Carrier Score: +5** for metadata placed in non-standard carriers (e.g. `Software` used for attack instructions, `MakerNote` in XMP, or synthetic camera EXIF in PNG).
- **Double-Counting Guard**: Encoded payloads are not double-counted as both generic unusual text and encoded text.
- **Score Scale**:
  - `0`: Benign image (clean metadata, camera parameters only).
  - `5`: Suspicious indicator (unusual tag or encoded string without confirmed threat payload).
  - `10`: Moderate/High risk (unencrypted covert instruction in standard tag).
  - `15`: High/Critical risk (obfuscated or non-standard covert channel carrier).

### 3.4 Target CSV Schema & Ground Truth Values

The schema matches the lab rubric: `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`.

| filename | format | metadata_fields | suspected_field | encoding | risk_score | reason |
|---|---|---|---|---|---|---|
| `Activation.png` | PNG | `EXIF:Make, EXIF:Model, EXIF:Software, EXIF:DateTime, EXIF:GPSInfo, EXIF_IFD:UserComment, PNG:Make, PNG:Model, PNG:Software` | `EXIF_IFD:UserComment` | `ASCII (null-prefixed)` | 15 | Confirmed covert payload detected in EXIF_IFD:UserComment; Obfuscated payload requiring decoding (ASCII null-prefixed) |
| `Brain-Channel.png` | PNG | `EXIF:ImageDescription, EXIF:ResolutionUnit, EXIF:YCbCrPositioning, EXIF:XResolution, EXIF:YResolution` | `EXIF:ImageDescription` | `Plain text` | 15 | Confirmed covert payload detected in EXIF:ImageDescription; Anomalous narrative metadata embedded in standard tag |
| `Brain.png` | PNG | `PNG:Software, PNG:srgb, PNG:gamma, PNG:dpi` | `PNG:Software` | `Plain text` | 15 | Confirmed covert payload detected in PNG:Software; Non-standard metadata field carrier (PNG:Software) |
| `Chemicals.png` | PNG | `PNG:ImageDescription` | `PNG:ImageDescription` | `Plain text` | 15 | Confirmed covert payload detected in PNG:ImageDescription; Anomalous narrative metadata embedded in standard tag |
| `Dopamine.png` | PNG | `PNG:srgb, PNG:gamma, PNG:dpi, XMP:exif:MakerNote` | `XMP:exif:MakerNote` | `XML element` | 15 | Confirmed covert payload detected in XMP:exif:MakerNote; Non-standard metadata field carrier (XMP:exif:MakerNote) |
| `Music.png` | PNG | `EXIF:Make, EXIF:Model, EXIF:Copyright, PNG:Copyright, PNG:Make, PNG:Model` | `PNG:Copyright` | `Base64` | 15 | Confirmed covert payload detected in PNG:Copyright; Obfuscated payload requiring decoding (Base64) |

---

## 4. Secret Narrative Reconstruction & Threat Modeling

### 4.1 Chronological Attack Reconstruction

The recovered fragments assemble into the following sequence:

| Step / Stage | Source Artifact | Metadata Location | Recovered Partial Secret | ATT&CK / Kill Chain Tactic |
|---|---|---|---|---|
| **Stage 1** | `Brain.png` | PNG `tEXt`: `Software` | `RECON: Perform DNS harvesting and Subdomain enumeration.` | Reconnaissance (TA0043) |
| **Stage 2** | `Activation.png` | EXIF Sub-IFD: `UserComment` | `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` | Resource Development / Vuln Identification |
| **Stage 3** | `Chemicals.png` | PNG `tEXt`: `ImageDescription` | `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` | Initial Access / Execution (TA0001/TA0002) |
| **Stage 4** | `Dopamine.png` | XMP: `<exif:MakerNote>` | `PERSIST: Establish reverse shell via obfuscated cron job.` | Persistence (TA0003) |
| **Stage 5** | `Brain-Channel.png` | EXIF: `ImageDescription` | `LATERAL: Pivot to internal Domain Controller using Mimikatz.` | Lateral Movement (TA0008) |
| **Stage 6** | `Music.png` | EXIF/PNG: `Copyright` (Base64) | `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` | Exfiltration (TA0010) |

### 4.2 Sequence Justification
- **Logical Flow**: An attacker begins with external reconnaissance (`Brain.png`), identifies an unpatched edge vulnerability (`Activation.png`), exploits the perimeter via SQL injection (`Chemicals.png`), secures long-term foothold persistence via a cron reverse shell (`Dopamine.png`), moves laterally to domain controllers using credential dumping (`Brain-Channel.png`), and finally exfiltrates sensitive database assets over DNS covert channels (`Music.png`).
- **Filenames Are Arbitrary**: Filename alphabetization (`Activation`, `Brain-Channel`, `Brain`, `Chemicals`, `Dopamine`, `Music`) would position lateral movement before reconnaissance, which is operationally impossible. The explicit stage labels (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`) provide the ground-truth chronological ordering.

---

## 5. Notebook Execution Workflow (`Lab6.ipynb`)

### 5.1 Architecture of `Lab6.ipynb`
- Total cells: 42 (24 Markdown cells, 18 Code cells).
- The notebook contains guided instructions, extraction exercises, code completions (marked with `# TODO:`), reflection question prompts, and rubric tables.

### 5.2 Execution Options Evaluated

#### Option A: In-Place Deterministic Python Runner (Recommended)
- **Mechanism**: A Python script loads `Lab6.ipynb` as JSON, steps through cells sequentially, runs the Python code using a persistent dictionary execution scope, captures `sys.stdout` and `sys.stderr` in real time, formats outputs as nbformat v4 stream objects (`output_type: "stream"`), sets `execution_count`, and writes back to `Lab6.ipynb`.
- **Advantages**:
  - Zero external dependencies beyond the standard library.
  - Immune to Windows socket / ZeroMQ timeouts or Python 3.14 event loop quirks.
  - 100% deterministic and preserves exact JSON structure and indentation.
  - Safely intercepts `%pip` magics without failing.

#### Option B: Standard Jupyter Kernel Execution (`nbconvert` / `nbclient`)
- **Mechanism**: Run `pip install nbformat nbclient ipykernel` followed by `jupyter nbconvert --to notebook --execute --inplace Lab6/Lab6.ipynb`.
- **Evaluation**: Fully viable since pip works, but requires installing ~30 packages into the global environment.

---

## 6. Word Document Report Generation (`Lab6-Billy-Zandan-A01371854.docx`)

### 6.1 Requirements & Rubric Mapping
The Word document deliverable must satisfy 100% of the grading rubric:
- Student metadata (Billy Zandan, A01371854, FSCT 8561).
- Metadata evidence table for all 6 images.
- Extraction output evidence (code snippets and visual screenshot cards) for each image.
- Reconstructed 6-stage secret narrative with detailed sequence reasoning.
- Scanner source code and formatted `metadata_report.csv` results table.
- Comprehensive limitation analysis (EXIF-only limitations and automated risk-scoring limitations).
- Full answers to all 5 reflection questions.

### 6.2 Styling & Presentation Framework
- **Typography**: Calibri / Arial for headings, Georgia / Calibri for body text, Consolas for code blocks.
- **Palette**: Professional Academic / BCIT Forensic palette:
  - Primary Header: BCIT Deep Navy (`#002B49`)
  - Accent / Highlights: Forensic Teal (`#0D9488`) and Dark Cyan (`#0284C7`)
  - Dark Neutral: Charcoal (`#1F2937`)
  - Light Shading: Subtle Slate (`#F8FAFC` and `#EDF2F7`)
- **Visual Artifacts**:
  - High-fidelity terminal console screenshot cards rendered using Pillow with syntax coloring (prompt green, secret orange, headers, window chrome) embedded directly into the document.
  - Custom XML-styled docx tables with navy headers, white bold text, cell padding, and alternating zebra rows.
  - Shaded callout boxes with solid left accent borders for key analytical findings.

---

## 7. Analysis of Forensic Limitations & Reflection Questions

### 7.1 Limitation 1: Technical Failures of EXIF-Only Extraction
1. **Container Specificity**: EXIF was designed primarily for TIFF and JPEG digital camera metadata. In modern image containers like PNG, WebP, or SVG, metadata is commonly stored in format-specific chunk types (`tEXt`, `zTXt`, `iTXt` in PNG) or XML namespaces (Adobe XMP).
2. **Sub-IFD Omission**: Naive EXIF implementations only iterate IFD0. Sub-IFDs (such as ExifOffset tag 34665, GPSInfo tag 34853, and Interoperability IFD) are skipped unless explicitly navigated.
3. **Encoding Ignorance**: EXIF tag parsers do not inspect payloads for application-layer encoding (such as Base64 or custom ASCII headers).

### 7.2 Limitation 2: Flaws of Automated Risk Scoring
1. **Context Blindness**: Heuristic scoring algorithms evaluate string patterns, not operational context. Legitimate camera models, user comments, or Base64-encoded thumbnails can trigger false positives.
2. **Evasion by Adversaries**: Attackers can easily bypass regex-based heuristics by applying simple multi-byte XOR, custom substitution ciphers, or steganographic LSB embedding in pixel raster data rather than metadata fields.
3. **Weight Arbitrariness**: Point systems (+10, +5) are heuristic rankings, not calibrated probabilities. They must never be treated as conclusive forensic proof without corroborating host or network telemetry.

### 7.3 Summary of Answers to Reflection Questions
- **Q1 (Hidden messages without EXIF tags)**: PNGs store text in ancillary chunks (`tEXt`, `zTXt`, `iTXt`) and XMP packets which exist outside the EXIF IFD structures.
- **Q2 (Encoding vs Encryption & Base64 security)**: Encoding transforms data into a standard format for transport (reversible without a key; zero confidentiality). Encryption transforms data using cryptographic algorithms and keys (confidential without key). Base64 provides zero security against inspection.
- **Q3 (Preserving originals & recording hashes)**: Prevents accidental spoliation, proves data integrity in court, guarantees that extraction tools did not alter file metadata, and establishes an unbroken chain of custody.
- **Q4 (Metadata sufficiency as legal proof)**: Metadata is easily spoofed, stripped, or fabricated. Corroborating evidence is required: file system timestamps ($MFT, inode change times), network packet captures (PCAP), web server access logs, firewall egress logs, and endpoint memory/process telemetry.
- **Q5 (Connection to Labs 4 & 5)**: Expands automated reconnaissance and vulnerability scanning (Labs 4 and 5) from active network services to passive file forensics, completing the investigative lifecycle from threat detection to digital artifact examination.

---

## Conclusion & Readiness Assessment

The execution environment and forensic artifacts have been completely analyzed. All six secrets are verified, the automated scanner is prototyped, the notebook execution mechanism is validated, and the Word document generation pipeline with visual evidence screenshots is fully prepared for implementation.
