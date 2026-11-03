# Investigation & Architecture Report: Metadata Scanner & Lab6 Instructions Plan

## 1. Observation

### 1.1 `metadata_scanner.py` Codebase & Execution Mechanics
- **File Location**: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py` (542 lines).
- **Core Architecture & Key Components**:
  - **Imports (Lines 1–19)**: Uses standard library packages (`argparse`, `base64`, `csv`, `dataclasses`, `io`, `os`, `pathlib.Path`, `re`, `sys`, `typing`) plus external `PIL.Image`, `PIL.ExifTags`, and `defusedxml.ElementTree` with fallback to `xml.etree.ElementTree`.
  - **Contract Fieldnames (Lines 23–31)**:
    ```python
    CSV_FIELDNAMES = [
        "filename",
        "format",
        "metadata_fields",
        "suspected_field",
        "encoding",
        "risk_score",
        "reason",
    ]
    ```
  - **Ground Truth Pattern Constants (Lines 34–60)**:
    - `LIFECYCLE_STAGE_PREFIXES = ("RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:")`
    - `THREAT_KEYWORDS = ("dns harvesting", "subdomain enumeration", "cve-2024-", "cve-", "sql injection", "reverse shell", "mimikatz", "dns covert channel", "domain controller", "cron job", "bypass waf", "payload")`
    - `EXIF_ASCII_PREFIX = b"ASCII\x00\x00\x00"` (EXIF standard 8-byte prefix for `UserComment`).
  - **Data Model (Lines 66–90)**:
    `ImageScanResult` dataclass holding `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`, and `recovered_secret: str = ""`. Its `to_csv_dict()` method converts the instance into exactly the 7 required CSV keys.
  - **Windows Console Hardening (Lines 94–102)**:
    `configure_utf8_streams()` calls `reconfigure(encoding="utf-8")` on `sys.stdout` and `sys.stderr` to prevent Windows `cp1252` `UnicodeEncodeError`.
  - **Multi-Layer Metadata Extraction (Lines 107–206)**:
    - `collect_metadata_field_names(img)`: aggregates field names across native PNG chunks (`img.info.keys()`), EXIF IFD0 tags (`ImageDescription`, `UserComment`, `Copyright`), Sub-IFD tags (`UserComment`), and GPS Sub-IFD (`GPSInfo`).
    - `extract_metadata_candidates(img)`: extracts candidate key-value pairs from `img.info` (including Adobe XMP `XML:com.adobe.xmp` parsed via ElementTree or regex fallback), EXIF IFD0 tags, Exif Sub-IFD (`tag 34665`), and GPS IFD (`tag 34853`). Records context flags: `has_gps`, `has_camera`, `has_xmp`.
  - **De-obfuscation & Covert Channel Matching (Lines 213–270)**:
    - Tests for EXIF UserComment 8-byte ASCII prefix (`b"ASCII\x00\x00\x00"`).
    - Tests for RFC 4648 Base64 strings (length $\ge 16$, modulo 4, valid character set, and printable ASCII ratio $> 0.85$).
    - Tests for XMP XML element encapsulation (`MakerNote` or `XML`).
    - Matches candidate text against `LIFECYCLE_STAGE_PREFIXES` or `THREAT_KEYWORDS`.
  - **Risk Scoring Engine (Lines 275–314)**:
    - Implements an additive heuristic model:
      - $+10$: Confirmed covert message detected in metadata.
      - $+5$: Encoded/obfuscated payload requiring computational decoding (Base64).
      - $+5$: Anomalous container or metadata indicator (camera hardware + GPS tags embedded on graphic, OR unusual XMP container/MakerNote).
      - **Double-Counting Guardrail**: The $+5$ modifiers are structured as mutually exclusive `if / elif / elif` branches, capping any additional modifier at $+5$. Scores are strictly bounded: 0 (benign), 10 (plaintext covert message), or 15 (encoded or container anomaly).
  - **Directory Scanning & Output Resolution (Lines 367–476)**:
    - Discovers all `*.png` files in target directory, sorted alphabetically.
    - Resolves relative paths dynamically to allow seamless execution from either repository root or `Lab6/`.
    - CLI arguments defined via `argparse`:
      - `-i`, `--images`, `--image-dir`, `-d` (default: `"Images"`)
      - `-o`, `--output`, `--output-csv` (default: `"metadata_report.csv"`)
      - `-v`, `--verbose` (prints detailed per-image diagnostic output including recovered secret)
      - `-q`, `--quiet` (suppresses console progress and summary banners)

### 1.2 Execution Verification & Generated CSV Output
- **Execution Command from Workspace Root**:
  ```powershell
  python Lab6\metadata_scanner.py -i Lab6\Images -o Lab6\metadata_report.csv -v
  ```
- **Exit Code**: `0`
- **Console Output**:
  ```text
  Scanning directory: C:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images
  Found 6 PNG image(s) to inspect.

  [1/6] Scanned Activation.png
        Suspected Field : UserComment
        Encoding        : EXIF ASCII header / plain text
        Risk Score      : 15
        Reason          : Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5).
        Recovered Secret: VULN: Identify unpatched CVE-2024-XXXX in web gateway.

  [2/6] Scanned Brain-Channel.png
        Suspected Field : ImageDescription
        Encoding        : None (plain text)
        Risk Score      : 10
        Reason          : Confirmed covert message in ImageDescription (+10).
        Recovered Secret: LATERAL: Pivot to internal Domain Controller using Mimikatz.

  [3/6] Scanned Brain.png
        Suspected Field : Software
        Encoding        : None (plain text)
        Risk Score      : 10
        Reason          : Confirmed covert message in Software (+10).
        Recovered Secret: RECON: Perform DNS harvesting and Subdomain enumeration.

  [4/6] Scanned Chemicals.png
        Suspected Field : ImageDescription
        Encoding        : None (plain text)
        Risk Score      : 10
        Reason          : Confirmed covert message in ImageDescription (+10).
        Recovered Secret: EXPLOIT: Deploy SQL Injection payload to bypass WAF.

  [5/6] Scanned Dopamine.png
        Suspected Field : XML:com.adobe.xmp (exif:MakerNote)
        Encoding        : XML encapsulation / plain text
        Risk Score      : 15
        Reason          : Confirmed covert message in XML:com.adobe.xmp (exif:MakerNote) (+10); unusual container / embedded XMP packet (+5).
        Recovered Secret: PERSIST: Establish reverse shell via obfuscated cron job.

  [6/6] Scanned Music.png
        Suspected Field : Copyright
        Encoding        : Base64
        Risk Score      : 15
        Reason          : Confirmed covert message in Copyright (+10); obfuscated with Base64 encoding requiring decoding (+5).
        Recovered Secret: EXFIL: Tunnel compressed database dump via DNS Covert Channel.
  ```
- **CSV Verification (`Lab6\metadata_report.csv`)**:
  - Header line: `filename,format,metadata_fields,suspected_field,encoding,risk_score,reason` (exact 7 columns).
  - Row count: Exactly 1 header row + 6 data rows.
  - Verbatim CSV contents:
    ```csv
    filename,format,metadata_fields,suspected_field,encoding,risk_score,reason
    Activation.png,PNG,"srgb, gamma, dpi, exif, Make, Model, Software, create-date, UserComment, GPSInfo",UserComment,EXIF ASCII header / plain text,15,Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5).
    Brain-Channel.png,PNG,"srgb, gamma, dpi, exif, ImageDescription",ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
    Brain.png,PNG,"srgb, gamma, dpi, Software",Software,None (plain text),10,Confirmed covert message in Software (+10).
    Chemicals.png,PNG,ImageDescription,ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
    Dopamine.png,PNG,"srgb, gamma, dpi, xmp, XML:com.adobe.xmp",XML:com.adobe.xmp (exif:MakerNote),XML encapsulation / plain text,15,Confirmed covert message in XML:com.adobe.xmp (exif:MakerNote) (+10); unusual container / embedded XMP packet (+5).
    Music.png,PNG,"srgb, gamma, dpi, Copyright, Make, Model, create-date, exif",Copyright,Base64,15,Confirmed covert message in Copyright (+10); obfuscated with Base64 encoding requiring decoding (+5).
    ```

### 1.3 Target Images Forensic Baseline Data
Direct cryptographic and metadata analysis confirms:
| Image File | SHA-256 Hash | Dimensions / Format | EXIF Tags Count | Primary Metadata Layer |
|---|---|---|---|---|
| `Activation.png` | `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904` | 800x600 PNG | 10 tags + GPS | EXIF Sub-IFD (`UserComment`) |
| `Brain-Channel.png` | `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359` | 800x600 PNG | 5 tags | EXIF IFD0 (`ImageDescription`) |
| `Brain.png` | `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e` | 800x600 PNG | 0 tags | PNG native text chunk (`Software`) |
| `Chemicals.png` | `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a` | 800x600 PNG | 0 tags | PNG native text chunk (`ImageDescription`) |
| `Dopamine.png` | `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472` | 800x600 PNG | 0 tags | Adobe XMP XML packet (`exif:MakerNote`) |
| `Music.png` | `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370` | 800x600 PNG | 9 tags | EXIF IFD0 / PNG text (`Copyright`) |

### 1.4 Windows UTF-8 BOM Console Encoding Quirk
- **Direct Observation**: When running `print(img.info.get('XML:com.adobe.xmp'))` directly on Windows with default `cp1252` console encoding:
  `UnicodeEncodeError: 'charmap' codec can't encode character '\ufeff' in position 17: character maps to <undefined>`.
