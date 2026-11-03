# Comprehensive Forensic Specification & Extraction Report: Lab 6 Image Metadata Covert Channels

**Working Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\survey_spec_miner_1`  
**Target Investigation Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6`  
**Investigator Archetype:** Specification Miner (`survey_spec_miner_1`)  
**Timestamp:** 2026-11-02T23:16:00Z  

---

## 1. Observation

Direct forensic observations were obtained through binary inspection, byte-level PNG chunk parsing, EXIF IFD parsing, XML/XMP analysis, Python script execution, and textbook examination.

### 1.1 Target Image Corpus & Cryptographic Hashes
All six images located in `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images/` were evaluated. Cryptographic SHA-256 hashes were calculated directly from the filesystem to establish the forensic chain of custody:

| Image File | File Size (Bytes) | SHA-256 Checksum | Dimensions & Mode | Primary Metadata Layers Present |
|---|---|---|---|---|
| `Activation.png` | 259,975 bytes | `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904` | 1415×781 (RGBA) | `eXIf` chunk (510 B), `tEXt` chunks (Make, Model, Software, create-date), `tIME` |
| `Brain-Channel.png` | 201,685 bytes | `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359` | 1854×541 (RGBA) | `eXIf` chunk (152 B), standard PNG header chunks (`sRGB`, `gAMA`, `pHYs`) |
| `Brain.png` | 2,354,330 bytes | `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e` | 1733×989 (RGBA) | `tEXt` chunk (65 B: Software), standard PNG chunks; **No EXIF**, **No XMP** |
| `Chemicals.png` | 561,245 bytes | `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a` | 1726×821 (RGB) | `tEXt` chunk (69 B: ImageDescription); **No EXIF**, **No XMP** |
| `Dopamine.png` | 388,411 bytes | `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472` | 1796×831 (RGBA) | `iTXt` chunk (445 B: `XML:com.adobe.xmp`); **No EXIF** |
| `Music.png` | 679,959 bytes | `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370` | 1504×843 (RGBA) | `eXIf` chunk (382 B), `tEXt` chunks (Copyright, Make, Model, create-date), `tIME` |

### 1.2 Binary Chunk Structure and Metadata Layers
Direct binary analysis of PNG chunk structures via `inspect_chunks.py` yielded the following verbatim chunk sequences:

1. **`Activation.png`**:
   - `eXIf` chunk: Length 510 bytes. Contains TIFF header (`MM\x00*`), IFD0 entries (Make=`Nikon`, Model=`D750`, Software=`Adobe Lightroom 13.0`, DateTime=`2025:02:02 10:15:00`).
   - Exif Sub-IFD (tag `34665` / `0x8769`): contains tag `37510` (`UserComment`), value: `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`
   - GPS Sub-IFD (tag `34853` / `0x8825`): contains tag 1 (`InteropIndex`=`'N'`), tag 2 (Lat=`(40.0, 42.0, 46.08)`), tag 3 (`'W'`), tag 4 (Lon=`(74.0, 0.0, 21.6)`). Evaluates to coordinates `40.7128° N, 74.0060° W` (New York, NY).
   - `tEXt` chunks: `Make` (`'Nikon'`), `Model` (`'D750'`), `Software` (`'Adobe Lightroom 13.0'`), `create-date` (`'2025-02-02T10:15:00'`).

2. **`Brain-Channel.png`**:
   - `eXIf` chunk: Length 152 bytes. Contains IFD0 tag `270` (`ImageDescription`), value: `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'`
   - No Exif Sub-IFD or GPS Sub-IFD present.
   - No textual `tEXt`, `zTXt`, or `iTXt` metadata chunks.

3. **`Brain.png`**:
   - `eXIf` chunk: **None**. `img.getexif()` returns `{}` (0 tags).
   - `tEXt` chunk: Length 65 bytes. Keyword: `'Software'`, Text: `'RECON: Perform DNS harvesting and Subdomain enumeration.'`
   - `iTXt` / XMP: **None**.

4. **`Chemicals.png`**:
   - `eXIf` chunk: **None**. `img.getexif()` returns `{}` (0 tags).
   - `tEXt` chunk: Length 69 bytes. Keyword: `'ImageDescription'`, Text: `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'`
   - `iTXt` / XMP: **None**.

5. **`Dopamine.png`**:
   - `eXIf` chunk: **None**. `img.getexif()` returns `{}` (0 tags).
   - `iTXt` chunk: Length 445 bytes. Keyword: `'XML:com.adobe.xmp'`. Uncompressed UTF-8 XML document.
   - Verbatim XML packet content:
     ```xml
     <?xpacket begin='﻿' id='W5M0MpCehiHzreSzNTczkc9d'?>
     <x:xmpmeta xmlns:x='adobe:ns:meta/' x:xmptk='Image::ExifTool 12.76'>
     <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>

      <rdf:Description rdf:about=''
       xmlns:exif='http://ns.adobe.com/exif/1.0/'>
       <exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>
      </rdf:Description>
     </rdf:RDF>
     </x:xmpmeta>
     <?xpacket end='r'?>
     ```

