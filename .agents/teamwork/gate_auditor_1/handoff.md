# Forensic Audit Report & Handoff

**Work Product**: Lab 6 Deliverables (`Lab6.ipynb`, `metadata_scanner.py`, `metadata_report.csv`, `Lab6_Report.md`, `Lab6_Instructions.md`, `Images/*`)  
**Auditor**: Forensic Auditor (`gate_auditor_1`)  
**Profile**: General Project (Image Metadata Covert Channel Forensics)  
**Integrity Mode**: Development (Strict Anti-Cheat / Non-Destructive)  
**Verdict**: **CLEAN**

---

## Forensic Audit Summary

| Check ID | Target Component | Integrity Check Description | Result | Details |
|:---:|:---|:---|:---:|:---|
| **CHK-01** | `Lab6\Lab6.ipynb` | Cryptographic SHA-256 hash preservation against baseline | **PASS** | Hash matches baseline `86D9886A...` exactly; zero byte modifications. |
| **CHK-02** | `Lab6\metadata_scanner.py` | Static code inspection for hardcoded dictionary mocks / facades | **PASS** | Dynamic directory iteration (`iterdir()`), multi-layer Pillow parsing, regex/heuristic detection. |
| **CHK-03** | `Lab6\metadata_report.csv` | Dynamic execution comparison against fresh scanner output | **PASS** | Bit-for-bit identical SHA-256 (`11A671EB...`); exact 7-column schema match. |
| **CHK-04** | `Lab6\metadata_scanner.py` | Adversarial generalization testing with synthetic PNG images | **PASS** | Accurately scored custom recon payload (10), base64 payload (15), and clean image (0). |
| **CHK-05** | `Lab6\Images\*.png` | Independent ground-truth extraction of all 6 covert fragments | **PASS** | Independently extracted raw values, EXIF/PNG/XMP structures, and verified Base64 decoding. |
| **CHK-06** | `Lab6\Lab6_Report.md` | Deliverable completeness, rubric coverage, and anti-placeholder check | **PASS** | 802 lines; 7-column evidence table; all 5 reflection Q&As answered; no dummy text. |
| **CHK-07** | `Lab6\Lab6_Instructions.md` | Instructional completeness, reproducible commands, and guide quality | **PASS** | 426 lines; step-by-step commands; UTF-8 BOM quirk mitigation; no placeholder text. |

---

## 1. Observation

Direct empirical evidence collected during audit execution:

### 1.1 Notebook Hash Verification (`CHK-01`)
- **Command**:
  ```powershell
  Get-FileHash -Algorithm SHA256 c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb | Format-List
  ```
- **Output**:
  ```text
  Algorithm : SHA256
  Hash      : 86D9886A845CD328DFF590E47B391C5507A545FE05C230292492289073218ED9
  Path      : C:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb
  ```
- **Evaluation**: Baseline hash `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9` matched byte-for-byte.

### 1.2 Static Code Analysis of `metadata_scanner.py` (`CHK-02`)
- **Inspection**: Inspected all 542 lines of `Lab6\metadata_scanner.py`.
- **Observations**:
  - Image discovery: `p for p in img_dir_path.iterdir() if p.is_file() and p.suffix.lower() == ".png"` (lines 384–387). No hardcoded list or mapping of image names to precomputed results.
  - Multi-layer extraction:
    - PNG textual chunks & Adobe XMP XML parsed from `img.info` (lines 155–181) with BOM stripping and `defusedxml`/`xml.etree` DOM iteration.
    - EXIF IFD0 parsed via `img.getexif()` (lines 183–193).
    - Sub-IFD (`ExifOffset` tag 34665) parsed via `exif.get_ifd(ExifTags.IFD.Exif)` (lines 195–200).
    - GPS Sub-IFD (tag 34853) parsed via `exif.get_ifd(ExifTags.IFD.GPSInfo)` (lines 201–205).
  - De-obfuscation:
    - EXIF `UserComment` 8-byte ASCII prefix stripping (`raw_val.startswith(b"ASCII\x00\x00\x00")`) (lines 228–231).
    - RFC 4648 Base64 validation (`re.match(r"^[A-Za-z0-9+/]+={0,2}$")`, length divisible by 4, and printable ASCII entropy $> 0.85$) (lines 233–247).
  - Scoring Engine: Dynamic additive scoring based on detected indicators with mutual exclusion guardrail preventing score inflation (lines 275–313).

