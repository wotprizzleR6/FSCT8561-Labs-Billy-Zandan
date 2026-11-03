## 2026-11-02T20:35:54Z
Read c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\ORIGINAL_REQUEST.md before doing anything else.
Also read:
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\orchestrator_1\PROJECT.md
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_1\analysis.md
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_1\handoff.md
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_2\analysis.md
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3\handoff.md

Your working directory is c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\worker_m2_1.
Your role: Core Implementation Specialist.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File write ownership: You have EXCLUSIVE write ownership for:
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb

Tasks:
1. Implement `Lab6/metadata_scanner.py`:
   - Standalone, robust, pure-Python automated metadata scanner.
   - Handles EXIF 0th IFD, EXIF Sub-IFD (IFD 34665 UserComment), native PNG text chunks (`img.info`), and XMP XML packets (`XML:com.adobe.xmp`).
   - Implements the 3-tier risk scoring model (+10 confirmed covert message with stage keywords/prefixes, +5 suspicious encoding such as Base64, +5 anomalous metadata structure such as camera/GPS in synthetic image or MakerNote in XMP).
   - Generates `Lab6/metadata_report.csv` with exactly 7 columns: `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`.
   - Execute it and verify the CSV output.
2. Update `Lab6/Lab6.ipynb`:
   - Preserve all cell indices (0 to 41).
   - Set student author to Billy Zandan (Student Number: A01371854).
   - Populate all analytical observation markdown cells (Cells 6, 10, 14, 17).
   - Implement code in practice cells (Cells 8, 12, 15, 19).
   - Implement extraction code in Section 5 cells (Cells 22, 24, 26, 28, 30, 32) so each outputs the image metadata and recovered payload cleanly.
   - Complete Cell 33 with the full 6-stage narrative secret and comprehensive Cyber Kill Chain / MITRE ATT&CK chronological justification.
   - Implement automated scanner starter cells (35, 37) and scanner execution cell (39), generating `metadata_report.csv`.
   - Answer all 5 reflection questions in Cell 40 thoroughly with deep, technical paragraphs covering defensive controls, protocol steganography, file format specs, automated triage pipelines, and enterprise sanitization policies.
3. Headless In-Place Execution of `Lab6.ipynb`:
   - From working directory `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6`, execute:
     `C:\Users\BillyZ\anaconda3\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace Lab6.ipynb`
   - Verify that execution completes with return code 0 and all cell outputs are populated in the notebook file.
4. Document all changes in `changes.md` and author a complete, self-contained `handoff.md` in your working directory.
When complete, send a message to caller with summary and path to handoff.md.