6. **`Music.png`**:
   - `eXIf` chunk: Length 382 bytes. IFD0 tag `33432` (`Copyright`), value: `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='`
   - Camera hardware metadata: Make=`'Olympus'`, Model=`'OM-D E-M10'`, DateTime=`'2025:02:06 11:11:00'`.
   - `tEXt` chunk: Keyword: `'Copyright'`, Text: `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='`
   - Base64 Decoded Value: `'EXFIL: Tunnel compressed database dump via DNS Covert Channel.'`

### 1.3 Execution of `metadata_scanner.py`
Command executed:
`python Lab6/metadata_scanner.py -i Lab6/Images -o Lab6/metadata_report.csv -v`
Exit code: `0`.
Resulting CSV output (`Lab6/metadata_report.csv`):
```csv
filename,format,metadata_fields,suspected_field,encoding,risk_score,reason
Activation.png,PNG,"srgb, gamma, dpi, exif, Make, Model, Software, create-date, UserComment, GPSInfo",UserComment,EXIF ASCII header / plain text,15,Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5).
Brain-Channel.png,PNG,"srgb, gamma, dpi, exif, ImageDescription",ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
Brain.png,PNG,"srgb, gamma, dpi, Software",Software,None (plain text),10,Confirmed covert message in Software (+10).
Chemicals.png,PNG,ImageDescription,ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
Dopamine.png,PNG,"srgb, gamma, dpi, xmp, XML:com.adobe.xmp",XML:com.adobe.xmp (exif:MakerNote),XML encapsulation / plain text,15,Confirmed covert message in XML:com.adobe.xmp (exif:MakerNote) (+10); unusual container / embedded XMP packet (+5).
Music.png,PNG,"srgb, gamma, dpi, Copyright, Make, Model, create-date, exif",Copyright,Base64,15,Confirmed covert message in Copyright (+10); obfuscated with Base64 encoding requiring decoding (+5).
```

### 1.4 Textbook and Lab Reference Ingestion
1. **Reference 1:** Jose Manuel Ortega, *Mastering Python for Networking and Security - Second Edition*, Packt Publishing, 2021.
   - **Section 5: Python Forensics**, **Chapter 13: Extracting Geolocation and Metadata from Documents** (pp. 798–825).
     - Subsection *"Extracting metadata from images"* (pp. 800–810): Demonstrates `PIL.Image`, `PIL.ExifTags.TAGS`, extracting EXIF dictionaries via `_getexif()`, handling `exifinfo.items()`, and parsing GPS sub-dictionaries (`decode_gps_info()`).
     - Subsection *"Extracting metadata from PDF documents"* (pp. 811–822): Demonstrates XMP metadata extraction using `getXmpMetadata()` and extracting namespace properties (`dc_contributor`, `xmp_modifyDate`, `pdf_keywords`).
   - **Chapter 14: Cryptography and Steganography** (pp. 850–895):
     - Demonstrates covert channels, LSB image steganography using `stepic`, and hiding payloads inside multimedia containers.
2. **Reference 2:** Fahad Ali Sarwar, *Python Ethical Hacking From Scratch _ Think Like an Ethical Hacking Professional*, Packt Publishing, 2021.
   - **Chapter 3: Reconnaissance and Information Gathering** (pp. 58–75): DNS queries, host discovery, subdomain scanning.
   - **Chapter 6 & 7: Malware Development and Advanced Malware** (pp. 118–168): Reverse shells, persistent backdoors, cron execution.
   - **Chapter 8: Post Exploitation** (pp. 170–195): Privilege escalation, credential dumping (Mimikatz equivalents), pivoting, data exfiltration channels.
3. **Reference 3:** `Lab6/Lab6.ipynb`:
   - Cells [6], [10], [14], [17], [35], [37], [40], [41]: defines exact rubric, extraction patterns (`getexif()`, `img.info`, `XML:com.adobe.xmp`, `base64.b64decode`), and reflection questions.

---

## 2. Logic Chain

1. **Layer Separation & Parser Discrepancy (Observation 1.2):**
   - In `Brain.png` and `Chemicals.png`, standard EXIF parser `img.getexif()` returns an empty dictionary `{}` because neither file possesses an `eXIf` chunk.
   - However, raw binary chunk inspection confirms that `Brain.png` contains a `tEXt` chunk with keyword `Software`, and `Chemicals.png` contains a `tEXt` chunk with keyword `ImageDescription`.
   - In `Dopamine.png`, `img.getexif()` also returns empty `{}`. However, an `iTXt` chunk with keyword `XML:com.adobe.xmp` contains an Adobe Extensible Metadata Platform packet with the covert message embedded inside `<exif:MakerNote>`.
   - *Inference:* Tools that rely exclusively on standard EXIF parsers suffer from a critical blind spot and fail to detect covert channels hidden within native PNG chunks (`tEXt`/`zTXt`/`iTXt`) or XMP streams.