- **Cause**: The XMP packet embedded by ExifTool contains the UTF-8 Byte Order Mark (`\ufeff`) at byte offset 0 (`<?xpacket begin='\ufeff'...`).
- **Resolution**: Code snippets provided in `Lab6_Instructions.md` must either call `val.lstrip('\ufeff')`, use `sys.stdout.reconfigure(encoding='utf-8')`, or decode with `errors='replace'`.

### 1.5 Academic & Forensic Textbook Alignment
- **Textbook 1: Jose Manuel Ortega, *Mastering Python for Networking and Security - Second Edition* (Packt 2021)**:
  - Chapter 14/15 (pages 799–810): Covers `PIL` / `Pillow`, importing `PIL.ExifTags`, using `_getexif()` / `getexif()`, iterating tags via `TAGS.get()`, extracting GPS coordinates from GPS IFD, and integrating command-line tools like `exiftool`.
- **Textbook 2: Fahad Ali Sarwar, *Python Ethical Hacking From Scratch* (Packt 2021)**:
  - Chapter 1 & 8 (pages 37, 172): Covers attack lifecycle phases, incident response, covering tracks, persistence mechanisms, and the forensic necessity of maintaining file hashes and corroborating log telemetry.

---

## 2. Logic Chain

### 2.1 Logic for Scanner Execution & Robustness
1. **Observation**: `metadata_scanner.py` provides an `argparse` CLI with defaults `Images` and `metadata_report.csv`.
2. **Observation**: `resolve_paths()` inspects both current working directory and script directory.
3. **Inference**: The script can be executed without error regardless of whether the user is in the repository root (`c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan`) or inside `Lab6/`.
4. **Conclusion**: The instruction guide must present both standard invocation commands clearly:
   - Root command: `python Lab6\metadata_scanner.py -i Lab6\Images -o Lab6\metadata_report.csv -v`
   - Subfolder command: `cd Lab6; python metadata_scanner.py -v`

