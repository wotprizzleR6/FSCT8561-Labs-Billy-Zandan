# Handoff Report: Specification Mining for Lab 6 (Covert Channels in Image Metadata)

**Agent:** `spec_miner_survey_1`  
**Working Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\spec_miner_survey_1`  
**Parent Agent:** `4454555e-8e94-46d7-b2c6-e12b4f18de76`  
**Timestamp:** 2026-11-02T20:56:00Z  
**Type:** Hard Handoff  

---

## 1. Observation

1. **Lab Notebook & Rubric Structure:**
   - File: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb`
   - Total Cells: 42 cells (24 markdown, 18 code).
   - Cell 41 verbatim grading rubric:
     - Component 1: *Metadata extraction and evidence documentation* — **25 pts**
     - Component 2: *Covert-channel detection and decoding* — **25 pts**
     - Component 3: *Six-stage secret reconstruction* — **20 pts**
     - Component 4: *Automated metadata scanner and CSV report* — **20 pts**
     - Component 5: *Interpretations, reflections, code quality, and presentation* — **10 pts**
     - Total: **100 pts**
   - Cell 41 verbatim submission requirements:
     - "Submit one PDF named Lab6-FirstName-LastName-StudentNumber.pdf that includes: Metadata evidence table for all six images... Screenshots of the extraction output... Complete reconstructed six-stage secret... Your completed Python metadata scanner... Scanner results: metadata_report.csv output as a table... Brief interpretation: Explain one limitation of EXIF-only extraction and one limitation of automated risk scoring... Answer to reflection questions."

2. **Reflection Prompts (Cell 40):**
   - Q1: "Why can an image contain a hidden message even when `getexif()` returns no tags?"
   - Q2: "How is **encoding** different from **encryption**? Is Base64 a secure way to hide information?"
   - Q3: "Why should investigators preserve the original files and record hashes?"
   - Q4: "Can metadata alone prove that an image was edited or that an incident occurred? What corroborating evidence would you need?"
   - Q5: "How does this investigation connect to the automated evidence collection and analysis you practised in Labs 4 and 5?"

3. **Textbook References:**
   - File: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Mastering Python for Networking and Security - Second -- Jose Manuel Ortega -- 2021 -- Packt Publishing -- 97c706086e42a54e17ca09f3b5d68f0f -- Anna’s Archive (2).pdf`
   - Chapter 13 (pp. 799–804): PIL/Pillow EXIF handling, `Image.open(...)._getexif()`, `from PIL.ExifTags import TAGS`, GPSInfo decoding, iterating tag dictionary.
   - Chapter 14 (pp. 854, 891–897): Cryptography vs. steganography, encoding vs. encryption, LSB pixel steganography with Pillow, hash verification via `hashlib`.

4. **Forensic Evidence & Recovered Secrets (Direct Python Probing):**
   - Target directory: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images\`
   - `Activation.png`:
     - Size: 259,975 bytes | SHA-256: `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904`
     - EXIF Sub-IFD (tag 37510 / UserComment): `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`
     - Decoded: `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` (Stage 2: VULN)
   - `Brain-Channel.png`:
     - Size: 201,685 bytes | SHA-256: `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359`
     - EXIF Tag 270 (ImageDescription): `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'` (Stage 5: LATERAL)
   - `Brain.png`:
     - Size: 2,354,330 bytes | SHA-256: `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e`
     - PNG Info key `'Software'`: `'RECON: Perform DNS harvesting and Subdomain enumeration.'` (Stage 1: RECON)
   - `Chemicals.png`:
     - Size: 561,245 bytes | SHA-256: `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a`
     - PNG Info key `'ImageDescription'`: `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'` (Stage 3: EXPLOIT)
   - `Dopamine.png`:
     - Size: 388,411 bytes | SHA-256: `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472`
     - XMP packet `XML:com.adobe.xmp`: `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>` (Stage 4: PERSIST)
   - `Music.png`:
     - Size: 679,959 bytes | SHA-256: `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370`
     - EXIF Tag 33432 & PNG Info `'Copyright'`: `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='`
     - Base64 Decoded: `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` (Stage 6: EXFIL)

5. **Scanner Requirements & CSV Schema (Cell 34, 38, 39):**
   - Required CSV columns: `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`.
   - Classroom heuristic risk scoring model:
     - `+10` for confirmed covert-message field
     - `+5` for suspicious encoded value requiring investigation
     - `+5` for additional unusual metadata indicator supported by evidence
     - Do not double-count encoded payloads as both encoded indicator and unusual indicator.

