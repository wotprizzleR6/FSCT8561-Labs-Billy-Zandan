# Original User Request

## Approved Task Prompt — 2026-11-02T23:09:20Z

Complete Lab 6 on covert channels in image metadata by answering all questions and meeting the grading rubric from Lab6.ipynb, using code examples from Lab6.ipynb and the two textbooks in the Lab6 folder, without modifying Lab6.ipynb.

Working directory: c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6
Integrity mode: development

## Reference Material
- Lab notebook and grading rubric: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb`
- Textbook 1: `Mastering Python for Networking and Security - Second` (present in `Lab6/` and `Lab3/`)
- Textbook 2: `Python Ethical Hacking From Scratch _ Think Like an Ethical` (present in `Lab6/` and `Lab3/`)
- Metadata scanner script: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py`

## Requirements

### R1. Complete Lab Answers and Evidence Report (`Lab6_Report.md`)
Perform metadata forensic extraction across all six images in `Images/` (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`) across EXIF, PNG text, and XMP metadata formats using relevant code examples from `Lab6.ipynb` and the referenced textbooks. Record the metadata type, field name, raw value, decoding method, recovered fragment, and interpretation for each image. Decode all encoded fragments and reconstruct the complete six-stage secret in logical incident narrative order with justification. Answer all reflection questions and address all 100-point rubric components in `Lab6_Report.md`. Do not modify or put results into `Lab6.ipynb`.

### R2. Lab Completion Instructions Guide (`Lab6_Instructions.md`)
Create a new Markdown file (`Lab6_Instructions.md`) containing clear, step-by-step instructions on how to complete Lab 6. Explain the environment setup, metadata extraction techniques (EXIF, PNG text, XMP), decoding procedures (Base64), narrative sequencing rationale, scanner execution, and verification steps.

### R3. Automated Metadata Scanner Execution and CSV Report
Execute `metadata_scanner.py` against the six images in `Images/` to generate `metadata_report.csv` with complete columns (`filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`). Include the generated CSV results table and a discussion of risk scoring and limitations in `Lab6_Report.md`.

## Acceptance Criteria

### Preservation and Structure
- [ ] `Lab6.ipynb` is unmodified.
- [ ] Two new Markdown files are created in `Lab6/`: `Lab6_Report.md` and `Lab6_Instructions.md`.

### Metadata Extraction and Forensic Evidence
- [ ] `Lab6_Report.md` contains an evidence table covering all six images (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`).
- [ ] For every image, the specific metadata type (EXIF / PNG text / XMP), tag or key name, raw value excerpt, decoding method, recovered fragment, and forensic interpretation are documented.
- [ ] All six partial secrets are recovered accurately, with all encoded values (such as Base64 in `Music.png`) properly decoded.

### Secret Reconstruction and Incident Narrative
- [ ] The six recovered fragments are assembled into the complete six-stage attack narrative in chronological/logical order.
- [ ] The sequencing rationale is documented and justified using the stage indicators found in the recovered evidence.

### Reflection and Analysis
- [ ] All five reflection questions from `Lab6.ipynb` are answered completely and thoroughly in `Lab6_Report.md`.
- [ ] Limitations of EXIF-only metadata extraction are documented.
- [ ] Limitations of automated risk scoring and heuristic detection are documented.

### Scanner Execution and CSV Report
- [ ] `metadata_scanner.py` executes successfully and generates `Lab6/metadata_report.csv`.
- [ ] `metadata_report.csv` contains header and exactly 6 data rows corresponding to the 6 images.
- [ ] `Lab6_Report.md` includes the full table of scanner results from `metadata_report.csv`.

### Instructional Guide
- [ ] `Lab6_Instructions.md` provides reproducible, step-by-step instructions for completing the lab, covering extraction commands/snippets, decoding, scanner execution, and evidence recording.