### 2.2 Logic for 7-Column CSV Format & Contract Conformance
1. **Observation**: R3 and the grading rubric require 7 specific columns: `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`.
2. **Observation**: `CSV_FIELDNAMES` and `ImageScanResult.to_csv_dict()` in `metadata_scanner.py` map exactly to these 7 keys.
3. **Observation**: The verified CSV output contains exactly these 7 columns with zero omissions or extra columns.
4. **Conclusion**: The output matches the grading rubric and contract expectations with 100% fidelity.

### 2.3 Logic for Risk Scoring Formula & Limitations
1. **Observation**: Rubric specifies: +10 for confirmed covert-message field, +5 for suspicious encoded value requiring investigation, +5 for additional unusual metadata indicator, avoiding double-counting.
2. **Observation**: `calculate_risk_score` awards 10 base points for `is_covert`, and an additional 5 points if Base64, camera/GPS on graphic, or XMP is present. Mutually exclusive branching caps the score at 15.
3. **Analytical Deductions on Scanner Limitations**:
   - *Heuristic Keyword Brittleness (False Negatives)*: The detector relies on known prefixes (`RECON:`, `VULN:`, etc.) and threat keywords (`mimikatz`, `dns harvesting`). If an adversary uses XOR obfuscation, modern steganography, non-English terminology, or innocuous phrasing ("Meeting rescheduled to Tuesday"), the score is 0.
   - *Heuristic Fragility / False Positives*: Benign administrative images containing embedded base64 thumbnails, technical diagrams displaying CVE numbers, or legitimate software tags could trigger false alerts.
   - *Base64 Heuristic Constraints*: Legitimate GUIDs, session tokens, or cryptographic hashes may trigger the Base64 pattern filter ($len \ge 16$, printable ratio $> 0.85$).
   - *Container vs Pixel Blind Spot*: The scanner analyzes only structured metadata headers (EXIF, PNG info, XMP). It does not analyze image pixel data (e.g. LSB steganography) or file slack.
   - *Static Weight Ceiling*: By capping modifiers at +5, the system cannot differentiate between an image with a single anomaly vs an image combining Base64 obfuscation, fake GPS coordinates, and foreign camera hardware.
   - *Context Ignorance*: The automated scanner cannot evaluate environmental intent (e.g. whether an image is an outdoor field photo that legitimately requires GPS, or a synthetic digital diagram where GPS is an anomaly).

