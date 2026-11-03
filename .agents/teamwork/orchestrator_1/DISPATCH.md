# Dispatch Log

## 2026-11-02T20:27:27Z

Complete all tasks in Lab 6 (Covert Channels in Image Metadata) using `Lab6.ipynb` and its grading rubric, executing and updating the notebook in place and producing a comprehensive report in `Lab6/Lab6_Report.docx`.

Working directory: c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6
Integrity mode: development

## Requirements

### R1. Metadata Extraction and Narrative Secret Reconstruction
Extract covert metadata (across EXIF, PNG text, and XMP) from all six images in `Images/`, decode all obfuscated/encoded message fragments, and reconstruct the full six-stage incident narrative secret in the correct sequence with a logical justification.

### R2. Automated Metadata Scanner and CSV Report
Implement an automated metadata scanner (`metadata_scanner.py` or within the notebook) that iterates across all images, inspects relevant metadata fields, assigns consistent and explainable risk scores with reasons, and generates `metadata_report.csv`.

### R3. Notebook Execution and Completion
Update and execute `Lab6.ipynb` in place with all code cells working, outputs displayed, and all analytical and reflection questions answered thoroughly.

### R4. Word Document Report Generation
Compile and format all deliverables into a new Word document saved at `Lab6/Lab6_Report.docx`, addressing all components in the Lab 6 grading rubric: evidence table for all six images, extraction output evidence, reconstructed six-stage secret narrative, scanner code and `metadata_report.csv` results table, limitation explanations (EXIF-only and automated risk scoring), and comprehensive answers to the reflection questions.

## Acceptance Criteria

### Metadata Extraction & Reconstruction
- [ ] Evidence for all six images is documented with metadata type, field name, raw value, decoding method, and recovered message fragment.
- [ ] The complete six-stage secret is reconstructed in the correct sequence with narrative justification.

### Automated Scanner & CSV Output
- [ ] An automated scanner runs across all six images and produces `metadata_report.csv`.
- [ ] `metadata_report.csv` contains rows for all six images with columns: `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, and `reason`.

### Notebook Deliverable
- [ ] `Lab6.ipynb` is updated and executed with no errors, displaying all relevant outputs and answers.

### Word Document Deliverable
- [ ] `Lab6/Lab6_Report.docx` is created and readable as a valid Word document.
- [ ] `Lab6/Lab6_Report.docx` includes the evidence table, extraction outputs, reconstructed secret, scanner implementation and CSV table, interpretation of limitations, and answers to all reflection questions from `Lab6.ipynb`.

===
Working directory: c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\orchestrator_1
Original request file: c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\ORIGINAL_REQUEST.md
Your identity: Project Orchestrator (teamwork_orchestrator)
Caller ID: d00707a2-8bbe-4423-9e2f-54433c72c93d
