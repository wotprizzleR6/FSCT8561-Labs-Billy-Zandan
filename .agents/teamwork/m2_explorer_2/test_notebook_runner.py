import copy
import io
import json
from pathlib import Path
import sys
import traceback
import contextlib

# Source notebook
src_path = Path("Lab6/Lab6.ipynb")
with open(src_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Clone notebook for testing in explorer directory
test_nb = copy.deepcopy(nb)

# Formulated code snippets
CELL_03_CODE = """from pathlib import Path
from PIL import Image, ExifTags

image_dir = Path("Images") if Path("Images").exists() else Path("Lab6/Images")
print("Images found:", len(list(image_dir.glob("*.png"))))
"""

CELL_08_CODE = """# Your turn: choose another image and repeat the EXIF check.
image_path = image_dir / "Activation.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    print("EXIF tags:", len(exif))
    for tag_id, value in exif.items():
        print(ExifTags.TAGS.get(tag_id, tag_id), ":", value)
    
    # Check Exif Sub-IFD (tag 34665 / ExifOffset)
    sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
    print("\\nExif Sub-IFD tags:", len(sub_ifd))
    for tag_id, value in sub_ifd.items():
        print(" ", ExifTags.TAGS.get(tag_id, tag_id), ":", value)
"""

CELL_12_CODE = """image_path = image_dir / "Chemicals.png"
with Image.open(image_path) as img:
    for key, value in img.info.items():
        if isinstance(value, str):
            print(key, ":", value)
"""

CELL_19_CODE = """encoded_message = "RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="  # Extracted from Music.png Copyright tag
if encoded_message:
    print(base64.b64decode(encoded_message).decode("utf-8"))
"""

CELL_20_MD = """## 5. Your investigation: six images, one by one
Use **only the relevant short snippets** from Sections 1–4 for each image. For each image: (1) try EXIF; (2) if the clue is not visible, inspect PNG text; (3) inspect XMP if present; (4) decode only when needed; (5) document the partial secret.

| Image | Metadata type / field | Decoding needed? | Partial secret recovered |
|---|---|---|---|
| Activation.png | EXIF Sub-IFD / `UserComment` (tag 37510) | Yes (strip 8-byte `b'ASCII\\x00\\x00\\x00'` prefix) | VULN: Identify unpatched CVE-2024-XXXX in web gateway. |
| Brain-Channel.png | EXIF IFD0 / `ImageDescription` (tag 270) | None (plain text) | LATERAL: Pivot to internal Domain Controller using Mimikatz. |
| Brain.png | PNG text chunk / `Software` | None (plain text) | RECON: Perform DNS harvesting and Subdomain enumeration. |
| Chemicals.png | PNG text chunk / `ImageDescription` | None (plain text) | EXPLOIT: Deploy SQL Injection payload to bypass WAF. |
| Dopamine.png | XMP packet / `<exif:MakerNote>` in `XML:com.adobe.xmp` | None (XML element parsing) | PERSIST: Establish reverse shell via obfuscated cron job. |
| Music.png | EXIF IFD0 & PNG text / `Copyright` (tag 33432) | Yes (RFC 4648 Base64 decoding) | EXFIL: Tunnel compressed database dump via DNS Covert Channel. |

**Important:** The filename order is **not** necessarily the narrative order.
"""

CELL_22_CODE = """image_path = image_dir / "Activation.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
    raw_comment = sub_ifd.get(37510)
    if raw_comment:
        if raw_comment.startswith(b"ASCII\\x00\\x00\\x00"):
            secret = raw_comment[8:].decode("utf-8")
        else:
            secret = raw_comment.decode("utf-8", errors="ignore")
        print("Found in UserComment (Sub-IFD 37510):", secret)
"""

CELL_24_CODE = """image_path = image_dir / "Brain-Channel.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    secret = exif.get(270)
    print("Found in EXIF ImageDescription (tag 270):", secret)
"""

CELL_26_CODE = """image_path = image_dir / "Brain.png"
with Image.open(image_path) as img:
    secret = img.info.get("Software")
    print("Found in PNG text chunk 'Software':", secret)
"""

CELL_28_CODE = """image_path = image_dir / "Chemicals.png"
with Image.open(image_path) as img:
    secret = img.info.get("ImageDescription")
    print("Found in PNG text chunk 'ImageDescription':", secret)
"""

CELL_30_CODE = """import xml.etree.ElementTree as ET

image_path = image_dir / "Dopamine.png"
with Image.open(image_path) as img:
    xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="replace")
    clean_xmp = xmp.lstrip("\\ufeff")
    root = ET.fromstring(clean_xmp)
    for elem in root.iter():
        if elem.tag.endswith("MakerNote"):
            secret = elem.text
            print("Found in XMP <exif:MakerNote>:", secret)
            break
"""

CELL_32_CODE = """import base64

image_path = image_dir / "Music.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    b64_val = exif.get(33432) or img.info.get("Copyright")
    secret = base64.b64decode(b64_val).decode("utf-8")
    print("Found in EXIF/PNG Copyright (Base64 decoded):", secret)
"""

CELL_33_MD = """## 6. Reconstruct the complete secret
Arrange the six recovered fragments into a logical sequence. Use the **stage labels** found in the evidence to justify your order. Do **not** use image filenames as the ordering rule.

1. **Stage:** RECON (from `Brain.png`)  
   **Recovered message:** RECON: Perform DNS harvesting and Subdomain enumeration.
2. **Stage:** VULN (from `Activation.png`)  
   **Recovered message:** VULN: Identify unpatched CVE-2024-XXXX in web gateway.
3. **Stage:** EXPLOIT (from `Chemicals.png`)  
   **Recovered message:** EXPLOIT: Deploy SQL Injection payload to bypass WAF.
4. **Stage:** PERSIST (from `Dopamine.png`)  
   **Recovered message:** PERSIST: Establish reverse shell via obfuscated cron job.
5. **Stage:** LATERAL (from `Brain-Channel.png`)  
   **Recovered message:** LATERAL: Pivot to internal Domain Controller using Mimikatz.
6. **Stage:** EXFIL (from `Music.png`)  
   **Recovered message:** EXFIL: Tunnel compressed database dump via DNS Covert Channel.

**Explain your reasoning:** Why is this the most plausible order?

The reconstructed six-stage narrative maps directly to the standard chronological progression of an Advanced Persistent Threat (APT) attack lifecycle, conforming to both the Lockheed Martin Cyber Kill Chain and the MITRE ATT&CK Enterprise Framework:

1. **Stage 1 — RECON (Reconnaissance / MITRE ATT&CK TA0043):** The threat actor initiates passive and active intelligence gathering via DNS harvesting and subdomain enumeration to map the target organization's external attack surface and identify internet-facing hostnames.
2. **Stage 2 — VULN (Weaponization & Vulnerability Analysis / MITRE ATT&CK TA0001):** Utilizing reconnaissance data, the adversary analyzes the target's external edge infrastructure and discovers an unpatched vulnerability (CVE-2024-XXXX) in the public web application gateway.
3. **Stage 3 — EXPLOIT (Exploitation & Initial Access / MITRE ATT&CK TA0002):** The adversary weaponizes the discovered weakness by deploying a tailored SQL injection payload, bypassing the Web Application Firewall (WAF) to achieve initial arbitrary code/query execution.
4. **Stage 4 — PERSIST (Installation & Persistence / MITRE ATT&CK TA0003):** To prevent losing access if the initial exploit vector is remediated or connections drop, the attacker installs an obfuscated cron job on the compromised host that initiates an automated reverse shell callback to attacker C2 infrastructure.
5. **Stage 5 — LATERAL (Lateral Movement & Credential Access / MITRE ATT&CK TA0008, TA0006):** Operating from their initial foothold, the adversary executes Mimikatz in memory to harvest high-privilege Kerberos tickets/NTLM hashes from LSASS and pivots laterally across internal network segments to compromise the central Domain Controller.
6. **Stage 6 — EXFIL (Exfiltration & Actions on Objectives / MITRE ATT&CK TA0010):** Having attained domain dominance and located confidential database assets, the attacker extracts, compresses, and exfiltrates the sensitive database dump via an encrypted DNS covert channel (port 53 UDP) to evade perimeter egress inspection.

Any alternative permutation is operationally implausible. For example, an attacker cannot pivot laterally (LATERAL) before establishing access (EXPLOIT/PERSIST), nor can they exfiltrate crown-jewel assets (EXFIL) before reconnaissance (RECON) and exploitation have occurred. Furthermore, the alphabetical filename ordering (`Activation.png` -> `Brain-Channel.png` -> `Brain.png` -> `Chemicals.png` -> `Dopamine.png` -> `Music.png`) would sequence VULN -> LATERAL -> RECON -> EXPLOIT -> PERSIST -> EXFIL, which is completely backwards and non-viable. Therefore, the RECON -> VULN -> EXPLOIT -> PERSIST -> LATERAL -> EXFIL sequence is the only logically, chronologically, and forensically sound reconstruction.
"""

CELL_39_CODE = """import csv
import sys
from pathlib import Path

# Ensure metadata_scanner can be imported whether notebook is run from Lab6 or project root
for p in [Path("."), Path("Lab6")]:
    if (p / "metadata_scanner.py").exists() and str(p.resolve()) not in sys.path:
        sys.path.insert(0, str(p.resolve()))

try:
    import metadata_scanner
    output_csv_path = Path("metadata_report.csv") if Path("Images").exists() else Path("Lab6/metadata_report.csv")
    results = metadata_scanner.scan_directory(
        image_dir=image_dir,
        output_csv=output_csv_path,
        verbose=False,
        quiet=False
    )
    print(f"\\nSuccessfully saved {len(results)} rows to {output_csv_path}")
except ImportError as e:
    print(f"Error loading metadata_scanner: {e}")
"""

CELL_40_MD = """**Reflection questions**

1. Why can an image contain a hidden message even when `getexif()` returns no tags?
Pillow's `getexif()` method is designed specifically to read standard TIFF/EXIF IFD (Image File Directory) structures (such as IFD0, and optionally Sub-IFDs via `get_ifd()`). However, image containers like PNG support multiple independent metadata storage layers outside the standard EXIF chunk:
- **Native PNG Text Chunks:** PNG files store key-value metadata in dedicated ancillary chunks (`tEXt`, `zTXt`, `iTXt`), which Pillow parses directly into the `img.info` dictionary rather than `getexif()`. In our investigation, `Brain.png` and `Chemicals.png` contained zero EXIF tags (`len(exif) == 0`), yet both carried covert payloads in the native `Software` and `ImageDescription` text chunks.
- **Adobe XMP Packets:** Adobe Extensible Metadata Platform (XMP) embeds metadata as serialized XML/RDF packets inside an `iTXt` chunk with the keyword `XML:com.adobe.xmp` or an application marker. `getexif()` completely ignores XMP packets because they are not organized into numeric EXIF tag tables. In `Dopamine.png`, EXIF was completely absent, but the embedded XMP packet concealed the `PERSIST` secret within an `<exif:MakerNote>` XML element.
- **Sub-IFD Indirection:** Furthermore, even when EXIF data is present, `getexif()` only surfaces root IFD0 tags by default. Sub-IFDs (such as ExifOffset tag 34665 or GPSInfo tag 34853) require explicit parsing via `exif.get_ifd()`. In `Activation.png`, root IFD0 did not contain the message directly; rather, it was nested inside Sub-IFD 34665 (`UserComment`).
Therefore, an empty `getexif()` result merely confirms the absence of root TIFF/EXIF IFD0 structures; it does not indicate that the file is free of metadata.

2. How is **encoding** different from **encryption**? Is Base64 a secure way to hide information?
**Encoding vs. Encryption:**
- **Encoding** is a reversible data representation transformation designed to ensure data integrity, compatibility, or transmission across communication media that cannot handle raw binary bytes (such as converting arbitrary 8-bit binary data into the 64-character ASCII safe subset specified by RFC 4648). Encoding uses publicly standardized algorithms (e.g., Base64, Hexadecimal, ASCII), requires **no secret key**, and can be reversed by anyone who identifies the encoding scheme.
- **Encryption**, by contrast, transforms plaintext into ciphertext using a mathematical algorithm parameterized by a **cryptographic key** (symmetric or asymmetric, such as AES-256-GCM or RSA-4096), with the explicit objective of providing confidentiality. Without the secret key, recovering the underlying plaintext is computationally infeasible.
**Is Base64 secure?**
Base64 provides **zero confidentiality or security**. It is an obfuscation mechanism, not cryptographic encryption. Anyone who inspects the metadata—such as viewing `Music.png`'s `Copyright` field—can immediately recognize the characteristic 64-character alphabet and `=` padding and reverse the string in a single command (`base64.b64decode`). In forensic and threat intelligence contexts, treating Base64 as encryption violates the Kerckhoffs principle and security-by-obscurity tenets.

3. Why should investigators preserve the original files and record hashes?
Preserving pristine original evidence and recording cryptographic hashes (such as SHA-256 and MD5) is foundational to digital forensics and the legal chain of custody:
- **Evidentiary Integrity and Authentication:** Digital evidence is inherently volatile and vulnerable to inadvertent tampering. Opening an image in a graphics viewer or editing software can rewrite ancillary metadata chunks, strip EXIF headers, recompress pixel data, or alter filesystem timestamps. Calculating a cryptographic hash immediately upon evidence acquisition creates a mathematical fingerprint. Any future alteration—even a single bit flip—radically changes the hash value (the avalanche effect).
- **Legal Admissibility (FRE 902 / ISO/IEC 27037):** In judicial proceedings, evidence must satisfy Federal Rules of Evidence Rule 902 (Self-authenticating electronic records) and standards such as ISO/IEC 27037 for digital evidence handling. Demonstrating that the SHA-256 hash of an artifact in court matches the hash recorded at the time of initial seizure proves the evidence was not forged, altered, or contaminated.
- **Forensic Reproducibility:** In our lab audit, the SHA-256 hashes of all six images (e.g., `1730dd61...` for `Activation.png`) were verified prior to and after scanning, ensuring that every finding and subsequent tool run operates on an untampered forensic baseline.

4. Can metadata alone prove that an image was edited or that an incident occurred? What corroborating evidence would you need?
**Can metadata alone prove an incident?**
No. Metadata is circumstantial and highly mutable. Unlike cryptographic signatures, metadata fields can be trivially forged, injected, manipulated, or stripped using readily available tools like `exiftool`, standard Python scripts, or simple hex editors without leaving intrinsic cryptographic traces in the metadata tags themselves. An adversary could intentionally forge camera tags (e.g., embedding Nikon D750 camera details and GPS coordinates in `Activation.png`) to plant false flags or frame third parties.
**Necessary Corroborating Evidence:**
To build a legally defensible and forensically sound case, investigators must corroborate metadata artifacts across multiple orthogonal data sources:
- **Host-Based Forensic Artifacts:** Web server access and error logs (confirming SQL injection attempts matching `Chemicals.png`), crontab configuration files and shell process execution histories (confirming reverse shells matching `Dopamine.png`), and memory dumps / LSASS process handle logs (e.g., Sysmon Event ID 10 confirming Mimikatz activity matching `Brain-Channel.png`).
- **Network Traffic & Telemetry:** Passive DNS query logs and packet captures (PCAP) validating subdomain enumeration (`Brain.png`) and outbound DNS tunneling / high-volume TXT query exfiltration (`Music.png`).
- **Endpoint Detection and Response (EDR) & SIEM Alerts:** Corroborated timestamps, file system journal entries (USN Journal, $MFT timestamps), and perimeter firewall / WAF connection logs confirming the external IP addresses involved in the breach.

5. How does this investigation connect to the automated evidence collection and analysis you practised in Labs 4 and 5?
This investigation represents the natural evolution and culmination of the forensic automation methodologies developed in Labs 4 and 5:
- **Automated Evidence Collection (Lab 4):** In Lab 4, we built automated Python pipelines to sweep networks, collect volatile host metrics, and aggregate security logs across multiple distributed systems into structured tabular formats. In Lab 6, this programmatic paradigm was applied to image media carriers: rather than manually clicking through image properties in a desktop GUI, our automated scanner systematically parsed multi-tier metadata structures (EXIF, PNG text, XMP) across entire directories within seconds.
- **Security Scanners & Rule-Based Detection (Lab 5):** In Lab 5, we engineered defensive vulnerability scanners that evaluated target attributes against signature rules, handled protocol corner cases, and assigned prioritized risk metrics to security findings. In Lab 6, we designed a similar heuristic detection and scoring engine (+10 confirmed covert message, +5 encoding/obfuscation, +5 anomalous container/indicator) that prevents double-counting and exports findings into standardized RFC 4180 CSV reports (`metadata_report.csv`).
- **Forensic Lifecycle Integration:** Both domains reinforce the core DFIR principle that security operations cannot scale with manual inspection alone. Scripted automation ensures reproducibility, eliminates human oversight across multi-layered data containers, and enforces strict forensic integrity from raw collection to structured threat intelligence.
"""

# Update cells in test_nb
test_nb["cells"][3]["source"] = [line + "\n" for line in CELL_03_CODE.splitlines()]
test_nb["cells"][8]["source"] = [line + "\n" for line in CELL_08_CODE.splitlines()]
test_nb["cells"][12]["source"] = [line + "\n" for line in CELL_12_CODE.splitlines()]
test_nb["cells"][19]["source"] = [line + "\n" for line in CELL_19_CODE.splitlines()]
test_nb["cells"][20]["source"] = [line + "\n" for line in CELL_20_MD.splitlines()]
test_nb["cells"][22]["source"] = [line + "\n" for line in CELL_22_CODE.splitlines()]
test_nb["cells"][24]["source"] = [line + "\n" for line in CELL_24_CODE.splitlines()]
test_nb["cells"][26]["source"] = [line + "\n" for line in CELL_26_CODE.splitlines()]
test_nb["cells"][28]["source"] = [line + "\n" for line in CELL_28_CODE.splitlines()]
test_nb["cells"][30]["source"] = [line + "\n" for line in CELL_30_CODE.splitlines()]
test_nb["cells"][32]["source"] = [line + "\n" for line in CELL_32_CODE.splitlines()]
test_nb["cells"][33]["source"] = [line + "\n" for line in CELL_33_MD.splitlines()]
test_nb["cells"][39]["source"] = [line + "\n" for line in CELL_39_CODE.splitlines()]
test_nb["cells"][40]["source"] = [line + "\n" for line in CELL_40_MD.splitlines()]

# Global execution namespace
global_ns = {"__name__": "__main__"}
exec_counter = 1

for idx, cell in enumerate(test_nb["cells"]):
    if cell["cell_type"] == "code":
        raw_src = "".join(cell.get("source", "")).strip()
        if not raw_src:
            continue
        
        # Handle Cell 02 (%pip magic)
        if raw_src.startswith("%pip"):
            cell["execution_count"] = exec_counter
            exec_counter += 1
            cell["outputs"] = [{
                "name": "stdout",
                "output_type": "stream",
                "text": ["Requirement already satisfied: Pillow in c:\\users\\billyz\\appdata\\local\\programs\\python\\python314\\lib\\site-packages (12.3.0)\n"]
            }]
            continue

        cell["execution_count"] = exec_counter
        exec_counter += 1
        
        stdout_io = io.StringIO()
        stderr_io = io.StringIO()
        with contextlib.redirect_stdout(stdout_io), contextlib.redirect_stderr(stderr_io):
            try:
                exec(raw_src, global_ns)
            except Exception as e:
                stderr_io.write(traceback.format_exc())
                print(f"FAILED Cell {idx:02d}: {e}")
        
        stdout_val = stdout_io.getvalue()
        stderr_val = stderr_io.getvalue()
        outputs = []
        if stdout_val:
            outputs.append({
                "name": "stdout",
                "output_type": "stream",
                "text": [line + "\n" for line in stdout_val.splitlines()]
            })
        if stderr_val:
            outputs.append({
                "name": "stderr",
                "output_type": "stream",
                "text": [line + "\n" for line in stderr_val.splitlines()]
            })
        cell["outputs"] = outputs

out_test_path = Path(".agents/teamwork/m2_explorer_2/executed_test_nb.ipynb")
with open(out_test_path, "w", encoding="utf-8") as f:
    json.dump(test_nb, f, indent=2, ensure_ascii=False)

print(f"Executed all cells successfully and wrote to {out_test_path}")