### 2.4 Logic for Reconstructed Narrative Timeline
1. **Observation**: The 6 recovered secrets begin with distinct operational prefixes:
   - `Brain.png`: `RECON: Perform DNS harvesting and Subdomain enumeration.`
   - `Activation.png`: `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`
   - `Chemicals.png`: `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`
   - `Dopamine.png`: `PERSIST: Establish reverse shell via obfuscated cron job.`
   - `Brain-Channel.png`: `LATERAL: Pivot to internal Domain Controller using Mimikatz.`
   - `Music.png`: `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`
2. **Inference**: These prefixes correspond to the standard Cyber Kill Chain / MITRE ATT&CK enterprise lifecycle:
   - Stage 1: Reconnaissance (harvesting target information)
   - Stage 2: Weaponization / Vulnerability Scanning (identifying vulnerable gateway)
   - Stage 3: Exploitation (delivering SQLi exploit to bypass perimeter security)
   - Stage 4: Persistence (establishing recurring access via cron job)
   - Stage 5: Lateral Movement (pivoting from DMZ to core Domain Controller via Mimikatz credential dumping)
   - Stage 6: Exfiltration (covert exfiltration of sensitive database dump over DNS tunnel)
3. **Conclusion**: Chronological narrative sequencing is objectively determined by operational attack progression, disproving the alphabetical filename order.

---

## 3. Caveats
1. **No Source Modification**: Investigation was conducted strictly read-only. `Lab6.ipynb` remains unmodified.
2. **Operating System Encoding**: The default code page in Windows cmd/PowerShell is `cp1252`. Code snippets for student execution in `Lab6_Instructions.md` must handle UTF-8 stream re-configuration to prevent crashes when printing `Dopamine.png`'s XMP metadata containing BOM `\ufeff`.
3. **Dependency Assumptions**: Tested on Python 3.14.8 with `Pillow 12.0.0`. `Pillow` is the only mandatory external library; `defusedxml` is optional as standard library `xml.etree.ElementTree` is used as a verified fallback.

---

## 4. Conclusion & Plan for `Lab6_Instructions.md`

### 4.1 Master Architectural Layout for `Lab6_Instructions.md`
The instruction document must be structured as follows:

