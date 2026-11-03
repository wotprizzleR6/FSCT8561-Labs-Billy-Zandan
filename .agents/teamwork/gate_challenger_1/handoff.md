# Empirical Challenger Gate Verification Report: Lab 6

**Verdict**: **APPROVE**  
**Agent**: `gate_challenger_1` (Critic / Specialist)  
**Date**: 2026-11-02T23:28:30Z  
**Target Files**:
- `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv`
- `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py`
- `c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb`

---

## 1. Observation

### 1.1 Direct Tool Invocations and Cryptographic Verifications

1. **Independent Execution of Metadata Scanner**:
   - **Command**:
     ```powershell
     python Lab6\metadata_scanner.py -i Lab6\Images -o .agents\teamwork\gate_challenger_1\test_report.csv -v
     ```
   - **Exit Code**: `0`
   - **Standard Output**:
     ```text
     Scanning directory: C:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images
     Found 6 PNG image(s) to inspect.

     [1/6] Scanned Activation.png
           Suspected Field : UserComment
           Encoding        : EXIF ASCII header / plain text
           Risk Score      : 15
           Reason          : Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5).
           Recovered Secret: VULN: Identify unpatched CVE-2024-XXXX in web gateway.

     [2/6] Scanned Brain-Channel.png
           Suspected Field : ImageDescription
           Encoding        : None (plain text)
           Risk Score      : 10
           Reason          : Confirmed covert message in ImageDescription (+10).
           Recovered Secret: LATERAL: Pivot to internal Domain Controller using Mimikatz.

     [3/6] Scanned Brain.png
           Suspected Field : Software
           Encoding        : None (plain text)
           Risk Score      : 10
           Reason          : Confirmed covert message in Software (+10).
           Recovered Secret: RECON: Perform DNS harvesting and Subdomain enumeration.

     [4/6] Scanned Chemicals.png
           Suspected Field : ImageDescription
           Encoding        : None (plain text)
           Risk Score      : 10
           Reason          : Confirmed covert message in ImageDescription (+10).
           Recovered Secret: EXPLOIT: Deploy SQL Injection payload to bypass WAF.

     [5/6] Scanned Dopamine.png
           Suspected Field : XML:com.adobe.xmp (exif:MakerNote)
           Encoding        : XML encapsulation / plain text
           Risk Score      : 15
           Reason          : Confirmed covert message in XML:com.adobe.xmp (exif:MakerNote) (+10); unusual container / embedded XMP packet (+5).
           Recovered Secret: PERSIST: Establish reverse shell via obfuscated cron job.

     [6/6] Scanned Music.png
           Suspected Field : Copyright
           Encoding        : Base64
           Risk Score      : 15
           Reason          : Confirmed covert message in Copyright (+10); obfuscated with Base64 encoding requiring decoding (+5).
           Recovered Secret: EXFIL: Tunnel compressed database dump via DNS Covert Channel.

     ================================================================================
     Scan complete. Exported 6 record(s) to: C:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\gate_challenger_1\test_report.csv
     ================================================================================
     ```

2. **Cryptographic Checksum & Byte Equivalence**:
   - `Lab6\metadata_report.csv` SHA-256: `11a671ebd807f466057c83adc03811e2e61553cbede793822c856072a93f2852`
   - `.agents\teamwork\gate_challenger_1\test_report.csv` SHA-256: `11a671ebd807f466057c83adc03811e2e61553cbede793822c856072a93f2852`
   - Byte-for-byte comparison: `b1 == b2` evaluates to `True`.

3. **`Lab6.ipynb` Immutability Verification**:
   - Expected SHA-256: `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`
   - Actual `Lab6\Lab6.ipynb` SHA-256: `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`
   - Result: 100% cryptographic match. 0 bytes modified.

4. **CSV Schema & Row Content Inspection**:
   - `Lab6\metadata_report.csv` contains exactly 7 non-empty lines (1 header + 6 data rows).
   - Header fields: `['filename', 'format', 'metadata_fields', 'suspected_field', 'encoding', 'risk_score', 'reason']`. Exact 7 columns, exact order.
   - Row 1: `Activation.png`, `PNG`, `"srgb, gamma, dpi, exif, Make, Model, Software, create-date, UserComment, GPSInfo"`, `UserComment`, `EXIF ASCII header / plain text`, `15`, `"Confirmed covert message in UserComment (+10); camera hardware and GPS tags embedded in graphic (+5)."`
   - Row 2: `Brain-Channel.png`, `PNG`, `"srgb, gamma, dpi, exif, ImageDescription"`, `ImageDescription`, `None (plain text)`, `10`, `"Confirmed covert message in ImageDescription (+10)."`
   - Row 3: `Brain.png`, `PNG`, `"srgb, gamma, dpi, Software"`, `Software`, `None (plain text)`, `10`, `"Confirmed covert message in Software (+10)."`
   - Row 4: `Chemicals.png`, `PNG`, `ImageDescription`, `ImageDescription`, `None (plain text)`, `10`, `"Confirmed covert message in ImageDescription (+10)."`
   - Row 5: `Dopamine.png`, `PNG`, `"srgb, gamma, dpi, xmp, XML:com.adobe.xmp"`, `XML:com.adobe.xmp (exif:MakerNote)`, `XML encapsulation / plain text`, `15`, `"Confirmed covert message in XML:com.adobe.xmp (exif:MakerNote) (+10); unusual container / embedded XMP packet (+5)."`
   - Row 6: `Music.png`, `PNG`, `"srgb, gamma, dpi, Copyright, Make, Model, create-date, exif"`, `Copyright`, `Base64`, `15`, `"Confirmed covert message in Copyright (+10); obfuscated with Base64 encoding requiring decoding (+5)."`

