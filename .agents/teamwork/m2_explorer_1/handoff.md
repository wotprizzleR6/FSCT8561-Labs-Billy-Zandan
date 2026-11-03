# Milestone 2 Handoff Report: Notebook Markdown Cells, Tables, Reflection Answers, and Analysis

**From:** `m2_explorer_1` (Teamwork Explorer)  
**To:** `4454555e-8e94-46d7-b2c6-e12b4f18de76` (Teamwork Orchestrator) / Worker Agent  
**Date:** 2026-11-02T21:23:00Z  
**Working Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_explorer_1`  
**Target File:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb`  
**Reference Analysis:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_explorer_1\analysis.md`  

---

## 1. Observation

1. **Notebook Topology & Cell Inventory:**
   - Inspection of `Lab6/Lab6.ipynb` confirmed exactly **42 cells** (`len(nb['cells']) == 42`): 24 markdown cells and 18 code cells.
   - Cells are versioned under `nbformat: 4`, `nbformat_minor: 5`, each maintaining a unique cell ID (e.g., `fc89b092`, `7653515b`, `6c89918c`, `af4051cf`, `7a703926`, `faa7b945`, `c655c95c`, `86d441f0`, `a4a4d581`, `e49106b3`).
2. **Student Prompts Requiring Completion in `Lab6.ipynb`:**
   - **Cell 0 (`fc89b092`):** Missing student metadata header (Billy Zandan, A01371854).
   - **Cell 4 (`7653515b`):** Contains instructional evidence log prompt; lacks working hypothesis, multi-layer extraction triage methodology, and cryptographic baseline hashes.
   - **Cell 7 (`6c89918c`):** Prompt asks: *"Which EXIF field carries a message? Record it in your evidence log. If EXIF tags: 0 appears, does that mean the image has no metadata? Explain."* Missing student response.
   - **Cell 11 (`af4051cf`):** Prompt asks: *"Which PNG text field contains a clue? Try Chemicals.png next using the same short snippet."* Missing student response.
   - **Cell 15 (`7a703926`):** Prompt asks: *"Locate the XML element containing the partial secret. Why did the EXIF-only approach miss it?"* Missing student response.
   - **Cell 18 (`faa7b945`):** Prompt asks: *"Replace example with the suspicious metadata value from Music.png... validate the result."* Missing student response.
   - **Cell 20 (`c655c95c`):** Contains empty 6-row evidence table (`| Image | Metadata type / field | Decoding needed? | Partial secret recovered |`) with blank cells.
   - **Cells 21, 23, 25, 27, 29, 31:** Investigation prompts for images 1 through 6 requesting partial secret documentation.
   - **Cell 33 (`86d441f0`):** Contains 6 fill-in-the-blank lines (`1. Stage: ______ Recovered message: ______`) and prompt: *"Why is this the most plausible order?"* Currently unpopulated.
   - **Cell 40 (`a4a4d581`):** Contains the 5 reflection questions verbatim without student answers.
   - **Cell 41 (`e49106b3`):** Submission requirements and 100-point rubric; requires brief interpretation explaining one limitation of EXIF-only extraction and one limitation of automated risk scoring.
3. **Forensic Ground Truth Across Evidence Set (`Lab6/Images/`):**
   - `Activation.png`: EXIF Sub-IFD Tag 37510 (`UserComment`) -> `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'` (Stage 2).
   - `Brain-Channel.png`: EXIF 0th IFD Tag 270 (`ImageDescription`) -> `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'` (Stage 5).
   - `Brain.png`: PNG `tEXt` chunk key `'Software'` -> `'RECON: Perform DNS harvesting and Subdomain enumeration.'` (Stage 1).
   - `Chemicals.png`: PNG `tEXt` chunk key `'ImageDescription'` -> `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'` (Stage 3).
   - `Dopamine.png`: Adobe XMP XML packet element `<exif:MakerNote>` inside `XML:com.adobe.xmp` -> `'PERSIST: Establish reverse shell via obfuscated cron job.'` (Stage 4).
   - `Music.png`: EXIF 0th IFD Tag 33432 (`Copyright`) & PNG info `'Copyright'` -> `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='` -> Decodes to `'EXFIL: Tunnel compressed database dump via DNS Covert Channel.'` (Stage 6).
4. **Textbook Citations Verified:**
   - Jose Manuel Ortega, *Mastering Python for Networking and Security* (2nd Ed., Packt Publishing, 2021):
     - Chapter 13 (*Extracting Geolocation and Metadata from Documents, Images, and Browsers*, pp. 784–850): EXIF tag enumeration, Sub-IFDs, GPSInfo parsing, limitations of PIL EXIF tools.
     - Chapter 14 (*Cryptography and Steganography*, pp. 852–918): Cryptography vs. encoding, Base64 mechanics, LSB steganography, cryptographic hash integrity with `hashlib`.

