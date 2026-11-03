# Handoff Report: Environment, Metadata Scanner Architecture, Notebook Execution, and Report Generation

**Date**: 2026-11-02  
**Agent**: Teamwork Explorer (Survey 3)  
**Parent Conversation ID**: `4454555e-8e94-46d7-b2c6-e12b4f18de76`  
**Working Directory**: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3`  
**Handoff Type**: Hard (Investigation & Technical Feasibility Complete)  

---

## 1. Observation

### 1.1 Python Environment & Tooling
- **Python Runtime**: Python 3.14.8 (64-bit AMD64) located at `C:\Users\BillyZ\AppData\Local\Programs\Python\Python314\python.exe`.
- **Installed Packages**:
  - `Pillow` version `12.3.0`
  - `python-docx` version `1.2.0`
  - `defusedxml` version `0.7.1`
  - `pandas` version `3.0.6`
  - `pypdf` version `6.21.2`
  - `reportlab` version `5.1.0`
- **Missing in global site-packages**: `jupyter`, `nbformat`, `nbclient`, `ipykernel`. However, `pip install --dry-run nbformat nbclient ipykernel` confirmed that all wheels are installable and internet connectivity is operational.
- **PowerShell Encoding**: Windows PowerShell terminal defaults to CP1252. Printing UTF-8 characters like the BOM (`\ufeff` in XMP metadata) raises `UnicodeEncodeError: 'charmap' codec can't encode character '\ufeff' in position 17: character maps to <undefined>`. Fixed by configuring `sys.stdout.reconfigure(encoding='utf-8')` in all extraction scripts.

### 1.2 Image Artifacts & Metadata Findings
All six image files located in `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images` were examined:
1. `Brain.png` (2,354,330 bytes, SHA256: `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e`):
   - `getexif()` returns 0 tags.
   - PNG chunk: `tEXt` (65 bytes).
   - In `img.info['Software']`: `"RECON: Perform DNS harvesting and Subdomain enumeration."`
2. `Activation.png` (259,975 bytes, SHA256: `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904`):
   - Top-level `getexif()` contains tag 34665 (`ExifOffset`: 204), but NOT tag 37510 (`UserComment`).
   - Calling `exif.get_ifd(ExifTags.IFD.Exif)` returns tag 37510 (`UserComment`): `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`
3. `Chemicals.png` (561,245 bytes, SHA256: `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a`):
   - `getexif()` returns 0 tags.
   - PNG chunk: `tEXt` (69 bytes).
   - In `img.info['ImageDescription']`: `"EXPLOIT: Deploy SQL Injection payload to bypass WAF."`
4. `Dopamine.png` (388,411 bytes, SHA256: `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472`):
   - `getexif()` returns 0 tags.
   - PNG chunk: `iTXt` (445 bytes).
   - In `img.info['XML:com.adobe.xmp']`: contains `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>`
5. `Brain-Channel.png` (201,685 bytes, SHA256: `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359`):
   - EXIF chunk present (152 bytes).
   - Top-level tag 270 (`ImageDescription`): `"LATERAL: Pivot to internal Domain Controller using Mimikatz."`
6. `Music.png` (679,959 bytes, SHA256: `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370`):
   - EXIF chunk (382 bytes) and PNG `tEXt` chunk (94 bytes) both carry tag `Copyright`: `"RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="`
   - Decoded via Base64: `"EXFIL: Tunnel compressed database dump via DNS Covert Channel."`

### 1.3 Textbook Alignment
- Ortega (2021) *Mastering Python for Networking and Security*, Chapter 13 (pp. 799-807):
  - Discusses `PIL.Image`, `PIL.ExifTags.TAGS`, and `_getexif()` for digital cameras and JPEGs.
  - Does NOT discuss PNG text chunks (`tEXt`) or XMP XML extraction, highlighting the exact technical gap that Lab 6 asks students to reflect upon.

---

## 2. Logic Chain

1. **Premise 1 (Direct Observation)**: In `Brain.png` and `Chemicals.png`, `img.getexif()` returns 0 tags, while the payloads reside exclusively in PNG `tEXt` chunks. In `Dopamine.png`, `img.getexif()` returns 0 tags, while the payload is in an `iTXt` XMP XML element.
   - *Inference*: Any tool or scanner that relies solely on standard EXIF (`getexif()`) will fail to detect 50% of the covert channels. The automated scanner must inspect both `img.getexif()` (including sub-IFDs) and `img.info` (`tEXt` and `iTXt`/XMP).