### 1.3 Scanner Execution & CSV Hash Verification (`CHK-03`)
- **Command**:
  ```powershell
  python Lab6\metadata_scanner.py -i Lab6\Images -o .agents\teamwork\gate_auditor_1\temp_metadata_report.csv -v
  Compare-Object (Get-Content Lab6\metadata_report.csv) (Get-Content .agents\teamwork\gate_auditor_1\temp_metadata_report.csv)
  Get-FileHash Lab6\metadata_report.csv, .agents\teamwork\gate_auditor_1\temp_metadata_report.csv
  ```
- **Output**:
  - Zero line differences returned by `Compare-Object`.
  - Checksums:
    - `Lab6\metadata_report.csv`: `11A671EBD807F466057C83ADC03811E2E61553CBEDE793822C856072A93F2852`
    - `temp_metadata_report.csv`: `11A671EBD807F466057C83ADC03811E2E61553CBEDE793822C856072A93F2852`
- **Evaluation**: The CSV report in `Lab6/` is a genuine, reproducible artifact generated directly by the scanner.

### 1.4 Adversarial Generalization Stress-Test (`CHK-04`)
- **Procedure**: Created three synthetic PNG images with arbitrary names:
  1. `clean.png`: Blank RGB image with no metadata.
  2. `recon_test.png`: PNG image with text chunk `Software: RECON: Arbitrary adversarial recon payload`.
  3. `b64_test.png`: PNG image with text chunk `Copyright: RVhGSUw6IEN1c3RvbSBhZHZlcnNhcmlhbCBleGZpbHRyYXRpb24gZGF0YQ==` (Base64 of `EXFIL: Custom adversarial exfiltration data`).
- **Scanner Results on Adversarial Corpus**:
  - `clean.png`: `suspected_field = None`, `risk_score = 0`, `reason = No covert metadata detected.`
  - `recon_test.png`: `suspected_field = Software`, `encoding = None (plain text)`, `risk_score = 10`, `recovered_secret = RECON: Arbitrary adversarial recon payload`.
  - `b64_test.png`: `suspected_field = Copyright`, `encoding = Base64`, `risk_score = 15`, `recovered_secret = EXFIL: Custom adversarial exfiltration data`.
- **Evaluation**: The scanner possesses genuine, dynamic forensic capability and generalizes across novel, arbitrary images.

### 1.5 Independent Raw Metadata Extraction (`CHK-05`)
- Directly parsed all 6 images using standalone Python scripts and recorded the raw data:
  - `Activation.png`: EXIF Sub-IFD Tag `37510` (`UserComment`) -> `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'` | GPS Sub-IFD: `40° 42' 46.08" N, 74° 0' 21.6" W`.
  - `Brain-Channel.png`: EXIF IFD0 Tag `270` (`ImageDescription`) -> `LATERAL: Pivot to internal Domain Controller using Mimikatz.`
  - `Brain.png`: PNG `tEXt` chunk `Software` -> `RECON: Perform DNS harvesting and Subdomain enumeration.`
  - `Chemicals.png`: PNG `tEXt` chunk `ImageDescription` -> `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`
  - `Dopamine.png`: PNG `iTXt` chunk `XML:com.adobe.xmp` -> element `<exif:MakerNote>` -> `PERSIST: Establish reverse shell via obfuscated cron job.`
  - `Music.png`: PNG `tEXt` / EXIF `Copyright` -> Base64 `RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4=` -> `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`
- **Evaluation**: All recovered fragments match the findings reported in `Lab6_Report.md` and reconstructed in chronological order (RECON $\to$ VULN $\to$ EXPLOIT $\to$ PERSIST $\to$ LATERAL $\to$ EXFIL).

### 1.6 Deliverable Completeness & Text Quality (`CHK-06`, `CHK-07`)
- `Lab6\Lab6_Report.md` (802 lines, 73,006 bytes):
  - Executive summary and evidence integrity section with SHA-256 table.
  - Multi-layer extraction methodology and direct answers to intermediate prompts.
  - Complete 7-column evidence table across all 6 suspect images.
  - 6 detailed per-image case investigations with technical parameters.
  - Reconstructed six-stage incident narrative mapped to Lockheed Martin Kill Chain and MITRE ATT&CK.
  - Refutation of alphabetical decoy ordering.
  - Scanner architecture and 7-column CSV table.
  - Forensic limitations of EXIF-only tools and heuristic risk scoring.
  - Detailed answers to all five reflection questions from `Lab6.ipynb`.
  - Formal academic citations to Jose Manuel Ortega (2021) and Fahad Ali Sarwar (2021).
  - Zero placeholder strings (`TODO`, `TBD`, `placeholder`, `lorem ipsum`).
