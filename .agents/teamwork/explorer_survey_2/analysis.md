# Lab 6 Forensic Investigation: Covert Channels in Image Metadata

**Investigator Role:** Image Metadata Explorer  
**Working Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_2`  
**Target Corpus:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images`  
**Date of Investigation:** 2026-11-02  

---

## Executive Summary

A comprehensive digital forensic examination was conducted on the image corpus located in `Lab6/Images` to identify covert communication channels embedded within image metadata. All six image files were confirmed to be valid Portable Network Graphics (PNG) images conforming to the PNG-1.2 specification. 

Each image was found to harbor exactly one fragment of a fictional six-stage cybersecurity incident narrative secret. The covert payloads span multiple distinct metadata architectures:
- **EXIF IFD0 Tags** (e.g., standard TIFF/EXIF tag `ImageDescription`)
- **EXIF Sub-IFD Tags** (e.g., private ExifOffset tag `UserComment` with ASCII character code header)
- **PNG Text Chunks** (`tEXt` chunks storing arbitrary key-value pairs like `Software` and `ImageDescription`)
- **Extensible Metadata Platform (XMP)** (embedded XML packets stored inside an `iTXt` chunk containing `<exif:MakerNote>`)
- **Encoded Payloads** (Base64 encoding within EXIF and PNG text `Copyright` tags)

When decoded and ordered chronologically according to the MITRE ATT&CK / Cyber Kill Chain framework, the six fragments assemble into a complete, coherent narrative tracing an advanced persistent threat (APT) intrusion from initial reconnaissance to covert data exfiltration.

---

## 1. Corpus Inventory and Forensic Hashes

All six images were hashed and inspected to verify format integrity, dimensions, and cryptographic signatures.

| Filename | Format | Dimensions | Mode | File Size (Bytes) | SHA-256 Hash |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Activation.png` | PNG | 1415 × 781 | RGBA | 259,975 B | `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904` |
| `Brain-Channel.png` | PNG | 1854 × 541 | RGBA | 201,685 B | `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359` |
| `Brain.png` | PNG | 1733 × 989 | RGBA | 2,354,330 B | `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e` |
| `Chemicals.png` | PNG | 1726 × 821 | RGB | 561,245 B | `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a` |
| `Dopamine.png` | PNG | 1796 × 831 | RGBA | 388,411 B | `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472` |
| `Music.png` | PNG | 1504 × 843 | RGBA | 679,959 B | `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370` |

### Supplementary Integrity Data
- **MD5 Hashes**:
  - `Activation.png`: `28a931ca770d9118a8286c0db414332c`
  - `Brain-Channel.png`: `8e8a9d7276707a9f18af7c2e09c70e3a`
  - `Brain.png`: `5d69dd3de9b5f8557ba26d8bcc644af4`
  - `Chemicals.png`: `694d3d3984e34b39a59e0305e837eb5f`
  - `Dopamine.png`: `22eedbe31ba01a541f29758f508d2a58`
  - `Music.png`: `5924abe517910c58798d5567ae27323d`
- **File End Integrity**: All six files end exactly at the final byte of the `IEND` chunk (length 0, CRC 4 bytes). There are zero trailing bytes appended after `IEND`, verifying that no end-of-file append steganography was used; all hidden data is confined to image metadata containers.

---

## 2. In-Depth Metadata Architecture Inspection

### 2.1 Activation.png
- **Structure**:
  - Contains an `eXIf` chunk (510 bytes) and multiple `tEXt` chunks.
  - Standard IFD0 tags: `Make` (Nikon), `Model` (D750), `Software` (Adobe Lightroom 13.0), `DateTime` (2025:02:02 10:15:00), `ResolutionUnit` (2), `XResolution` (72.0), `YResolution` (72.0), `ExifOffset` (204), `GPSInfo` (396).
  - Calling top-level `img.getexif()` returns 10 tags but **does not expose the covert payload directly**.
  - **Exif Sub-IFD (tag 0x8769 / 34665)** contains:
    - Tag `0x9286` (decimal 37510, `UserComment`):
      Raw bytes: `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`
  - **GPS Sub-IFD (tag 0x8825 / 34853)** contains:
    - `GPSLatitude`: `40° 42' 46.08" N`
    - `GPSLongitude`: `74° 0' 21.6" W` (geographic coordinates situated in New York / Jersey City harbor area).
