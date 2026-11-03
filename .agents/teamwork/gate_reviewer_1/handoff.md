# Gate Review Evaluation Report: Lab 6 Deliverables & Rubric Conformance

## 1. Observation

Direct observations and programmatic execution results across all target artifacts and requirements:

1. **Student Notebook Immutability (`Lab6/Lab6.ipynb`)**:
   - Verification command executed:
     ```powershell
     Get-FileHash -Algorithm SHA256 "c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb"
     ```
   - Observed output:
     ```text
     Algorithm   Hash                                                               Path
     ---------   ----                                                               ----
     SHA256      86D9886A845CD328DFF590E47B391C5507A545FE05C230292492289073218ED9  C:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb
     ```
   - Required baseline: `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`.
   - Result: Exact match. The notebook has not been modified or corrupted.

2. **Image Corpus Ground Truth & Checksum Verification**:
   - Verification command executed:
     ```powershell
     Get-ChildItem "Lab6\Images\*.png" | ForEach-Object { [PSCustomObject]@{ Name=$_.Name; Length=$_.Length; Hash=(Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLower() } } | Format-Table -AutoSize
     ```
   - Observed results:
     - `Activation.png`: Size `259975` bytes, SHA-256 `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904`
     - `Brain-Channel.png`: Size `201685` bytes, SHA-256 `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359`
     - `Brain.png`: Size `2354330` bytes, SHA-256 `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e`
     - `Chemicals.png`: Size `561245` bytes, SHA-256 `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a`
     - `Dopamine.png`: Size `388411` bytes, SHA-256 `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472`
     - `Music.png`: Size `679959` bytes, SHA-256 `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370`
   - Comparison with `Lab6/Lab6_Report.md` Table 1 (lines 46–54): Exact 100% byte-for-byte and hash match across all six images.

3. **Automated Metadata Scanner Execution (`Lab6/metadata_scanner.py`)**:
   - Verification command executed:
     ```powershell
     python "c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py" -i "c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images" -o "c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv" --verbose
     ```
   - Execution status: Exit code 0 (clean execution without errors or warnings).
   - Observed scanner output:
     - All 6 PNG images parsed.
     - Scanned `Activation.png`: Suspected Field `UserComment`, Encoding `EXIF ASCII header / plain text`, Risk Score `15`, Secret `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`
     - Scanned `Brain-Channel.png`: Suspected Field `ImageDescription`, Encoding `None (plain text)`, Risk Score `10`, Secret `LATERAL: Pivot to internal Domain Controller using Mimikatz.`
     - Scanned `Brain.png`: Suspected Field `Software`, Encoding `None (plain text)`, Risk Score `10`, Secret `RECON: Perform DNS harvesting and Subdomain enumeration.`
     - Scanned `Chemicals.png`: Suspected Field `ImageDescription`, Encoding `None (plain text)`, Risk Score `10`, Secret `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`
     - Scanned `Dopamine.png`: Suspected Field `XML:com.adobe.xmp (exif:MakerNote)`, Encoding `XML encapsulation / plain text`, Risk Score `15`, Secret `PERSIST: Establish reverse shell via obfuscated cron job.`
     - Scanned `Music.png`: Suspected Field `Copyright`, Encoding `Base64`, Risk Score `15`, Secret `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`
   - Verification of `Lab6/metadata_report.csv`:
     - Exactly 8 lines (1 header line + 6 image records + 1 trailing newline).
     - Standard 7 columns present: `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`.
     - Exact verbatim match with Table 3 (lines 625–633) in `Lab6_Report.md`.