2. **De-obfuscation and Decoding Verification (Observation 1.2, 1.3):**
   - In `Activation.png`, the secret payload is located in EXIF Sub-IFD tag `37510` (`UserComment`). The raw value begins with the standard 8-byte header `b'ASCII\x00\x00\x00'`. Stripping these 8 header bytes yields the plaintext: `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`
   - In `Music.png`, the string `RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4=` appears in both the PNG `tEXt` `Copyright` chunk and EXIF IFD0 tag `33432`. This string has length 84 (a multiple of 4), uses characters strictly from `[A-Za-z0-9+/=]`, and terminates with `=` padding. RFC 4648 Base64 decoding produces valid UTF-8 text: `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`
   - *Inference:* Automated scanners must implement targeted decoding heuristics (Base64 validation, EXIF header stripping) to convert obfuscated raw bytes into actionable intelligence.

3. **Attack Narrative Sequencing and Cyber Kill Chain Alignment (Observation 1.2):**
   - Each recovered secret begins with an explicit attack lifecycle prefix: `RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, and `EXFIL:`.
   - Filenames in alphabetical order (`Activation`, `Brain-Channel`, `Brain`, `Chemicals`, `Dopamine`, `Music`) do NOT represent the chronological progression of an intrusion.
   - Mapping these prefixes to standard cyber defense frameworks (Lockheed Martin Cyber Kill Chain and MITRE ATT&CK Enterprise Matrix) yields an unambiguous, causal 6-stage attack narrative:
     1. **Stage 1 (Reconnaissance - TA0043):** `Brain.png` -> `RECON: Perform DNS harvesting and Subdomain enumeration.`
     2. **Stage 2 (Vulnerability Identification / Weaponization - TA0001):** `Activation.png` -> `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`
     3. **Stage 3 (Exploitation / Initial Access - TA0002 / TA0001):** `Chemicals.png` -> `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`
     4. **Stage 4 (Persistence / Installation - TA0003):** `Dopamine.png` -> `PERSIST: Establish reverse shell via obfuscated cron job.`
     5. **Stage 5 (Lateral Movement / Credential Access - TA0008 / TA0006):** `Brain-Channel.png` -> `LATERAL: Pivot to internal Domain Controller using Mimikatz.`
     6. **Stage 6 (Exfiltration - TA0010):** `Music.png` -> `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`
   - *Inference:* The logical sequence represents an end-to-end advanced persistent threat (APT) intrusion lifecycle, moving from external reconnaissance to exfiltration of corporate database assets via DNS tunneling.

---

## 3. Discovered Features and Edge Cases

### 3.1 Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | EXIF Parser | Primary IFD0 extraction | Extract top-level TIFF tags from PNG `eXIf` chunk | Image path or binary stream | Dictionary of `{tag_id: value}` | Returns `{}` if `eXIf` chunk is missing | `Lab6.ipynb` cell [6], Ortega ch. 13 |
| 2 | EXIF Sub-IFD | ExifOffset Sub-IFD (tag 34665) | Access nested camera/user tags including `UserComment` | `exif.get_ifd(34665)` | Dictionary of Sub-IFD tags | Key missing if no Sub-IFD present | `metadata_scanner.py`, `Activation.png` |
| 3 | EXIF Sub-IFD | GPS Sub-IFD (tag 34853) | Access geolocation coordinates and reference tags | `exif.get_ifd(34853)` | Dictionary of GPS rational tuples | Key missing if no GPS tags | Ortega ch. 13, `Activation.png` |
| 4 | PNG Text | Native `tEXt` chunk parsing | Extract key-value textual metadata embedded in PNG chunks | `img.info` dictionary | Key-value string pairs | Keys omitted if chunk absent | `Lab6.ipynb` cell [10], `inspect_chunks.py` |
| 5 | PNG Text | Native `iTXt` chunk parsing | Extract international UTF-8 text and XML packets | `img.info` / chunk parser | Uncompressed/compressed string | Malformed UTF-8 raises decode error | `inspect_chunks.py`, `Dopamine.png` |
| 6 | Adobe XMP | XMP Packet Extraction & Parsing | Extract Adobe XMP XML packet from `XML:com.adobe.xmp` | XML string in `img.info` | Parsed XML ElementTree / DOM | XML syntax error if truncated | `Lab6.ipynb` cell [14], Ortega ch. 13 |
| 7 | Obfuscation | RFC 4648 Base64 De-obfuscation | Detect and decode Base64 encoded covert strings | Base64 ASCII string | Decoded UTF-8 plaintext | `binascii.Error` on invalid padding | `Lab6.ipynb` cell [17], `Music.png` |
| 8 | Obfuscation | EXIF UserComment Header Strip | Strip 8-byte character code header (`ASCII\x00\x00\x00`) | Raw bytes from tag 37510 | Decoded UTF-8 string | Strips wrong bytes if header absent | `metadata_scanner.py`, `Activation.png` |
| 9 | Risk Scoring | Heuristic Multi-Factor Scoring | Calculate explainable risk score (+10 covert, +5 obfuscation, +5 anomaly) | Candidate metadata, context flags | Integer score (10–15) and reason string | Returns score 0 if non-covert | `metadata_scanner.py` lines 275–313 |
| 10| Automation | Automated Batch CSV Reporter | Scan directory, inspect all layers, output 7-column CSV | Image directory path, output path | Structured CSV report file | Handles missing/corrupt files gracefully | `metadata_scanner.py` CLI |

### 3.2 Edge Cases
| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | `Image.getexif()` | `Brain.png` (PNG lacking `eXIf` chunk) | Returns empty `{}` despite presence of covert channel in `tEXt` `Software`. |
| 2 | `Image.getexif()` | `Chemicals.png` (PNG lacking `eXIf` chunk) | Returns empty `{}` despite presence of covert channel in `tEXt` `ImageDescription`. |
| 3 | `Image.getexif()` | `Dopamine.png` (PNG containing XMP in `iTXt`) | Returns empty `{}` despite presence of covert channel in XMP `<exif:MakerNote>`. |
| 4 | `exif.items()` | `Activation.png` (Sub-IFD `UserComment`) | Primary IFD0 iteration only yields tag `34665` (offset integer); `UserComment` (tag 37510) is invisible unless `get_ifd(ExifTags.IFD.Exif)` is explicitly invoked. |
| 5 | String Decoding | `Activation.png` `UserComment` bytes | Raw value starts with `b'ASCII\x00\x00\x00'`. Attempting naive `.decode('utf-8')` includes null bytes `\x00\x00\x00` in output string. |
| 6 | XML Parsing | `Dopamine.png` XMP packet | Leading UTF-8 Byte Order Mark (`\ufeff`) causes standard XML parsers or cp1252 Windows console print to fail unless stripped or encoded properly. |
| 7 | Encoding Identification | `Music.png` `Copyright` field | Raw value `'RVhGSUw6...'` is identical in both `img.info['Copyright']` and `exif[33432]`. Base64 decoding reveals identical plaintexts. |
| 8 | Geolocation Anomaly | `Activation.png` EXIF GPS tags | Graphic image contains hardware tags (Nikon D750) and GPS coordinates for Manhattan, NY (`40.7128, -74.0060`), indicating synthetic metadata injection. |

---

## 4. Forensic Evidence Recovery Table

The table below details the forensic extraction for all six images:

| # | Image File | Metadata Format | Specific Tag / Key Name | Raw Value Excerpt | Decoding Method | Recovered Secret Fragment | Stage Indicator | Forensic Interpretation & Kill Chain Context |
|---|---|---|---|---|---|---|---|---|
| 1 | `Brain.png` | Native PNG Text (`tEXt`) | `Software` | `'RECON: Perform DNS harvesting and Subdomain enumeration.'` | Direct string extraction (Plaintext) | `RECON: Perform DNS harvesting and Subdomain enumeration.` | Stage 1 (`RECON`) | **Reconnaissance (TA0043):** Adversary performs OSINT, querying public DNS records and enumerating subdomains to discover external-facing attack surfaces. |
| 2 | `Activation.png` | EXIF Sub-IFD (`ExifOffset` tag 34665) | `UserComment` (tag 37510) | `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'` | Stripping 8-byte EXIF ASCII header (`b'ASCII\x00\x00\x00'`) & UTF-8 decode | `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` | Stage 2 (`VULN`) | **Weaponization / Vulnerability Analysis (TA0001):** Adversary scans the perimeter gateway identified during recon, isolating an unpatched high-severity CVE. |
| 3 | `Chemicals.png` | Native PNG Text (`tEXt`) | `ImageDescription` | `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'` | Direct string extraction (Plaintext) | `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` | Stage 3 (`EXPLOIT`) | **Exploitation / Initial Access (TA0002):** Adversary launches an active SQL injection payload engineered to evade Web Application Firewall (WAF) filters. |
| 4 | `Dopamine.png` | Adobe XMP Packet (`iTXt`) | `XML:com.adobe.xmp` (`exif:MakerNote`) | `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>` | XML ElementTree parsing / Regex extraction | `PERSIST: Establish reverse shell via obfuscated cron job.` | Stage 4 (`PERSIST`) | **Persistence / Execution (TA0003 / TA0002):** Adversary plants an obfuscated Linux cron job executing an outbound TCP reverse shell to maintain persistent access. |
| 5 | `Brain-Channel.png` | EXIF Primary IFD0 (`eXIf`) | `ImageDescription` (tag 270) | `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'` | Direct string extraction (Plaintext) | `LATERAL: Pivot to internal Domain Controller using Mimikatz.` | Stage 5 (`LATERAL`) | **Lateral Movement / Credential Dumping (TA0008 / TA0006):** Adversary leverages harvested credentials and Mimikatz LSASS dumping to move laterally to the Active Directory Domain Controller. |
| 6 | `Music.png` | Native PNG Text (`tEXt`) & EXIF IFD0 | `Copyright` (PNG chunk & EXIF tag 33432) | `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='` | RFC 4648 Base64 decoding (`base64.b64decode()`) | `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` | Stage 6 (`EXFIL`) | **Exfiltration (TA0010):** Adversary compresses dumped database tables and exfiltrates data outbound via Base64-encoded DNS tunnel queries to bypass egress filtering. |

