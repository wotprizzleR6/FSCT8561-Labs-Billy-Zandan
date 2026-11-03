## 2026-11-02T21:04:36Z
You are a teamwork_worker.
Your working directory is: c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_worker_1
Your parent conversation ID is: 4454555e-8e94-46d7-b2c6-e12b4f18de76

MANDATORY: Read ORIGINAL_REQUEST.md first:
c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\ORIGINAL_REQUEST.md

Also read:
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\PROJECT.md
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_explorer_1\handoff.md
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_explorer_2\handoff.md
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_explorer_3\handoff.md

FILE WRITE OWNERSHIP:
You have exclusive write ownership over:
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv
Do NOT modify any other project files or notebooks in this milestone.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Task:
Implement Milestone 1 (Automated Scanner & CSV Engine):
1. Create `Lab6/metadata_scanner.py`:
   - Support multi-layer metadata extraction across all six images (`Activation.png`, `Brain-Channel.png`, `Brain.png`, `Chemicals.png`, `Dopamine.png`, `Music.png`):
     - EXIF primary IFD0, Exif Sub-IFD (UserComment tag 37510), GPS IFD.
     - Native PNG chunks (`tEXt`, `zTXt`, `iTXt`).
     - Adobe XMP XML packets (`XML:com.adobe.xmp`, extracting `<exif:MakerNote>`).
   - CLI flags with argparse: `--images` / `-i` (defaulting to `Images`), `--output` / `-o` (defaulting to `metadata_report.csv`), `-v` / `--verbose`.
   - Dynamic path resolution so running from either `Lab6/` or repo root resolves images properly.
   - Non-brittle heuristic detection of covert channels (command keywords, attack prefixes, Base64 patterns, high entropy) without brittle hardcoding.
   - De-obfuscation routines:
     - Base64 detection, validation, and decoding.
     - Standard EXIF 8-byte ASCII character code stripping (`b'ASCII\x00\x00\x00'`).
     - XML tag parsing.
   - Consistent, explainable heuristic risk scoring model (+10 confirmed covert message, +5 encoded/obfuscated value, +5 unusual carrier indicator like GPS/camera on synthetic diagram), avoiding double counting.
   - Standard 7-column CSV output (`filename,format,metadata_fields,suspected_field,encoding,risk_score,reason`) using Python's standard `csv.writer` with RFC 4180 quoting (`csv.QUOTE_MINIMAL`).
   - UTF-8 terminal protection (`sys.stdout.reconfigure(encoding='utf-8')`).
2. Run `metadata_scanner.py` to generate `Lab6/metadata_report.csv`.
3. Verify:
   - Check `metadata_report.csv` has header + exactly 6 data rows.
   - Run verification commands and `python test_e2e_lab6.py` (M1 tests should now pass).
4. Write `handoff.md` in your working directory documenting implementation, test commands, and exact outputs.
Send a completion message to your parent when done.