4. **Forensic Examination Report Content (`Lab6/Lab6_Report.md`)**:
   - File length: 802 lines, 73,006 bytes.
   - Master Evidence Table (Section 3.1, lines 274–281): Covers all 6 images with Metadata Type, Field Name / Tag ID, Raw Value Excerpt, Decoding Method, Recovered Secret Fragment, and Forensic Interpretation.
   - Per-image forensic write-ups (Section 3.2, lines 285–411): Each image details file integrity, parser navigation, de-obfuscation methodology, and operational context. Includes GPS decoding for `Activation.png` (`40° 42' 46.08" N, 74° 0' 21.6" W` $\to$ Wall Street, NYC).
   - Covert-channel detection and decoding (Section 4, lines 414–483): Details `UserComment` 8-byte ASCII prefix stripping (`ASCII\x00\x00\x00`), Base64 RFC 4648 validation heuristics (length, alphabet, padding, printable entropy ratio > 0.85), and XMP XML ElementTree parsing with Windows BOM (`\ufeff`) stripping.
   - Six-stage incident narrative (Section 5, lines 485–570): Ordered as `RECON` (`Brain.png`) $\to$ `VULN` (`Activation.png`) $\to$ `EXPLOIT` (`Chemicals.png`) $\to$ `PERSIST` (`Dopamine.png`) $\to$ `LATERAL` (`Brain-Channel.png`) $\to$ `EXFIL` (`Music.png`). Includes Table 2 mapping each stage to Cyber Kill Chain, MITRE ATT&CK tactics/techniques, and textbooks. Includes Section 5.3 explicitly refuting the alphabetical filename decoy.
   - Scanner architecture & CSV reproduction (Section 6, lines 572–654): Explains 3-phase pipeline, verbatim CSV reproduction, additive scoring model (+10 base, +5 encoding, +5 container anomaly, capped at 15 with double-counting guardrail), and per-image score justifications.
   - Methodological limitations (Section 7, lines 656–696): Details 4 distinct limitations of EXIF-only metadata extraction (container blind spots, sub-IFD traversal failures, inability to parse XML, web/social media sanitization) and 5 distinct limitations of automated heuristic risk scoring (keyword brittleness, Base64 ambiguity, pixel steganography blind spot, static scoring caps, contextual agnosticism).
   - Reflection questions (Section 8, lines 698–773): Verbatim answers to all five reflection questions from `Lab6.ipynb` with extensive forensic justification.
   - Academic citations (Section 9, lines 774–802): Explicit citations to Jose Manuel Ortega (2021) Chapters 13 & 14, and Fahad Ali Sarwar (2021) Chapters 1, 3, 4, 6, 8, as well as ISO/IEC 27037, NIST SP 800-86, ISO/IEC 15948, RFC 4648, and MITRE ATT&CK.

5. **Instructional Guide (`Lab6/Lab6_Instructions.md`)**:
   - File length: 426 lines, 21,831 bytes.
   - Complete step-by-step instructions for environment preparation, baseline hashing, multi-layer extraction, decoding, narrative reconstruction, automated scanner execution, and verification.

---

## 2. Logic Chain