2. **Premise 2 (Direct Observation)**: In `Activation.png`, tag 37510 (`UserComment`) is absent from top-level `exif.items()`, residing strictly in `exif.get_ifd(ExifTags.IFD.Exif)`.
   - *Inference*: A multi-IFD traversal pattern is mandatory to avoid missing hidden payloads in EXIF sub-IFDs.

3. **Premise 3 (Direct Observation)**: The recovered string prefixes are: `RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, and `EXFIL:`.
   - *Inference*: These six labels map sequentially to the classic Lockheed Martin Cyber Kill Chain and MITRE ATT&CK enterprise lifecycle:
     1. Reconnaissance (`Brain.png`)
     2. Vulnerability Identification (`Activation.png`)
     3. Exploitation (`Chemicals.png`)
     4. Persistence (`Dopamine.png`)
     5. Lateral Movement (`Brain-Channel.png`)
     6. Exfiltration (`Music.png`)
   - *Inference*: The narrative ordering is independent of file names or directory listing order.

4. **Premise 4 (Direct Observation & Prototype Execution)**: Prototyped scanner `test_scanner.py` successfully iterated all 6 images, parsed all metadata types, detected Base64 and null-padded ASCII encodings, computed consistent risk scores (15 across all six images under the classroom heuristic model), and exported clean records.
   - *Inference*: The automated scanner architecture is verified and ready for deployment in `Lab6.ipynb` and standalone `metadata_scanner.py`.

5. **Premise 5 (Direct Observation & Prototype Execution)**: `python-docx` 1.2.0 executed custom XML cell shading, cell margins, and embedded high-resolution Pillow-rendered console screenshot cards without errors.
   - *Inference*: `Lab6/Lab6-Billy-Zandan-A01371854.docx` can be programmatically generated with professional BCIT-compliant formatting, tables, and visual evidence cards.

---

## 3. Caveats

1. **Python 3.14 Execution Environment**: Python 3.14 is very new (released Sept 2026). While standard libraries, Pillow, and python-docx function properly, Jupyter ZeroMQ sockets on Windows can occasionally experience event loop timeouts. A deterministic in-process notebook runner avoids this risk entirely.
2. **Classroom Risk Model Scope**: The scoring system (+10 covert payload, +5 obfuscation, +5 anomalous carrier) produces a score of 15 for all six images. This reflects the scenario where every image was intentionally loaded with an attack fragment. In real-world enterprise environments, clean baseline images would score 0, while benign camera images with GPS or copyright tags would score 1-4.
3. **No Project File Modification**: As an explorer subagent, all testing and prototyping were performed exclusively within `.agents/teamwork/explorer_survey_3/`. No project files in `Lab6/` were modified.

---

## 4. Conclusion

1. **Feasibility**: All lab requirements, rubrics, and deliverables are fully achievable with the existing environment.
2. **Forensic Narrative**: The 6-stage secret is completely recovered, decoded, and logically sequenced based on Cyber Kill Chain progression.
3. **Scanner Architecture**: The scanner logic is verified to handle EXIF IFDs, PNG text chunks, XMP XML, and Base64 decoding, exporting `metadata_report.csv` cleanly.
4. **Deliverables Plan**:
   - `Lab6.ipynb`: Can be cleanly populated and executed in-place with all outputs preserved.
   - `metadata_report.csv`: Ready for automated generation.
   - `Lab6/Lab6-Billy-Zandan-A01371854.docx`: High-quality Word document pipeline with embedded screenshot cards and custom-styled evidence tables is fully prepared.

---

## 5. Verification Method

To independently verify the observations, inferences, and prototypes:

1. **Verify Python Environment & Core Imports**:
   ```powershell
   python -c "import sys, PIL, defusedxml, docx, pandas; print(sys.version); print('PIL:', PIL.__version__); print('Docx:', docx.__version__)"
   ```

2. **Verify Image Forensic Extraction & Narrative Ordering**:
   ```powershell
   python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3\test_scanner.py
   ```

3. **Verify Docx Styling & Embedded Visual Screenshots**:
   ```powershell
   python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3\test_screenshot.py
   python c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3\test_docx.py
   ```

4. **Invalidation Conditions**:
   - If `test_scanner.py` fails to extract any of the six secrets or crashes on sub-IFDs.
   - If `Music.png` Base64 string fails to decode into the DNS covert channel exfiltration message.
   - If `python-docx` fails to generate a readable `.docx` document.
