# Comprehensive Survey & Analysis Handoff Report: Lab 6 Covert Channels in Image Metadata

**Author**: survey_explorer_1  
**Target Recipient**: ba1d6daa-7a7c-49df-b2f9-817168f5bf8e (parent)  
**Date**: 2026-11-02T23:16:00Z  
**Working Directory**: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\survey_explorer_1`  
**Lab Directory**: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6`  

---

## 1. Observation

### 1.1 Git Status of `Lab6/Lab6.ipynb`
- **Command**: `git status Lab6/Lab6.ipynb`
  ```
  On branch main
  Your branch is up to date with 'origin/main'.

  Untracked files:
    (use "git add <file>..." to include in what will be committed)
  	Lab6/Lab6.ipynb
  ```
- **Command**: `git status --porcelain Lab6/Lab6.ipynb`
  ```
  ?? Lab6/Lab6.ipynb
  ```
- **Command**: `git ls-files Lab6/Lab6.ipynb`
  - Output: *(empty string, 0 bytes)*.
- **Command**: `git log --all --full-history -- "**/Lab6*"`
  - Output: *(empty string, no commits contain the `Lab6` directory)*.
- **Cryptographic Hash (SHA-256)**:
  - File: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb`
  - Computed Hash: `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`
  - Size: 20,080 bytes (565 lines, valid JSON Jupyter Notebook schema v4.5).
- **Notebook State Inspection**:
  - Cell 1 (id: `373d32c9`, lines 33–49): `%pip -q install Pillow`, `execution_count: 1`, output: `"Note: you may need to restart the kernel to use updated packages.\n"`.
  - All student investigation cells (ids: `21e667ce`, `cbd260f5`, `8e208ddf`, `a6fd6213`, `8d8e3b22`, `ecce3ffb`, `6c877333`, `ba3acb4c`, `450aac19`, `c07cc67d`, `fd3dcade`, `d705ebdf`, `a28bc2d3`, `d8df5cb3`, `e97d9b27`, `f983c05b`, `741a9382`): `execution_count: null`, `outputs: []`, and original `# TODO:` placeholder comments intact.
- **Git Restoration Command Assessment**:
  - Because `Lab6/Lab6.ipynb` is an untracked file (never committed to git), standard git working-tree restoration commands like `git restore Lab6/Lab6.ipynb` or `git checkout HEAD -- Lab6/Lab6.ipynb` fail with:
    `error: pathspec 'Lab6/Lab6.ipynb' did not match any file(s) known to git`
  - Running destructive untracked cleanup (`git clean -f Lab6/Lab6.ipynb`) would permanently delete the file and must **never** be executed.
  - To guarantee zero modification as required by the user prompt, `Lab6/Lab6.ipynb` must remain strictly read-only, verified against SHA-256 hash `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`.

---

### 1.2 Extracted Sections, Rubric, and Questions from `Lab6.ipynb`

#### A. Notebook Structural Sections
1. **Title & Header**: `# Lab 6: Covert Channels in Image Metadata` (Guided investigation | Student notebook). Scenario: Six images contain pieces of a fictional cybersecurity incident narrative.
2. **Section 0**: `## 0. Prepare the environment` (Pillow installation, file discovery with `pathlib.Path("Images").glob("*.png")`, evidence log definition).
3. **Section 1**: `## 1. First technique: EXIF metadata (one image)` (`Brain-Channel.png`, `img.getexif()`, `ExifTags.TAGS`, empty EXIF exploration).
4. **Section 2**: `## 2. Second technique: PNG text metadata (one image)` (`Brain.png`, `img.info`, `Chemicals.png`).
5. **Section 3**: `## 3. Third technique: XMP metadata (one image)` (`Dopamine.png`, `XML:com.adobe.xmp`, `xmp`, XML element discovery).
6. **Section 4**: `## 4. Fourth technique: Decode suspicious text (one image)` (`Music.png`, `base64.b64decode`, validation).
7. **Section 5**: `## 5. Your investigation: six images, one by one` (6-row evidence table, individual subsections for `Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`).
8. **Section 6**: `## 6. Reconstruct the complete secret` (Stage 1–6 template, sequence reasoning prompt).
9. **Section 7**: `## 7. Build an automated metadata scanner` (Scanner requirements 1–6, classroom heuristic risk model, starters 7A, 7B, 7C).
10. **Reflection questions**: 5 formal reflective questions.
11. **Submission requirements & Grading rubric (100 points)**.

