# Comprehensive Review & Adversarial Challenge Report: Lab 6 Instructions

**Reviewer & Adversarial Critic**: gate_reviewer_2  
**Date**: November 2, 2026  
**Subject**: Evaluation of `Lab6/Lab6_Instructions.md` and Verification of `Lab6/Lab6.ipynb` Integrity  
**Verdict**: **APPROVE**  
**Overall Risk Assessment**: **LOW**

---

## 1. Observation

Direct evidentiary observations obtained via independent file inspection, hashing, and command execution:

### 1.1 Notebook Immutability & Integrity Check
- **Target File**: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb`
- **Expected SHA-256 Hash**: `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`
- **Executed Command**:
  ```powershell
  Get-FileHash -Algorithm SHA256 Lab6\Lab6.ipynb | Select-Object -ExpandProperty Hash
  ```
- **Verbatim Output**:
  `86D9886A845CD328DFF590E47B391C5507A545FE05C230292492289073218ED9`
- **Observation Result**: Match is exact. `Lab6.ipynb` has not been modified.

### 1.2 Verification of Target Document Structure & Scope
- **Target File**: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6_Instructions.md` (426 lines, 21,831 bytes)
- **Content Structure Verified**:
  - **Section 1 (lines 10–54)**: Objective & Prerequisites (Learning outcomes, Python 3.8+ dependencies, directory layout, and non-execution directive).
  - **Section 2 (lines 56–109)**: Step 1: Environment Setup & Cryptographic Baselines (Virtual environment, `pip install Pillow defusedxml`, SHA-256 verification table and Python script).
  - **Section 3 (lines 111–178)**: Step 2: EXIF Metadata Extraction (`img.getexif()` on `Brain-Channel.png` IFD0; Sub-IFD and GPS Sub-IFD navigation on `Activation.png`; stripping `ASCII\x00\x00\x00`).
  - **Section 4 (lines 180–219)**: Step 3: PNG Text Chunk Extraction (`img.info` access on `Brain.png` and `Chemicals.png`; explanation of why EXIF parsers miss native PNG chunks).
  - **Section 5 (lines 221–273)**: Step 4: XMP Packet Extraction & XML Parsing (Adobe XMP in `iTXt` on `Dopamine.png`; Windows UTF-8 BOM `\ufeff` handling; `sys.stdout.reconfigure(encoding='utf-8')`).
  - **Section 6 (lines 275–315)**: Step 5: Base64 Decoding Procedure (Validation criteria: length mod 4 == 0, alphabet regex; decoding `Music.png` `Copyright`; distinction between encoding vs encryption).
  - **Section 7 (lines 317–347)**: Step 6: Narrative Sequencing Rationale & Timeline Construction (Reconstructing 6-stage lifecycle RECON $\to$ VULN $\to$ EXPLOIT $\to$ PERSIST $\to$ LATERAL $\to$ EXFIL; Lockheed Martin Cyber Kill Chain and MITRE ATT&CK mapping; refuting alphabetical artifact decoy).
  - **Section 8 (lines 349–396)**: Step 7: Automated Metadata Scanner Execution (`metadata_scanner.py` architecture; Option A and Option B CLI execution; 7-column CSV schema; explainable risk scoring formula; 4 critical scanner limitations).
  - **Section 9 (lines 398–426)**: Step 8: Forensic Evidence Verification & Submission Checklist (Post-inspection SHA-256 hash matching; notebook immutability; 3 deliverables verification; 100-point rubric compliance checklist).

### 1.3 Independent Execution of Embedded Code Snippets
All code snippets presented in `Lab6_Instructions.md` were independently tested in the environment:
1. **Section 2.2 Baseline Hash Verification**:
   - Python script (lines 88–99) executed successfully.
   - Output matched all 6 expected image SHA-256 hashes and file sizes (`Activation.png` 259,975 B, `Brain-Channel.png` 201,685 B, `Brain.png` 2,354,330 B, `Chemicals.png` 561,245 B, `Dopamine.png` 388,411 B, `Music.png` 679,959 B).
2. **Section 3.1 EXIF IFD0 Extraction**:
   - Snippet (lines 118–130) executed on `Brain-Channel.png`.
   - Output: Tag 270 (`ImageDescription`) = `"LATERAL: Pivot to internal Domain Controller using Mimikatz."`
3. **Section 3.2 Sub-IFD and GPS Extraction**:
   - Snippet (lines 146–171) executed on `Activation.png`.
   - Output: Header `b"ASCII\x00\x00\x00"` stripped; Recovered secret = `"VULN: Identify unpatched CVE-2024-XXXX in web gateway."`; GPS tags extracted: `(40.0, 42.0, 46.08) N, (74.0, 0.0, 21.6) W`.
