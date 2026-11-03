# Handoff Report: Milestone 1 Automated Metadata Scanner Architecture

**Agent:** Teamwork Explorer (`m1_explorer_1`)  
**Date:** 2026-11-02  
**Target Milestone:** Milestone 1 — Automated Scanner Architecture & Multi-Layer Extraction Flow  
**Target Implementer:** Teamwork Worker (`m1_worker_1`) / Orchestrator  
**Working Directory:** `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_explorer_1`

---

## 1. Observation

Direct programmatic and forensic observations were performed on the target environment and evidence set:

1. **Target Image Evidence Set (`Lab6/Images`):**
   - Execution command:
     `python -c "from PIL import Image, ExifTags; from pathlib import Path; ..."`
   - Output confirmed the exact metadata containers and values across all 6 PNG files:
     - `Activation.png`: EXIF IFD0 contains 10 tags (`Make: 'Nikon'`, `Model: 'D750'`, `Software: 'Adobe Lightroom 13.0'`, `GPSInfo: 396`, `ExifOffset: 204`). The Exif Sub-IFD (`0x8769`) contains 7 tags, including Tag 37510 (`UserComment`): `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`. GPS Sub-IFD (`0x8825`) contains 5 coordinates tags. `img.info` contains 8 keys: `['srgb', 'gamma', 'dpi', 'exif', 'Make', 'Model', 'Software', 'create-date']`.
     - `Brain-Channel.png`: EXIF IFD0 contains 5 tags, including Tag 270 (`ImageDescription`): `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'`. `img.info` contains only `['srgb', 'gamma', 'dpi', 'exif']`.
     - `Brain.png`: EXIF IFD0 contains 0 tags (`len(exif) == 0`). `img.info` contains 4 keys: `['srgb', 'gamma', 'dpi', 'Software']`, where `img.info['Software']` = `'RECON: Perform DNS harvesting and Subdomain enumeration.'`.
     - `Chemicals.png`: EXIF IFD0 contains 0 tags. `img.info` contains 1 key: `['ImageDescription']`, where `img.info['ImageDescription']` = `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'`.
     - `Dopamine.png`: EXIF IFD0 contains 0 tags. `img.info` contains `['srgb', 'gamma', 'dpi', 'xmp', 'XML:com.adobe.xmp']`. XML parsing using both `defusedxml.ElementTree` and standard `xml.etree.ElementTree` confirms element `<exif:MakerNote>` text is `'PERSIST: Establish reverse shell via obfuscated cron job.'`.
     - `Music.png`: EXIF IFD0 contains 9 tags, including Tag 33432 (`Copyright`): `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='`. `img.info` contains 8 keys, including `'Copyright'` with the identical Base64 string. RFC 4648 Base64 decoding yields `'EXFIL: Tunnel compressed database dump via DNS Covert Channel.'`.

2. **Notebook Specifications (`Lab6/Lab6.ipynb`):**
   - In `Lab6.ipynb`, Cells 34–39 define Step 7 ("Build an automated metadata scanner"):
     - Cell 34: Outlines requirements (loop 6 images, extract EXIF/PNG/XMP, record filename/format/fields/suspected_field/encoding, assign explainable risk score, export to `metadata_report.csv`).
     - Cell 34 notes: "Suggested classroom risk model: +10 for a confirmed covert-message field, +5 for a suspicious encoded value requiring investigation, and +5 for an additional unusual metadata indicator supported by evidence. Avoid double-counting an encoded message as both an encoded indicator and an additional unusual indicator."
     - Cell 38: Starter row schema: `{"filename": ..., "format": ..., "metadata_fields": ..., "risk_score": ...}`.
     - Cell 39: DictWriter export template with columns: `filename`, `format`, `metadata_fields`, `suspected_field`, `encoding`, `risk_score`, `reason`.

3. **Interface Contract (`PROJECT.md` & `ORIGINAL_REQUEST.md`):**
   - Script target: `Lab6/metadata_scanner.py`.
   - CSV target: `Lab6/metadata_report.csv`.
   - Required CSV columns: `filename,format,metadata_fields,suspected_field,encoding,risk_score,reason`.
   - Data rows: Exactly 6 rows, one per image, UTF-8 encoded.

---

## 2. Logic Chain

1. **Failure of Monolithic Extraction (Obs. 1):**  
   Because `Brain.png`, `Chemicals.png`, and `Dopamine.png` contain 0 EXIF tags in IFD0, an EXIF-only tool would miss 50% of the dataset. Conversely, checking only `img.info` keys would miss `ImageDescription` in `Brain-Channel.png` (which is stored exclusively in EXIF IFD0). Therefore, the extraction engine must combine EXIF IFD0, EXIF Sub-IFDs (`0x8769` and `0x8825`), PNG text chunks (`img.info`), and XMP XML packets into a unified discovery pool.