1. **Rubric Component 1: Metadata extraction and evidence documentation (25 pts)**:
   - *Observation Reference*: Observation 2 (hash baseline) and Observation 4 (Master Evidence Table & Case Write-ups).
   - *Deduction*: All six suspect images (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`) were inspected across EXIF, PNG text chunks, and XMP. The 6-row master table contains all seven contractual columns, raw byte/string values, tag IDs, decoding procedures, and forensic interpretations. The per-image case write-ups provide exhaustive technical detail, meeting the highest standard for full credit (25/25).

2. **Rubric Component 2: Covert-channel detection and decoding (25 pts)**:
   - *Observation Reference*: Observation 3 (scanner output) and Observation 4 (Section 4 payload analysis).
   - *Deduction*: All six hidden fragments were recovered accurately. The specific decoding mechanisms required—stripping the 8-byte ASCII prefix (`ASCII\x00\x00\x00`) from EXIF tag 37510 in `Activation.png`, RFC 4648 Base64 decoding in `Music.png`, and XML ElementTree parsing of `<exif:MakerNote>` with leading BOM (`\ufeff`) stripping in `Dopamine.png`—are thoroughly analyzed, documented, and demonstrated with working code. Meets full-credit expectations (25/25).

3. **Rubric Component 3: Six-stage secret reconstruction (20 pts)**:
   - *Observation Reference*: Observation 4 (Section 5 narrative and Table 2 framework mapping).
   - *Deduction*: The six recovered messages are sequenced in logical cyber incident lifecycle order:
     1. Stage 1: `RECON` (`Brain.png`)
     2. Stage 2: `VULN` (`Activation.png`)
     3. Stage 3: `EXPLOIT` (`Chemicals.png`)
     4. Stage 4: `PERSIST` (`Dopamine.png`)
     5. Stage 5: `LATERAL` (`Brain-Channel.png`)
     6. Stage 6: `EXFIL` (`Music.png`)
     The sequence is justified via the Lockheed Martin Cyber Kill Chain and MITRE ATT&CK Enterprise Matrix. Furthermore, Section 5.3 rigorously refutes the alphabetical filename decoy by explaining causal dependency and network topology constraints (e.g., Domain Controllers reside internally and cannot be compromised prior to external gateway exploitation and persistence). Meets full-credit expectations (20/20).

4. **Rubric Component 4: Automated metadata scanner & CSV report (20 pts)**:
   - *Observation Reference*: Observation 3 (successful execution and CSV output) and Observation 4 (Section 6 architecture and scoring model).
   - *Deduction*: `metadata_scanner.py` is an independent, non-trivial, modular utility that iterates through all six images, inspects multi-layer metadata, detects covert indicators, computes explainable risk scores (10 to 15), and exports `metadata_report.csv` conforming to the 7-column schema. Table 3 verbatim reproduces the CSV output with individual score rationales. Meets full-credit expectations (20/20).

5. **Rubric Component 5: Interpretations, reflections, code quality, presentation (10 pts)**:
   - *Observation Reference*: Observation 4 (Sections 7, 8, 9) and Observation 5 (`Lab6_Instructions.md`).
   - *Deduction*: All five reflection questions from `Lab6.ipynb` are answered verbatim with extensive forensic depth. Limitations of EXIF-only tools (4 distinct factors) and heuristic risk scoring (5 distinct factors) are analyzed in detail. All required textbook chapters (Ortega 2021 Ch. 13 & 14; Sarwar 2021 Ch. 1, 3, 6, 8) and forensic standards are properly cited. Meets full-credit expectations (10/10).

6. **Integrity & Anti-Cheat Inspection**:
   - *Observation Reference*: Observations 1, 2, 3, 4, 5.
   - *Deduction*:
     - No hardcoded test results embedded in source code: `metadata_scanner.py` parses live image files dynamically using Pillow and XML parsing.
     - No dummy or facade implementations: The scanner is 542 lines of genuine, cross-platform Python with CLI arguments and robust error handling.
     - No shortcuts or external delegation: All analysis is self-contained.
     - No fabricated outputs: All cryptographic hashes, byte sizes, GPS coordinates, and recovered texts were independently reproduced and verified against ground-truth files.
     - Notebook immutability preserved: `Lab6.ipynb` has a verified SHA-256 match.

---

## 3. Caveats

- **Lab Scope**: The scope of investigation was focused on the six PNG images provided in `Lab6/Images/`. Trailing slack space after the PNG `IEND` chunk and LSB pixel steganography were evaluated theoretically as potential limitations of metadata scanners, but no covert pixel steganography payloads were present in the provided image corpus (the investigation correctly targeted metadata channels as designed).
- **No caveats that invalidate or limit the approval verdict.**

---

## 4. Conclusion

**Verdict: APPROVE**

The work product in `Lab6/` strictly and comprehensively satisfies 100% of the grading rubric (100/100 points) from `Lab6.ipynb` and all requirements specified in `ORIGINAL_REQUEST.md`:
- `Lab6/Lab6.ipynb` was NOT modified (SHA-256: `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`).
- `Lab6/Lab6_Report.md` is an outstanding, professional-grade forensic investigation report covering all evidence tables, per-image write-ups, payload decodings, incident kill chain sequencing, decoy refutations, automated scanner results, limitations, reflection questions, and academic citations.
- `Lab6/metadata_scanner.py` is a robust, production-grade CLI utility that executes cleanly and produces `Lab6/metadata_report.csv`.
- `Lab6/Lab6_Instructions.md` provides clear, reproducible, step-by-step instructions.
- Zero integrity violations were detected.

---

## 5. Verification Method

To independently verify this evaluation, execute the following commands in the workspace:

1. **Verify `Lab6.ipynb` Immutability**:
   ```powershell
   Get-FileHash -Algorithm SHA256 "Lab6\Lab6.ipynb"
   # Expected Hash: 86D9886A845CD328DFF590E47B391C5507A545FE05C230292492289073218ED9
   ```

2. **Verify Image File Integrity**:
   ```powershell
   Get-ChildItem "Lab6\Images\*.png" | ForEach-Object { [PSCustomObject]@{ Name=$_.Name; Hash=(Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLower() } } | Format-Table -AutoSize
   ```

3. **Execute Automated Scanner & Validate Output**:
   ```powershell
   python "Lab6\metadata_scanner.py" -i "Lab6\Images" -o "Lab6\metadata_report.csv" --verbose
   Get-Content "Lab6\metadata_report.csv"
   ```

4. **Inspect Forensic Report & Instruction Files**:
   ```powershell
   Get-Item "Lab6\Lab6_Report.md", "Lab6\Lab6_Instructions.md" | Select-Object Name, Length
   ```

**Invalidation Conditions**:
- Any change to `Lab6/Lab6.ipynb` that alters its SHA-256 hash.
- Any discrepancy between the CSV generated by `metadata_scanner.py` and Table 3 in `Lab6_Report.md`.