4. **Section 4.1 PNG Text Extraction**:
   - Snippet (lines 192–206) executed on `Brain.png` and `Chemicals.png`.
   - Output: `len(img.getexif()) == 0`; `Brain.png` `Software` = `"RECON: Perform DNS harvesting and Subdomain enumeration."`; `Chemicals.png` `ImageDescription` = `"EXPLOIT: Deploy SQL Injection payload to bypass WAF."`
5. **Section 5.2 XMP XML Parsing**:
   - Snippet (lines 239–266) executed on `Dopamine.png`.
   - Output: BOM `\ufeff` cleanly handled; `<exif:MakerNote>` parsed = `"PERSIST: Establish reverse shell via obfuscated cron job."`
6. **Section 6.2 Base64 Decoding**:
   - Snippet (lines 288–304) executed on `Music.png`.
   - Output: Base64 string decoded to `"EXFIL: Tunnel compressed database dump via DNS Covert Channel."`
7. **Section 8.2 Scanner CLI Execution**:
   - Option A (`python Lab6\metadata_scanner.py -i Lab6\Images -o Lab6\metadata_report.csv -v`) and Option B (`python metadata_scanner.py -v`) executed with zero errors, generating the exact 7-column CSV `Lab6/metadata_report.csv` with 6 rows.

---

## 2. Logic Chain

1. **Premise 1 (Requirement Verification)**:
   The mandate specified checking that `Lab6_Instructions.md` provides complete, step-by-step reproducible instructions covering environment setup, dependencies, EXIF metadata extraction, PNG text chunk extraction, XMP packet parsing (including Windows UTF-8 BOM `\ufeff` handling), Base64 decoding, narrative sequencing rationale, scanner execution, and verification steps.
   - *Observation Connection*: Observations in Section 1.2 and 1.3 show that Sections 1 through 9 of `Lab6_Instructions.md` address all nine required topics systematically, leaving no gaps.

2. **Premise 2 (Reproducibility & Code Snippet Correctness)**:
   Any instructional guide must contain functional, bug-free code snippets that execute cleanly in the designated execution environment.
   - *Observation Connection*: Every code snippet in `Lab6_Instructions.md` was executed verbatim via Python 3.14. Each snippet completed with exit code 0 and produced exact matching outputs. Cross-platform path fallbacks (`Path("Lab6/Images") if Path("Lab6").exists() else Path("Images")`) guarantee that commands succeed whether the user runs from the repository root or within the `Lab6` directory.

3. **Premise 3 (Notebook Preservation)**:
   The user and task constraints strictly forbid modifications to `Lab6.ipynb`.
   - *Observation Connection*: Cryptographic validation (Section 1.1) proves that `Lab6.ipynb` has a SHA-256 hash identical to the baseline reference `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`. No cells, outputs, or metadata were altered.

4. **Premise 4 (Alignment with Coursework & Textbooks)**:
   Instructional techniques must align with the provided lab notebook starter code and textbook references.
   - *Observation Connection*: Snippets directly derive from and expand on `Lab6.ipynb` cells 6, 10, 14, 17, and 37. Metadata extraction methodologies mirror Jose Manuel Ortega's *Mastering Python for Networking and Security* (Chapter 13, pp. 799–804) and Fahad Ali Sarwar's *Python Ethical Hacking From Scratch*.

5. **Premise 5 (Adversarial Robustness & Integrity)**:
   The solution must be free of integrity violations (no hardcoded answers masquerading as dynamic detection, no bypassed tasks, no self-certifying fabrications).
   - *Observation Connection*: `metadata_scanner.py` utilizes heuristic detection rules, dynamically traversing multi-layer containers, extracting strings, stripping headers, and parsing Base64. It does not hardcode detector outputs. `Lab6_Instructions.md` provides clear educational guidance without taking shortcuts.

---

## 3. Quality Review Findings

### Verified Claims
- **Claim**: `Lab6.ipynb` is unmodified.  
  *Verified via*: `Get-FileHash -Algorithm SHA256 Lab6\Lab6.ipynb` $\to$ `86D9886A845CD328DFF590E47B391C5507A545FE05C230292492289073218ED9` [PASS]
- **Claim**: All 6 image hashes match pre- and post-inspection baselines.  
  *Verified via*: Cryptographic comparison of pre/post execution hashes [PASS]
- **Claim**: XMP parsing avoids Windows console encoding crashes.  
  *Verified via*: Executed snippet with UTF-8 stream reconfiguration and BOM stripping on Windows PowerShell [PASS]
- **Claim**: Base64 decoding produces valid ASCII plaintext.  
  *Verified via*: Executed `base64.b64decode` on `Music.png` Copyright string [PASS]
- **Claim**: `metadata_scanner.py` CLI options A and B work as documented.  
  *Verified via*: Executed both commands; generated 7-column `metadata_report.csv` [PASS]

