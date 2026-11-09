# TEST READY: Automated E2E Test Suite for Lab 7 Submission Guide

**Milestone:** M2 (E2E Testing Track)  
**Test Suite Path:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab7\test_submission_guide.py`  
**Target Deliverable:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab7\Lab7_Submission_Guide.docx`  
**Source Notebook (Read-Only):** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab7\Lab7.ipynb`  
**Test Framework:** Python `unittest` + `python-docx` (OpenXML parsing)  
**Status:** READY FOR VERIFICATION  

---

## 1. Quick Start / Test Runner Commands

Run the full automated E2E test suite with structured summary output:
```bash
python Lab7/test_submission_guide.py
```
Or with verbose standard `unittest` output:
```bash
python -m unittest Lab7/test_submission_guide.py -v
```

---

## 2. Test Architecture & Tier Breakdown (41 Tests)

| Tier | Category | Tests | Target / Description | Pass Criteria |
|---|---|:---:|---|---|
| **Invariant** | Notebook Immutability | 6 | `Lab7.ipynb` strict byte-level preservation | `git status` clean, SHA-256 (`a9d5655f...`), git blob SHA-1 (`c3c39216...`), size (62,369 B), 35 cells & 16 outputs intact |
| **Tier 1** | Document Structure & OpenXML | 5 | Packaging, docx validity, metadata, sections | Valid ZIP, `word/document.xml`, `python-docx` loadable, student metadata, all 10 major sections |
| **Tier 2** | 19 Screenshot Callouts | 6 | Screenshot containers, numbering, framing, output | All 19 screenshots (1–19), target cell citations (Cells 2..34), framing instructions, expected outputs, placeholder boxes |
| **Tier 3** | Concise Written Answers | 19 | Checkpoints & lab questions across Parts 0–6 | RGBA, SHA-256, value 201 LSB experiments, capacity (4,999 vs 3,749 B), Task 3A reference questions, Stepic verification, ISO/IEC 27037 extraction integrity, 300-word reflection essay |
| **Tier 4** | Robustness, Extension & Scenarios | 5 | Robustness tests, extension, rubric, checklist | Lossy JPEG compression, spatial resampling, RGBA vs RGB extension, 100-mark rubric table, 9-item checklist, grader flow |

---

## 3. Pre-Execution Validation Baseline (Missing Document Test)

As mandated by the testing protocol, `test_submission_guide.py` was executed prior to the generation of `Lab7_Submission_Guide.docx` to verify that the test harness correctly asserts deliverable presence:

```text
============================================================================
  E2E VERIFICATION SUMMARY REPORT (PRE-EXECUTION BASELINE)