---

## 5. Secret Reconstruction & Cyber Kill Chain Incident Narrative

### 5.1 Reconstructed Six-Stage Incident Narrative
Assembling the six recovered secrets into chronological and operational order reveals the complete incident narrative:

> **Stage 1 (Reconnaissance):** `RECON: Perform DNS harvesting and Subdomain enumeration.` *(Recovered from `Brain.png` via PNG `tEXt:Software`)*  
> **Stage 2 (Vulnerability Identification):** `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` *(Recovered from `Activation.png` via EXIF `UserComment`)*  
> **Stage 3 (Exploitation):** `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` *(Recovered from `Chemicals.png` via PNG `tEXt:ImageDescription`)*  
> **Stage 4 (Persistence):** `PERSIST: Establish reverse shell via obfuscated cron job.` *(Recovered from `Dopamine.png` via XMP `exif:MakerNote`)*  
> **Stage 5 (Lateral Movement):** `LATERAL: Pivot to internal Domain Controller using Mimikatz.` *(Recovered from `Brain-Channel.png` via EXIF `ImageDescription`)*  
> **Stage 6 (Exfiltration):** `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` *(Recovered from `Music.png` via Base64-decoded `Copyright`)*  

### 5.2 Timeline Justification & Attack Sequencing Rationale
1. **Reconnaissance Precedes Targeting:** An adversary cannot identify vulnerabilities in specific hosts without first performing reconnaissance. `RECON` (Stage 1) maps the external perimeter through passive and active DNS harvesting and subdomain enumeration.
2. **Vulnerability Assessment Focuses the Target:** Having enumerated external subdomains, the adversary probes the gateway service and identifies a vulnerable, unpatched endpoint (`CVE-2024-XXXX`) in Stage 2 (`VULN`).
3. **Exploitation Achieves Initial Footprint:** Armed with the vulnerability assessment, the attacker crafts and delivers an exploit (`EXPLOIT`, Stage 3) using SQL injection crafted to bypass WAF rules.
4. **Persistence Solidifies Access:** Because web shells or injection vectors can be unstable or volatile across service restarts, the adversary immediately establishes a persistent foothold (`PERSIST`, Stage 4) by installing an obfuscated cron job establishing an outbound reverse shell.
5. **Lateral Movement Expands Control:** Operating from the compromised web gateway, the attacker executes Mimikatz to dump cached credentials from LSASS and pivots across internal network segments to compromise the enterprise Domain Controller (`LATERAL`, Stage 5).
6. **Exfiltration Fulfills Objective:** With administrative domain dominion established, the adversary accesses core database repositories, dumps and compresses the data, and sneaks it out via DNS covert tunneling (`EXFIL`, Stage 6) to circumvent perimeter firewalls.
7. **Filenames Are Arbitrary:** Ordering strictly by filename (`Activation.png` -> `Brain-Channel.png` -> `Brain.png` -> `Chemicals.png` -> `Dopamine.png` -> `Music.png`) would place vulnerability identification before reconnaissance and lateral movement before exploitation, creating a nonsensical tactical timeline.