- **Encoding/Obfuscation**:
  - EXIF standard 8-byte character code prefix `b'ASCII\x00\x00\x00'` preceding the ASCII text payload.
- **Covert Field**: `EXIF Sub-IFD: UserComment` (Tag ID `0x9286` / 37510).
- **Recovered Fragment**: `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`

---

### 2.2 Brain-Channel.png
- **Structure**:
  - Contains an `eXIf` chunk (152 bytes).
  - IFD0 contains 5 tags: `ResolutionUnit` (2), `YCbCrPositioning` (1), `XResolution` (72.0), `YResolution` (72.0), and `ImageDescription` (tag `0x010e` / 270).
  - `img.info` contains: `{'srgb': 0, 'gamma': 0.45455, 'dpi': (95.9866, 95.9866), 'exif': b'...'}`.
  - No PNG text chunks or XMP packets are present.
- **Encoding/Obfuscation**:
  - Plaintext ASCII string.
- **Covert Field**: `EXIF IFD0: ImageDescription` (Tag ID `0x010e` / 270).
- **Recovered Fragment**: `LATERAL: Pivot to internal Domain Controller using Mimikatz.`

---

### 2.3 Brain.png
- **Structure**:
  - EXIF: `img.getexif()` returns **0 tags** (no `eXIf` chunk in PNG).
  - Contains standard PNG header chunks (`IHDR`, `sRGB`, `gAMA`, `pHYs`) and a `tEXt` chunk (65 bytes).
  - `img.info` contains: `{'srgb': 0, 'gamma': 0.45455, 'dpi': (95.9866, 95.9866), 'Software': 'RECON: Perform DNS harvesting and Subdomain enumeration.'}`.
- **Encoding/Obfuscation**:
  - Plaintext ASCII string in PNG native key-value pair.
- **Covert Field**: `PNG text chunk: Software`.
- **Recovered Fragment**: `RECON: Perform DNS harvesting and Subdomain enumeration.`

---

### 2.4 Chemicals.png
- **Structure**:
  - EXIF: `img.getexif()` returns **0 tags** (no `eXIf` chunk).
  - Contains minimal chunks: `IHDR`, a single `tEXt` chunk (69 bytes), `IDAT`, and `IEND`. Color mode is `RGB` (no alpha channel).
  - `img.info` contains: `{'ImageDescription': 'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'}`.
- **Encoding/Obfuscation**:
  - Plaintext ASCII string in PNG native key-value pair.
- **Covert Field**: `PNG text chunk: ImageDescription`.
- **Recovered Fragment**: `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`

---