6. **Environment & Deliverables Specification:**
   - Active workspace: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan`
   - User identity: Billy Zandan (A01371854)
   - Word Document: `Lab6/Lab6-Billy-Zandan-A01371854.docx` (python-docx 1.2.0 installed)
   - Executed Notebook: `Lab6/Lab6.ipynb` (in-place execution)
   - CSV Report: `Lab6/metadata_report.csv`

---

## 2. Logic Chain

1. **Extraction Technique Selection (From Observation 1, 4):**
   Relying exclusively on `img.getexif()` extracts metadata from only `Brain-Channel.png` and `Music.png`. Images `Brain.png` and `Chemicals.png` store messages in PNG text chunks (`img.info`), `Dopamine.png` stores its message in XMP XML (`img.info['XML:com.adobe.xmp']`), and `Activation.png` stores its message in the Exif sub-IFD (`ExifOffset` tag 37510 `UserComment`). Therefore, an exhaustive extraction engine must probe: (a) top-level EXIF, (b) EXIF sub-IFDs, (c) PNG text chunks, and (d) XMP XML packets.

2. **Narrative Sequencing Logic (From Observation 4):**
   Each recovered secret begins with an explicit attack lifecycle prefix:
   - `Brain.png`: `RECON`
   - `Activation.png`: `VULN`
   - `Chemicals.png`: `EXPLOIT`
   - `Dopamine.png`: `PERSIST`
   - `Brain-Channel.png`: `LATERAL`
   - `Music.png`: `EXFIL`
   This sequence maps directly to the standard Lockheed Martin Cyber Kill Chain and MITRE ATT&CK enterprise tactics: Reconnaissance (Stage 1) → Vulnerability Analysis (Stage 2) → Exploitation (Stage 3) → Persistence (Stage 4) → Lateral Movement (Stage 5) → Exfiltration (Stage 6). Sorting by image filename would yield `Activation (2) -> Brain-Channel (5) -> Brain (1) -> Chemicals (3) -> Dopamine (4) -> Music (6)`, which violates operational logic because lateral movement via Mimikatz cannot precede initial reconnaissance or exploitation.

3. **Scanner Heuristic Scoring Consistency (From Observation 1, 5):**
   Under the classroom risk model:
   - `Activation.png`: +10 confirmed covert message (`VULN:...`), +5 camera/GPS tags embedded in a synthetic graphic = **15**.
   - `Brain-Channel.png`: +10 confirmed covert message (`LATERAL:...`) = **10**.
   - `Brain.png`: +10 confirmed covert message (`RECON:...`) = **10**.
   - `Chemicals.png`: +10 confirmed covert message (`EXPLOIT:...`) = **10**.
   - `Dopamine.png`: +10 confirmed covert message (`PERSIST:...`) = **10**.
   - `Music.png`: +10 confirmed covert message (`EXFIL:...`), +5 Base64 encoded payload = **15** (avoiding double-counting).

4. **Deliverables Cohesion (From Observation 1, 6):**
   The grading rubric assigns 25 points to extraction and evidence documentation, 25 points to covert-channel decoding, 20 points to secret reconstruction, 20 points to scanner implementation & CSV, and 10 points to presentation and reflection. Creating `Lab6/Lab6-Billy-Zandan-A01371854.docx` and executing `Lab6/Lab6.ipynb` in place with all evidence screenshots, outputs, and markdown answers fulfills 100% of the rubric criteria.

---

## 3. Caveats

- **No Caveats:** All authoritative sources (`Lab6.ipynb`, textbook PDF, all 6 target images, student identification) were accessed directly, probed without errors, and verified.

---

## 4. Conclusion

The specification mining investigation is complete. All authoritative requirements, grading breakdowns, technical mechanics, secret fragments, incident sequence logic, scanner rules, CSV schemas, reflection question answers, and deliverable specifications have been exhaustively documented in `survey_spec.md`. No project files were modified.

---

## 5. Verification Method

To independently verify the findings in this report:
1. **Inspect Survey Spec:**
   `view_file` on `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\spec_miner_survey_1\survey_spec.md`.
2. **Verify Metadata Extraction Independently:**
   Run the following Python one-liner to confirm all six secrets and hashes:
   ```powershell
   python -c "
   from pathlib import Path; from PIL import Image, ExifTags; import base64, xml.etree.ElementTree as ET
   p = Path(r'c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images')
   # Activation
   with Image.open(p / 'Activation.png') as img:
       print('Activation:', img.getexif().get_ifd(0x8769)[37510][8:].decode('utf-8'))
   # Brain-Channel
   with Image.open(p / 'Brain-Channel.png') as img:
       print('Brain-Channel:', img.getexif()[270])
   # Brain
   with Image.open(p / 'Brain.png') as img:
       print('Brain:', img.info['Software'])
   # Chemicals
   with Image.open(p / 'Chemicals.png') as img:
       print('Chemicals:', img.info['ImageDescription'])
   # Dopamine
   with Image.open(p / 'Dopamine.png') as img:
       print('Dopamine:', ET.fromstring(img.info['XML:com.adobe.xmp'].strip()).find('.//{http://ns.adobe.com/exif/1.0/}MakerNote').text)
   # Music
   with Image.open(p / 'Music.png') as img:
       print('Music:', base64.b64decode(img.info['Copyright']).decode('utf-8'))
   "
   ```
3. **Invalidation Conditions:**
   - Any modification to the binary contents of files in `Lab6/Images/` altering hashes.
   - Any alteration to the rubric table in `Lab6/Lab6.ipynb` cell 41.
