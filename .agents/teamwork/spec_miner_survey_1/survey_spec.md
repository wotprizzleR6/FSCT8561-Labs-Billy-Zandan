# Lab 6 Authoritative Specification Survey: Covert Channels in Image Metadata

**Author:** Teamwork Specification Miner  
**Date:** 2026-11-02  
**Target Course:** FSCT 8561  
**Student:** Billy Zandan (A01371854)  
**Primary Deliverables:** `Lab6/Lab6.ipynb`, `Lab6/Lab6-Billy-Zandan-A01371854.docx`, `Lab6/metadata_report.csv`

---

## 1. Executive Summary & Authoritative Specification Sources

This survey documents all authoritative specifications, technical constraints, grading criteria, evidence inventories, and deliverable standards for Lab 6 (*Covert Channels in Image Metadata*).

The authoritative specifications were mined directly from:
1. **Lab Notebook & Instructor Rubric:** `Lab6/Lab6.ipynb` (42 cells: 24 markdown, 18 code).
2. **Textbook:** *Mastering Python for Networking and Security* (2nd Edition, 2021) by Jose Manuel Ortega (Packt Publishing):
   - **Chapter 13 (pp. 784–850):** *Extracting Geolocation and Metadata from Documents, Images, and Browsers* — specifically PIL/Pillow EXIF extraction (`_getexif()`, `ExifTags.TAGS`, GPSInfo decoding, `TAGS.values()`).
   - **Chapter 14 (pp. 852–918):** *Cryptography and Steganography* — distinction between encryption and encoding, steganography concepts (LSB embedding), Stepic library, and hash integrity with `hashlib`.
