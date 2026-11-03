# Handoff Report — Lab 6 Specification Mining

**Author:** Lab 6 Specification Miner  
**Target:** Team Orchestrator (`0990deed-eb58-4c28-ae86-efa3d3d229fd`)  
**Type:** Hard Handoff (Investigation & Specification Mining Complete)  
**Working Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_1`  
**Reference Document:** `.agents/teamwork/explorer_survey_1/analysis.md`  

---

## 1. Observation

1. **Workspace and File Hierarchy:**
   - Path `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6` contains:
     - `Lab6.ipynb` (20,080 bytes)
     - `Images/` containing 6 PNG images: `Activation.png` (259,975 B), `Brain-Channel.png` (201,685 B), `Brain.png` (2,354,330 B), `Chemicals.png` (561,245 B), `Dopamine.png` (388,411 B), `Music.png` (679,959 B).
   - Author profile identified from `Lab0/Lab0-Billy-Zandan-A01371854.pdf`: Student Billy Zandan (Student Number: A01371854). Course: FSCT 8561.

2. **Notebook Cell Structure (`Lab6.ipynb`):**
   - Exactly 42 cells (indices 0 to 41), comprising 19 code cells and 23 markdown cells.
   - Cells 0–4: Introduction, scenario, environment check (`Images found: 6`), and evidence log instructions.
   - Cells 5–8: Technique 1 (EXIF metadata via `img.getexif()`), observation prompts, and practice cell for `Activation.png`.
   - Cells 9–12: Technique 2 (PNG text metadata via `img.info`), observation prompts, and practice cell for `Chemicals.png`.
   - Cells 13–15: Technique 3 (XMP metadata via `XML:com.adobe.xmp`), observation prompts for `Dopamine.png`.
   - Cells 16–19: Technique 4 (Base64 decoding via `base64.b64decode()`), observation prompts for `Music.png`.
   - Cells 20–32: Section 5 systematic investigation across all 6 images with individual markdown headings and code cells (Cells 22, 24, 26, 28, 30, 32).
   - Cell 33: Section 6 reconstruction template (numbered stages 1–6) and logical justification prompt.
   - Cells 34–39: Section 7 automated metadata scanner requirements, 3-tier risk model (+10, +5, +5), starter cells (35, 37), and scanner implementation cell (39) writing to `metadata_report.csv`.
   - Cell 40: 5 formal reflection questions.
   - Cell 41: Submission requirements and official 100-point grading rubric (25 pts extraction evidence, 25 pts covert channel decoding, 20 pts 6-stage narrative reconstruction, 20 pts scanner & CSV report, 10 pts interpretations & presentation).

3. **Verbatim Metadata Extraction Findings (Observed via Python 3.14 & PIL):**
   - `Activation.png` (MD5 `28a931ca770d9118a8286c0db414332c`, SHA-256 `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904`):
     - `img.getexif()` returns 10 top-level tags (`Make: Nikon`, `Model: D750`, `GPSInfo: 396`, `ExifOffset: 204`).
     - SubIFD `ExifOffset` (IFD 34665) tag 37510 (`UserComment`) contains: `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`.
   - `Brain-Channel.png` (MD5 `8e8a9d7276707a9f18af7c2e09c70e3a`, SHA-256 `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359`):
     - `img.getexif()` contains tag 270 (`ImageDescription`): `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'`.
   - `Brain.png` (MD5 `5d69dd3de9b5f8557ba26d8bcc644af4`, SHA-256 `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e`):
     - `img.getexif()` returns 0 tags.
     - `img.info['Software']` contains: `'RECON: Perform DNS harvesting and Subdomain enumeration.'`.
   - `Chemicals.png` (MD5 `694d3d3984e34b39a59e0305e837eb5f`, SHA-256 `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a`):
     - `img.getexif()` returns 0 tags.
     - `img.info['ImageDescription']` contains: `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'`.
   - `Dopamine.png` (MD5 `22eedbe31ba01a541f29758f508d2a58`, SHA-256 `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472`):
     - `img.getexif()` returns 0 tags.
     - `img.info['XML:com.adobe.xmp']` contains XMP packet with `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>`.
   - `Music.png` (MD5 `5924abe517910c58798d5567ae27323d`, SHA-256 `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370`):
     - EXIF tag 33432 (`Copyright`) and `img.info['Copyright']` contain: `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='`.
     - Base64 decoded: `'EXFIL: Tunnel compressed database dump via DNS Covert Channel.'`.

4. **Environment Packages:**
   - Python 3.14 (`C:\Users\BillyZ\AppData\Local\Programs\Python\Python314\python.exe`)
   - `Pillow` is installed and verified.
   - `python-docx` is installed and verified.

---

## 2. Logic Chain