### 2.5 Dopamine.png
- **Structure**:
  - EXIF: `img.getexif()` returns **0 tags** (no `eXIf` chunk).
  - Contains standard PNG header chunks and an `iTXt` chunk (445 bytes).
  - `img.info` contains keys `xmp` and `XML:com.adobe.xmp`.
  - The `iTXt` chunk contains a serialized Extensible Metadata Platform (XMP) packet produced via ExifTool 12.76:
    ```xml
    <?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>
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
- **Encoding/Obfuscation**:
  - XML element `<exif:MakerNote>` inside uncompressed UTF-8 XMP metadata stream with leading UTF-8 BOM (`\xef\xbb\xbf`).
- **Covert Field**: `XMP: exif:MakerNote` (embedded within `XML:com.adobe.xmp` / `xmp`).
- **Recovered Fragment**: `PERSIST: Establish reverse shell via obfuscated cron job.`

---

### 2.6 Music.png
- **Structure**:
  - Contains an `eXIf` chunk (382 bytes) and several `tEXt` chunks (`Make`, `Model`, `create-date`, `Copyright`).
  - EXIF IFD0 contains 9 tags: `Make` (Olympus), `Model` (OM-D E-M10), `DateTime` (2025:02:06 11:11:00), `ExifOffset` (264), `Copyright` (tag `0x8298` / 33432).
  - The value of `Copyright` appears identically in both:
    1. EXIF tag `0x8298` (`Copyright`)
    2. PNG text chunk `Copyright`
  - Raw value: `"RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="`
- **Encoding/Obfuscation**:
  - Base64 encoding. Decoding yields:
    `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`
- **Covert Field**: `EXIF / PNG text chunk: Copyright` (Tag ID `0x8298` / 33432).
- **Recovered Fragment**: `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`

---

## 3. Comprehensive Evidence Table

| Image Filename | Primary Metadata Container | Field / Tag Identifier | Raw Recovered Value | Encoding / Obfuscation | Recovered Message Fragment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Activation.png` | EXIF (Sub-IFD `0x8769`) | Tag `37510` (`0x9286`, `UserComment`) | `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'` | EXIF ASCII header prefix (`ASCII\x00\x00\x00`) | `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` |
| `Brain-Channel.png` | EXIF (IFD0) | Tag `270` (`0x010e`, `ImageDescription`) | `"LATERAL: Pivot to internal Domain Controller using Mimikatz."` | Plaintext | `LATERAL: Pivot to internal Domain Controller using Mimikatz.` |
| `Brain.png` | PNG Text Chunk | `tEXt: Software` | `"RECON: Perform DNS harvesting and Subdomain enumeration."` | Plaintext | `RECON: Perform DNS harvesting and Subdomain enumeration.` |
| `Chemicals.png` | PNG Text Chunk | `tEXt: ImageDescription` | `"EXPLOIT: Deploy SQL Injection payload to bypass WAF."` | Plaintext | `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` |
| `Dopamine.png` | XMP Packet (`iTXt`) | `<exif:MakerNote>` | `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>` | XML encapsulation (UTF-8 BOM) | `PERSIST: Establish reverse shell via obfuscated cron job.` |
| `Music.png` | EXIF & PNG Text | Tag `33432` (`0x8298`, `Copyright`) / `tEXt: Copyright` | `"RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="` | Base64 | `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` |

---

## 4. Secret Narrative Reconstruction and Sequencing Justification

### 4.1 Chronological Incident Narrative Sequence

| Stage | Stage Prefix | Source Image | Recovered Incident Narrative Message | Attack Lifecycle Mapping |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `RECON` | `Brain.png` | `RECON: Perform DNS harvesting and Subdomain enumeration.` | Reconnaissance (MITRE ATT&CK TA0043) |
| **2** | `VULN` | `Activation.png` | `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` | Vulnerability Assessment / Weaponization (TA0001) |
| **3** | `EXPLOIT` | `Chemicals.png` | `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` | Initial Exploitation / Execution (TA0002) |
| **4** | `PERSIST` | `Dopamine.png` | `PERSIST: Establish reverse shell via obfuscated cron job.` | Persistence (MITRE ATT&CK TA0003) |
| **5** | `LATERAL` | `Brain-Channel.png` | `LATERAL: Pivot to internal Domain Controller using Mimikatz.` | Lateral Movement / Credential Access (TA0008 / TA0006) |
| **6** | `EXFIL` | `Music.png` | `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` | Exfiltration (MITRE ATT&CK TA0010) |