```markdown
# Lab 6 Completion Guide: Covert Channels in Image Metadata
**FSCT 8561: Practical Step-by-Step Investigative & Forensic Protocol**

## 1. Objective & Prerequisites
- 1.1 Lab Scope & Learning Outcomes
- 1.2 System Requirements & Dependencies (Python 3.8+, Pillow, defusedxml)
- 1.3 Repository & Directory Layout
- 1.4 Ethical Boundaries & Non-Execution Directive

## 2. Step 1: Environment Setup & Forensic Baseline
- 2.1 Python Environment & Package Installation
- 2.2 Verifying Target PNG Images
- 2.3 Establishing Cryptographic Baselines (Pre-Inspection SHA-256 Hashes)

## 3. Step 2: EXIF Metadata Extraction
- 3.1 EXIF Architecture & Pillow Interface (`img.getexif()`, `ExifTags.TAGS`)
- 3.2 Advanced IFD Parsing: Sub-IFD and GPS Sub-IFD
- 3.3 Practical Extraction Walkthrough:
  - Inspecting `Brain-Channel.png` (Direct IFD0 `ImageDescription`)
  - Inspecting `Activation.png` (Exif Sub-IFD `UserComment` & GPS Anomaly)
- 3.4 Forensic Interpretation of EXIF Extraction Limits

## 4. Step 3: PNG Text Chunk Extraction
- 4.1 PNG Native Text Chunks (`tEXt`, `zTXt`, `iTXt`) and Pillow's `img.info`
- 4.2 Practical Extraction Walkthrough:
  - Inspecting `Brain.png` (Native `Software` text chunk)
  - Inspecting `Chemicals.png` (Native `ImageDescription` text chunk)
- 4.3 Why EXIF Parsers Fail on Native PNG Text Chunks

## 5. Step 4: XMP Packet Extraction & XML Parsing
- 5.1 Adobe Extensible Metadata Platform (XMP) Inside PNG Containers
- 5.2 Handling Character Encodings & UTF-8 BOM (`\ufeff`) on Windows Consoles
- 5.3 XML Parsing Code Snippet (`xml.etree.ElementTree` & Regex Fallback)
- 5.4 Practical Extraction Walkthrough:
  - Inspecting `Dopamine.png` (Extracting `exif:MakerNote` from XMP)

## 6. Step 5: Base64 Decoding Procedure
- 6.1 Identifying Obfuscated & Encoded Metadata
- 6.2 Forensic Base64 Validation Criteria (Padding, Length, Printable Entropy)
- 6.3 Practical Decoding Walkthrough:
  - Inspecting & Decoding `Music.png` (`Copyright` field Base64 string)
- 6.4 Theoretical Distinction: Encoding vs Encryption in Incident Forensics

## 7. Step 6: Narrative Sequencing Rationale & Timeline Construction
- 7.1 Reconstructing the Six-Stage Cyber Incident Narrative
- 7.2 Cyber Kill Chain & MITRE ATT&CK Framework Mapping
- 7.3 Rejecting Alphabetical Artifact Decoys: Methodological Justification
- 7.4 Master Incident Timeline Matrix

## 8. Step 7: Automated Metadata Scanner Execution
- 8.1 Scanner Architecture & Execution Pipeline (`metadata_scanner.py`)
- 8.2 Command Line Execution (Root vs Lab6 Subdirectory Invocations)
- 8.3 The 7-Column CSV Output Schema Verification
- 8.4 Risk Scoring Formula, Weights, and Modifier Mechanics
- 8.5 Critical Limitations of Automated Heuristic Scanners

## 9. Step 8: Forensic Evidence Verification & Submission Checklist
- 9.1 Integrity Verification: Post-Inspection SHA-256 Hash Matching
- 9.2 Verification of Notebook Immutability (`Lab6.ipynb`)
- 9.3 Deliverables Compilation Guide (`Lab6_Report.md`, `metadata_report.csv`, PDF submission)
- 9.4 100-Point Grading Rubric Compliance Checklist
```

### 4.2 Detailed Content Specifications for Key Steps

