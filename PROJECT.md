# Project: Lab 7 Steganography & LSB Forensics Report Enhancement

## Architecture
- Target Document: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab7\Lab7-Billy-Zandan-A01371854.docx`
- Authoritative Specifications: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab7\Lab7-2.ipynb` (Cell 34 100-mark rubric and 9-item checklist)
- Master Pre-executed Outputs: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab7\Lab7.ipynb` and standalone scripts (`Part0_Code.py` through `Part5_4...py`, `Robustness_Test.py`, `Optional_Extension_RGBA_vs_RGB.py`)
- E2E Test Suite: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab7\test_submission_guide.py`
- Manipulation Engine: Python `python-docx` 1.2.0 script executing clean in-place OpenXML document transforms.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Student Metadata Header | Student Name (Billy Zandan), ID (A01371854), Course (FSCT 8561), Institution (BCIT), Title | M1 | Survey 3 / Rubric |
| 2 | 100-Mark Rubric Table | Table documenting all 6 rubric categories and 100-mark allocation | M1 | Cell 34 / Survey 1 |
| 3 | 9-Item Submission Checklist Matrix | Structured checklist table with item number, requirement, verification evidence, and status | M1 | Cell 34 / Survey 1 |
| 4 | Figure Callouts & Numbering | Explicit Figure 1 to Figure 19 labels with notebook cell and script citations | M1 | Survey 3 / R1 |
| 5 | Exact Python Code Blocks | Verbatim Python code blocks for each of the 19 figures | M1 | Survey 2 / R1 |
| 6 | Verbatim Terminal Outputs | Exact stdout streams, hashes, and assertion results matching figures | M1 | Survey 2 / R1 |
| 7 | Explicit Output Explanations | Detailed narrative explaining what each screenshot proves (zero unexplained screenshots) | M1 | Survey 3 / R1 |
| 8 | Part 1 Value 201 Analysis | Value 201 LSB manipulation, assertions, max variance explanation (Δ ∈ {0, ±1}, ≤ 0.39%) | M1 | Survey 1 / Cell 8 |
| 9 | Part 2 Capacity & Errata | Capacity formulas (4,999 B vs 3,749 B) and correction of 10-pixel PDF errata (40 vs 42 px) | M1 | Survey 1 / Cell 12 |
| 10 | Part 3 Manual Stego Analysis | 5 architectural questions, 4 defensive encoder checks, clean-room payload recovery | M1 | Survey 1 / Cells 14-18 |
| 11 | Part 4 Stepic Stego Analysis | Stepic payload `"80,443,3478,5060"`, RGB conversion requirement, verification rationale | M1 | Survey 1 / Cells 20-22 |
| 12 | Part 5 Differencing & Forensics | Logo: 39 px (0.003719%), Profile: 43 px (0.003977%), SHA-256 digests, extraction immutability | M1 | Survey 1 / Cells 24-30 |
| 13 | Robustness Test Documentation | Test 1: Lossy JPEG DCT quantization destroys LSBs; Test 2: Spatial bilinear downscaling destroys LSBs | M1 | Survey 1 / Checklist 7 |
| 14 | Optional Extension Analysis | RGBA vs RGB tradeoffs: 25% capacity reduction vs zero alpha bitplane degradation | M1 | Survey 1 / Rubric |
| 15 | Part 6 Security Reflection | 250–350-word essay strictly covering all 7 required prompts with forensic rigor | M1 | Survey 1 / Cell 34 |
| 16 | Direct In-Place Modification | Apply all updates directly to `Lab7/Lab7-Billy-Zandan-A01371854.docx` preserving clean formatting | M1 | R2 / Acceptance Criteria |
| 17 | E2E Automated Test Suite Pass | 100% pass on `test_submission_guide.py` verifying all structural and rubric criteria | M2 | Acceptance Criteria |
| 18 | Multi-Reviewer Approval | Independent Reviewers confirm report quality, explanations, and rubric compliance | M2 | Acceptance Criteria |
| 19 | Adversarial Challenger Check | Empirical verification of docx structure, paragraph flow, images, and tables | M2 | Acceptance Criteria |
| 20 | Forensic Auditor Integrity Check | Verify zero hardcoding of phony outputs, genuine OpenXML document structure | M2 | Hard Constraints |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | In-Place DOCX Enhancement | Features 1–16: Update `Lab7-Billy-Zandan-A01371854.docx` in-place with metadata, rubric & checklist tables, callouts, exact code, verbatim outputs, and explicit explanations for all 19 figures | none | DONE |
| 2 | Verification, Adversarial Hardening & Forensic Audit | Features 17–20: Execute `test_submission_guide.py`, dispatch 2 Reviewers, 2 Challengers, and 1 Forensic Auditor | M1 | DONE |

## Interface Contracts
### Worker ↔ Target Document
- Target File: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab7\Lab7-Billy-Zandan-A01371854.docx`
- Modification Method: In-place edit via `python-docx`
- Preserved Elements: All 19 embedded images (`image1.png` - `image19.png`), existing high-quality student answers (Check-in 0, Part 1, Part 2, Part 3A, Part 4B, Part 5A, Part 6 essay).
- Added Elements: Student metadata header, 100-mark rubric table, 9-item checklist table, 19 callout headers, 19 exact code listings, 19 output blocks, 19 explicit explanations, Robustness test analysis, Optional extension analysis.

## Code Layout
- `Lab7/Lab7-Billy-Zandan-A01371854.docx`: Target deliverable document.
- `Lab7/Lab7-2.ipynb`: Authoritative starter notebook with rubric and checklist (READ-ONLY, NO EXECUTION).
- `Lab7/Lab7.ipynb`: Master pre-executed notebook with verbatim stdout streams (READ-ONLY).
- `Lab7/test_submission_guide.py`: E2E automated test suite.
- `Lab7/Lab8_outputs/`: Image assets and steganographic outputs.
- `.agents/teamwork/`: Metadata, plans, progress, and reports (NO SOURCE CODE).