3. **Target Evidence Set:** `Lab6/Images/` containing six PNG files (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`).
4. **Prior Course Precedents:** Automated scanning patterns, heuristic rules, and structured CSV reporting established in `Lab4` (traffic anomaly detection) and `Lab5` (`http_scanner.py`, `vulnerability_detector.py`).

---

## 2. Grading Rubric & Breakdown (100 Points Total)

| Rubric Component | Points | Full-Credit Expectations & Criteria | Authoritative Cell Source |
|---|:---:|---|---|
| **1. Metadata extraction and evidence documentation** | **25** | Appropriate EXIF/PNG/XMP extraction for all six images; accurate field identification; clear evidence screenshots/terminal logs and complete evidence tables. | `Lab6.ipynb` Cell 41 |
| **2. Covert-channel detection and decoding** | **25** | All six hidden fragments recovered accurately; encoded content decoded correctly (Base64 in `Music.png`, ASCII prefix stripping in `Activation.png`, XML extraction in `Dopamine.png`); extraction methods documented. | `Lab6.ipynb` Cell 41 |
| **3. Six-stage secret reconstruction** | **20** | Complete secret assembled in correct operational sequence with rigorous logical justification based on the Cyber Kill Chain / MITRE ATT&CK progression. Filename ordering explicitly rejected. | `Lab6.ipynb` Cells 33, 41 |
| **4. Automated metadata scanner and CSV report** | **20** | Scanner iterates through all six images, inspects EXIF, PNG text, and XMP metadata, identifies suspected covert fields, exports complete CSV rows (`metadata_report.csv`), and applies consistent, explainable heuristic risk scores (+10/+5/+5 rules). | `Lab6.ipynb` Cells 34, 38, 39, 41 |
| **5. Interpretations, reflections, code quality, and presentation** | **10** | Clean, reproducible, error-free Python code; thorough analysis of EXIF-only limitations and automated risk-scoring limitations; comprehensive answers to all five reflection questions; professional Word report. | `Lab6.ipynb` Cells 40, 41 |
| **Total** | **100** | **Comprehensive fulfillment across all lab dimensions.** | |

---

## 3. Forensic Evidence Inventory & Cryptographic Baselines

To maintain chain of custody and forensic integrity per Chapter 14 and Reflection Question 3, all six target images were cryptographically hashed and inspected:

| Filename | File Size (Bytes) | Dimensions (WxH) | Color Mode | MD5 Hash | SHA-256 Hash | Primary Metadata Container |
|---|:---:|:---:|:---:|---|---|---|
| `Activation.png` | 259,975 | 1415 × 781 | RGBA | `28a931ca770d9118a8286c0db414332c` | `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904` | EXIF Sub-IFD (ExifOffset / UserComment) & GPS IFD |
| `Brain-Channel.png`| 201,685 | 1854 × 541 | RGBA | `8e8a9d7276707a9f18af7c2e09c70e3a` | `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359` | EXIF 0th IFD (ImageDescription) |
| `Brain.png` | 2,354,330 | 1733 × 989 | RGBA | `5d69dd3de9b5f8557ba26d8bcc644af4` | `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e` | PNG Text Chunk (`img.info['Software']`) |
| `Chemicals.png` | 561,245 | 1726 × 821 | RGB | `694d3d3984e34b39a59e0305e837eb5f` | `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a` | PNG Text Chunk (`img.info['ImageDescription']`) |
| `Dopamine.png` | 388,411 | 1796 × 831 | RGBA | `22eedbe31ba01a541f29758f508d2a58` | `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472` | XMP Packet (`XML:com.adobe.xmp`, `exif:MakerNote`) |
| `Music.png` | 679,959 | 1504 × 843 | RGBA | `5924abe517910c58798d5567ae27323d` | `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370` | EXIF 0th IFD (Copyright) & PNG Info (`Copyright`) |

---

## 4. Metadata Extraction Mechanics & Secret Decoding Analysis

### 4.1 Image 1: `Activation.png`
- **Metadata Container:** EXIF Metadata (specifically located inside the Exif Sub-IFD pointed to by `ExifOffset` / tag 34665, accessible via `exif.get_ifd(0x8769)` or legacy `_getexif()`).
- **Discovered Field:** Tag ID 37510 (`ExifTags.TAGS[37510]` = `UserComment`).
- **Raw Value:** `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`
- **Encoding & Decoding Technique:** The raw value contains the standard EXIF 8-byte character identification code (`ASCII\x00\x00\x00`). Decoding requires stripping the initial 8 bytes and decoding the remainder with UTF-8:
  ```python
  raw_bytes = ifd[37510]
  if raw_bytes.startswith(b"ASCII\x00\x00\x00"):
      secret = raw_bytes[8:].decode("utf-8")
  ```
- **Recovered Secret Fragment:** `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`
- **Incident Stage:** Stage 2 (`VULN`).
- **Additional Indicators:** Contains camera hardware EXIF tags (Nikon D750, Adobe Lightroom 13.0) and embedded GPS tags (Latitude 40° 42' 46.08" N, Longitude 74° 0' 21.6" W) inside a synthetic graphic, indicating deliberate metadata injection.

### 4.2 Image 2: `Brain-Channel.png`
- **Metadata Container:** EXIF Metadata (0th IFD, returned directly by `img.getexif()`).
- **Discovered Field:** Tag ID 270 (`ExifTags.TAGS[270]` = `ImageDescription`).
- **Raw Value:** `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'`
- **Encoding & Decoding Technique:** None; stored as a readable ASCII string.
- **Recovered Secret Fragment:** `LATERAL: Pivot to internal Domain Controller using Mimikatz.`
- **Incident Stage:** Stage 5 (`LATERAL`).

### 4.3 Image 3: `Brain.png`
- **Metadata Container:** PNG Textual Metadata Chunk (`tEXt`/`zTXt`/`iTXt` exposed via `img.info`). Top-level `getexif()` returns 0 tags.
- **Discovered Field:** Key `'Software'` in `img.info`.
- **Raw Value:** `'RECON: Perform DNS harvesting and Subdomain enumeration.'`
- **Encoding & Decoding Technique:** None; stored as a plain text string within the PNG chunk dictionary.
- **Recovered Secret Fragment:** `RECON: Perform DNS harvesting and Subdomain enumeration.`
- **Incident Stage:** Stage 1 (`RECON`).
- **Additional Indicators:** The `'Software'` field is typically reserved for rendering or creation software names (e.g. Photoshop, GIMP). Populating it with attack reconnaissance directives is a clear indicator of covert channel abuse.

### 4.4 Image 4: `Chemicals.png`
- **Metadata Container:** PNG Textual Metadata Chunk exposed via `img.info`. Top-level `getexif()` returns 0 tags.
- **Discovered Field:** Key `'ImageDescription'` in `img.info`.
- **Raw Value:** `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'`
- **Encoding & Decoding Technique:** None; stored as plain text.
- **Recovered Secret Fragment:** `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`
- **Incident Stage:** Stage 3 (`EXPLOIT`).

### 4.5 Image 5: `Dopamine.png`
- **Metadata Container:** Adobe XMP (Extensible Metadata Platform) XML packet embedded in PNG chunk (`XML:com.adobe.xmp` and `xmp`). Top-level `getexif()` returns 0 tags.
- **Discovered Field:** Element `<exif:MakerNote>` inside the RDF Description node (`xmlns:exif="http://ns.adobe.com/exif/1.0/"`).
- **Raw Value:**
  ```xml
  <x:xmpmeta xmlns:x='adobe:ns:meta/' x:xmptk='Image::ExifTool 12.76'>
  <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
   <rdf:Description rdf:about='' xmlns:exif='http://ns.adobe.com/exif/1.0/'>
    <exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>
   </rdf:Description>
  </rdf:RDF>
  </x:xmpmeta>
  ```
- **Encoding & Decoding Technique:** XML parsing via `xml.etree.ElementTree` or regular expression search (`re.search(r'<exif:MakerNote>(.*?)</exif:MakerNote>', xmp_str)`).
- **Recovered Secret Fragment:** `PERSIST: Establish reverse shell via obfuscated cron job.`
- **Incident Stage:** Stage 4 (`PERSIST`).

### 4.6 Image 6: `Music.png`
- **Metadata Container:** EXIF 0th IFD Tag 33432 (`Copyright`) and mirrored PNG info key `'Copyright'`.
- **Discovered Field:** `Copyright` (Tag ID 33432 / `img.info['Copyright']`).
- **Raw Value:** `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='`
- **Encoding & Decoding Technique:** Standard Base64 RFC 4648 encoding. Decoded using Python's `base64` module:
  ```python
  import base64
  b64_val = "RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="
  secret = base64.b64decode(b64_val).decode("utf-8")
  ```
- **Recovered Secret Fragment:** `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`
- **Incident Stage:** Stage 6 (`EXFIL`).
- **Additional Indicators:** Padding characters (`=`) and standard Base64 character set inside a legal rights field (`Copyright`).

---

## 5. Narrative Secret Reconstruction & Cyber Attack Lifecycle

### 5.1 Reconstructed Incident Narrative (Operational Sequence)

| Stage # | Incident Stage Label | Source Image | Recovered Secret Message Narrative | Operational Tactic (MITRE ATT&CK / Kill Chain) |
|:---:|:---:|:---:|---|---|
| **1** | **RECON** | `Brain.png` | `RECON: Perform DNS harvesting and Subdomain enumeration.` | Reconnaissance (TA0043) / Active Scanning (T1595) |
| **2** | **VULN** | `Activation.png` | `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` | Weaponization & Vulnerability Analysis / Public-Facing Application (T1190) |
| **3** | **EXPLOIT** | `Chemicals.png` | `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` | Initial Access (TA0001) / Exploit Public-Facing Application (T1190) |
| **4** | **PERSIST** | `Dopamine.png` | `PERSIST: Establish reverse shell via obfuscated cron job.` | Persistence (TA0003) & Execution (TA0002) / Scheduled Task/Job: Cron (T1053.003) |
| **5** | **LATERAL** | `Brain-Channel.png` | `LATERAL: Pivot to internal Domain Controller using Mimikatz.` | Lateral Movement (TA0008) & Credential Access (TA0006) / OS Credential Dumping: LSASS (T1003.001) |
| **6** | **EXFIL** | `Music.png` | `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` | Exfiltration (TA0010) / Exfiltration Over Alternative Protocol: Protocol Tunneling (T1048.003 / T1071.004) |

### 5.2 Sequence Reasoning & Rejection of Filename Order

1. **Alignment with Standard Security Frameworks:**
   The assembled narrative reflects the textbook operational attack lifecycle (Lockheed Martin Cyber Kill Chain and MITRE ATT&CK Enterprise Framework). Every attack begins with reconnaissance (`RECON`), identifies vulnerabilities (`VULN`), delivers an exploit to gain entry (`EXPLOIT`), anchors persistent footholds (`PERSIST`), escalates privileges and expands across the subnet (`LATERAL`), and concludes with data exfiltration (`EXFIL`).
2. **Technical Dependency Logic:**
   - An adversary cannot exploit an unpatched web gateway (`EXPLOIT`) before discovering the asset and its vulnerability (`RECON`, `VULN`).
   - Lateral movement to an internal Domain Controller via Mimikatz (`LATERAL`) requires prior command execution and persistent shell access on an initial host (`PERSIST`).
   - Exfiltration of a database dump (`EXFIL`) requires successful database access and privilege elevation achieved in the intermediate exploitation and pivoting stages.
3. **Forensic Rejection of Filename Alphabetical Ordering:**
   Sorting by filename yields: `Activation.png` (VULN) → `Brain-Channel.png` (LATERAL) → `Brain.png` (RECON) → `Chemicals.png` (EXPLOIT) → `Dopamine.png` (PERSIST) → `Music.png` (EXFIL). This order is nonsensical: pivoting to a Domain Controller (LATERAL) cannot precede reconnaissance (RECON) or initial exploitation (EXPLOIT). Filenames are arbitrary forensic container labels and must not be used as operational sequencing criteria.

---

## 6. Automated Metadata Scanner & Heuristic Risk Model

### 6.1 Requirements & Specifications (Cells 34, 38, 39)
The scanner must:
1. Automatically iterate over all PNG files in `Lab6/Images/` using `pathlib.Path`.
2. Inspect multiple metadata abstraction layers:
   - EXIF 0th IFD tags via `img.getexif()`.
   - EXIF Sub-IFD tags (ExifOffset / 0x8769 and GPSInfo / 0x8825) via `exif.get_ifd()` or `_getexif()`.
   - PNG textual chunks (`tEXt`/`zTXt`/`iTXt`) via `img.info`.
   - XMP XML metadata packets via `img.info.get('XML:com.adobe.xmp')` or `img.info.get('xmp')`.
3. Detect covert-channel indicators and encoded strings (Base64 patterns, known incident keywords).
4. Apply the classroom heuristic risk model without hardcoding outputs.
5. Export results to `metadata_report.csv` using `csv.DictWriter`.

### 6.2 CSV Schema Specification
The output CSV `metadata_report.csv` must strictly include these 7 columns:
1. `filename`: Image filename (e.g. `Activation.png`).
2. `format`: Image file format (e.g. `PNG`).
3. `metadata_fields`: Comma-separated list of discovered metadata fields across EXIF, PNG text, and XMP.
4. `suspected_field`: Specific metadata tag or XML element identified as containing covert content.
5. `encoding`: Detected encoding or representation (e.g. `Base64`, `EXIF ASCII header / plain text`, `XML encapsulation`, `None (plain text)`).
6. `risk_score`: Numeric score computed by heuristic evaluation.
7. `reason`: Concise explanation of findings justifying the score.

### 6.3 Classroom Heuristic Risk Scoring Rules
- **Rule 1 (+10 points):** Confirmed covert-message field containing cybersecurity attack lifecycle keywords (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`).
- **Rule 2 (+5 points):** Suspicious encoded text requiring investigation (e.g., Base64 padding, regex pattern matching Base64 alphabets of length > 24).
- **Rule 3 (+5 points):** Additional unusual metadata indicator supported by evidence (e.g., camera hardware/GPS tags embedded in a non-photo graphic, software metadata abused for arbitrary directives, presence of XMP packet without EXIF).
- **Constraint:** Avoid double-counting an encoded payload as both an encoded indicator and an additional unusual indicator. Scores are heuristics, not forensic probabilities.

### 6.4 Expected Scanner Results Table (`metadata_report.csv`)

| filename | format | metadata_fields | suspected_field | encoding | risk_score | reason |
|---|---|---|---|---|:---:|---|
| `Activation.png` | PNG | `srgb, gamma, dpi, exif, Make, Model, Software, create-date, UserComment, GPSInfo` | `UserComment` | `EXIF ASCII header / plain text` | 15 | Confirmed covert message in EXIF UserComment (+10); camera and GPS tags embedded in graphic (+5). |
| `Brain-Channel.png` | PNG | `srgb, gamma, dpi, exif, ImageDescription` | `ImageDescription` | `None (plain text)` | 10 | Confirmed covert message in EXIF ImageDescription (+10). |
| `Brain.png` | PNG | `srgb, gamma, dpi, Software` | `Software` | `None (plain text)` | 10 | Confirmed covert message in PNG text Software chunk (+10). |
| `Chemicals.png` | PNG | `ImageDescription` | `ImageDescription` | `None (plain text)` | 10 | Confirmed covert message in PNG text ImageDescription chunk (+10). |
| `Dopamine.png` | PNG | `srgb, gamma, dpi, xmp, XML:com.adobe.xmp` | `XML:com.adobe.xmp (exif:MakerNote)` | `XML encapsulation / plain text` | 10 | Confirmed covert message inside XMP MakerNote element (+10). |
| `Music.png` | PNG | `srgb, gamma, dpi, Copyright, Make, Model, create-date, exif` | `Copyright` | `Base64` | 15 | Confirmed covert message (+10) obfuscated with Base64 encoding requiring decoding (+5). |

---

## 7. Authoritative Synthesis: Reflection Questions & Limitations

### 7.1 Reflection Question 1: Why can an image contain a hidden message even when `getexif()` returns no tags?
- **Root Cause & Architecture:** EXIF is a standard created by JEITA/CIPA specifically for JPEG and TIFF file formats to store camera exposure data. PNG is an extensible chunk-based architecture (`IHDR`, `IDAT`, `IEND`, `tEXt`, `zTXt`, `iTXt`, `eXIf`).
- **Pillow Implementation Specifics:** In PIL/Pillow, `img.getexif()` queries only the dedicated EXIF metadata block (0th IFD). If an image stores metadata in PNG textual chunks (`tEXt`/`zTXt`/`iTXt`) or Adobe XMP XML blocks (`XML:com.adobe.xmp`), `getexif()` returns an empty dictionary (0 tags).
- **Concrete Lab Evidence:** `Brain.png` and `Chemicals.png` contain secrets within PNG text chunks (`img.info`), and `Dopamine.png` stores its secret in an XMP packet. None of these are accessible via `getexif()`. Additionally, in `Activation.png`, the secret is stored in an Exif sub-IFD (`ExifOffset` tag 37510 `UserComment`), which is missed if an analyst only iterates the top-level IFD returned by `getexif()`.

### 7.2 Reflection Question 2: How is encoding different from encryption? Is Base64 a secure way to hide information?
- **Core Distinction:**
  - *Encoding* is a public, deterministic representation transformation intended to preserve data integrity across transport media that only support certain character sets (e.g. converting 8-bit binary data to 6-bit ASCII characters via Base64 per RFC 4648). It involves **no secret key**, and anyone who identifies the algorithm can reverse it instantly.
  - *Encryption* is a mathematical cryptographic transformation designed to guarantee confidentiality. It converts plaintext into ciphertext using an encryption algorithm and a secret cryptographic key (e.g. AES-256-GCM, RSA-4096). Without the key, recovering the plaintext is computationally infeasible.
- **Security Assessment:** Base64 provides **zero security or confidentiality**. It is purely syntactic obfuscation. As demonstrated with `Music.png`, any forensic analyst or automated scanner can identify the Base64 character distribution and padding (`=`) and decode the plaintext in milliseconds. Relying on Base64 violates Kerckhoffs's principle.

### 7.3 Reflection Question 3: Why should investigators preserve original files and record hashes?
- **Forensic Chain of Custody & Admissibility:** Under digital forensic standards (ISO/IEC 27037 and the Federal Rules of Evidence Rule 901/902), evidence must be proven untampered from the point of seizure to courtroom presentation. Recording cryptographic hashes (SHA-256, MD5) at acquisition creates an immutable mathematical fingerprint.
- **Verification of Bit-for-Bit Authenticity:** If a forensic image or extracted file has an identical SHA-256 hash to the original seized file, it proves non-repudiation and proves that no evidence spoliation, accidental modification, or tampering occurred during analysis.
- **Metadata Fragility:** Merely opening an image in a graphics viewer, copying it across operating systems, or launching an automated script that re-saves images can alter filesystem MAC (Modify, Access, Create) timestamps, recalculate PNG CRC32 checksums, or strip metadata chunks. Forensic investigators must work exclusively on verified forensic duplicates while preserving write-blocked originals.

### 7.4 Reflection Question 4: Can metadata alone prove that an image was edited or that an incident occurred? What corroborating evidence would you need?
- **Circumstantial Nature of Metadata:** Metadata is non-binding, mutable, and trivial to manipulate. With command-line utilities like ExifTool or standard Python scripts, an adversary can easily inject fabricated timestamps, false camera models, fake GPS coordinates, or forged narrative notes into image headers without touching image pixels. Therefore, metadata alone provides investigative leads, not definitive proof of an incident.
- **Corroborating Multi-Source Forensic Artifacts Required:**
  1. *Network Captures (PCAPs):* Corroborating DNS queries, HTTP payloads, or exfiltration streams matching the recovered timeline (e.g., DNS exfiltration tunnels matching Stage 6).
  2. *Web Application & Perimeter Logs:* WAF alerts, reverse proxy logs, and HTTP server access logs showing SQL injection attempts (Stage 3) and gateway probing (Stage 2).
  3. *Endpoint Event Logs:* Windows Security Event Logs (Event ID 4688 for process creation showing `mimikatz.exe`, Event ID 4624 for logon events, Event ID 7045 for service creation) and Linux syslog/auditd entries for cron job installations (Stage 4).
  4. *Volatile Memory (RAM):* Memory dumps analyzed via Volatility to identify active injected threads, LSASS memory handles, or active network sockets.
  5. *Filesystem Timeline Artifacts:* Windows Prefetch, Shimcache, Amcache, and USN Journal records proving file execution at the suspected incident time.

### 7.5 Reflection Question 5: How does this investigation connect to automated evidence collection in Labs 4 and 5?
- **Evolution of Automated Security Analysis Across the Course:**
  - *Lab 4 (Network Telemetry):* Focused on bulk packet capture parsing (`.pcap`), automated flow feature extraction, and algorithmic anomaly detection for botnet traffic.
  - *Lab 5 (Application Scanning):* Developed automated active HTTP security scanners (`http_scanner.py` and `vulnerability_detector.py`) to systematically test endpoints, evaluate response headers/bodies for vulnerability signatures (SQLi, XSS), apply classification rules, and generate structured CSV reports.
  - *Lab 6 (Host & File Forensics):* Extends this automated methodology to media file forensics. Rather than manually inspecting binary headers in hex editors, we construct an automated metadata extraction engine that parses heterogeneous metadata layers (EXIF, PNG info, XMP), detects obfuscated covert channels, calculates objective heuristic risk scores, and outputs standardized audit tables (`metadata_report.csv`).
- **Defensive Cohesion:** Together, Labs 4, 5, and 6 construct a complete defense-in-depth investigative framework: network layer (Lab 4), application layer (Lab 5), and file/endpoint artifact layer (Lab 6).

### 7.6 Core Forensic Limitations Analysis
1. **Limitation of EXIF-Only Extraction:**
   EXIF extraction engines inspect only the EXIF block. They are entirely blind to metadata housed in other format-specific structures, including PNG textual chunks (`tEXt`/`zTXt`/`iTXt`), Adobe XMP XML packets, ICC color profiles, and IPTC headers. Furthermore, naive EXIF scanners only evaluate the 0th IFD, missing data nested in sub-IFDs (`ExifOffset`, `GPSInfo`, `MakerNote`). In this lab, an EXIF-only tool misses 50% of the covert narrative fragments (`Brain.png`, `Chemicals.png`, `Dopamine.png`).
2. **Limitation of Automated Risk Scoring:**
   Automated scoring engines rely on static heuristics (e.g. string matching, regex patterns for Base64, metadata presence rules). These heuristics cannot comprehend semantic context, human intent, or subtle steganography. They suffer from high false-positive rates (flagging legitimate Base64 thumbnails, legal copyright notices, or authentic developer software strings) and severe false-negative rates (failing to detect LSB pixel steganography, encrypted high-entropy payloads, or covert messages hidden in mundane fields like image dimensions). Automated risk scoring is an initial triage mechanism, not a substitute for human forensic analysis.

---

## 8. Deliverable Specifications

### 8.1 Word Document Report: `Lab6/Lab6-Billy-Zandan-A01371854.docx`
Must be generated using `python-docx` and structured professionally with consistent formatting, clear headings, student identification, formatted tables, code listings, and forensic exhibits:
- **Title Block / Metadata:** Billy Zandan (A01371854), FSCT 8561, Lab 6: Covert Channels in Image Metadata.
- **Section 1: Executive Summary & Evidence Inventory:** Overview of the investigation, cryptographic hashes (MD5, SHA-256), file attributes.
- **Section 2: Forensic Metadata Evidence Table:** Comprehensive table detailing all six images (Filename, Container Type, Field Name, Raw Value, Decoding Method, Recovered Fragment, Stage).
- **Section 3: Detailed Image-by-Image Forensic Extraction Evidence:** Six subsections (`Activation.png` through `Music.png`) containing code snippets, terminal output text, and technical analysis of each container.
- **Section 4: Reconstructed Incident Narrative Secret:** Numbered 6-stage narrative, complete assembled secret transcript, and rigorous Cyber Kill Chain / MITRE ATT&CK justification.
- **Section 5: Automated Metadata Scanner & Evaluation:** Scanner architectural overview, heuristic risk scoring rules, complete formatted `metadata_report.csv` results table, and Python implementation code.
- **Section 6: Critical Forensic Limitations:** In-depth evaluations of EXIF-only extraction limitations and automated risk-scoring limitations.
- **Section 7: Reflection Questions:** Complete, detailed, authoritative answers to Questions 1 through 5.

### 8.2 Updated Notebook: `Lab6/Lab6.ipynb`
Must be executed and saved in place with all 42 cells intact:
- All `# TODO` code cells completed and executed with clean stdout:
  - Cell 8: EXIF check on `Activation.png`.
  - Cell 12: PNG text check on `Chemicals.png`.
  - Cell 19: Base64 decoding on `Music.png`.
  - Cells 22, 24, 26, 28, 30, 32: Individual investigations for all six images.
  - Cells 35, 37, 39: Automated scanner starter, single-row starter, and full scanner execution generating `metadata_report.csv`.
- Markdown cells and tables completed:
  - Cell 20: Populated investigation evidence table.
  - Cell 33: Populated 6-stage sequence and logical justification.
  - Cell 40: Fully answered reflection questions 1 through 5.

### 8.3 Scanner CSV Output: `Lab6/metadata_report.csv`
Must exist in `Lab6/` with 6 rows (plus header) matching the 7 specified columns.

---

## 9. Features Discovered Table

Report of all discovered features probed across the authoritative sources:

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|---|---|---|---|---|---|---|
| 1 | Setup & Environment | Pillow Installation & Import | Image processing library Pillow providing `PIL.Image` and `PIL.ExifTags` | `%pip -q install Pillow` | Module loaded | `ModuleNotFoundError` if Pillow is not installed | `Lab6.ipynb` Cell 2, 3 |
| 2 | Setup & Environment | Image Directory Resolution | Pathlib resolution of image directory `Images/` containing 6 target PNGs | `Path("Images")` | `Path` object, glob generator | `FileNotFoundError` if directory does not exist | `Lab6.ipynb` Cell 3 |
| 3 | Metadata Extraction | Top-Level EXIF Tag Extraction | Extracting 0th IFD tags from image using `img.getexif()` and mapping IDs with `ExifTags.TAGS` | Image object (`Brain-Channel.png`, `Music.png`) | Dictionary of tag ID -> value | Returns empty dict if no EXIF present | `Lab6.ipynb` Cell 6, Textbook Ch 13 |
| 4 | Metadata Extraction | Sub-IFD EXIF Extraction | Extracting nested IFD tags (`ExifOffset` / 0x8769 and `GPSInfo` / 0x8825) via `exif.get_ifd()` | Tag integer ID (34665, 34853) | Dictionary of sub-IFD tags | Key error or empty dict if sub-IFD absent | Textbook Ch 13, Python probe |
| 5 | Metadata Extraction | Legacy EXIF Extraction (`_getexif`) | Flattened extraction of all EXIF tags including Sub-IFD UserComment | Image object (`Activation.png`) | Dictionary of tag IDs | Returns `None` if image has no EXIF data | Textbook p. 802 |
| 6 | Metadata Extraction | PNG Textual Chunk Extraction | Extracting key-value text chunks (`tEXt`/`zTXt`/`iTXt`) via `img.info` | Image object (`Brain.png`, `Chemicals.png`) | Dictionary of info keys and string values | Keys absent if chunks not present | `Lab6.ipynb` Cell 10, 11 |
| 7 | Metadata Extraction | XMP XML Packet Extraction | Extracting Extensible Metadata Platform XML packets via `img.info['XML:com.adobe.xmp']` | Image object (`Dopamine.png`) | XML string / UTF-8 byte string | `KeyError` or `None` if XMP chunk absent | `Lab6.ipynb` Cell 14, 15 |
| 8 | Covert Channel Decoding | Base64 Payload Decoding | Decoding Base64-encoded strings embedded in metadata | Base64 ASCII string (`Music.png`) | Decoded UTF-8 plaintext string | `binascii.Error` / `ValueError` on invalid padding/alphabet | `Lab6.ipynb` Cell 17, 19 |
| 9 | Covert Channel Decoding | EXIF ASCII Prefix Stripping | Stripping standard 8-byte `ASCII\x00\x00\x00` header from EXIF UserComment | Bytes object (`Activation.png`) | Clean UTF-8 plaintext string | `UnicodeDecodeError` if bytes corrupted | Textbook Ch 13, Python probe |
| 10 | Covert Channel Decoding | XML Element Text Extraction | Parsing XML tree and extracting text from `<exif:MakerNote>` | XML string (`Dopamine.png`) | Plaintext incident string | `ET.ParseError` if XML is malformed | `Lab6.ipynb` Cell 14, Python probe |
| 11 | Forensic Integrity | Cryptographic Hashing | Calculating SHA-256 and MD5 hashes of evidence images | Raw file bytes | Hexadecimal hash digests | `IOError` if file unreadable | Textbook Ch 14, Reflection Q3 |
| 12 | Secret Reconstruction | Operational Kill Chain Ordering | Ordering 6 recovered secret fragments by attack lifecycle rather than filename | 6 secret fragments with stage tags | Ordered 6-stage narrative | Misordered narrative if sorted by filename | `Lab6.ipynb` Cell 33, 41 |
| 13 | Automated Scanner | Automated Multi-Container Iteration | Looping over all images and harvesting EXIF, PNG info, and XMP | Directory path `Images/` | Consolidated metadata list per image | Graceful handling of missing containers | `Lab6.ipynb` Cell 34, 38, 39 |
| 14 | Automated Scanner | Heuristic Covert Channel Detector | Detecting incident keywords and encoded payloads across metadata fields | Metadata dictionary | Suspected field name, encoding type | Returns empty string if no anomalies | `Lab6.ipynb` Cell 34, 38, 39 |
| 15 | Automated Scanner | Heuristic Risk Scoring Engine | Computing numerical risk score based on +10/+5/+5 rules | Detected indicators | Integer risk score, text justification | Score remains 0 if image is benign | `Lab6.ipynb` Cell 34, 38, 39 |
| 16 | Automated Scanner | CSV Audit Report Export | Exporting scan observations to `metadata_report.csv` | List of result dictionaries | Saved `metadata_report.csv` file | `IOError` / `csv.Error` on write failure | `Lab6.ipynb` Cell 38, 39 |
| 17 | Forensic Analysis | EXIF-Only Limitation Evaluation | Documenting architectural blind spots of relying only on `getexif()` | Forensic observations | Critical limitation essay | Incomplete report if omitted | `Lab6.ipynb` Cell 41 |
| 18 | Forensic Analysis | Risk-Scoring Limitation Evaluation | Documenting architectural false-positive/negative limits of heuristic scoring | Risk model analysis | Critical limitation essay | Incomplete report if omitted | `Lab6.ipynb` Cell 41 |
| 19 | Deliverable Reporting | Word Document Generation | Generating professional `.docx` report satisfying all rubric points | Formatted text, tables, code listings | Valid `Lab6-Billy-Zandan-A01371854.docx` | `PackageNotFoundError` if template invalid | `ORIGINAL_REQUEST.md`, Cell 41 |
| 20 | Deliverable Reporting | In-Place Notebook Execution | Populating all notebook markdown and code cells with execution state | Python code, markdown text | Updated `Lab6.ipynb` with outputs | Execution exception halts run | `ORIGINAL_REQUEST.md`, Cell 41 |

---

## 10. Edge Cases Table

Report of edge cases probed and observed during specification discovery:

| # | Feature | Input / Condition | Observed Behavior & Forensic Handling |
|---|---|---|---|
| 1 | Top-Level `getexif()` on PNG files | Images with metadata stored exclusively in PNG text chunks or XMP (`Brain.png`, `Chemicals.png`, `Dopamine.png`) | `getexif()` returns an empty dictionary (`len(exif) == 0`). An analyst or tool assuming `getexif()` is exhaustive misses all covert channels. Must probe `img.info` directly. |
| 2 | EXIF Sub-IFD UserComment Tag | `Activation.png` containing secret in ExifOffset IFD (tag 37510) | Top-level `getexif()` items do not enumerate tag 37510 directly in Pillow unless `exif.get_ifd(0x8769)` or `_getexif()` is called. Furthermore, the value contains an 8-byte prefix `b'ASCII\x00\x00\x00'` which must be sliced before decoding. |
| 3 | Redundant Field Storage | `Music.png` and `Activation.png` storing metadata in both EXIF blocks and PNG info dictionaries | In `Music.png`, `'Copyright'` appears in both EXIF tag 33432 and `img.info['Copyright']`. In `Activation.png`, `'Make'` and `'Model'` appear in both. Automated scanners must deduplicate fields when compiling `metadata_fields`. |
| 4 | XMP Packet Encoding Variations | `Dopamine.png` storing XMP under both `'xmp'` (raw bytes) and `'XML:com.adobe.xmp'` (decoded string) | `img.info` contains both keys. If reading `'xmp'`, the byte string must be decoded (`.decode('utf-8', errors='replace')`). The XML contains RDF namespaces (`xmlns:exif`), requiring namespace-aware XML search or regex. |
| 5 | Base64 Obfuscation Detection | `Music.png` containing `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='` | String exhibits Base64 characteristics: length is multiple of 4 (76 chars), valid Base64 character set, and ends with `=` padding. Naive detectors might misidentify or fail to decode; heuristic must validate decoding before flagging. |
| 6 | Synthetic Camera Metadata in Graphic Images | Non-photographic diagram images (`Activation.png`, `Music.png`) containing camera hardware tags (Nikon D750, Olympus OM-D) | Digital drawings and diagrams do not originate from physical camera sensors. The presence of camera EXIF tags, shutter profiles, and GPS coordinates in vector/diagram graphics is an anomalous indicator of metadata injection (+5 risk). |
| 7 | Filename Ordering vs Narrative Sequence | Alphabetical order of filenames (`Activation`, `Brain-Channel`, `Brain`, `Chemicals`, `Dopamine`, `Music`) | Sorting chronologically by filename produces `VULN` (2) → `LATERAL` (5) → `RECON` (1) → `EXPLOIT` (3) → `PERSIST` (4) → `EXFIL` (6), violating operational attack logic. The narrative sequence must strictly follow stage prefix labels. |
| 8 | Double-Counting Heuristic Penalty | Image with encoded covert message (`Music.png`) | Scoring rule strictly prohibits double-counting an encoded payload as both an encoded indicator (+5) and an unusual indicator (+5). Total score is capped at 15 (+10 confirmed covert message, +5 encoded value). |
| 9 | Non-Ascii / Null-Byte Chunks in Raw EXIF | Raw EXIF chunk in `img.info['exif']` | `img.info['exif']` contains raw binary TIFF headers (`b'Exif\x00\x00II*...'`). Treating all `img.info` values as strings causes unhandled encoding exceptions. Scanner must filter by `isinstance(v, str)` or handle binary decoding. |

---

## 11. Verification & Compliance Checklist

- [x] All 42 notebook cells from `Lab6.ipynb` audited and mapped.
- [x] Grading rubric points (25 + 25 + 20 + 20 + 10 = 100 pts) fully defined.
- [x] All 6 partial secrets and incident stages recovered and verified.
- [x] All 6 cryptographic hashes (MD5, SHA-256) calculated and logged.
- [x] Reconstructed six-stage narrative justified against Cyber Kill Chain and MITRE ATT&CK.
- [x] Classroom heuristic risk scoring rules (+10/+5/+5) and CSV schema documented.
- [x] All 5 reflection questions and 2 technical limitations comprehensively synthesized.
- [x] Deliverable specifications for Word document (`Lab6-Billy-Zandan-A01371854.docx`) and updated notebook (`Lab6.ipynb`) established.
- [x] Features Discovered table and Edge Cases table completed per Specification Miner standard.