#### Step 1: Environment Setup
- Provide exact terminal commands:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install Pillow defusedxml
  ```
- Include python verification snippet for file presence and SHA-256 calculation.

#### Step 2: EXIF Metadata Extraction
- Provide concise, reproducible Python snippet:
  ```python
  from pathlib import Path
  from PIL import Image, ExifTags

  image_path = Path("Images") / "Brain-Channel.png"
  with Image.open(image_path) as img:
      exif = img.getexif()
      print(f"EXIF tags count: {len(exif)}")
      for tag_id, value in exif.items():
          tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
          print(f"  {tag_name}: {value}")
  ```
- Sub-IFD inspection snippet for `Activation.png`:
  ```python
  image_path = Path("Images") / "Activation.png"
  with Image.open(image_path) as img:
      exif = img.getexif()
      sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
      raw_comment = sub_ifd.get(37510)  # UserComment
      if isinstance(raw_comment, bytes) and raw_comment.startswith(b"ASCII\x00\x00\x00"):
          print("UserComment:", raw_comment[8:].decode("utf-8"))
      gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
      print("GPS Coordinates:", gps_ifd)
  ```

#### Step 3: PNG Text Chunk Extraction
- Provide snippet for reading `img.info`:
  ```python
  from pathlib import Path
  from PIL import Image

  for filename in ["Brain.png", "Chemicals.png"]:
      with Image.open(Path("Images") / filename) as img:
          print(f"=== {filename} ===")
          for key, val in img.info.items():
              if isinstance(val, str):
                  print(f"  {key}: {val}")
  ```

#### Step 4: XMP Packet Extraction
- Provide snippet with Windows UTF-8 console stream hardening and BOM stripping:
  ```python
  import sys
  import xml.etree.ElementTree as ET
  from pathlib import Path
  from PIL import Image

  if hasattr(sys.stdout, "reconfigure"):
      sys.stdout.reconfigure(encoding="utf-8")

  with Image.open(Path("Images") / "Dopamine.png") as img:
      xmp_raw = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
      if isinstance(xmp_raw, bytes):
          xmp_raw = xmp_raw.decode("utf-8", errors="replace")
      xmp_clean = xmp_raw.lstrip("\ufeff")
      
      root = ET.fromstring(xmp_clean)
      for elem in root.iter():
          if elem.tag.endswith("MakerNote") and elem.text:
              print("XMP MakerNote:", elem.text.strip())
  ```

#### Step 5: Base64 Decoding Procedure
- Provide decoding snippet for `Music.png`:
  ```python
  import base64
  from pathlib import Path
  from PIL import Image

  with Image.open(Path("Images") / "Music.png") as img:
      raw_copyright = img.info.get("Copyright")
      print("Raw Copyright:", raw_copyright)
      decoded_secret = base64.b64decode(raw_copyright).decode("utf-8")
      print("Decoded Secret:", decoded_secret)
  ```

#### Step 6: Narrative Sequencing Rationale & Timeline Construction
- Tabulate the reconstructed 6-stage sequence:
  1. `Brain.png` (Stage 1 - RECON): `RECON: Perform DNS harvesting and Subdomain enumeration.`
  2. `Activation.png` (Stage 2 - VULN): `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`
  3. `Chemicals.png` (Stage 3 - EXPLOIT): `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`
  4. `Dopamine.png` (Stage 4 - PERSIST): `PERSIST: Establish reverse shell via obfuscated cron job.`
  5. `Brain-Channel.png` (Stage 5 - LATERAL): `LATERAL: Pivot to internal Domain Controller using Mimikatz.`
  6. `Music.png` (Stage 6 - EXFIL): `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`
- Justify narrative order via Cyber Kill Chain phases and explain why alphabetical naming is an intentional decoy.

#### Step 7: Automated Metadata Scanner Execution
- Provide exact CLI execution commands:
  ```powershell
  # From workspace root:
  python Lab6\metadata_scanner.py -i Lab6\Images -o Lab6\metadata_report.csv -v

  # From Lab6 directory:
  cd Lab6
  python metadata_scanner.py -v
  ```
- Explain the 7 output CSV columns and the scoring model:
  - Base Score: $+10$ for confirmed covert message.
  - Modifiers: $+5$ for Base64, $+5$ for container anomaly (GPS/camera on graphic or XMP container).
  - Mutually exclusive branching prevents double-counting (maximum single image score is 15).
- Detail the 6 core limitations of heuristic scanning for inclusion in reflection analyses.

#### Step 8: Forensic Evidence Verification & Integrity Checks
- Explain pre- and post-analysis hash comparison.
- Validate non-modification of `Lab6.ipynb`.
- Confirm rubric coverage: 25 pts Evidence Table, 25 pts Decoding, 20 pts Reconstructed Secret, 20 pts Scanner & CSV, 10 pts Reflection & Quality.

---

## 5. Verification Method

### 5.1 Independent Reproduction Commands
To verify all findings independently:

1. **Verify Scanner Execution & 7-Column CSV**:
   ```powershell
   python Lab6\metadata_scanner.py -i Lab6\Images -o Lab6\metadata_report.csv -v
   ```
   *Expected outcome*: Scans 6 images, logs recovery of 6 secret fragments, writes 7-column CSV with 6 data rows to `Lab6\metadata_report.csv`.

2. **Verify CSV Column Schema**:
   ```powershell
   python -c "import csv; f=open('Lab6/metadata_report.csv'); r=csv.reader(f); cols=next(r); print('Columns:', cols); assert cols==['filename', 'format', 'metadata_fields', 'suspected_field', 'encoding', 'risk_score', 'reason'], 'Schema mismatch!'; print('Rows:', len(list(r)))"
   ```
   *Expected outcome*: Confirms exact 7 column names and exactly 6 data rows.

3. **Verify Target Image SHA-256 Baselines**:
   ```powershell
   python -c "import hashlib, glob, pathlib; [print(p.name, hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(pathlib.Path('Lab6/Images').glob('*.png'))]"
   ```
   *Expected outcome*: Matches all 6 verified SHA-256 hashes recorded in Section 1.3.

4. **Verify Notebook Immutability**:
   ```powershell
   git status --porcelain Lab6\Lab6.ipynb
   ```
   *Expected outcome*: Clean status (no modifications to `Lab6.ipynb`).

### 5.2 Invalidation Conditions
- Any modification to `Lab6\Lab6.ipynb` invalidates acceptance criteria.
- Alteration of any target PNG image hash indicates tampering/spoliation.
- CSV schema missing any of the 7 specified column names invalidates R3.
- Failure to handle Windows UTF-8 BOM in XMP parsing invalidates reproducible execution.
