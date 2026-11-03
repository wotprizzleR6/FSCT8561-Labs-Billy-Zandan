# Lab 6 Specification Mining Report: Covert Channels in Image Metadata

**Author / Analyst:** Specification Miner  
**Date:** 2026-11-02  
**Target Lab:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6`  
**Reference Notebook:** `Lab6/Lab6.ipynb`  
**Image Directory:** `Lab6/Images/`  
**Target Report Output:** `Lab6/Lab6_Report.docx`  
**Target CSV Output:** `Lab6/metadata_report.csv`  

---

## 1. Executive Summary

Lab 6 focuses on digital forensics, specifically detecting and extracting covert communication channels embedded within digital image metadata across three distinct formats and containers:
1. **EXIF Metadata** (TIFF-style headers, 0th IFD, and SubIFDs including Exif IFD and GPS IFD)
2. **PNG Text Chunks** (`tEXt`/`zTXt`/`iTXt` metadata exposed via Pillow's `img.info`)
3. **XMP Metadata** (Extensible Metadata Platform XML packets embedded in PNG chunks)

Six PNG images are provided in `Lab6/Images/`. Each image conceals exactly one partial secret fragment representing a stage in a fictional cyber incident. Together, these six fragments reconstruct a complete six-stage attack narrative corresponding to the Cyber Kill Chain / MITRE ATT&CK attack lifecycle.

The lab requires:
- Performing step-by-step metadata extraction in `Lab6.ipynb`.
- Documenting evidence in an evidence log table.
- Reconstructing and logically ordering the six-stage narrative.
- Building an automated Python metadata scanner that scans all images, assigns explainable risk scores based on heuristic indicators, and outputs `metadata_report.csv`.
- Answering five analytical reflection questions and explaining technical limitations (EXIF-only extraction limitations and automated risk scoring limitations).
- Compiling all evidence, screenshots, code, CSV output, analysis, and reflections into a formal Microsoft Word report saved at `Lab6/Lab6_Report.docx`.

---

## 2. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Metadata Extraction | Standard EXIF Tag Extraction | Extracting 0th IFD EXIF tags via Pillow `img.getexif()` and mapping tag IDs via `ExifTags.TAGS`. | PNG image with EXIF chunk (`Brain-Channel.png`, `Music.png`) | Dictionary of tag names and values (e.g., `ImageDescription`, `Copyright`, `Make`, `Model`) | Returns empty `{}` / `EXIF tags: 0` if no EXIF header exists | Notebook Section 1 (Cell 5-8), PIL probing |
| 2 | Metadata Extraction | EXIF Sub-IFD / UserComment Extraction | Extracting nested EXIF SubIFDs (IFD 34665 `ExifOffset`) to inspect `UserComment` (tag 37510). | Image with nested SubIFD (`Activation.png`) | Binary payload `b'ASCII\x00\x00\x00...'` containing `VULN:...` | Top-level `getexif()` only shows offset `ExifOffset: 204`; requires `get_ifd(ExifTags.IFD.Exif)` or `_getexif()` | Probe script on `Activation.png` |
| 3 | Metadata Extraction | PNG Text Chunk Extraction | Reading textual key-value metadata from PNG chunks (`tEXt`/`zTXt`/`iTXt`) via `img.info`. | PNG image with text metadata (`Brain.png`, `Chemicals.png`) | String key-value pairs (e.g., `Software`, `ImageDescription`) | Non-string info values (e.g. tuples, binary) must be filtered or decoded | Notebook Section 2 (Cell 9-12), PIL probing |
| 4 | Metadata Extraction | XMP Metadata XML Extraction | Locating XML-based Extensible Metadata Platform packets under `XML:com.adobe.xmp` or `xmp` keys in `img.info`. | PNG image containing XMP packet (`Dopamine.png`) | XML string / bytes containing `<rdf:RDF>` and `<exif:MakerNote>` | Missing key returns `None`; binary bytes must be decoded with `utf-8` / `errors="replace"` | Notebook Section 3 (Cell 13-15), PIL probing |
| 5 | De-obfuscation / Decoding | Base64 Covert Payload Decoding | Identifying Base64-encoded ASCII strings in metadata values and decoding to plaintext. | Base64 string from `Music.png` `Copyright` field | Plaintext message fragment `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` | Invalid padding / character causes `binascii.Error` / `UnicodeDecodeError` | Notebook Section 4 (Cell 16-19), PIL probing |
| 6 | Forensic Analysis | Six-Stage Secret Narrative Reconstruction | Reassembling the six recovered secret fragments into chronological order based on stage prefix labels. | Six recovered message strings with prefixes `RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:` | Numbered chronological list (Stages 1 through 6) with Cyber Kill Chain justification | Incorrect ordering if filenames are used instead of stage semantics | Notebook Section 6 (Cell 33), Analysis |
| 7 | Automation & Tooling | Automated Metadata Scanner | Python script / function iterating over all images, extracting EXIF, PNG text, XMP, detecting covert channels, and computing risk scores. | Directory of PNG images (`Lab6/Images/*.png`) | List of structured dictionaries with risk assessment | Unhandled metadata formats or missing files could throw exceptions | Notebook Section 7 (Cell 34-39) |
| 8 | Reporting & Export | CSV Report Generation | Writing automated scanner findings to `metadata_report.csv` with 7 required columns using `csv.DictWriter`. | List of result dictionaries | CSV file `metadata_report.csv` with header row and 6 image data rows | Schema mismatch or missing keys raise `ValueError` | Notebook Cell 38-39, ORIGINAL_REQUEST.md |
| 9 | Reporting & Deliverable | Microsoft Word Lab Report | Comprehensive professional Word report documenting evidence, tables, screenshots, code, narrative, limitations, and reflections. | Lab deliverables, extracted data, forensic logs | Valid `.docx` file at `Lab6/Lab6_Report.docx` | Missing rubric components results in mark deduction | ORIGINAL_REQUEST.md, Cell 41 Rubric |

---

## 3. Edge Cases & Forensic Quirks Discovered

| # | Feature / Artifact | Input / Scenario | Observed Behavior & Technical Cause | Impact & Handling Recommendation |
|---|--------------------|------------------|-------------------------------------|-----------------------------------|
| 1 | EXIF Sub-IFD vs 0th IFD | `Activation.png` scanned with standard `img.getexif()` loop | `img.getexif()` returns 10 tags, but does NOT display tag 37510 (`UserComment`). Only tag 34665 (`ExifOffset: 204`) is visible at top level. | Must query SubIFD via `img.getexif().get_ifd(ExifTags.IFD.Exif)[37510]` or `img._getexif()`. |
| 2 | EXIF `UserComment` Header | `Activation.png` tag 37510 raw bytes | Value is `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`. An 8-byte charset prefix (`ASCII\x00\x00\x00`) precedes the text. | Strip the 8-byte prefix before displaying or decoding string. |
| 3 | Zero EXIF in Valid PNG | `Brain.png` and `Chemicals.png` probed with `img.getexif()` | `len(exif) == 0`. No EXIF metadata chunk exists. Naive scripts checking only EXIF report "no metadata found". | The metadata is stored in native PNG text chunks accessible via `img.info['Software']` and `img.info['ImageDescription']`. |
| 4 | XMP in PNG without EXIF | `Dopamine.png` probed with `img.getexif()` | `len(exif) == 0`. EXIF is empty. | Secret is embedded inside XMP XML packet stored under `XML:com.adobe.xmp` or `xmp` within `img.info`. Must parse XML or regex `<exif:MakerNote>`. |
| 5 | UTF-8 Byte Order Mark (BOM) in XMP | `Dopamine.png` XMP packet printed to Windows console | XMP packet starts with `<?xpacket begin='\xef\xbb\xbf' ...?>`. Direct output to standard Windows `cp1252` console raises `UnicodeEncodeError`. | Must reconfigure stdout to UTF-8 (`sys.stdout.reconfigure(encoding='utf-8')`) or decode with UTF-8. |
| 6 | Redundant / Dual Metadata Storage | `Music.png` metadata inspection | The Base64 string appears in BOTH EXIF tag 33432 (`Copyright`) AND `img.info['Copyright']` PNG text chunk. | Scanner must avoid double-counting or inflating risk score twice for the same field in multiple containers. |
| 7 | Filename Order vs Narrative Order | Alphabetical ordering of images (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`) | Alphabetical order produces: VULN -> LATERAL -> RECON -> EXPLOIT -> PERSIST -> EXFIL. This is chronologically nonsensical. | Ordering MUST be reconstructed based on incident lifecycle semantics: RECON (1), VULN (2), EXPLOIT (3), PERSIST (4), LATERAL (5), EXFIL (6). |
| 8 | Classroom Risk Scoring Heuristic vs True Probability | Risk scoring across the 6 images | Heuristic model (+10 confirmed covert, +5 encoded, +5 unusual metadata) produces scores of 10 or 15. It reflects suspicion indicators, NOT mathematical attack probabilities. | Report must clearly articulate this limitation to avoid false confidence in automated forensic scoring. |

---

## 4. Complete Cell-by-Cell Structure of `Lab6.ipynb`

`Lab6.ipynb` consists of **42 cells** (indices 0 to 41):

### Header & Environment Setup (Cells 0–4)
- **Cell 0 (Markdown):** Title `# Lab 6: Covert Channels in Image Metadata`, Guided investigation scenario (6 images containing 1 partial secret each), Learning goals, instructions ("First practise each small snippet on one image. Then select and run the relevant snippets on each of the six images, one at a time. You will write the final secret yourself. No completed secret is provided in this student notebook.").
- **Cell 1 (Markdown):** `## 0. Prepare the environment` - Instructions to keep notebook beside `Lab6` folder containing `Images`.
- **Cell 2 (Code):** `%pip -q install Pillow` (Contains existing output: `"Note: you may need to restart the kernel to use updated packages.\n"`).
- **Cell 3 (Code):** Verification snippet:
  ```python
  from pathlib import Path
  from PIL import Image, ExifTags

  image_dir = Path("Images")
  print("Images found:", len(list(image_dir.glob("*.png"))))
  ```
  Expected output: `Images found: 6`
- **Cell 4 (Markdown):** `### Your evidence log` - Instruction: "For each image, record the metadata type, field name, raw value (or a short excerpt), decoding method (if any), recovered message, and your interpretation. Do not assume that `getexif()` displays all metadata."

### Technique 1: EXIF Metadata (Cells 5–8)
- **Cell 5 (Markdown):** `## 1. First technique: EXIF metadata (one image)` - Explains EXIF metadata, camera details, tags. Prompts trying `Brain-Channel.png`.
- **Cell 6 (Code):** Practice snippet for `Brain-Channel.png`:
  ```python
  image_path = image_dir / "Brain-Channel.png"
  with Image.open(image_path) as img:
      exif = img.getexif()
      print("EXIF tags:", len(exif))
      for tag_id, value in exif.items():
          print(ExifTags.TAGS.get(tag_id, tag_id), ":", value)
  ```
- **Cell 7 (Markdown):** 
  - **Question 1:** *"Observe: Which EXIF field carries a message? Record it in your evidence log."*
  - **Question 2:** *"Try it yourself: Change `image_path` to a different image. If `EXIF tags: 0` appears, does that mean the image has no metadata? Explain."*
- **Cell 8 (Code):**
  ```python
  # Your turn: choose another image and repeat the EXIF check.
  image_path = image_dir / "Activation.png"
  # TODO: reuse the short EXIF snippet above
  ```

### Technique 2: PNG Text Metadata (Cells 9–12)
- **Cell 9 (Markdown):** `## 2. Second technique: PNG text metadata (one image)` - Explains PNG textual chunks not returned by `getexif()`. Prompts trying `Brain.png`.
- **Cell 10 (Code):** Practice snippet for `Brain.png`:
  ```python
  image_path = image_dir / "Brain.png"
  with Image.open(image_path) as img:
      for key, value in img.info.items():
          if isinstance(value, str):
              print(key, ":", value)
  ```
- **Cell 11 (Markdown):**
  - **Question 3:** *"Observe: Which PNG text field contains a clue? Try **Chemicals.png** next using the same short snippet."*
- **Cell 12 (Code):**
  ```python
  image_path = image_dir / "Chemicals.png"
  # TODO: reuse the PNG text snippet above
  ```

### Technique 3: XMP Metadata (Cells 13–15)
- **Cell 13 (Markdown):** `## 3. Third technique: XMP metadata (one image)` - Explains XMP XML-based metadata in PNG files. Prompts trying `Dopamine.png`.
- **Cell 14 (Code):** Practice snippet for `Dopamine.png`:
  ```python
  image_path = image_dir / "Dopamine.png"
  with Image.open(image_path) as img:
      xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
      if isinstance(xmp, bytes):
          xmp = xmp.decode("utf-8", errors="replace")
      print(xmp if xmp else "No XMP found")
  ```
- **Cell 15 (Markdown):**
  - **Question 4:** *"Observe: Locate the XML element containing the partial secret. Why did the EXIF-only approach miss it? Note: XMP may appear under either `XML:com.adobe.xmp` or `xmp`, depending on how the file was created and the software version."*

### Technique 4: Decode Suspicious Text (Cells 16–19)
- **Cell 16 (Markdown):** `## 4. Fourth technique: Decode suspicious text (one image)` - Explains encoded text in metadata. Prompts inspecting `Music.png`, identifying Base64, and decoding.
- **Cell 17 (Code):** Practice snippet:
  ```python
  import base64

  example = "SGVsbG8="
  print(base64.b64decode(example).decode("utf-8"))
  ```
- **Cell 18 (Markdown):**
  - **Prompt:** *"Your turn: Replace `example` with the suspicious metadata value from **Music.png**. Do not assume every long string is Base64; use the context and validate the result."*
- **Cell 19 (Code):**
  ```python
  encoded_message = ""  # TODO: paste the encoded value found in Music.png
  if encoded_message:
      print(base64.b64decode(encoded_message).decode("utf-8"))
  ```

### Section 5: Six Images Investigation (Cells 20–32)
- **Cell 20 (Markdown):** `## 5. Your investigation: six images, one by one` - Summary instructions and Evidence Table Template:
  ```markdown
  | Image | Metadata type / field | Decoding needed? | Partial secret recovered |
  |---|---|---|---|
  | Activation.png | | | |
  | Brain-Channel.png | | | |
  | Brain.png | | | |
  | Chemicals.png | | | |
  | Dopamine.png | | | |
  | Music.png | | | |
  ```
  Note: *"The filename order is not necessarily the narrative order."*
- **Cell 21 (Markdown):** `### Investigation 1: Activation.png` - "Choose and reuse the appropriate short extraction snippet(s) above. Record the evidence in your table. **What is the partial secret?**"
- **Cell 22 (Code):** Code block for `Activation.png` (`# TODO: paste or adapt the relevant short snippet from Sections 1–4`).
- **Cell 23 (Markdown):** `### Investigation 2: Brain-Channel.png` - "What is the partial secret?"
- **Cell 24 (Code):** Code block for `Brain-Channel.png` (`# TODO: paste or adapt...`).
- **Cell 25 (Markdown):** `### Investigation 3: Brain.png` - "What is the partial secret?"
- **Cell 26 (Code):** Code block for `Brain.png` (`# TODO: paste or adapt...`).
- **Cell 27 (Markdown):** `### Investigation 4: Chemicals.png` - "What is the partial secret?"
- **Cell 28 (Code):** Code block for `Chemicals.png` (`# TODO: paste or adapt...`).
- **Cell 29 (Markdown):** `### Investigation 5: Dopamine.png` - "What is the partial secret?"
- **Cell 30 (Code):** Code block for `Dopamine.png` (`# TODO: paste or adapt...`).
- **Cell 31 (Markdown):** `### Investigation 6: Music.png` - "What is the partial secret?"
- **Cell 32 (Code):** Code block for `Music.png` (`# TODO: paste or adapt...`).

### Section 6: Reconstruct the Complete Secret (Cell 33)
- **Cell 33 (Markdown):**
  - Narrative template (Stages 1 through 6):
    ```markdown
    1. **Stage:** __________  **Recovered message:** __________________________________
    2. **Stage:** __________  **Recovered message:** __________________________________
    3. **Stage:** __________  **Recovered message:** __________________________________
    4. **Stage:** __________  **Recovered message:** __________________________________
    5. **Stage:** __________  **Recovered message:** __________________________________
    6. **Stage:** __________  **Recovered message:** __________________________________
    ```
  - Prompt: *"Explain your reasoning: Why is this the most plausible order?"*

### Section 7: Automated Metadata Scanner (Cells 34–39)
- **Cell 34 (Markdown):** `## 7. Build an automated metadata scanner` - Requirements 1–6 and Suggested Classroom Risk Model:
  - +10 for confirmed covert-message field
  - +5 for suspicious encoded value requiring investigation
  - +5 for additional unusual metadata indicator supported by evidence
  - Avoid double-counting
  - Scores are heuristics, not forensic probabilities.
- **Cell 35 (Code):** Step 7A Starter: Loop through images (`sorted(image_dir.glob("*.png"))`).
- **Cell 36 (Markdown):** Step 7B Starter: Create one result row.
- **Cell 37 (Code):** Starter dictionary row for `Brain.png`.
- **Cell 38 (Markdown):** Step 7C Instructions: Complete scanner or write `metadata_scanner.py`, extend dict with `suspected_field`, `encoding`, `reason`, use `csv.DictWriter`, avoid hardcoding secret messages.
- **Cell 39 (Code):** Scanner implementation cell exporting to `metadata_report.csv`.

### Section 8: Reflection & Submission Rubric (Cells 40–41)
- **Cell 40 (Markdown):** 5 Reflection Questions (see Section 6 below).
- **Cell 41 (Markdown):** Submission requirements and official 100-point grading rubric (see Section 8 below).

---

## 5. Detailed Forensic Image Metadata Extraction Specification

Below is the verified forensic evidence extracted directly from all six images in `Lab6/Images/`:

### Summary Evidence Table

| # | Filename | File Size | SHA-256 Hash | Metadata Container | Exact Tag / Field Name | Raw Extracted Value | Decoding Method | Recovered Secret Fragment | Narrative Stage & Label |
|---|----------|-----------|--------------|--------------------|------------------------|---------------------|-----------------|---------------------------|-------------------------|
| 1 | `Activation.png` | 259,975 B | `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904` | EXIF Sub-IFD (IFD 34665 `ExifOffset`) | Tag 37510 (`UserComment`) | `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'` | Strip 8-byte ASCII charset header (`ASCII\x00\x00\x00`) and decode UTF-8 | `VULN: Identify unpatched CVE-2024-XXXX in web gateway.` | Stage 2: `VULN` (Vulnerability Scanning) |
| 2 | `Brain-Channel.png` | 201,685 B | `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359` | EXIF 0th IFD | Tag 270 (`ImageDescription`) | `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'` | None (Plaintext string) | `LATERAL: Pivot to internal Domain Controller using Mimikatz.` | Stage 5: `LATERAL` (Lateral Movement) |
| 3 | `Brain.png` | 2,354,330 B | `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e` | PNG Text Chunk (`tEXt`/`zTXt`) | `img.info['Software']` | `'RECON: Perform DNS harvesting and Subdomain enumeration.'` | None (Plaintext string) | `RECON: Perform DNS harvesting and Subdomain enumeration.` | Stage 1: `RECON` (Reconnaissance) |
| 4 | `Chemicals.png` | 561,245 B | `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a` | PNG Text Chunk (`tEXt`) | `img.info['ImageDescription']` | `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'` | None (Plaintext string) | `EXPLOIT: Deploy SQL Injection payload to bypass WAF.` | Stage 3: `EXPLOIT` (Exploitation) |
| 5 | `Dopamine.png` | 388,411 B | `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472` | XMP Metadata XML Packet | `XML:com.adobe.xmp` / `xmp` -> `<exif:MakerNote>` | `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>` | Parse XML / Regex search for `<exif:MakerNote>` content | `PERSIST: Establish reverse shell via obfuscated cron job.` | Stage 4: `PERSIST` (Persistence) |
| 6 | `Music.png` | 679,959 B | `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370` | EXIF 0th IFD & PNG Text Chunk | Tag 33432 (`Copyright`) / `img.info['Copyright']` | `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='` | Base64 decode (`base64.b64decode(...).decode('utf-8')`) | `EXFIL: Tunnel compressed database dump via DNS Covert Channel.` | Stage 6: `EXFIL` (Exfiltration) |

---

## 6. Narrative Secret Reconstruction & Sequence Justification

### Chronological Secret Narrative (Stages 1 through 6)

1. **Stage 1 (RECON) — `Brain.png`:**
   > `RECON: Perform DNS harvesting and Subdomain enumeration.`
2. **Stage 2 (VULN) — `Activation.png`:**
   > `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`
3. **Stage 3 (EXPLOIT) — `Chemicals.png`:**
   > `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`
4. **Stage 4 (PERSIST) — `Dopamine.png`:**
   > `PERSIST: Establish reverse shell via obfuscated cron job.`
5. **Stage 5 (LATERAL) — `Brain-Channel.png`:**
   > `LATERAL: Pivot to internal Domain Controller using Mimikatz.`
6. **Stage 6 (EXFIL) — `Music.png`:**
   > `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`

### Technical & Forensic Justification
The sequence follows the standard **Lockheed Martin Cyber Kill Chain** and **MITRE ATT&CK Framework**:
- **Reconnaissance (Stage 1):** An adversary begins by gathering intelligence on the target's external footprint (DNS harvesting, subdomain enumeration) to identify potential attack surfaces.
- **Vulnerability Scanning (Stage 2):** Having mapped the external perimeter, the adversary evaluates specific assets for exploitable flaws, discovering an unpatched vulnerability (`CVE-2024-XXXX`) in the web gateway.
- **Exploitation (Stage 3):** The adversary weaponizes and launches an exploit (SQL Injection payload designed to bypass Web Application Firewall filters) to breach the initial perimeter.
- **Persistence (Stage 4):** Once initial execution is achieved, the adversary ensures durable, recurring access by installing a reverse shell via an obfuscated cron job scheduled task.
- **Lateral Movement & Credential Access (Stage 5):** Operating from their initial foothold, the adversary dumps credentials using Mimikatz to pivot through the internal subnet towards high-value infrastructure (the Domain Controller).
- **Exfiltration (Stage 6):** With administrative access obtained, the adversary extracts sensitive data (compressed database dump) and covertly tunnels it out via DNS queries to evade standard egress inspection.

---

## 7. Analytical & Reflection Questions Specification

### Inline Notebook Questions
- **Cell 7 (Observation 1):** *"Which EXIF field carries a message? Record it in your evidence log."*
  - **Answer:** In `Brain-Channel.png`, EXIF Tag 270 (`ImageDescription`) contains the covert message: `"LATERAL: Pivot to internal Domain Controller using Mimikatz."`
- **Cell 7 (Try it yourself / Observation 2):** *"Change `image_path` to a different image. If `EXIF tags: 0` appears, does that mean the image has no metadata? Explain."*
  - **Answer:** No. `img.getexif()` solely parses standard TIFF-formatted EXIF chunks. Formats like PNG support native text chunks (`tEXt`, `zTXt`, `iTXt` accessed via `img.info`) and XMP data packets (`XML:com.adobe.xmp`), which exist completely outside the EXIF IFD structure. An image showing 0 EXIF tags can still hold extensive native or XMP metadata.
- **Cell 11 (Observation 3):** *"Which PNG text field contains a clue? Try Chemicals.png next using the same short snippet."*
  - **Answer:** In `Brain.png`, the `Software` field in `img.info` contains `"RECON: Perform DNS harvesting and Subdomain enumeration."` In `Chemicals.png`, the `ImageDescription` field in `img.info` contains `"EXPLOIT: Deploy SQL Injection payload to bypass WAF."`
- **Cell 15 (Observation 4):** *"Locate the XML element containing the partial secret. Why did the EXIF-only approach miss it? Note: XMP may appear under either `XML:com.adobe.xmp` or `xmp`, depending on how the file was created and the software version."*
  - **Answer:** The partial secret is contained within the `<exif:MakerNote>` XML element inside the `<rdf:Description>` node. The EXIF-only approach missed it because `Dopamine.png` contains no binary EXIF chunk header; the metadata was authored as an Extensible Metadata Platform (XMP) XML document packaged within an international textual chunk (`iTXt`), which is only exposed under `img.info['XML:com.adobe.xmp']` or `img.info['xmp']`.
- **Cell 18 (Technique 4 / Decoding):** *"Replace `example` with the suspicious metadata value from Music.png. Do not assume every long string is Base64; use the context and validate the result."*
  - **Answer:** Raw value found in `Music.png`'s `Copyright` field is `RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4=`. Base64 decoding produces: `"EXFIL: Tunnel compressed database dump via DNS Covert Channel."`

### Cell 40: Formal Reflection Questions
1. **Q1: Why can an image contain a hidden message even when `getexif()` returns no tags?**
   - **Comprehensive Answer:** Digital image formats (notably PNG, GIF, and TIFF) support multiple independent metadata containers. Pillow's `getexif()` specifically parses TIFF/EXIF IFDs (Image File Directories). PNG files store textual metadata in distinct chunks (`tEXt` for Latin-1, `zTXt` for compressed text, and `iTXt` for UTF-8 and XMP XML packets). If an author embeds data directly into PNG text chunks or XMP blocks without injecting an EXIF header, `getexif()` returns 0 tags even though rich metadata resides in other valid chunks exposed via `img.info`.
2. **Q2: How is encoding different from encryption? Is Base64 a secure way to hide information?**
   - **Comprehensive Answer:** Encoding is a publicly known, algorithmic transformation designed to ensure data integrity across text-based protocols (e.g., converting arbitrary binary into 64 printable ASCII characters) without requiring any secret key. Anyone encountering Base64 can decode it instantly without authorization. In contrast, encryption applies a mathematical algorithm parameterized by a secret cryptographic key, ensuring confidentiality such that unauthorized parties cannot read the plaintext. Base64 provides zero confidentiality or security; it is merely an obfuscation or transport mechanism.
3. **Q3: Why should investigators preserve the original files and record hashes?**
   - **Comprehensive Answer:** In forensic science, evidence admissibility in court requires establishing a strict chain of custody and demonstrating that digital evidence has not been altered, tainted, or fabricated. Computing cryptographic hashes (e.g., SHA-256 and MD5) upon acquisition provides a mathematical fingerprint of the exact bitstream. If an investigator operates on live files, opening or saving them in editing software can strip, rewrite, or normalize metadata chunks, destroying covert channel artifacts and invalidating findings. Preserving bit-for-bit copies and verifying hashes guarantees reproducibility.
4. **Q4: Can metadata alone prove that an image was edited or that an incident occurred? What corroborating evidence would you need?**
   - **Comprehensive Answer:** No, metadata alone cannot prove that an incident occurred or conclusively identify an attacker because metadata is trivially spoofed, altered, stripped, or injected using open-source tools like ExifTool. In a forensic investigation, metadata is circumstantial evidence that must be corroborated with:
     - Network packet captures (PCAP) showing covert DNS tunneling or HTTP SQLi requests matching the timestamps.
     - Web server and WAF access logs corroborating the exploit requests.
     - Host-based endpoint telemetry (EDR/Sysmon) recording cron job creation, Mimikatz process execution, or LSASS memory access.
     - File system forensic timestamps ($MFT, $LogFile) and file origin artifacts (Zone.Identifier Alternate Data Streams).
5. **Q5: How does this investigation connect to the automated evidence collection and analysis you practised in Labs 4 and 5?**
   - **Comprehensive Answer:** In Lab 4, we built automated traffic sniffers and anomaly detectors to parse PCAP files, extract protocol headers, and flag statistical volume bursts. In Lab 5, we developed HTTP vulnerability scanners to systematically probe endpoints, parse status codes, and classify security findings into CSV reports with heuristic risk ratings. Lab 6 applies this exact paradigm to static binary image analysis: parsing structured protocol/container fields (EXIF, PNG, XMP), detecting suspicious payloads, scoring risk heuristically, and exporting structured CSV deliverables. All three labs demonstrate the end-to-end pipeline of automated extraction, pattern classification, risk evaluation, and forensic documentation.

### Technical Limitations (Required for Section 8 and Word Report)
- **Limitation 1: EXIF-Only Extraction Limitations:**
  An EXIF-only analysis tool will fail completely when analyzing PNG, WebP, or SVG graphics that employ format-native text chunks or XMP data structures. Furthermore, even within files containing EXIF, tools that inspect only the top-level 0th IFD miss covert payloads concealed inside nested SubIFDs (such as `ExifOffset` IFD 34665 or GPS IFD 34853), resulting in false negatives.
- **Limitation 2: Automated Risk Scoring Limitations:**
  Heuristic risk scoring models rely on predefined pattern matching (e.g., regex for Base64 or known keywords). They are subject to false positives (flagging legitimate Base64 image thumbnails or legitimate camera serial numbers) and false negatives (failing to detect novel encoding schemes, steganographic LSB alterations, encrypted blobs, or zero-width character obfuscation). Heuristic scores do not represent forensic certainty or true Bayesian attack probabilities.

---

## 8. Automated Metadata Scanner Specification & CSV Schema

### Schema Definition
Output File: `Lab6/metadata_report.csv`  
Columns (7 required fields):
1. `filename` — Name of the image file (e.g., `Brain.png`)
2. `format` — Image format string reported by Pillow (e.g., `PNG`)
3. `metadata_fields` — Comma-separated list of metadata keys/tags discovered in `img.info`
4. `suspected_field` — Exact field name identified as harboring the covert message (e.g., `PNG:Software`, `EXIF:ImageDescription`, `EXIF:UserComment`, `XMP:exif:MakerNote`, `EXIF/PNG:Copyright`)
5. `encoding` — Encoding mechanism identified (e.g., `Plain text`, `ASCII (stripped header)`, `Base64`)
6. `risk_score` — Integer risk score evaluated according to the classroom heuristic model
7. `reason` — Clear technical rationale explaining the assigned risk score and observed evidence

### Risk Model Heuristics (Cell 34)
- **Base Covert Indicator:** `+10` points for identifying a confirmed covert-channel message field (e.g. matching attack stage indicator `RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`).
- **Encoding Suspicion:** `+5` points for suspicious encoded value requiring decoding/investigation (e.g. Base64 string in `Music.png`).
- **Anomalous Metadata Indicator:** `+5` points for an additional unusual metadata artifact supported by evidence (e.g. camera make/model and GPS coordinates embedded inside a web PNG graphic in `Activation.png`, or hidden XML MakerNote packet in `Dopamine.png`).
- **Constraint:** Avoid double-counting an encoded payload as both an encoded indicator and an additional unusual indicator.

### Expected CSV Data Rows

```csv
filename,format,metadata_fields,suspected_field,encoding,risk_score,reason
Activation.png,PNG,"srgb, gamma, dpi, exif, Make, Model, Software, create-date",EXIF:UserComment,ASCII (stripped header),15,"Confirmed covert channel (VULN: stage) in EXIF SubIFD UserComment (+10); anomalous presence of camera hardware EXIF and GPS tags in a synthetic web graphic (+5)."
Brain-Channel.png,PNG,"srgb, gamma, dpi, exif",EXIF:ImageDescription,Plain text,10,"Confirmed covert channel (LATERAL: stage) in standard EXIF ImageDescription tag (+10)."
Brain.png,PNG,"srgb, gamma, dpi, Software",PNG:Software,Plain text,10,"Confirmed covert channel (RECON: stage) embedded directly in native PNG text chunk Software (+10)."
Chemicals.png,PNG,ImageDescription,PNG:ImageDescription,Plain text,10,"Confirmed covert channel (EXPLOIT: stage) embedded directly in native PNG text chunk ImageDescription (+10)."
Dopamine.png,PNG,"srgb, gamma, dpi, xmp, XML:com.adobe.xmp",XMP:exif:MakerNote,Plain text (XML),15,"Confirmed covert channel (PERSIST: stage) in XMP XML packet (+10); disguised under exif:MakerNote XML tag within an iTXt chunk with no EXIF header (+5)."
Music.png,PNG,"srgb, gamma, dpi, Copyright, Make, Model, create-date, exif",EXIF/PNG:Copyright,Base64,15,"Confirmed covert channel (EXFIL: stage) in Copyright tag (+10); suspicious Base64 encoded payload requiring de-obfuscation (+5)."
```

---

## 9. Word Report Specification (`Lab6/Lab6_Report.docx`)

### Deliverable Requirements
- File Path: `Lab6/Lab6_Report.docx`
- Author: Billy Zandan (Student ID: A01371854)
- Target Course: FSCT 8561 (Digital Forensics / Information Security)
- Formatting: Clean professional layout, title page/header, structured section headings (Heading 1, 2, 3), formatted tables with styling and borders, code blocks in shaded callout boxes / monospaced font.

### Required Document Structure & Sections
1. **Title & Document Metadata:**
   - Title: Lab 6: Covert Channels in Image Metadata — Forensic Investigation & Automated Scanner
   - Student Name: Billy Zandan
   - Student Number: A01371854
   - Date: November 2026
   - Scenario & Investigation Overview
2. **Executive Summary & Threat Landscape:**
   - Forensic background on covert metadata channels (steganography vs. metadata manipulation).
   - Attack vectors exploiting EXIF, PNG chunks, and XMP.
3. **Comprehensive Forensic Evidence Log (All 6 Images):**
   - Full evidence table including Image Name, File Size, MD5 & SHA-256 hashes, Metadata Container, Tag/Field Name, Raw Value, Decoding Method, Decoded Message, and Narrative Stage.
4. **Step-by-Step Investigation & Extraction Proof (Images 1–6):**
   - Detailed walkthrough for each image (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`).
   - Code snippet used to extract the metadata.
   - Textual screenshot / verbatim extraction output showing proof of recovery.
   - Technical analysis of the container mechanism.
5. **Reconstruction of the Six-Stage Incident Narrative:**
   - Chronological table (Stages 1 through 6).
   - In-depth forensic justification linking each stage to the Lockheed Martin Cyber Kill Chain and MITRE ATT&CK tactics.
6. **Automated Metadata Scanner Implementation:**
   - Complete Python code of `metadata_scanner.py`.
   - Architectural design decisions (handling EXIF SubIFDs, PNG text, XMP regex, Base64 detection, heuristic scoring).
   - Formatted results table of `metadata_report.csv`.
7. **Forensic Analysis of Limitations:**
   - Limitation 1: Limitations of EXIF-Only Metadata Extraction (missed PNG text, missed XMP, missed SubIFDs).
   - Limitation 2: Limitations of Automated Heuristic Risk Scoring (false positives, false negatives, lack of forensic probability).
8. **Answers to Reflection Questions:**
   - Complete, rigorous forensic answers to all 5 reflection questions from Cell 40.
9. **Conclusion & Recommendations:**
   - Summary of findings, forensic remediation, metadata stripping in egress proxies/WAFs.

---

## 10. Official Grading Rubric Cross-Reference (100 Points)

| Rubric Component | Max Points | Notebook / Report Requirements | Miner Verification Notes |
|---|---:|---|---|
| **Metadata extraction and evidence documentation** | **25** | Appropriate EXIF/PNG/XMP extraction for all six images; accurate field identification; clear evidence screenshots and tables. | All 6 images probed. Verified exact fields: `UserComment` in SubIFD, `ImageDescription` in EXIF, `Software` in PNG, `ImageDescription` in PNG, `exif:MakerNote` in XMP, `Copyright` in EXIF/PNG. Hashes and raw values recorded. |
| **Covert-channel detection and decoding** | **25** | All six hidden fragments recovered accurately; encoded content decoded correctly; extraction methods explained. | Base64 decoded in `Music.png`, ASCII header stripped in `Activation.png`, XML element parsed in `Dopamine.png`. All 6 messages verified. |
| **Six-stage secret reconstruction** | **20** | Complete secret assembled in correct order with a logical justification. | Reconstructed: RECON -> VULN -> EXPLOIT -> PERSIST -> LATERAL -> EXFIL. Mapped to Cyber Kill Chain and ATT&CK. |
| **Automated metadata scanner and CSV report** | **20** | Scanner iterates through all six images, checks relevant metadata types, identifies suspected fields, exports complete CSV rows, and applies consistent, explainable risk scores. | Schema verified (7 columns). Classroom risk scoring heuristic defined (+10, +5, +5). CSV table fully populated and validated. |
| **Interpretations, reflections, code quality, and presentation** | **10** | Readable, reproducible Python code; clear report organization; thoughtful explanation of EXIF-only and risk-scoring limitations. | 5 reflection questions thoroughly answered; both EXIF-only and risk-scoring limitations documented in depth; Word doc layout designed. |
| **Total** | **100** | | Full coverage of all 100 points. |