============================================================================
Verification Tier                                | Total  | Pass   | Fail  
----------------------------------------------------------------------------
✓ Invariant: Notebook Immutability               | 6      | 6      | 0     
✗ Tier 1: Document Structure & OpenXML           | 5      | 0      | 5     
✗ Tier 2: 19 Screenshot Callouts                 | 6      | 0      | 6     
✗ Tier 3: Concise Written Answers                | 19     | 0      | 19    
✗ Tier 4: Robustness, Extension & Scenarios      | 5      | 0      | 5     
----------------------------------------------------------------------------
TOTAL: 41 tests | PASSED: 6 | FAILED/ERROR: 35
============================================================================
Exit Code: 1 (Properly fails on missing deliverable)
```

---

## 4. Feature Coverage Checklist

### Invariant: Notebook Preservation
- [x] `test_notebook_file_exists`: Verifies `Lab7.ipynb` is present in `Lab7/`
- [x] `test_notebook_git_clean`: Verifies `git status --porcelain Lab7/Lab7.ipynb` is strictly clean
- [x] `test_notebook_sha256_hash`: Verifies SHA-256 digest `a9d5655f0c39aa956ded377214575df046b9be3246d9ace6201a528a5072edb5`
- [x] `test_notebook_git_blob_sha1`: Verifies git blob object SHA-1 `c3c3921640de184580d2011b0fc8825057ad7d78`
- [x] `test_notebook_exact_size`: Verifies byte size is exactly 62,369 bytes (CRLF) or 61,194 bytes (LF)
- [x] `test_notebook_json_structure_and_cell_outputs`: Verifies 35 JSON cells and 16 code cells retain pre-executed outputs

### Tier 1: Document Packaging & Section Structure
- [x] `test_docx_file_exists`: Deliverable exists and is >10 KB
- [x] `test_docx_valid_zip_openxml`: Valid ZIP packaging with `[Content_Types].xml` and `word/document.xml`
- [x] `test_docx_loadable_by_python_docx`: Clean loading without parser exceptions
- [x] `test_docx_title_and_metadata_block`: Course ID ("FSCT 8561"), Lab identifier, student metadata placeholder
- [x] `test_docx_all_10_major_sections_present`: All 10 major functional sections verified:
  1. Section 0: Checklist and Rubric Matrix
  2. Part 0: Setup and Evidence Inventory
  3. Part 1: Binary and LSB Fundamentals
  4. Part 2: Calculate Capacity Before Writing
  5. Part 3: Manual LSB Encoding and Extraction
  6. Part 4: Stepic Implementation & Verification
  7. Part 5: File Integrity, Visual, and Pixel Analysis
  8. Part 6: Security Analysis and Reflection
  9. Two Robustness Tests
  10. Optional Extension (RGBA vs RGB-Only)

### Tier 2: Screenshot Callout Containers (19 Callouts)
- [x] `test_callout_containers_total_count`: At least 19 callout containers identified
- [x] `test_all_19_screenshot_indices_present`: Indices 1 through 19 each verified
  - Screenshot 1: Part 0 Step 0.1 (Cell 2) — File inventory metadata
  - Screenshot 2: Part 0 Step 0.3 (Cell 4) — Cryptographic baseline SHA-256 digests
  - Screenshot 3: Part 1 Step 1.1 (Cell 6) — Worked single-bit modification (Value 150)
  - Screenshot 4: Part 1 Step 1.3 (Cell 8) — Value 201 bitwise modification experiment
  - Screenshot 5: Part 1 Step 1.4 (Cell 10) — Letters-to-bits encoding and null sentinel
  - Screenshot 6: Part 2 Step 2.2 (Cell 12) — Capacity calculations & 40-pixel requirement
  - Screenshot 7: Part 3 Step 3.1 (Cell 14) — Reference script verification test ("HI")
  - Screenshot 8: Part 3 Step 3.3 (Cell 16) — Defensive manual encoder (`encode_checked`)
  - Screenshot 9: Part 3 Step 3.4 (Cell 18) — Clean-room manual decoder (`decode_manual`)
  - Screenshot 10: Part 4 Step 4.1 (Cell 20) — Port list payload formatting
  - Screenshot 11: Part 4 Step 4.2 (Cell 22) — Stepic RGB conversion and bitstream save
  - Screenshot 12: Part 4 Step 4.4 (Cell 24) — Stepic extraction and payload recovery
  - Screenshot 13: Part 5 Step 5.1 (Cell 26) — Image differencing framework reference
  - Screenshot 14: Part 5 Step 5.3 (Cell 28) — Comprehensive pixel differencing metrics
  - Screenshot 15: Part 5 Step 5.5 (Cell 30) — Non-destructive extraction (ISO/IEC 27037)
  - Screenshot 16: Part 5 Step 5.7 (Cell 32) — Side-by-side visual comparison pairs
  - Screenshot 17: Part 6 Step 6.1 (Cell 33) — 300-word security reflection essay
  - Screenshot 18: Robustness / Checklist 7 — Lossy JPEG and spatial resampling tests
  - Screenshot 19: Submission / Checklist — Completed checklist and grading rubric
- [x] `test_screenshot_cell_citations`: Explicit target cell references (Cells 2..34)
- [x] `test_screenshot_capture_instructions`: Explicit framing / capture instructions
- [x] `test_screenshot_expected_output_descriptions`: Verbatim expected outputs
- [x] `test_screenshot_placeholder_boxes`: Styled dotted placeholder indicators

### Tier 3: Concise, Direct Written Answers
- [x] `test_part0_checkin0_rgba_definition`: RGBA 4-channel model, luminance, opacity, 32-bit depth
- [x] `test_part0_checkin0_sha256_forensic_rationale`: Digital baseline, chain of custody, ISO/IEC 27037
- [x] `test_part1_small_modifications_value_201_results`: Values 200 and 201 produced
- [x] `test_part1_small_modifications_invariance_explanation`: 201 is odd (`11001001`), bit 0 already 1, OR with 1 unchanged
- [x] `test_part1_max_numerical_difference`: Maximum difference is exactly 1 (0.39% luminance)
- [x] `test_part2_capacity_100x100_rgba`: Exactly 4,999 message bytes calculated
- [x] `test_part2_capacity_rgb_comparison_and_alpha_benefit`: Exactly 3,749 message bytes, 25% drop, alpha preserved
- [x] `test_part2_payload_pixel_discrepancy`: 20 bytes requires 40 pixels (not 10 pixels)
- [x] `test_part3_task3a_convert_rgba_reason`: Standardizing 4-channel format to prevent indexing errors
- [x] `test_part3_task3a_two_pixels_per_byte`: 4 bits/pixel in RGBA, 8-bit byte requires 2 pixels
- [x] `test_part3_task3a_null_terminator_sentinel`: In-band null terminator sentinel delimiter
- [x] `test_part3_task3a_capacity_overflow_and_guard`: IndexError on overflow, defensive pre-flight capacity check
- [x] `test_part3_task3a_png_vs_jpeg_rationale`: Lossless Deflate vs lossy DCT quantization scrambling LSBs
- [x] `test_part4_task4b_extraction_verification_rationale`: File save only proves I/O, extraction confirms payload integrity
- [x] `test_part5_task5a_hash_comparison_scope`: Byte-level identity vs inability to prove causality or intent
- [x] `test_part5_task5a_checkpoint_identical_appearance`: Hash divergence does not prove stego alone; required tests
- [x] `test_part5_task5b_extraction_non_destructiveness`: ISO/IEC 27037 principle; pre-hash == post-hash
- [x] `test_part5_task5c_visual_observation_and_jnd`: Variance <= 1 falls below Just Noticeable Difference (JND)
- [x] `test_part6_security_reflection_essay`: 7-point reflection essay, verbatim recovered payloads, 250–350 words

### Tier 4: Robustness Tests, Optional Extension & Application Scenarios
- [x] `test_robustness_test_1_lossy_compression`: Lossy JPEG compression, DCT quantization, decoder corruption
- [x] `test_robustness_test_2_spatial_resampling`: Spatial resampling / resizing / cropping, interpolation disrupting alignment
- [x] `test_optional_extension_rgba_vs_rgb_analysis`: Capacity tradeoff (25% reduction), alpha preservation advantages
- [x] `test_rubric_table_and_checklist_matrix`: 100-mark rubric criteria, 9-item checklist mapping
- [x] `test_scenario_student_and_grader_completeness`: Student metadata block, professional formatting, grader review flow