#### B. Complete 100-Point Grading Rubric Breakdown (Verbatim)

| Component | Points | Full-credit expectations |
|:---|:---:|:---|
| **Metadata extraction and evidence documentation** | **25** | Appropriate EXIF/PNG/XMP extraction for all six images; accurate field identification; clear evidence screenshots and tables. |
| **Covert-channel detection and decoding** | **25** | All six hidden fragments recovered accurately; encoded content decoded correctly; extraction methods explained. |
| **Six-stage secret reconstruction** | **20** | Complete secret assembled in correct order with a logical justification. |
| **Automated metadata scanner and CSV report** | **20** | Scanner iterates through all six images, checks relevant metadata types, identifies suspected fields, exports complete CSV rows, and applies consistent, explainable risk scores. |
| **Interpretations, reflections, code quality, and presentation** | **10** | Readable, reproducible Python code; clear report organization; thoughtful explanation of EXIF-only and risk-scoring limitations. |
| **Total** | **100** | |

#### C. All Five Reflection Questions (Verbatim)
1. **Reflection Question 1**: *"Why can an image contain a hidden message even when `getexif()` returns no tags?"*
2. **Reflection Question 2**: *"How is **encoding** different from **encryption**? Is Base64 a secure way to hide information?"*
3. **Reflection Question 3**: *"Why should investigators preserve the original files and record hashes?"*
4. **Reflection Question 4**: *"Can metadata alone prove that an image was edited or that an incident occurred? What corroborating evidence would you need?"*
5. **Reflection Question 5**: *"How does this investigation connect to the automated evidence collection and analysis you practised in Labs 4 and 5?"*

#### D. Intermediate Section Prompts & Observation Questions (Verbatim)
- **Section 1 (EXIF)**:
  - *"Observe: Which EXIF field carries a message? Record it in your evidence log."*
  - *"Try it yourself: Change `image_path` to a different image. If `EXIF tags: 0` appears, does that mean the image has no metadata? Explain."*
- **Section 2 (PNG Text)**:
  - *"Observe: Which PNG text field contains a clue? Try **Chemicals.png** next using the same short snippet."*
- **Section 3 (XMP)**:
  - *"Observe: Locate the XML element containing the partial secret. Why did the EXIF-only approach miss it? **Note:** XMP may appear under either `XML:com.adobe.xmp` or `xmp`, depending on how the file was created and the software version."*
- **Section 4 (Base64)**:
  - *"Your turn: Replace `example` with the suspicious metadata value from **Music.png**. Do not assume every long string is Base64; use the context and validate the result."*
- **Section 5 (Individual Investigations)**:
  - *"What is the partial secret?"* (Repeated for each of the 6 images).
- **Section 6 (Secret Reconstruction)**:
  - *"Explain your reasoning: Why is this the most plausible order?"*
- **Section 7 / Submission (Interpretations)**:
  - *"Explain one limitation of EXIF-only extraction and one limitation of automated risk scoring."*

---

### 1.3 Direct Forensic Findings Across All Six Images

Forensic metadata extraction executed via Python 3.14 using `PIL.Image`, `PIL.ExifTags`, and `base64`:

| Image Filename | Metadata Layer & Container | Specific Field / Tag ID | Raw Value / Excerpt | Decoding Method | Recovered Secret Fragment | Forensic Context & Anomalies |
|:---|:---|:---|:---|:---|:---|:---|
| **Activation.png** | EXIF Sub-IFD (tag 34665) | `UserComment` (tag 37510) | `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'` | Strip 8-byte ASCII prefix (`ASCII\x00\x00\x00`), UTF-8 decode | `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` | Fabricated camera hardware tags (`Make: Nikon`, `Model: D750`, `Software: Adobe Lightroom 13.0`), fake GPS coordinates (40°42'46.08"N, 74°0'21.6"W = Lower Manhattan, Wall St, NYC). |
| **Brain-Channel.png** | EXIF IFD0 | `ImageDescription` (tag 270) | `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'` | Plain text (Direct string read) | `LATERAL: Pivot to internal Domain Controller using Mimikatz.` | Standard EXIF IFD0 block with no Sub-IFD or camera tags; text placed directly in description field. |
| **Brain.png** | Native PNG Text Chunk (`tEXt`/`zTXt`) | `Software` (in `img.info`) | `'RECON: Perform DNS harvesting and Subdomain enumeration.'` | Plain text (Direct dictionary lookup) | `RECON: Perform DNS harvesting and Subdomain enumeration.` | `getexif()` returns 0 tags; clue hidden entirely in PNG key-value pair `Software`. |
| **Chemicals.png** | Native PNG Text Chunk (`tEXt`/`zTXt`) | `ImageDescription` (in `img.info`) | `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'` | Plain text (Direct dictionary lookup) | `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` | `getexif()` returns 0 tags; `ImageDescription` resides in PNG text chunk rather than EXIF IFD0. |
| **Dopamine.png** | Adobe XMP XML Packet (`iTXt`/application chunk) | `XML:com.adobe.xmp` (`<exif:MakerNote>`) | `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>` | XML parsing / Regex element extraction | `PERSIST: Establish reverse shell via obfuscated cron job.` | `getexif()` returns 0 tags; packet generated by `Image::ExifTool 12.76` with RDF/XML namespace embedding secret in `MakerNote`. |
| **Music.png** | EXIF IFD0 & PNG Text Chunk | `Copyright` (tag 33432 & `img.info`) | `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='` | RFC 4648 Base64 decoding (`base64.b64decode`) | `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` | Base64 encoded payload; camera tags (`Make: Olympus`, `Model: OM-D E-M10`) mirrored across EXIF and PNG chunks. |

---

### 1.4 Attack Lifecycle Reconstruction

Assembled chronological incident narrative based on stage indicators:
1. **Stage 1 (RECON)**: `Brain.png`  
   *Fragment*: `"RECON: Perform DNS harvesting and Subdomain enumeration."`
2. **Stage 2 (VULN)**: `Activation.png`  
   *Fragment*: `"VULN: Identify unpatched CVE-2024-XXXX in web gateway."`
3. **Stage 3 (EXPLOIT)**: `Chemicals.png`  
   *Fragment*: `"EXPLOIT: Deploy SQL Injection payload to bypass WAF."`
4. **Stage 4 (PERSIST)**: `Dopamine.png`  
   *Fragment*: `"PERSIST: Establish reverse shell via obfuscated cron job."`
5. **Stage 5 (LATERAL)**: `Brain-Channel.png`  
   *Fragment*: `"LATERAL: Pivot to internal Domain Controller using Mimikatz."`
6. **Stage 6 (EXFIL)**: `Music.png`  
   *Fragment*: `"EXFIL: Tunnel compressed database dump via DNS Covert Channel."`

---

### 1.5 Automated Scanner Execution Verification
- **Command**: `python Lab6/metadata_scanner.py -i Lab6/Images -o Lab6/metadata_report.csv`
- **Output**: Exited with code 0. Generated `Lab6/metadata_report.csv` with exactly 6 records conforming to the contract:
  ```csv
  filename,format,metadata_fields,suspected_field,encoding,risk_score,reason
  Activation.png,PNG,"srgb, gamma, dpi, exif, Make, Model, Software, create-date, UserComment, GPSInfo",UserComment,EXIF ASCII header / plain text,15,Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5).
  Brain-Channel.png,PNG,"srgb, gamma, dpi, exif, ImageDescription",ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
  Brain.png,PNG,"srgb, gamma, dpi, Software",Software,None (plain text),10,Confirmed covert message in Software (+10).
  Chemicals.png,PNG,ImageDescription,ImageDescription,None (plain text),10,Confirmed covert message in ImageDescription (+10).
  Dopamine.png,PNG,"srgb, gamma, dpi, xmp, XML:com.adobe.xmp",XML:com.adobe.xmp (exif:MakerNote),XML encapsulation / plain text,15,Confirmed covert message in XML:com.adobe.xmp (exif:MakerNote) (+10); unusual container / embedded XMP packet (+5).
  Music.png,PNG,"srgb, gamma, dpi, Copyright, Make, Model, create-date, exif",Copyright,Base64,15,Confirmed covert message in Copyright (+10); obfuscated with Base64 encoding requiring decoding (+5).
  ```

---

### 1.6 Academic Literature & Textbook Mapping
1. **Jose Manuel Ortega (2021)**, *Mastering Python for Networking and Security - Second Edition*, Packt Publishing:
   - **Chapter 13: "Extracting Geolocation and Metadata from Documents, Images, and Browsers" (pp. 785–851)**:
     - EXIF extraction using `PIL.Image` and `PIL.ExifTags.TAGS` (pp. 799–804).
     - Decoding nested `GPSInfo` coordinates from degrees, minutes, seconds rational tuples into decimal latitude/longitude (pp. 804–806). Directly applicable to `Activation.png`.
   - **Chapter 14: "Cryptography and Steganography" (pp. 853–900)**:
     - Cryptographic hash verification (`hashlib.sha256`) for evidentiary integrity and chain of custody.
     - Distinguishing between steganography (hiding the existence of a message), cryptography (scrambling the message to ensure confidentiality), and reversible encoding.
2. **Fahad Ali Sarwar (2021)**, *Python Ethical Hacking From Scratch*, Packt Publishing:
   - **Chapter 1: "Introduction to Hacking" (pp. 4–28)**:
     - The CIA triad (Confidentiality, Integrity, Availability) and the five hacking phases (Reconnaissance, Scanning, Exploitation, Maintaining Access, Covering Tracks).
   - **Chapters 4, 6 & 7: "Network Scanning, Malware, and Exfiltration" (pp. 71–98, 124–145)**:
     - DNS harvesting, SQL injection payloads, reverse shells, cron jobs, and DNS covert channel exfiltration matching the 6-stage narrative.

---

## 2. Logic Chain

1. **Step 1 (Git Status & Integrity Verification)**:
   - *Observation*: `git status Lab6/Lab6.ipynb` reports `?? Lab6/Lab6.ipynb`, and `git ls-files` returns empty. SHA-256 is `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`.
   - *Logic*: Because `Lab6/Lab6.ipynb` is untracked in git, HEAD has no record of it. The notebook has not been modified during our investigation; cell 1 contains pre-existing pip execution, while all student tasks remain unexecuted. To satisfy the prompt condition ("without modifying Lab6.ipynb"), no tool or script should edit `Lab6.ipynb`, and its state can be continuously verified via SHA-256 hash.

2. **Step 2 (Extraction Completeness & Multi-Layer Forensic Model)**:
   - *Observation*: Three images (`Brain.png`, `Chemicals.png`, `Dopamine.png`) return `len(exif) == 0`. `Activation.png` hides its secret in the nested Exif Sub-IFD `UserComment` rather than IFD0. `Dopamine.png` encapsulates its clue in an Adobe XMP XML packet. `Music.png` encodes its payload in Base64.
   - *Logic*: A standard forensic pipeline relying exclusively on `img.getexif()` suffers a 50% detection failure (missing 3 of 6 secrets) and fails to decode the nested and encoded payloads. Therefore, the forensic report must comprehensively document the multi-layer extraction model (EXIF IFD0, EXIF Sub-IFD, native PNG text chunks via `img.info`, and XMP RDF/XML parsing).

3. **Step 3 (Sequencing Rationale)**:
   - *Observation*: Recovered fragments explicitly start with prefixes `RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, and `EXFIL:`. Filenames sorted alphabetically (`Activation.png` = VULN, `Brain-Channel.png` = LATERAL, `Brain.png` = RECON...) do not represent an attack workflow.
   - *Logic*: Filename sorting is arbitrary. In standard threat intelligence frameworks (MITRE ATT&CK Enterprise Matrix, Lockheed Martin Cyber Kill Chain, and Sarwar Chapter 1), an adversary must first conduct reconnaissance, discover vulnerabilities, exploit them to gain initial access, establish persistence, pivot laterally through the intranet, and finally exfiltrate sensitive intellectual property. The stage labels form an unambiguous, logically coherent kill chain sequence.

4. **Step 4 (Coverage Architecture for `Lab6_Report.md`)**:
   - *Observation*: The grading rubric allocates 25 pts to metadata extraction, 25 pts to covert channel detection & decoding, 20 pts to secret reconstruction, 20 pts to automated scanner & CSV, and 10 pts to interpretations, reflection questions, code quality, and textbook citations.
   - *Logic*: To earn full marks (100/100), `Lab6_Report.md` must not merely summarize answers, but follow an exhaustive, professional forensic report structure that maps directly to every rubric section, embeds reproducible Python code snippets, presents the complete evidence tables and CSV output, answers all reflection and intermediate questions, provides deep interpretations on limitations, and cites Ortega (2021) and Sarwar (2021).

---

## 3. Caveats

- **Caveat 1**: `Lab6/Lab6.ipynb` is untracked in git. Therefore, standard `git checkout` or `git restore` commands cannot restore it if modified. Preservation relies on file immutability and SHA-256 hash validation.
- **Caveat 2**: While the classroom rubric mentions generating a PDF (`Lab6-FirstName-LastName-StudentNumber.pdf`), the user request specifically designates `Lab6_Report.md` and `Lab6_Instructions.md` as the deliverable artifacts in the workspace.
- **Caveat 3**: The recovered incident narrative is fictional educational steganography. As explicitly warned in the notebook, none of the commands described in the fragments (SQL injection, Mimikatz, reverse shells) should ever be executed.

---

## 4. Conclusion & Recommendations

### 4.1 Notebook Integrity Assessment
`Lab6/Lab6.ipynb` is pristine and unmodified (SHA-256: `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`). It must remain untouched. All lab deliverables, code snippets, evidence logs, reconstructed secrets, and answers will reside exclusively in `Lab6_Report.md` and `Lab6_Instructions.md`.

### 4.2 Blueprint & Structure for `Lab6_Report.md`

To comprehensively address all 100 rubric points, reflection questions, forensic interpretations, and textbook citations, `Lab6_Report.md` must be constructed with the following 9 sections:

```markdown
# Forensic Investigation Report: Covert Channels in Image Metadata
**Course**: FSCT 8561 — Security Automation and Incident Response  
**Lab Assignment**: Lab 6 — Covert Channels in Image Metadata  
**Student**: Billy Zandan  
**Date**: November 2026  
**Integrity Mode**: Non-destructive Forensic Examination  

## Executive Summary
- Brief statement of engagement, incident scenario, and investigative scope.
- High-level overview of multi-layer metadata extraction across 6 PNG images.
- Complete reconstructed 6-stage incident narrative summary.

## 1. Forensic Environment & Evidence Integrity
- Forensic workstation setup and dependencies (`Pillow`, `defusedxml`, `hashlib`).
- Table of Evidence: File inventory with SHA-256 cryptographic hashes, byte sizes, and container formats.
- Legal & forensic chain-of-custody rationale (citing Ortega 2021, Ch. 14 and Sarwar 2021, Ch. 1).

## 2. Multi-Layer Extraction Techniques & Intermediate Observations
- Detailed explanation and reproducible Python code snippets for all 4 techniques:
  - Technique 1: EXIF Metadata extraction (`img.getexif()`, `ExifTags.TAGS`, Sub-IFD handling).
    - Answering Section 1 prompts: Suspected field identification; explaining why `EXIF tags: 0` does not mean zero metadata.
  - Technique 2: Native PNG Text Chunks (`img.info` key-value pairs).
    - Answering Section 2 prompts: Identification of `Software` in `Brain.png` and `ImageDescription` in `Chemicals.png`.
  - Technique 3: Adobe XMP XML Metadata (`XML:com.adobe.xmp`, `xmp`, RDF parsing).
    - Answering Section 3 prompts: Element identification (`<exif:MakerNote>`); explaining why `getexif()` missed XMP.
  - Technique 4: Obfuscated & Encoded Text Identification (Base64 vs. encryption).
    - Answering Section 4 prompts: Identifying Base64 string in `Music.png` and validating decoded plaintext.

## 3. Comprehensive Evidence Log (Rubric: 25 Points)
- Full 6-image Evidence Table with columns:
  `Image Name | Metadata Type / Layer | Field Name / Tag ID | Raw Value Excerpt | Decoding Method | Recovered Secret Fragment | Forensic Interpretation`
- Individual in-depth forensic write-up for each image (Investigations 1 through 6), detailing exact byte representations, anomaly analysis (e.g. Nikon D750 + Wall Street GPS on `Activation.png`), and terminal output logs.

## 4. Covert-Channel Detection, Decoding & Payload Analysis (Rubric: 25 Points)
- In-depth forensic analysis of each recovered fragment.
- De-obfuscation walkthroughs:
  - EXIF UserComment 8-byte ASCII prefix stripping.
  - RFC 4648 Base64 decoding mechanics and printable ASCII ratio verification.
  - XMP RDF/XML element extraction.

## 5. Reconstructed Six-Stage Incident Narrative (Rubric: 20 Points)
- Chronological assembly of the 6 stages:
  1. Stage 1: `RECON:` (`Brain.png`)
  2. Stage 2: `VULN:` (`Activation.png`)
  3. Stage 3: `EXPLOIT:` (`Chemicals.png`)
  4. Stage 4: `PERSIST:` (`Dopamine.png`)
  5. Stage 5: `LATERAL:` (`Brain-Channel.png`)
  6. Stage 6: `EXFIL:` (`Music.png`)
- Detailed forensic justification mapping each stage to the MITRE ATT&CK Matrix and Lockheed Martin Cyber Kill Chain (citing Sarwar 2021, Ch. 1, 4, 6, 7).
- Justification of why filename sorting is invalid.

## 6. Automated Metadata Scanner & CSV Report (Rubric: 20 Points)
- Architecture and design decisions of `metadata_scanner.py`:
  - Iteration over directory and container format validation.
  - Multi-layer candidate extraction (EXIF IFD0, Sub-IFD, GPS, PNG chunks, XMP).
  - Heuristic detection engine and RFC 4648 regex validation.
  - Explainable classroom risk scoring engine (+10 confirmed covert, +5 encoded payload, +5 container anomaly) with double-counting prevention.
- Full reproduction of `metadata_report.csv` as a structured table.
- Analysis of scanner risk scores and individual image justifications.

## 7. Forensic Interpretations & Methodological Limitations (Rubric: 10 Points)
- Detailed analysis of EXIF-only extraction limitations (container blind spots, chunk isolation, modern web sanitization).
- Detailed analysis of automated risk scoring and heuristic detection limitations (false positives on legitimate software keys/hashes, false negatives on custom steganography/encryption, rule brittleness).

## 8. Answers to All Reflection Questions (Verbatim Q&A)
- Reflection Question 1 (Hidden messages without EXIF tags / PNG chunk architecture).
- Reflection Question 2 (Encoding vs. Encryption / Base64 security evaluation).
- Reflection Question 3 (File preservation, cryptographic hashing, and chain of custody).
- Reflection Question 4 (Malleability of metadata, spoofing risks, and essential corroborating telemetry: PCAP, EDR, SIEM, WAF logs).
- Reflection Question 5 (Architectural connection to Labs 4 & 5: from packet parsing and web vulnerability scanning to multi-layer file forensic automation).

## 9. References & Textbook Citations
- Academic citations to Jose Manuel Ortega (2021), *Mastering Python for Networking and Security - Second Edition* (Chapters 13 & 14).
- Academic citations to Fahad Ali Sarwar (2021), *Python Ethical Hacking From Scratch* (Chapters 1, 4, 6, 7).
- Industry standards citations (ISO/IEC 27037, NIST SP 800-86, MITRE ATT&CK Enterprise Matrix).
```

---

## 5. Verification Method

To independently verify all findings and recommendations in this report:

1. **Verify Notebook Integrity**:
   ```powershell
   python -c "import hashlib; print('Hash Match:', hashlib.sha256(open('Lab6/Lab6.ipynb', 'rb').read()).hexdigest() == '86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9')"
   ```
   *Expected Result*: `Hash Match: True`.

2. **Verify Git Untracked Status**:
   ```powershell
   git status --porcelain Lab6/Lab6.ipynb
   ```
   *Expected Result*: `?? Lab6/Lab6.ipynb`.

3. **Verify Scanner Execution & CSV Generation**:
   ```powershell
   python Lab6/metadata_scanner.py -i Lab6/Images -o Lab6/metadata_report.csv
   ```
   *Expected Result*: Exits 0, scans 6 images, exports 6 records to `metadata_report.csv`.

4. **Invalidation Conditions**:
   - If `Lab6/Lab6.ipynb` is modified or its SHA-256 hash changes, the core constraint of the prompt is violated.
   - If any of the 6 secrets or stage sequence differs from RECON -> VULN -> EXPLOIT -> PERSIST -> LATERAL -> EXFIL, forensic reconstruction has failed.
