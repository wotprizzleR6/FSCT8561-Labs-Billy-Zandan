# Project: Lab 6 — Covert Channels in Image Metadata

## Architecture
This project investigates, extracts, decodes, automates detection of, and documents covert channels embedded in digital image metadata across EXIF (0th IFD and Exif Sub-IFD), PNG native text chunks (`tEXt`/`zTXt`/`iTXt`), and XMP XML packets.

The system consists of:
1. **Extraction & Decoding Engine (`metadata_scanner.py` / standalone modules)**: Multi-layer pure-Python metadata extractor utilizing `PIL.Image`, `PIL.ExifTags`, `xml.etree.ElementTree` / `defusedxml`, and `base64`.
2. **Automated Risk Scoring & CSV Generation**: Evaluates detected fields using regex heuristics, Base64 entropy detection, and anomalous metadata presence, producing `Lab6/metadata_report.csv` adhering to the exact 7-column schema.
3. **Jupyter Notebook (`Lab6/Lab6.ipynb`)**: Executed in place using Anaconda `jupyter nbconvert --execute --inplace` with all 42 cells populated, code outputs preserved, analytical observations detailed, and reflection questions answered.
4. **Comprehensive Word Report (`Lab6/Lab6_Report.docx`)**: Authored via `python-docx` for student Billy Zandan (A01371854), fulfilling all 100 points of the Lab 6 grading rubric.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Forensic Hash & Image Identification | Record SHA-256 and MD5 hashes, dimensions, file size for all 6 images | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Multi-Channel Metadata Extraction | Extract EXIF 0th IFD, EXIF Sub-IFD (UserComment), PNG text chunks, and XMP packets | M1 | ORIGINAL_REQUEST §R1 |
| 3 | Payload Decoding & De-obfuscation | Strip ASCII/null headers, decode Base64 strings, sanitize payloads | M1 | ORIGINAL_REQUEST §R1 |
| 4 | Attack Narrative Secret Reconstruction | Reconstruct 6-stage Cyber Kill Chain sequence with chronological justification | M1 | ORIGINAL_REQUEST §R1 |
| 5 | Automated Scanner Implementation | Implement `metadata_scanner.py` with multi-format inspection and heuristic scoring | M2 | ORIGINAL_REQUEST §R2 |
| 6 | CSV Report Generation | Generate `Lab6/metadata_report.csv` with required 7 columns and explainable risk scores | M2 | ORIGINAL_REQUEST §R2 |
| 7 | Notebook Cell Population | Fill all analytical observations and reflection responses in `Lab6.ipynb` | M2 | ORIGINAL_REQUEST §R3 |
| 8 | Headless In-Place Notebook Execution | Execute `Lab6.ipynb` via `jupyter nbconvert` ensuring zero runtime errors | M2 | ORIGINAL_REQUEST §R3 |
| 9 | Word Document Report Creation | Generate `Lab6/Lab6_Report.docx` with professional formatting, rubric compliance | M3 | ORIGINAL_REQUEST §R4 |
| 10 | Limitation Analyses & Reflections | Detailed analysis of EXIF-only limitations, automated scoring limits, and 5 reflections | M3 | ORIGINAL_REQUEST §R4 |
| 11 | End-to-End Quality & Forensic Integrity | Independent review, test validation, and forensic integrity audit | M4 | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Metadata Extraction & Narrative Reconstruction | Verify extraction scripts, decode all 6 images, document evidence table & narrative sequence | Survey | DONE |
| M2 | Technical Implementation: Scanner, CSV & Notebook | Implement `metadata_scanner.py`, generate `metadata_report.csv`, update & execute `Lab6.ipynb` in place | M1 | IN_PROGRESS |
| M3 | Report Generation: Word Document Deliverable | Author comprehensive `Lab6_Report.docx` via `generate_report.py` adhering to 100-pt rubric | M2 | PLANNED |
| M4 | Final Quality Verification & Forensic Integrity Audit | Multi-agent review, challenger validation, and forensic integrity audit | M3 | PLANNED |

## Interface Contracts
### `metadata_scanner.py` -> `metadata_report.csv`
- Output path: `Lab6/metadata_report.csv`
- Columns: `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`
- Required rows: Exactly 6 rows corresponding to `Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`.
- Risk scores: 10 or 15, supported by transparent reasoning.

### `Lab6.ipynb` Execution Contract
- Headless execution runner: `C:\Users\BillyZ\anaconda3\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace Lab6.ipynb`
- Execution working directory: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6`
- Zero errors: Every code cell executes with exit code 0, outputs written into notebook JSON.

### Report Generation Contract
- Generator script: `Lab6/generate_report.py` (executed via Python 3.14 `python.exe`)
- Output path: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6_Report.docx`
- Author: Billy Zandan (A01371854), Course: FSCT 8561
- Sections: Title Page/Executive Summary, Evidence Table, Covert Metadata Extraction Deep Dive, Narrative Reconstruction & Cyber Kill Chain, Automated Metadata Scanner & CSV Analysis, Technical Limitations & Countermeasures, Analytical Reflection Questions, Appendices.

## Code Layout
- `Lab6/Images/`: Source image corpus (6 PNG files)
- `Lab6/Lab6.ipynb`: Primary student laboratory notebook
- `Lab6/metadata_scanner.py`: Standalone automated metadata scanner script
- `Lab6/metadata_report.csv`: Automated scanner output CSV
- `Lab6/generate_report.py`: Programmatic Word report builder
- `Lab6/Lab6_Report.docx`: Final Word document deliverable