5. **CLI Robustness Stress-Testing**:
   - Non-existent input directory: `python Lab6\metadata_scanner.py -i non_existent_folder_xyz` -> Exited with code `1`, printed error message to stderr.
   - Quiet mode: `python Lab6\metadata_scanner.py -i Lab6\Images -o <tmp> -q` -> Exited with code `0`, suppressed console output, created valid CSV.
   - Empty input directory: `python Lab6\metadata_scanner.py -i <empty_dir> -o <tmp>` -> Exited with code `0`, outputted 1-line header-only CSV.
   - Help flag: `python Lab6\metadata_scanner.py --help` -> Exited with code `0`, printed complete usage docs.

---

## 2. Logic Chain

1. **Schema Integrity**:
   - *Observation 4* shows the header line parsed by Python's standard `csv.reader` contains exactly `['filename', 'format', 'metadata_fields', 'suspected_field', 'encoding', 'risk_score', 'reason']`. This satisfies R3 and acceptance criteria for exact 7 contract columns without deviation.
2. **Data Row Completeness**:
   - *Observation 4* demonstrates exactly 6 data rows, each corresponding to one of the 6 files in `Lab6/Images` (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`). Every row has 7 values, with proper CSV quoting preventing comma delimiter injection in multi-valued fields like `metadata_fields` and semicolon-separated `reason`.
3. **Risk Scoring Model Correctness**:
   - *Observation 1 and 4* demonstrate that all risk scores are either 10 or 15.
   - Plaintext covert messages (`Brain.png`, `Brain-Channel.png`, `Chemicals.png`) receive base score 10.
   - Encoded covert messages (`Music.png` with Base64) receive 10 + 5 = 15.
   - Obfuscated/anomalous container payloads (`Activation.png` with camera/GPS metadata on graphic; `Dopamine.png` with XMP MakerNote) receive 10 + 5 = 15.
   - The double-counting guardrail in `calculate_risk_score()` ensures scores do not exceed 15.
4. **Reproducibility and Execution Parity**:
   - *Observations 1 and 2* confirm that re-running `metadata_scanner.py` from scratch on `Lab6\Images` outputs a CSV (`test_report.csv`) with the identical SHA-256 hash (`11a671ebd807f466057c83adc03811e2e61553cbede793822c856072a93f2852`) as `Lab6\metadata_report.csv`. Exit code is 0.
5. **Notebook Preservation**:
   - *Observation 3* proves `Lab6\Lab6.ipynb` retains its pristine SHA-256 hash `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`. No modifications or cell runs occurred within the student notebook.

---

## 3. Caveats

- **Lab6_Report.md Table 3 Minor Wording Divergence**:
  - In `Lab6_Report.md` Table 3 (line 630), row 4 states: `Confirmed covert message in Chemicals (+10).`
  - In `Lab6\metadata_report.csv` row 4, the field value is: `Confirmed covert message in ImageDescription (+10).`
  - `metadata_report.csv` is the primary machine-readable deliverable and is 100% correct and generated by code. This minor Markdown text variant in the narrative table does not impact CSV integrity or script execution.
- No other caveats or unexplored failure modes identified.

---

## 4. Conclusion

All empirical challenge criteria specified in `ORIGINAL_REQUEST.md` and the dispatch instructions have been rigorously tested and satisfied:
1. `metadata_report.csv` conforms to the 7-column schema, 6-row completeness, and valid 10/15 risk score model.
2. `metadata_scanner.py` runs with exit code 0 and produces an identical CSV output (SHA-256: `11a671ebd807f466057c83adc03811e2e61553cbede793822c856072a93f2852`).
3. `Lab6\Lab6.ipynb` is unmodified (SHA-256: `86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9`).

**Final Gate Assessment**: **APPROVE**

---

## 5. Verification Method

To independently verify all claims made in this report, execute the following commands from the repository root:

```powershell
# 1. Verify Lab6.ipynb hash integrity
python -c "import hashlib; h = hashlib.sha256(open(r'Lab6\Lab6.ipynb', 'rb').read()).hexdigest(); assert h == '86d9886a845cd328dff590e47b391c5507a545fe05c230292492289073218ed9', f'Hash mismatch: {h}'; print('Notebook hash OK:', h)"

# 2. Run metadata scanner to temporary location
python Lab6\metadata_scanner.py -i Lab6\Images -o .agents\teamwork\gate_challenger_1\test_report.csv -v

# 3. Verify byte equivalence between generated and repository CSV
python -c "import hashlib; h1 = hashlib.sha256(open(r'Lab6\metadata_report.csv', 'rb').read()).hexdigest(); h2 = hashlib.sha256(open(r'.agents\teamwork\gate_challenger_1\test_report.csv', 'rb').read()).hexdigest(); assert h1 == h2, f'{h1} != {h2}'; print('CSV hash OK:', h1)"

# 4. Verify exact 7 columns and 6 rows
python -c "import csv; r = list(csv.reader(open(r'Lab6\metadata_report.csv', 'r', encoding='utf-8'))); assert len(r[0]) == 7; assert len(r) == 7; print('Columns:', len(r[0]), 'Data rows:', len(r)-1)"
```