2. **Necessity of Targeted De-Obfuscation (Obs. 1):**  
   - In `Activation.png`, Tag 37510 begins with `b'ASCII\x00\x00\x00'`. Naive string matching will fail unless the 8-byte charset prefix is sliced.
   - In `Music.png`, Tag 33432 contains an 84-character Base64 payload. The scanner must detect Base64 via length/regex heuristics and safely verify decoding to printable text.
   - In `Dopamine.png`, the payload is encapsulated within `<exif:MakerNote>`. ElementTree parsing with RDF namespace stripping is necessary to extract the inner text.

3. **Heuristic Scoring Model Alignment (Obs. 2):**  
   Applying the classroom rubric rules without hardcoding:
   - Base = 0.
   - Confirmed covert message prefix (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`): +10. (Applies to all 6 images).
   - Suspicious encoding (Base64 in `Music.png`, ASCII null-prefix in `Activation.png`): +5.
   - Anomalous container/indicator (camera hardware and GPS tags in synthetic diagram `Activation.png`): +5.
   - Enforcing the non-double-counting guard guarantees scores of 10 or 15 with explicit, itemized reasoning in the `reason` column.

4. **CLI & Module Dual-Use Contract (Obs. 2, 3):**  
   `metadata_scanner.py` must support direct terminal execution with flags (`--image-dir`, `--output-csv`, `--verbose`, `--quiet`) and sensible default resolution, while exporting reusable functions (`scan_directory`, `scan_single_image`) for import into `Lab6.ipynb` and E2E test suites.

---

## 3. Caveats

1. **Scoring Model Interpretations:**  
   Some heuristic configurations assign +5 for non-standard carrier fields (e.g., using `Software` in `Brain.png` or `ImageDescription` in `Chemicals.png`). Under that alternative interpretation, all six images would receive a score of 15. However, following the starter code and `survey_spec.md` where plain-text fields in standard descriptive tags receive 10, images with plain text receive 10, and images with encoding or anomalous camera/GPS indicators receive 15. The scanner's reason field clearly lists individual point additions to satisfy both interpretations.
2. **Steganographic Invisibility:**  
   As noted in forensic analysis, this metadata scanner inspects only metadata fields. It cannot detect LSB steganography in image pixel rasters (`IDAT` chunks) or appended overlay data after `IEND`. This limitation is documented in `analysis.md` and fulfills rubric requirements for the written deliverables.

---

## 4. Conclusion

The technical design and architectural specification for `Lab6/metadata_scanner.py` is fully formulated and documented in `analysis.md`. The design satisfies all interface contracts from `PROJECT.md`, `ORIGINAL_REQUEST.md`, and `Lab6.ipynb`:
- Implements pure-Python extraction utilizing Pillow (`PIL.Image`, `PIL.ExifTags`), XML parsing (`defusedxml.ElementTree` / `xml.etree.ElementTree`), and `base64`.
- Unifies EXIF IFD0, Exif Sub-IFD (`0x8769`), GPS Sub-IFD (`0x8825`), PNG text chunks (`img.info`), and XMP XML packets.
- Provides modular, well-typed function architectures ready for immediate implementation by the Worker.
- Produces a compliant 7-column UTF-8 CSV at `Lab6/metadata_report.csv` with explainable, non-double-counted risk scores (10 and 15) and documented reasons.

---

## 5. Verification Method

The Worker and parent orchestrator can independently verify this technical design and its resulting implementation using the following commands:

1. **Inspect Analysis Specification:**
   - File: `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_explorer_1\analysis.md`
   - Verify all 8 core sections, data models, function signatures, and ground truth mapping tables are present.

2. **Verify Target Environment & Libraries:**
   ```powershell
   python -c "import PIL, defusedxml, xml.etree.ElementTree, base64, csv, argparse; print('Core dependencies available!')"
   ```

3. **Verify Scanner Implementation (Upon Worker Completion):**
   ```powershell
   # CLI execution test
   python Lab6/metadata_scanner.py --verbose

   # CSV schema and data validation
   python -c "
   import csv
   with open('Lab6/metadata_report.csv', encoding='utf-8') as f:
       rows = list(csv.DictReader(f))
   assert len(rows) == 6, f'Expected 6 rows, got {len(rows)}'
   expected_headers = ['filename', 'format', 'metadata_fields', 'suspected_field', 'encoding', 'risk_score', 'reason']
   assert list(rows[0].keys()) == expected_headers
   for r in rows:
       assert int(r['risk_score']) in (10, 15)
   print('Verification Passed: metadata_report.csv is 100% compliant!')
   "
   ```