1. **Metadata Channel Diversity (Step 1 -> Observation 3):**
   Three distinct channels are utilized: EXIF (standard tags & SubIFDs), native PNG text chunks (`img.info`), and XMP XML packets. An extraction tool inspecting only EXIF (`img.getexif()`) misses 4 out of the 6 covert messages (`Brain.png`, `Chemicals.png`, `Dopamine.png`, and the nested SubIFD in `Activation.png`). Therefore, the implementation must query both `img.getexif()`, `exif.get_ifd(ExifTags.IFD.Exif)`, `img.info`, and XMP keys.

2. **Attack Lifecycle Reconstruction (Step 2 -> Observation 3):**
   The six extracted fragments possess explicit operational prefixes: `RECON`, `VULN`, `EXPLOIT`, `PERSIST`, `LATERAL`, and `EXFIL`. Mapping these to the Cyber Kill Chain and MITRE ATT&CK matrices establishes an unambiguous chronological sequence:
   - Stage 1: RECON (`Brain.png`) -> Reconnaissance / OSINT.
   - Stage 2: VULN (`Activation.png`) -> Vulnerability scanning / CVE discovery.
   - Stage 3: EXPLOIT (`Chemicals.png`) -> Exploitation / SQLi WAF bypass.
   - Stage 4: PERSIST (`Dopamine.png`) -> Persistence / cron reverse shell.
   - Stage 5: LATERAL (`Brain-Channel.png`) -> Lateral movement / Mimikatz DC compromise.
   - Stage 6: EXFIL (`Music.png`) -> Exfiltration / DNS covert channel.
   Ordering by filename would break the causal sequence.

3. **Scanner Architecture & CSV Schema (Step 3 -> Observation 2 & ORIGINAL_REQUEST.md):**
   The automated scanner must output a 7-column CSV (`metadata_report.csv`): `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`. The risk model heuristic adds +10 for confirmed covert messages, +5 for Base64 encoding requiring investigation, and +5 for anomalous metadata (such as camera hardware/GPS embedded in web graphics or hidden XMP MakerNote). This yields scores of 10 or 15 across the images.

4. **Deliverable Completeness (Step 4 -> Observation 2, 4, ORIGINAL_REQUEST.md):**
   The required deliverables are:
   - `Lab6/Lab6.ipynb`: Updated in place with working code cells and cell outputs.
   - `Lab6/metadata_report.csv`: Complete 6-row CSV matching the schema.
   - `Lab6/Lab6_Report.docx`: Complete professional Word report adhering to the 100-point rubric, authored under Billy Zandan (A01371854).

---

## 3. Caveats

- **No Caveats:** All 6 images were successfully opened, inspected, and verified with byte-level precision.
- **Assumptions:** Student identity is Billy Zandan (Student Number A01371854), confirmed via `Lab0/Lab0-Billy-Zandan-A01371854.pdf`.

---

## 4. Conclusion

Specification mining for Lab 6 is 100% complete. Every requirement, cell prompt, hidden message, decoding mechanism, rubric component, risk scoring rule, and report section has been extracted, verified, and documented in detail in `analysis.md`. The orchestrator and implementation subagents have all required specifications to execute `Lab6.ipynb`, generate `metadata_scanner.py` and `metadata_report.csv`, and author `Lab6/Lab6_Report.docx`.

---

## 5. Verification Method

To independently verify the observations:

1. **Verify All Recovered Secrets:**
   ```powershell
   python -c "
   from PIL import Image, ExifTags
   import base64

   # 1. Brain.png (RECON)
   with Image.open('Lab6/Images/Brain.png') as img:
       print('Stage 1 (Brain.png):', img.info['Software'])

   # 2. Activation.png (VULN)
   with Image.open('Lab6/Images/Activation.png') as img:
       comment = img.getexif().get_ifd(ExifTags.IFD.Exif)[37510]
       print('Stage 2 (Activation.png):', comment[8:].decode('utf-8'))

   # 3. Chemicals.png (EXPLOIT)
   with Image.open('Lab6/Images/Chemicals.png') as img:
       print('Stage 3 (Chemicals.png):', img.info['ImageDescription'])

   # 4. Dopamine.png (PERSIST)
   with Image.open('Lab6/Images/Dopamine.png') as img:
       import re
       xmp = img.info['XML:com.adobe.xmp']
       m = re.search(r'<exif:MakerNote>(.*?)</exif:MakerNote>', xmp)
       print('Stage 4 (Dopamine.png):', m.group(1))

   # 5. Brain-Channel.png (LATERAL)
   with Image.open('Lab6/Images/Brain-Channel.png') as img:
       print('Stage 5 (Brain-Channel.png):', img.getexif()[270])

   # 6. Music.png (EXFIL)
   with Image.open('Lab6/Images/Music.png') as img:
       raw = img.getexif()[33432]
       print('Stage 6 (Music.png):', base64.b64decode(raw).decode('utf-8'))
   "
   ```
2. **Inspect Detailed Analysis:**
   Read `.agents/teamwork/explorer_survey_1/analysis.md`.