### 4.2 Narrative Justification
1. **Stage 1 (RECON — `Brain.png`)**: Any structured cyber attack commences with passive and active reconnaissance. The adversary maps the external infrastructure of the target enterprise by querying public DNS zones and enumerating subdomains to identify internet-facing entry points.
2. **Stage 2 (VULN — `Activation.png`)**: With external assets cataloged, the attacker assesses target attack surfaces and discovers an unpatched critical vulnerability (CVE-2024-XXXX) in the organization's perimeter web gateway.
3. **Stage 3 (EXPLOIT — `Chemicals.png`)**: Armed with actionable vulnerability intelligence, the threat actor launches an exploit—specifically crafting and deploying an obfuscated SQL Injection payload tailored to bypass the Web Application Firewall (WAF) and execute malicious commands.
4. **Stage 4 (PERSIST — `Dopamine.png`)**: After obtaining an initial execution foothold on the compromised web gateway, the attacker cements their access by installing an obfuscated Unix cron job configured to spawn a periodic outbound reverse shell. This ensures survival across process terminations and server restarts.
5. **Stage 5 (LATERAL — `Brain-Channel.png`)**: Leveraging the established persistent foothold, the adversary deploys credential-harvesting tools (Mimikatz) to extract Kerberos tickets and plaintext administrative credentials from memory, subsequently pivoting laterally across the internal LAN toward the primary Domain Controller.
6. **Stage 6 (EXFIL — `Music.png`)**: Having achieved domain dominance and located confidential backend databases, the adversary dumps and compresses database records, exfiltrating the data via an encrypted/encoded DNS covert tunnel to circumvent conventional firewall egress blocks.

---

## 5. Automated Metadata Scanner and CSV Model

### 5.1 Risk Scoring Heuristic Model
The lab requirements define a consistent, explainable heuristic scoring model:
- **Base Covert Narrative Payload (+10)**: Assigned when an image is confirmed to carry an incident narrative fragment (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`).
- **Suspicious Obfuscation / Encoding (+5)**: Assigned when the payload requires non-trivial decoding (e.g., Base64 in `Music.png`).
- **Additional Unusual Metadata Indicator (+5)**: Assigned when an image possesses abnormal forensic attributes, such as an embedded Exif Sub-IFD with camera hardware profiles and GPS coordinates attached to a synthetic software diagram (`Activation.png`).

### 5.2 Evaluated Scanner Output (`metadata_report.csv`)

| filename | format | metadata_fields | suspected_field | encoding | risk_score | reason |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| `Activation.png` | PNG | `srgb, gamma, dpi, exif, Make, Model, Software, create-date, GPSInfo, ResolutionUnit, ExifOffset, DateTime, YCbCrPositioning, XResolution, YResolution, ExifOffset.ExifVersion, ExifOffset.ComponentsConfiguration, ExifOffset.FlashPixVersion, ExifOffset.DateTimeOriginal, ExifOffset.DateTimeDigitized, ExifOffset.ColorSpace, ExifOffset.UserComment, GPSInfo_IFD` | `EXIF Sub-IFD: UserComment` | `ASCII header prefix` | **15** | Confirmed covert incident narrative message in EXIF sub-IFD tag 'UserComment'; Unusual GPS metadata sub-IFD embedded in PNG diagram |
| `Brain-Channel.png` | PNG | `srgb, gamma, dpi, exif, ResolutionUnit, ImageDescription, YCbCrPositioning, XResolution, YResolution` | `EXIF: ImageDescription` | `None` | **10** | Confirmed covert incident narrative message in EXIF tag 'ImageDescription' |
| `Brain.png` | PNG | `srgb, gamma, dpi, Software` | `PNG text: Software` | `None` | **10** | Confirmed covert incident narrative message in PNG text chunk 'Software' |
| `Chemicals.png` | PNG | `ImageDescription` | `PNG text: ImageDescription` | `None` | **10** | Confirmed covert incident narrative message in PNG text chunk 'ImageDescription' |
| `Dopamine.png` | PNG | `srgb, gamma, dpi, xmp, XML:com.adobe.xmp` | `XMP: exif:MakerNote` | `None` | **10** | Confirmed covert incident narrative message in XMP element 'exif:MakerNote' |
| `Music.png` | PNG | `srgb, gamma, dpi, Copyright, Make, Model, create-date, exif, ResolutionUnit, ExifOffset, DateTime, YCbCrPositioning, XResolution, YResolution, ExifOffset.ExifVersion, ExifOffset.ComponentsConfiguration, ExifOffset.FlashPixVersion, ExifOffset.DateTimeOriginal, ExifOffset.DateTimeDigitized, ExifOffset.ColorSpace` | `PNG text: Copyright` | `Base64` | **15** | Confirmed covert incident narrative message in PNG text chunk 'Copyright'; Suspicious Base64 encoding decoded to incident secret |

---

## 6. Verification and Extraction Code Snippets

### 6.1 Individual Extraction Snippets (for Notebook Sections 1–5)

#### Section 1: EXIF Extraction (`Brain-Channel.png`)
```python
from pathlib import Path
from PIL import Image, ExifTags

image_path = Path("Images") / "Brain-Channel.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    print("EXIF tags:", len(exif))
    for tag_id, value in exif.items():
        print(ExifTags.TAGS.get(tag_id, tag_id), ":", value)
```
*Output:* `ImageDescription : LATERAL: Pivot to internal Domain Controller using Mimikatz.`

#### Section 2: PNG Text Chunk Extraction (`Brain.png` & `Chemicals.png`)
```python
image_path = Path("Images") / "Brain.png"
with Image.open(image_path) as img:
    for key, value in img.info.items():
        if isinstance(value, str):
            print(key, ":", value)
```
*Output for Brain.png:* `Software : RECON: Perform DNS harvesting and Subdomain enumeration.`  
*Output for Chemicals.png:* `ImageDescription : EXPLOIT: Deploy SQL Injection payload to bypass WAF.`

#### Section 3: XMP Extraction (`Dopamine.png`)
```python
image_path = Path("Images") / "Dopamine.png"
with Image.open(image_path) as img:
    xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="replace")
    print(xmp if xmp else "No XMP found")