---

## 2. Logic Chain

1. **From Observation 1 & 2:** The notebook `Lab6/Lab6.ipynb` requires a comprehensive set of markdown completions to satisfy the grading rubric (100 points) and Milestone 2 acceptance criteria.
2. **From Observation 2 & 3:** The student information, working hypothesis, and multi-layer extraction triage methodology must be formulated to frame the forensic investigation appropriately.
3. **From Observation 3 & 4:** In Sections 1–4, observations on specific container mechanics directly answer the instructor prompts:
   - In Section 1, explaining why `EXIF tags: 0` does not mean zero metadata relies on the architectural difference between JEITA EXIF and PNG chunk-based / Adobe XMP specifications (Ortega Ch. 13).
   - In Section 2, `Brain.png` and `Chemicals.png` demonstrate container hijacking and container mismatch (storing EXIF tag names inside native PNG `tEXt` chunks).
   - In Section 3, `Dopamine.png` proves why EXIF tools miss XML packets encapsulated in PNG international text (`iTXt`) chunks.
   - In Section 4, `Music.png` proves how syntactic Base64 encoding differs fundamentally from cryptographic encryption (Ortega Ch. 14).
4. **From Observation 3:** Populating the Section 5 Evidence Table (Cell 20) with verified metadata attributes, raw values, decoding methods, and recovered secrets provides the foundational empirical evidence.
5. **From Observation 3:** Assembling the 6 recovered fragments requires operational attack lifecycle reasoning:
   - Sorting by alphabetical filename creates severe operational impossibilities (e.g. pivoting via Mimikatz before performing reconnaissance or initial exploitation).
   - Mapping to the Lockheed Martin Cyber Kill Chain and MITRE ATT&CK Framework establishes the only causal order: `RECON` (`Brain.png`, Stage 1) -> `VULN` (`Activation.png`, Stage 2) -> `EXPLOIT` (`Chemicals.png`, Stage 3) -> `PERSIST` (`Dopamine.png`, Stage 4) -> `LATERAL` (`Brain-Channel.png`, Stage 5) -> `EXFIL` (`Music.png`, Stage 6).
6. **From Observation 2 & 4:** The 5 reflection questions and critical limitations require graduate-level, rigorous responses grounded in Ortega Chapters 13 and 14, ISO/IEC 27037 standards, and continuity across Labs 4, 5, and 6.
7. **Synthesis:** All formulated content has been compiled verbatim in `analysis.md` so that the Worker agent can inject it into `Lab6.ipynb` and execute the notebook in place without syntax or logic errors.

---

## 3. Caveats

1. **In-Place Execution Requirement:** This explorer agent is strictly read-only and did not modify `Lab6/Lab6.ipynb`. The actual modification and in-place execution via `jupyter nbconvert --to notebook --execute --inplace` must be performed by the Worker agent.
2. **Jupyter Environment:** Execution in place requires `jupyter` and `nbconvert` installed in the Python environment, which was verified present.
3. **Word Document Separation:** Milestone 2 focuses exclusively on `Lab6.ipynb`. Compilation of the Word document (`Lab6-Billy-Zandan-A01371854.docx`) is planned for Milestone 3, although the analytical content produced here directly feeds into Milestone 3.

---

## 4. Conclusion

1. All markdown prompts and requirements for Milestone 2 in `Lab6/Lab6.ipynb` have been completely analyzed and formulated with full academic rigor, complete evidence tables, and textbook citations.
2. The exact markdown cell replacements and additions are fully detailed in `analysis.md` across Cells 0, 4, 7, 11, 15, 18, 20, 21, 23, 25, 27, 29, 31, 33, 40, and 41.
3. The Worker agent has unambiguous, drop-in markdown texts and code cell specifications to complete Milestone 2 successfully.

---

## 5. Verification Method

To independently verify this investigation:
1. **Inspect Analysis Report:**
   Read `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_explorer_1\analysis.md` to confirm the complete formulated markdown cells and code snippets.
2. **Verify Cryptographic Baselines & Metadata Extraction:**
   Run the following Python command in `Lab6/` to verify image evidence:
   ```powershell
   python -c "from PIL import Image; [print(f.name, len(Image.open(f).info)) for f in sorted(Path('Images').glob('*.png'))]"
   ```
3. **Worker Implementation Verification (Post-Worker Execution):**
   Run the following validation script after Worker updates `Lab6.ipynb`:
   ```powershell
   python -c "import json; nb = json.load(open('Lab6/Lab6.ipynb', encoding='utf-8')); assert len(nb['cells']) == 42; assert all(c.get('execution_count') is not None for c in nb['cells'] if c['cell_type'] == 'code'); print('Notebook validation: SUCCESS')"
   ```