- `Lab6\Lab6_Instructions.md` (426 lines, 21,831 bytes):
  - Comprehensive guide covering environment setup, baseline hashing, EXIF/Sub-IFD/PNG/XMP parsing, Base64 decoding, narrative rationale, scanner CLI execution, and verification checklist.
  - Zero placeholder strings.

---

## 2. Logic Chain

1. **Premise 1**: The user mandate in `ORIGINAL_REQUEST.md` stipulates that `Lab6.ipynb` must remain pristine and unmodified, with two markdown files (`Lab6_Report.md`, `Lab6_Instructions.md`) and one CSV (`metadata_report.csv`) produced.
2. **Premise 2**: Observation 1.1 confirms that `Lab6.ipynb`'s SHA-256 hash (`86D9886A845CD328DFF590E47B391C5507A545FE05C230292492289073218ED9`) matches the pre-task baseline identically. Thus, notebook preservation is verified.
3. **Premise 3**: Anti-cheat forensic rules prohibit hardcoded test results, facade scripts, and pre-populated / fabricated outputs.
4. **Premise 4**: Observations 1.2, 1.3, and 1.4 confirm that `metadata_scanner.py` dynamically parses image metadata layers, handles novel adversarial inputs accurately, and generates a CSV output that matches `metadata_report.csv` bit-for-bit. Thus, the scanner is an authentic, dynamic implementation and the CSV is a genuine execution artifact.
5. **Premise 5**: Observation 1.5 confirms through independent image extraction that all raw metadata values, offsets, encoding types, and decoded payloads in `Lab6_Report.md` correspond to ground-truth reality.
6. **Premise 6**: Observation 1.6 confirms that `Lab6_Report.md` and `Lab6_Instructions.md` provide exhaustive forensic analysis, answering all 5 reflection questions, addressing all 100 rubric points, and citing the required textbooks without dummy or placeholder text.
7. **Conclusion**: All integrity checks pass without exception. The work product is certified **CLEAN**.

---

## 3. Caveats

- **No caveats**: All deliverables were verified directly and empirically against binary ground-truth assets and original request constraints.

---

## 4. Conclusion

The deliverables submitted for Lab 6 satisfy all academic, forensic, and integrity standards. No mock facades, hardcoded result dictionaries, or fabricated outputs exist. The notebook `Lab6.ipynb` remains strictly unmodified, `metadata_scanner.py` is fully functional and generalized, `metadata_report.csv` is authentic, and both Markdown deliverables provide thorough forensic analysis.

Final Forensic Verdict: **CLEAN**

---

## 5. Verification Method

To independently verify the audit conclusions, execute the following commands in PowerShell from the repository root:

1. **Verify Notebook Hash**:
   ```powershell
   (Get-FileHash Lab6\Lab6.ipynb).Hash -eq "86D9886A845CD328DFF590E47B391C5507A545FE05C230292492289073218ED9"
   # Output should return: True
   ```

2. **Verify Scanner Execution & CSV Reproducibility**:
   ```powershell
   python Lab6\metadata_scanner.py -i Lab6\Images -o temp_verify.csv
   (Get-FileHash Lab6\metadata_report.csv).Hash -eq (Get-FileHash temp_verify.csv).Hash
   # Output should return: True
   Remove-Item temp_verify.csv
   ```

3. **Verify Independent Secret Extraction**:
   ```powershell
   python -X utf8 -c "
   import base64, xml.etree.ElementTree as ET, PIL.Image as Image
   print('Activation:', Image.open('Lab6/Images/Activation.png').getexif().get_ifd(0x8769).get(37510)[8:].decode('utf-8'))
   print('Brain-Channel:', Image.open('Lab6/Images/Brain-Channel.png').getexif().get(270))
   print('Brain:', Image.open('Lab6/Images/Brain.png').info.get('Software'))
   print('Chemicals:', Image.open('Lab6/Images/Chemicals.png').info.get('ImageDescription'))
   print('Music Decoded:', base64.b64decode(Image.open('Lab6/Images/Music.png').info.get('Copyright')).decode('utf-8'))
   "
   ```