```
*Output:* Serialized RDF XML stream showing `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>`.

#### Section 4: Base64 Decoding (`Music.png`)
```python
import base64
from pathlib import Path
from PIL import Image

image_path = Path("Images") / "Music.png"
with Image.open(image_path) as img:
    encoded_message = img.info.get("Copyright", "")
    if encoded_message:
        decoded_text = base64.b64decode(encoded_message).decode("utf-8")
        print("Decoded Secret:", decoded_text)
```
*Output:* `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`

#### Investigation 1 Snippet: Sub-IFD UserComment (`Activation.png`)
```python
from pathlib import Path
from PIL import Image, ExifTags

image_path = Path("Images") / "Activation.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    # UserComment resides in Exif Sub-IFD (0x8769)
    sub_ifd = exif.get_ifd(0x8769)
    user_comment = sub_ifd.get(37510)  # 0x9286
    if isinstance(user_comment, bytes):
        if user_comment.startswith(b"ASCII\x00\x00\x00"):
            user_comment = user_comment[8:].decode("utf-8")
        else:
            user_comment = user_comment.decode("utf-8", errors="replace")
    print("UserComment:", user_comment)
```
*Output:* `UserComment: VULN: Identify unpatched CVE-2024-XXXX in web gateway.`

---

## 7. Analytical and Reflection Answers

### 7.1 Reflection Question Answers
1. **Why can an image contain a hidden message even when `getexif()` returns no tags?**  
   Pillow's `img.getexif()` method specifically reads TIFF/EXIF IFD0 directory structures. Image formats, particularly PNG, support multiple independent metadata containers that reside outside IFD0:
   - PNG native textual chunks (`tEXt`, `zTXt`, `iTXt`) which are parsed into `img.info`.
   - Extensible Metadata Platform (XMP) packets serialized into XML streams within `iTXt` chunks (under `XML:com.adobe.xmp`).
   - Private EXIF Sub-IFDs (such as `ExifOffset` `0x8769` or `GPSInfo` `0x8825`), which require explicit traversal and do not surface in IFD0 tag counts.
   Thus, `getexif()` returning 0 tags merely indicates the absence of standard top-level EXIF tags, not the absence of metadata.

2. **How is encoding different from encryption? Is Base64 a secure way to hide information?**  
   - **Encoding** is a publicly known, algorithmic data representation transformation (such as Base64, ASCII, or Hex) intended to ensure safe transmission across text-only or binary-restricted channels. It uses no secret key and provides zero confidentiality; anyone can reverse it instantly.
   - **Encryption** is a mathematical transformation governed by a secret cryptographic key (such as AES-GCM or RSA) designed to enforce data confidentiality. Without the secret key, decryption is computationally infeasible.
   - Base64 is **not** secure. In forensics and cybersecurity, Base64 is merely obfuscation, not encryption, and can be trivially detected and decoded by automated inspection tools.

3. **Why should investigators preserve the original files and record hashes?**  
   - Digital evidence must satisfy the legal standard of forensic chain of custody and evidentiary integrity.
   - Any inadvertent modification—such as opening an image in a graphic viewer that auto-rotates, optimizes, rewrites EXIF chunks, or strips metadata—irreversibly alters the binary file and changes its cryptographic hash.
   - Computing cryptographic hashes (SHA-256, MD5) at the point of seizure or initial triage establishes a mathematical benchmark proving that the evidence examined in court or post-incident analysis is identical to what was originally discovered.

4. **Can metadata alone prove that an image was edited or that an incident occurred? What corroborating evidence would you need?**  
   - No. Metadata is easily forged, edited, or stripped using readily available utilities (e.g., ExifTool, hex editors) without altering image pixels. An attacker can plant misleading timestamps or false attribution tags (anti-forensics).
   - To validate that an incident occurred or that an image was modified as part of an attack, investigators require corroborating multi-source evidence:
     - **Network logs**: NetFlow, Zeek/Suricata logs, DNS query logs verifying outbound queries during DNS tunneling.
     - **Host artifacts**: Windows Security Event Logs (Event IDs 4624, 4672), Sysmon Event ID 1 (process creation for `mimikatz.exe` or `cron`), and PowerShell script-block logging.
     - **Web server access logs**: HTTP server and WAF logs capturing SQL injection payloads and response status codes.
     - **File system timestamps**: Master File Table ($MFT) and USN Journal records establishing file creation and modification timestamps.

5. **How does this investigation connect to the automated evidence collection and analysis you practised in Labs 4 and 5?**  
   - In Labs 4 and 5, automated scripts processed log volumes, memory dumps, and network streams to extract indicators of compromise (IoCs), normalize diverse field structures, and generate standardized triage reports.
   - In Lab 6, this paradigm is extended to media forensics: an automated pipeline traverses heterogeneous metadata schemas (EXIF, PNG text, XMP), normalizes encoded strings, computes heuristic risk scores, and outputs structured forensic reports (`metadata_report.csv`), demonstrating that automated collection and triage are essential across all forensic domains.

### 7.2 Tool Limitations Analysis
- **Limitation of EXIF-Only Extraction**:
  Relying solely on EXIF extraction tools causes severe blind spots. In PNG-based corpora, four out of six covert messages were located outside standard EXIF IFD0 (`tEXt` chunks in `Brain.png` and `Chemicals.png`, `iTXt`/XMP in `Dopamine.png`, and Sub-IFD `UserComment` in `Activation.png`). An EXIF-only tool would produce a 66.7% false-negative rate on this corpus.
- **Limitation of Automated Risk Scoring**:
  Automated heuristic scoring relies on deterministic pattern matching and static keyword/character sets. It can trigger **false positives** by flagging legitimate Base64 color profiles, thumbnails, or camera debug notes as malicious. Conversely, it can suffer **false negatives** when facing encrypted, high-entropy payloads, non-standard steganographic algorithms (e.g., LSB replacement in image pixels), or zero-width character steganography.