### Coverage Gaps
- None. Every required section and artifact is fully addressed.

### Unverified Items
- None.

---

## 4. Adversarial Challenges & Stress-Test Results

### Challenge 1: Windows Console CP1252 Encoding Crash on XMP BOM
- **Assumption Challenged**: Standard `print()` of extracted XMP packets will succeed on Windows default command prompt/PowerShell sessions.
- **Attack Scenario**: Windows console environments defaulting to code page `cp1252` throw `UnicodeEncodeError: 'charmap' codec can't encode character '\ufeff'` when printing raw strings containing the zero-width non-breaking space (BOM) inserted by ExifTool into XMP headers.
- **Stress-Test**: Tested snippet in Section 5.2 with `sys.stdout.reconfigure(encoding="utf-8")` and `xmp_clean = xmp_raw.lstrip("\ufeff")`.
- **Result**: [PASS] Stream reconfiguration and BOM stripping completely eliminate the encoding crash.

### Challenge 2: Working Directory Ambiguity (Root vs Subfolder Execution)
- **Assumption Challenged**: Users will execute scripts from a single assumed directory.
- **Attack Scenario**: If a student executes from `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan` vs `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6`, hardcoded paths like `Images/Activation.png` or `Lab6/Images/Activation.png` will fail with `FileNotFoundError`.
- **Stress-Test**: Tested all snippets with conditional resolution `Path("Lab6/Images/...") if Path("Lab6").exists() else Path("Images/...")`. Tested `metadata_scanner.py` from root (Option A) and from `Lab6` (Option B).
- **Result**: [PASS] Both execution contexts resolve images and output paths seamlessly.

### Challenge 3: Decoy Traps in Chronological Ordering
- **Assumption Challenged**: Attack phases follow the alphabetical sorting of file names.
- **Attack Scenario**: Alphabetical ordering (`Activation` $\to$ `Brain-Channel` $\to$ `Brain` $\to$ `Chemicals` $\to$ `Dopamine` $\to$ `Music`) yields `VULN` $\to$ `LATERAL` $\to$ `RECON` $\to$ `EXPLOIT` $\to$ `PERSIST` $\to$ `EXFIL`, placing lateral movement before reconnaissance or perimeter breach.
- **Stress-Test**: Evaluated narrative sequencing justification in Section 7.
- **Result**: [PASS] Section 7.3 explicitly identifies and refutes the alphabetical decoy, anchoring the true sequence to the Cyber Kill Chain and MITRE ATT&CK tactics (`RECON` $\to$ `VULN` $\to$ `EXPLOIT` $\to$ `PERSIST` $\to$ `LATERAL` $\to$ `EXFIL`).

---

## 5. Caveats

1. **Pillow Version Specificity**:
   Section 1.2 lists `Pillow >= 9.0.0`. In Pillow, `exif.get_ifd(ExifTags.IFD.Exif)` was officially introduced in version 9.2.0 (July 2022). In any modern Python environment (such as the verified Python 3.14 environment which installs Pillow 12.3.0), this is non-problematic. However, if an investigator attempted execution on an archived Pillow 9.0.0 build, `get_ifd` would be absent. A minor recommendation is to prefer Pillow $\ge$ 9.2.0.
2. **Read-Only Notebook Enforcement**:
   Notebook immutability is maintained via procedural integrity checks. While `Lab6.ipynb` has zero modifications, making the file OS-level read-only (`attrib +r Lab6\Lab6.ipynb`) can provide defense-in-depth against accidental Jupyter autosaves.

---

## 6. Conclusion & Verdict

`Lab6/Lab6_Instructions.md` is an outstanding, professional, and fully reproducible instructional guide that satisfies all grading rubric requirements, assignment specifications, and security standards. It contains complete step-by-step procedures, fully tested Python snippets, robust cross-platform path handling, and rigorous explanations of covert channel mechanics. Cryptographic verification confirms that `Lab6/Lab6.ipynb` remains strictly unmodified (SHA-256: `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`).

**Final Verdict**: **APPROVE**

---

## 7. Verification Method

To independently verify this evaluation, run the following commands in PowerShell from the repository root:

1. **Verify Notebook Immutability**:
   ```powershell
   Get-FileHash -Algorithm SHA256 Lab6\Lab6.ipynb
   # Expected Hash: 86D9886A845CD328DFF590E47B391C5507A545FE05C230292492289073218ED9
   ```

2. **Verify Image File Baselines**:
   ```powershell
   Get-FileHash -Algorithm SHA256 Lab6\Images\*.png | Format-Table -AutoSize
   ```

3. **Verify Scanner CLI Execution**:
   ```powershell
   python Lab6\metadata_scanner.py -i Lab6\Images -o Lab6\metadata_report.csv -v
   Get-Content Lab6\metadata_report.csv
   ```