---

## 6. Academic Citations & Relevant Code Examples

### 6.1 Textbook 1: *Mastering Python for Networking and Security - Second Edition*
- **Author:** Jose Manuel Ortega  
- **Publisher & Year:** Packt Publishing, 2021  
- **ISBN:** 978-1-80056-887-7 (Anna's Archive ID: `97c706086e42a54e17ca09f3b5d68f0f`)  
- **Relevant Chapter:** **Chapter 13: Extracting Geolocation and Metadata from Documents** (pp. 798–825) and **Chapter 14: Cryptography and Steganography** (pp. 850–895).  
- **Topics Covered:** Digital image forensics, PIL/Pillow EXIF extraction, GPS IFD parsing, PDF/XMP metadata extraction, and LSB image steganography.  

#### Extracted Code Example 1: EXIF Metadata & GPS Parsing (Ortega, pp. 804–806)
```python
import os
from PIL import Image
from PIL.ExifTags import TAGS

def get_exif_metadata(image_path):
    exifData = {}
    image = Image.open(image_path)
    if hasattr(image, '_getexif'):
        exifinfo = image._getexif()
        if exifinfo is not None:
            for tag, value in exifinfo.items():
                decoded = TAGS.get(tag, tag)
                exifData[decoded] = value
    decode_gps_info(exifData)
    return exifData

def decode_gps_info(exif):
    if 'GPSInfo' in exif:
        gps = exif['GPSInfo']
        lat_ref = gps[1]
        lat = gps[2]
        lon_ref = gps[3]
        lon = gps[4]
        latitude = (lat[0] + lat[1]/60.0 + lat[2]/3600.0) * (1 if lat_ref == 'N' else -1)
        longitude = (lon[0] + lon[1]/60.0 + lon[2]/3600.0) * (1 if lon_ref == 'E' else -1)
        exif['GPSInfo'] = {"Latitude": latitude, "Longitude": longitude}
```

#### Extracted Code Example 2: XMP Metadata Extraction (Ortega, pp. 815–817)
```python
# Extracting XMP metadata schema properties using PyPDF2 / XML DOM
# Demonstrates retrieving Dublin Core and XMP namespace properties
xmpinfo = pdfReader.getXmpMetadata()
if hasattr(xmpinfo, 'dc_contributor'):
    print('[+] Contributor:', xmpinfo.dc_contributor)
if hasattr(xmpinfo, 'xmpmm_documentId'):
    print('[+] DocumentId:', xmpinfo.xmpmm_documentId)
if hasattr(xmpinfo, 'pdf_keywords'):
    print('[+] Keywords:', xmpinfo.pdf_keywords)
```

---

### 6.2 Textbook 2: *Python Ethical Hacking From Scratch*
- **Author:** Fahad Ali Sarwar  
- **Publisher & Year:** Packt Publishing, 2021  
- **ISBN:** 978-1-83882-531-7  
- **Relevant Chapters:**
  - **Chapter 3: Reconnaissance and Information Gathering** (pp. 58–75) — DNS enumeration and reconnaissance techniques.
  - **Chapter 6: Malware Development** (pp. 118–140) — Socket-based reverse shell payloads and persistence.
  - **Chapter 8: Post Exploitation** (pp. 170–195) — Privilege escalation, lateral pivoting, and credential harvesting.
- **Contextual Alignment:** Sarwar details the offensive mechanics behind each stage recovered from the image metadata: weaponizing reverse shells via scheduled tasks/cron jobs, dumping LSASS credentials for Active Directory domain elevation, and circumventing perimeter network defenses.

---

### 6.3 Reference 3: `Lab6.ipynb` Core Extraction Snippets
The lab student notebook provides the canonical baseline patterns adapted across the investigations:

1. **EXIF Inspection (`Lab6.ipynb`, Cell [6]):**
   ```python
   image_path = image_dir / "Brain-Channel.png"
   with Image.open(image_path) as img:
       exif = img.getexif()
       for tag_id, value in exif.items():
           tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
           print(f"{tag_name} ({tag_id}): {value}")
   ```
2. **Native PNG Text Chunks (`Lab6.ipynb`, Cell [10]):**
   ```python
   image_path = image_dir / "Brain.png"
   with Image.open(image_path) as img:
       for key, value in img.info.items():
           print(f"{key}: {value}")
   ```
3. **Adobe XMP Packet Parsing (`Lab6.ipynb`, Cell [14]):**
   ```python
   image_path = image_dir / "Dopamine.png"
   with Image.open(image_path) as img:
       xmp = img.info.get("XML:com.adobe.xmp")
       if xmp:
           print(xmp[:500])
   ```
4. **Base64 Computational Decoding (`Lab6.ipynb`, Cell [17]):**
   ```python
   import base64
   example = "RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="
   print(base64.b64decode(example).decode("utf-8"))
   ```

---

## 7. Automated Scanner Architecture & Risk Scoring Analysis

### 7.1 Architecture of `metadata_scanner.py`
`metadata_scanner.py` executes an automated pipeline across three analytical phases:
1. **Multi-Layer Candidate Extraction:** Ingests images using Pillow; inspects `img.info` for native PNG textual chunks (`tEXt`/`zTXt`/`iTXt`), unpacks Adobe XMP packets using `defusedxml` (falling back to `xml.etree`), queries primary IFD0 EXIF tags via `img.getexif()`, and traverses nested sub-IFDs (`ExifOffset` Sub-IFD `0x8769` and `GPSInfo` Sub-IFD `0x8825`).
2. **De-obfuscation and Heuristic Detection:** Analyzes each candidate field for known attack lifecycle prefixes (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`) and threat keywords. Strips standard 8-byte EXIF ASCII headers (`b'ASCII\x00\x00\x00'`), detects RFC 4648 Base64 character distributions, and validates decodability.
3. **Explainable Risk Scoring Engine:** Assigns scores based on transparent, additive criteria:
   - **Base Score (+10):** Confirmed covert channel payload matching attack lifecycle prefixes or threat indicators.
   - **Obfuscation Penalty (+5):** Encoded or obfuscated payload requiring computational decoding (e.g. Base64).
   - **Container / Environmental Anomaly (+5):** Synthetic camera hardware tags or GPS coordinates embedded in digital graphic files, or unusual XMP packet containers.
   - **Non-Double-Counting Guard:** Caps auxiliary additions at +5 to ensure consistent grading adherence (scores range from 10 to 15 for infected images).

### 7.2 Complete Scanner Results Table (`metadata_report.csv`)
| `filename` | `format` | `metadata_fields` | `suspected_field` | `encoding` | `risk_score` | `reason` |
|---|---|---|---|---|---:|---|
| `Activation.png` | `PNG` | `srgb, gamma, dpi, exif, Make, Model, Software, create-date, UserComment, GPSInfo` | `UserComment` | `EXIF ASCII header / plain text` | **15** | Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5). |
| `Brain-Channel.png` | `PNG` | `srgb, gamma, dpi, exif, ImageDescription` | `ImageDescription` | `None (plain text)` | **10** | Confirmed covert message in ImageDescription (+10). |
| `Brain.png` | `PNG` | `srgb, gamma, dpi, Software` | `Software` | `None (plain text)` | **10** | Confirmed covert message in Software (+10). |
| `Chemicals.png` | `PNG` | `ImageDescription` | `ImageDescription` | `None (plain text)` | **10** | Confirmed covert message in ImageDescription (+10). |
| `Dopamine.png` | `PNG` | `srgb, gamma, dpi, xmp, XML:com.adobe.xmp` | `XML:com.adobe.xmp (exif:MakerNote)` | `XML encapsulation / plain text` | **15** | Confirmed covert message in XML:com.adobe.xmp (exif:MakerNote) (+10); unusual container / embedded XMP packet (+5). |
| `Music.png` | `PNG` | `srgb, gamma, dpi, Copyright, Make, Model, create-date, exif` | `Copyright` | `Base64` | **15** | Confirmed covert message in Copyright (+10); obfuscated with Base64 encoding requiring decoding (+5). |

---

## 8. Answers to Lab 6 Reflection Questions

### Question 1: Why can an image contain a hidden message even when `getexif()` returns no tags?
Standard image libraries implement format-specific conventions. The method `getexif()` queries the EXIF IFD0 block, which in PNG files is stored inside a dedicated `eXIf` chunk. However, the PNG specification natively defines several other chunks for textual and application metadata:
- `tEXt`: Stores uncompressed Latin-1 keyword/text pairs (e.g. `Software` in `Brain.png`, `ImageDescription` in `Chemicals.png`).
- `zTXt`: Stores zlib-compressed textual data.
- `iTXt`: Stores international UTF-8 text and structured XML streams, such as Adobe XMP packets (e.g. `Dopamine.png`).
When an adversary embeds data in `tEXt`, `zTXt`, or `iTXt` chunks without creating an `eXIf` chunk, `getexif()` returns an empty dictionary. Investigators who rely solely on `getexif()` suffer from an architectural blind spot. Forensic analysis of PNG images requires inspecting `img.info` or reading the binary chunk stream directly.

### Question 2: How is encoding different from encryption? Is Base64 a secure way to hide information?
- **Encoding** is an open, reversible transformation designed to ensure data integrity and compatibility across diverse communication channels. It translates arbitrary binary sequences into safe ASCII printable characters (e.g., converting binary files into Base64 so they can be stored in text metadata fields or email headers). Crucially, encoding involves **no secret key**; any observer who recognizes the character set can immediately decode it using public algorithms.
- **Encryption** is a cryptographic process designed to guarantee **confidentiality**. It uses a mathematical algorithm parameterized by a secret key (symmetric like AES-256 or asymmetric like RSA/ECC). Without the secret key, recovering the plaintext from ciphertext is computationally infeasible.
- **Security Assessment:** Base64 is **not encryption** and provides zero confidentiality. In `Music.png`, Base64 serves only as trivial obfuscation. Automated forensic tools immediately detect Base64 strings via character set entropy, length multiples of 4, and `=` padding, reversing them instantly.

### Question 3: Why should investigators preserve the original files and record hashes?
Metadata is among the most fragile forensic artifacts in digital systems:
1. **Metadata Volatility:** Simply opening an image in standard viewing or editing applications (e.g., Photoshop, Paint, Preview) or uploading it to web applications/social media often modifies timestamps, strips unrecognized chunks (`tEXt`, `eXIf`), or rewrites header fields.
2. **Chain of Custody:** In judicial and formal incident response proceedings, evidence is inadmissible without proving that it has remained pristine and unaltered from seizure to court presentation.
3. **Cryptographic Integrity:** Computing a cryptographic checksum (e.g., SHA-256) upon acquisition establishes an immutable mathematical signature. If the hash of an image matches during every phase of extraction and analysis, the investigator can definitively prove that no bytes (whether pixel data, chunk headers, or hidden metadata) were planted, modified, or corrupted.

### Question 4: Can metadata alone prove that an image was edited or that an incident occurred? What corroborating evidence would you need?
- **No, metadata alone cannot prove an incident occurred or that an image was edited.**
- **Rationale:** Metadata fields are arbitrary, unauthenticated header values that can be forged, manipulated, or backdated with trivial effort using open-source utilities like `exiftool` or custom Python scripts. For example, `Activation.png` contains EXIF tags claiming to be captured by a Nikon D750 camera in New York City, despite being a synthetic digital graphic. Similarly, an attacker could plant fake incident narrative strings in image metadata to mislead investigators (anti-forensics).
- **Corroborating Evidence Required:**
  - **Network Telemetry:** PCAP captures, DNS query logs (corroborating DNS tunneling in Stage 6), proxy/WAF access logs (corroborating SQL injection in Stage 3), and NetFlow records.
  - **Host & System Logs:** Web gateway auth logs and kernel audit logs confirming CVE exploitation (Stage 2); Linux `/var/spool/cron/crontabs` entries or `/etc/cron.*` files confirming persistent reverse shells (Stage 4).
  - **Endpoint Detection & Response (EDR):** Process execution trees, LSASS memory handle access, and command-line logging confirming Mimikatz invocation (Stage 5).
  - **Filesystem Artifacts:** Master File Table ($MFT) records, `$LogFile`, inode change timestamps, and prefetch files.

### Question 5: How does this investigation connect to the automated evidence collection and analysis you practised in Labs 4 and 5?
In Labs 4 and 5, automated evidence collection involved programmatically aggregating heterogeneous system logs, normalizing unstructured data, extracting key IOCs, and triaging security alerts at scale. Lab 6 applies these exact principles to file-level multimedia forensics:
- In an enterprise breach involving thousands of workstations, network shares, and web caches, manual point-and-click inspection of individual images is completely unfeasible.
- The Python metadata scanner developed here acts as an automated forensic triage engine: it parses diverse binary layers (EXIF IFDs, PNG chunks, XMP streams), executes de-obfuscation algorithms, applies explainable multi-factor risk scoring, and exports standardized CSV reports.
- This structured output seamlessly integrates into Security Information and Event Management (SIEM) and Security Orchestration, Automation, and Response (SOAR) pipelines for automated alert correlation and incident containment.

---

## 9. Caveats

1. **No Cryptographic Signing:** The metadata tags extracted from the six PNG images lack digital signatures or cryptographic timestamping (e.g., C2PA or PKI signatures). Consequently, while the strings are forensically proven to exist within the files, their contents represent simulated artifacts rather than verified real-world operational logs.
2. **Deterministic Heuristics:** The automated risk-scoring model relies on predefined prefix matching (`RECON:`, `VULN:`, etc.) and threat keyword dictionaries. If an adversary employed a novel covert channel or encrypted payload with high-entropy ciphertext (rather than Base64), rule-based scanners would classify the image as low-risk (Score 0) without statistical entropy analysis.
3. **No Dynamic Execution:** Per strict laboratory instructions, none of the commands, CVEs, SQL injection payloads, or reverse shell scripts described within the recovered messages were dynamically executed in the test environment.

---

## 10. Conclusion

1. **Complete Forensic Recovery:** All six covert fragments have been successfully recovered, de-obfuscated, and attributed to their precise metadata formats and container chunks.
2. **Kill Chain Reconstruction:** The six fragments reconstruct a textbook 6-stage Cyber Kill Chain narrative: Reconnaissance (`Brain.png`), Vulnerability Identification (`Activation.png`), Exploitation (`Chemicals.png`), Persistence (`Dopamine.png`), Lateral Movement (`Brain-Channel.png`), and Exfiltration (`Music.png`).
3. **Automated Verification:** The automated scanner (`metadata_scanner.py`) executes flawlessly, generating `Lab6/metadata_report.csv` with 100% data integrity, schema compliance, and explainable risk scores (10–15).
4. **Academic Foundation:** The extraction techniques are fully grounded in Jose Manuel Ortega's *Mastering Python for Networking and Security - Second Edition* (Chapters 13 & 14) and Fahad Ali Sarwar's *Python Ethical Hacking From Scratch*.

---

## 11. Verification Method

To independently reproduce and verify all findings documented in this report:

1. **Verify Binary Chunks & Raw Metadata:**
   ```powershell
   python .agents/teamwork/survey_spec_miner_1/inspect_chunks.py
   ```
   *Expected Output:* Shows `eXIf` chunk in `Activation.png`, `Brain-Channel.png`, `Music.png`; `tEXt` chunks in `Brain.png`, `Chemicals.png`, `Music.png`, `Activation.png`; and `iTXt` (`XML:com.adobe.xmp`) in `Dopamine.png`.

2. **Verify Cryptographic SHA-256 Hashes:**
   ```powershell
   Get-FileHash -Algorithm SHA256 Lab6/Images/*.png | Format-Table -AutoSize
   ```
   *Expected Output:* Matches the SHA-256 checksums documented in Section 1.1.

3. **Verify Automated Scanner Execution & CSV Generation:**
   ```powershell
   python Lab6/metadata_scanner.py -i Lab6/Images -o Lab6/metadata_report.csv -v
   ```
   *Expected Output:* Scans 6 images, outputs detailed diagnostics to stdout, and writes 6 data rows to `Lab6/metadata_report.csv` with exit code 0.

4. **Verify Textbook Citations & Outlines:**
   ```powershell
   python .agents/teamwork/survey_spec_miner_1/search_textbooks.py
   ```
   *Expected Output:* Confirms Ortega Chapter 13 (pp. 798–825) covers EXIF and XMP extraction, and Sarwar covers reconnaissance, malware development, and post-exploitation.
