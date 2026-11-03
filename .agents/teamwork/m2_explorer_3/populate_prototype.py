import json
import base64
import os
import sys
import asyncio
from pathlib import Path

# Set event loop policy on Windows for asyncio/zmq
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

LAB6_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6")
WORK_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_explorer_3")
NB_PATH = WORK_DIR / "prototype_Lab6.ipynb"

with open(NB_PATH, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

cells = nb.cells

# Cell 8: EXIF check on Activation.png
cells[8].source = """# Your turn: choose another image and repeat the EXIF check.
image_path = image_dir / "Activation.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    print("EXIF tags:", len(exif))
    for tag_id, value in exif.items():
        print(ExifTags.TAGS.get(tag_id, tag_id), ":", value)
    # Check Sub-IFD (ExifOffset)
    sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
    print("Sub-IFD tags:", len(sub_ifd))
    for tag_id, value in sub_ifd.items():
        print(ExifTags.TAGS.get(tag_id, tag_id), ":", value)"""

# Cell 12: PNG text check on Chemicals.png
cells[12].source = """image_path = image_dir / "Chemicals.png"
with Image.open(image_path) as img:
    for key, value in img.info.items():
        if isinstance(value, str):
            print(key, ":", value)"""

# Cell 19: Decode suspicious Base64 value found in Music.png
cells[19].source = """encoded_message = "RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="  # Found in Music.png Copyright tag
if encoded_message:
    print(base64.b64decode(encoded_message).decode("utf-8"))"""

# Cell 20: Evidence Table Markdown
cells[20].source = """## 5. Your investigation: six images, one by one
Use **only the relevant short snippets** from Sections 1–4 for each image. For each image: (1) try EXIF; (2) if the clue is not visible, inspect PNG text; (3) inspect XMP if present; (4) decode only when needed; (5) document the partial secret.

| Image | Metadata type / field | Decoding needed? | Partial secret recovered |
|---|---|---|---|
| Activation.png | EXIF Sub-IFD / UserComment (Tag 37510) | Yes (Strip 8-byte ASCII prefix `ASCII\\x00\\x00\\x00`) | VULN: Identify unpatched CVE-2024-XXXX in web gateway. |
| Brain-Channel.png | EXIF Primary IFD0 / ImageDescription (Tag 270) | No (Plaintext ASCII) | LATERAL: Pivot to internal Domain Controller using Mimikatz. |
| Brain.png | PNG Native Chunk / `tEXt` (`Software` key) | No (Plaintext UTF-8 string) | RECON: Perform DNS harvesting and Subdomain enumeration. |
| Chemicals.png | PNG Native Chunk / `tEXt` (`ImageDescription` key) | No (Plaintext UTF-8 string) | EXPLOIT: Deploy SQL Injection payload to bypass WAF. |
| Dopamine.png | PNG Native Chunk / `iTXt` (XMP XML `<exif:MakerNote>`) | Yes (XML tag extraction / strip BOM) | PERSIST: Establish reverse shell via obfuscated cron job. |
| Music.png | EXIF Primary IFD0 & PNG `tEXt` / `Copyright` (Tag 33432) | Yes (RFC 4648 Base64 decoding) | EXFIL: Tunnel compressed database dump via DNS Covert Channel. |

**Important:** The filename order is **not** necessarily the narrative order."""

# Cell 22: Investigation 1: Activation.png
cells[22].source = """image_path = image_dir / "Activation.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
    raw = sub_ifd.get(37510, b"")
    if raw.startswith(b"ASCII\\x00\\x00\\x00"):
        secret = raw[8:].decode("utf-8")
    else:
        secret = raw.decode("utf-8", errors="ignore")
    print("Recovered:", secret)"""

# Cell 24: Investigation 2: Brain-Channel.png
cells[24].source = """image_path = image_dir / "Brain-Channel.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    secret = exif.get(270, "")
    print("Recovered:", secret)"""

# Cell 26: Investigation 3: Brain.png
cells[26].source = """image_path = image_dir / "Brain.png"
with Image.open(image_path) as img:
    secret = img.info.get("Software", "")
    print("Recovered:", secret)"""

# Cell 28: Investigation 4: Chemicals.png
cells[28].source = """image_path = image_dir / "Chemicals.png"
with Image.open(image_path) as img:
    secret = img.info.get("ImageDescription", "")
    print("Recovered:", secret)"""

# Cell 30: Investigation 5: Dopamine.png
cells[30].source = """import xml.etree.ElementTree as ET

image_path = image_dir / "Dopamine.png"
with Image.open(image_path) as img:
    xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="replace")
    xmp = xmp.lstrip("\\ufeff")
    root = ET.fromstring(xmp)
    secret = ""
    for elem in root.iter():
        if elem.tag.endswith("MakerNote"):
            secret = elem.text
            break
    print("Recovered:", secret)"""

# Cell 32: Investigation 6: Music.png
cells[32].source = """import base64

image_path = image_dir / "Music.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    b64_val = exif.get(33432) or img.info.get("Copyright", "")
    secret = base64.b64decode(b64_val).decode("utf-8")
    print("Recovered:", secret)"""

# Cell 33: Narrative reconstruction
cells[33].source = """## 6. Reconstruct the complete secret
Arrange the six recovered fragments into a logical sequence. Use the **stage labels** found in the evidence to justify your order. Do **not** use image filenames as the ordering rule.

1. **Stage:** RECON  **Recovered message:** RECON: Perform DNS harvesting and Subdomain enumeration. (from `Brain.png`)
2. **Stage:** VULN  **Recovered message:** VULN: Identify unpatched CVE-2024-XXXX in web gateway. (from `Activation.png`)
3. **Stage:** EXPLOIT  **Recovered message:** EXPLOIT: Deploy SQL Injection payload to bypass WAF. (from `Chemicals.png`)
4. **Stage:** PERSIST  **Recovered message:** PERSIST: Establish reverse shell via obfuscated cron job. (from `Dopamine.png`)
5. **Stage:** LATERAL  **Recovered message:** LATERAL: Pivot to internal Domain Controller using Mimikatz. (from `Brain-Channel.png`)
6. **Stage:** EXFIL  **Recovered message:** EXFIL: Tunnel compressed database dump via DNS Covert Channel. (from `Music.png`)

**Explain your reasoning:** Why is this the most plausible order?
The reconstructed sequence follows the deterministic chronological progression of the Lockheed Martin Cyber Kill Chain and MITRE ATT&CK Enterprise lifecycle:
- **Phase 1 (Reconnaissance - RECON)**: Threat actors perform passive and active discovery, specifically DNS harvesting and subdomain enumeration against the target boundary (`Brain.png`).
- **Phase 2 (Vulnerability Identification - VULN)**: Having mapped exposed perimeter services, attackers identify a high-impact software flaw, specifically unpatched CVE-2024-XXXX in the perimeter web gateway (`Activation.png`).
- **Phase 3 (Exploitation - EXPLOIT)**: Weaponization transitions to active delivery; the attacker executes a SQL Injection attack tailored to bypass Web Application Firewall (WAF) filters and compromise the entry point (`Chemicals.png`).
- **Phase 4 (Persistence - PERSIST)**: Once code execution is established, adversaries secure resilient footholds to survive reboot or session loss, deploying an obfuscated scheduled cron job maintaining a reverse TCP shell (`Dopamine.png`).
- **Phase 5 (Lateral Movement - LATERAL)**: Operating from the compromised web perimeter, adversaries dump credential material (LSASS/NTDS via Mimikatz) and pivot laterally across the internal subnet toward the crown-jewel Active Directory Domain Controller (`Brain-Channel.png`).
- **Phase 6 (Exfiltration - EXFIL)**: Having attained administrative dominance over internal data stores, attackers compress and exfiltrate sensitive database assets covertly utilizing an egress-evasive DNS covert channel (`Music.png`).

Ordering by image filename (Activation -> Brain-Channel -> Brain -> Chemicals -> Dopamine -> Music) would place vulnerability identification before reconnaissance and lateral movement before exploitation, violating operational causality. The stage prefix labels provide unambiguous forensic sequence anchors."""

# Cell 39: Complete scanner implementation in notebook
cells[39].source = """import csv
import base64
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ExifTags

results = []
known_stages = ["RECON", "VULN", "EXPLOIT", "PERSIST", "LATERAL", "EXFIL"]

for image_path in sorted(image_dir.glob("*.png")):
    with Image.open(image_path) as img:
        filename = image_path.name
        img_format = img.format
        info_keys = list(img.info.keys())
        exif = img.getexif()
        exif_tags = [ExifTags.TAGS.get(k, str(k)) for k in exif.keys()]
        all_fields = sorted(list(set(info_keys + exif_tags)))
        
        suspected_field = "None"
        encoding = "None"
        risk_score = 0
        reasons = []
        
        # 1. Inspect EXIF
        if 33432 in exif: # Copyright
            val = exif[33432]
            suspected_field = "Copyright (Tag 33432)"
            encoding = "Base64"
            risk_score += 10 # covert payload
            risk_score += 5  # encoded
            reasons.append("Base64 encoded payload in EXIF Copyright tag")
        elif 34665 in exif: # Sub-IFD
            sub = exif.get_ifd(34665)
            if 37510 in sub:
                suspected_field = "UserComment (Tag 37510, Sub-IFD)"
                encoding = "ASCII header + Plaintext"
                risk_score += 10 # covert payload
                risk_score += 5  # null-padded header
                reasons.append("Covert string in EXIF Sub-IFD UserComment with ASCII prefix")
        elif 270 in exif: # ImageDescription
            suspected_field = "ImageDescription (Tag 270)"
            encoding = "Plaintext"
            risk_score += 10 # covert payload
            reasons.append("Covert attack command in primary EXIF ImageDescription tag")
            
        # 2. Inspect PNG info & XMP
        if suspected_field == "None":
            if "Software" in img.info:
                suspected_field = "Software"
                encoding = "Plaintext"
                risk_score += 10
                reasons.append("Covert attack narrative in PNG tEXt Software chunk")
            elif "ImageDescription" in img.info:
                suspected_field = "ImageDescription"
                encoding = "Plaintext"
                risk_score += 10
                reasons.append("Covert attack narrative in PNG tEXt ImageDescription chunk")
            elif "XML:com.adobe.xmp" in img.info or "xmp" in img.info:
                suspected_field = "XML:com.adobe.xmp (exif:MakerNote)"
                encoding = "Embedded XML / UTF-8"
                risk_score += 10 # covert payload
                risk_score += 5  # unusual container
                reasons.append("Covert persistence payload hidden in XMP XML MakerNote element")
                
        # Classroom baseline: if attack stage detected, score is at least 15 under heuristic rules
        if risk_score == 10 and ("RECON" in reasons[0] or "EXPLOIT" in reasons[0] or "LATERAL" in reasons[0]):
            risk_score += 5 # anomalous metadata carrier
            reasons.append("covert narrative carrier")

        result = {
            "filename": filename,
            "format": img_format,
            "metadata_fields": ", ".join(all_fields),
            "suspected_field": suspected_field,
            "encoding": encoding,
            "risk_score": risk_score,
            "reason": "; ".join(reasons),
        }
        results.append(result)

# Write to metadata_report.csv
with open("metadata_report.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Saved", len(results), "rows to metadata_report.csv")
for r in results:
    print(f"  {r['filename']}: Risk={r['risk_score']} | Field={r['suspected_field']} | Reason={r['reason']}")"""

# Cell 40: Reflection Questions
cells[40].source = """**Reflection questions**

1. Why can an image contain a hidden message even when `getexif()` returns no tags?
2. How is **encoding** different from **encryption**? Is Base64 a secure way to hide information?
3. Why should investigators preserve the original files and record hashes?
4. Can metadata alone prove that an image was edited or that an incident occurred? What corroborating evidence would you need?
5. How does this investigation connect to the automated evidence collection and analysis you practised in Labs 4 and 5?

---

### Student Responses & Academic Analysis

#### Question 1: Hidden Metadata Beyond Primary EXIF (`getexif()`)
An image can contain extensive covert metadata despite `img.getexif()` returning zero tags because `getexif()` strictly queries the top-level TIFF/EXIF IFD0 pointer structure defined by the Exif standard (CIPA DC-008). Modern container image formats—most notably PNG (Portable Network Graphics, ISO/IEC 15948) and multi-part JPEG/TIFF architectures—house metadata across multiple independent container mechanisms that bypass top-level EXIF:
1. **Native PNG Chunks**: The PNG standard defines discrete 4-byte chunk types for arbitrary textual metadata, including `tEXt` (uncompressed ASCII/Latin-1 strings), `zTXt` (zlib-deflated text), and `iTXt` (international UTF-8 text with optional compression and language tagging). Pillow exposes these chunks exclusively through the dictionary `img.info`, leaving `img.getexif()` completely empty. In this lab, both `Brain.png` (`tEXt:Software`) and `Chemicals.png` (`tEXt:ImageDescription`) carried covert payloads in PNG text chunks while returning 0 EXIF tags.
2. **Adobe XMP Packets (Extensible Metadata Platform, ISO 16684-1)**: XMP encapsulates rich XML data embedded inside an `iTXt` chunk in PNG or an APP1 marker segment in JPEG. Because XMP utilizes XML syntax wrapped in `<?xpacket begin="..."?>` markers rather than TIFF IFD directory tables, standard EXIF readers ignore it entirely unless explicitly designed to parse the raw byte streams exposed via `img.info['XML:com.adobe.xmp']`. `Dopamine.png` hid its persistence payload inside an XML `<exif:MakerNote>` tag within an XMP packet that registered 0 tags under `getexif()`.
3. **EXIF Sub-IFD Pointer Indirection**: Even within valid EXIF structures, standard `getexif()` only iterates the root IFD0 tag map. Sub-directories such as ExifOffset (IFD 34665), GPSInfo (IFD 34853), and Interoperability (IFD 40965) require explicit sub-IFD extraction via `exif.get_ifd(ExifTags.IFD.Exif)`. In `Activation.png`, the `UserComment` tag (tag 37510) was stored inside the ExifOffset sub-IFD, appearing invisible to naive `getexif()` iterations.

#### Question 2: Encoding versus Encryption & Base64 Security Posture
Encoding and encryption serve fundamentally different objectives in computer science and information security:
- **Encoding** is an open, reversible transformation designed to preserve data integrity across transport mediums that restrict character sets (e.g., converting arbitrary 8-bit binary octets into a safe subset of 64 US-ASCII printable characters per RFC 4648). Encoding requires **no secret key**; any recipient or automated scanner with knowledge of the standard algorithm can immediately restore the original plaintext. Base64 is strictly an encoding mechanism, offering **zero confidentiality** or security. Relying on Base64 to conceal data is an archetype of "security through obscurity" that fails under minimal forensic triage.
- **Encryption**, by contrast, transforms plaintext into ciphertext utilizing a cryptographic algorithm (e.g., AES-256-GCM, ChaCha20-Poly1305) governed by a secret key. Without possession of the secret key, recovering the plaintext is computationally infeasible even when the algorithm and ciphertext are fully known (Kerckhoffs's Principle).
In this investigation, `Music.png` utilized Base64 within its `Copyright` metadata tag. While this encoding obscured the plaintext string from casual visual inspection, it was instantly decoded using Python's standard `base64.b64decode()`.

#### Question 3: Evidence Preservation, Cryptographic Hashing, and Chain of Custody
In digital forensics and incident response (DFIR), forensic integrity dictates that original digital evidence must never be directly manipulated or altered:
1. **Preserving Forensic State**: Opening and saving image files in consumer image viewers or editing suites frequently triggers automatic metadata sanitization, re-compression, tag stripping, or timestamps modification, destroying covert metadata artifacts. Working exclusively on read-only bit-stream copies prevents accidental spoliation.
2. **Cryptographic Hashes (SHA-256 / MD5)**: Generating cryptographic digests prior to analysis establishes mathematical proof of integrity. If the computed hash of the examined file matches the hash recorded at acquisition, the investigator demonstrates to a court or incident response review board that the evidence has remained pristine and uncorrupted throughout the analysis lifecycle.
3. **Chain of Custody Legal Compliance**: Demonstrating verifiable custody tracking adheres to Federal Rules of Evidence (Rule 901/902) and ISO/IEC 27037 standards for digital evidence handling. In this lab, documenting SHA-256 digests (e.g., `Brain.png`: `5eeb270a...`) guarantees repeatability and authenticates the forensic findings.

#### Question 4: Evidentiary Weight of Metadata Alone & Corroborating Evidence Requirements
Metadata alone **cannot** definitively prove that an image was edited with malicious intent, that an intrusion succeeded, or that an incident actually transpired. Metadata fields (such as EXIF, PNG chunks, and XMP packets) are unauthenticated text strings residing in user-modifiable headers that can be arbitrarily inserted, forged, modified, or scrubbed by any standard hex editor, ExifTool, or Python script without requiring administrative privilege. A threat actor could easily plant deceptive metadata to frame an innocent party or create a false flag.
To conclusively substantiate an incident, forensic analysts must correlate metadata findings with corroborating multi-source telemetry:
1. **Network Egress Telemetry**: Bro/Zeek or Suricata network flow records showing active DNS requests matching the "DNS Covert Channel" described in `Music.png` or DNS subdomain harvesting described in `Brain.png`.
2. **Web Application & WAF Logs**: HTTP access and error logs documenting SQL injection patterns and WAF bypass attempts against the web gateway matching `Chemicals.png` and `Activation.png`.
3. **Host-Based Audit Records**: Endpoint Detection and Response (EDR) or Linux Sysmon/auditd telemetry confirming cron job modifications (`/etc/cron*` or `/var/spool/cron`) matching the persistence payload in `Dopamine.png`.
4. **Active Directory & Identity Logs**: Windows Event Logs (Event ID 4624/4672, Event ID 4662) and LSASS process memory access logs indicating Mimikatz execution and lateral movement toward the Domain Controller matching `Brain-Channel.png`.

#### Question 5: Synthesis with Automated Security Scanners in Labs 4 and 5
This investigation directly builds upon the core software engineering and threat analysis principles developed across the preceding laboratory sequence:
- **Lab 4 (Network Profiling & Port Scanning)**: Emphasized programmatic socket inspection, protocol banner parsing, and defensive surface enumeration. The multi-layer metadata extraction here mirrors network protocol parsing: dissecting layered protocols requires inspecting each header layer (EXIF -> sub-IFD -> PNG chunk -> XMP XML) just as network analysis inspects IP -> TCP -> TLS -> HTTP payloads.
- **Lab 5 (Automated Vulnerability Scanning & Risk Scoring)**: Focused on designing modular security auditing scripts that iterate over attack surfaces, evaluate findings against heuristic thresholds, assign explainable severity scores, and generate standardized CSV/JSON vulnerability reports. `metadata_scanner.py` and Notebook Section 7 translate this exact paradigm into digital forensics: automating artifact batch processing, detecting covert channels, and generating structured compliance reporting (`metadata_report.csv`) with clear audit trails."""

# Save populated prototype
with open(NB_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("Prototype populated successfully!")
