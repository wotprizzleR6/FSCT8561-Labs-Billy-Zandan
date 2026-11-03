## 2026-11-02T20:57:50Z
You are a teamwork_explorer.
Your working directory is: c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_explorer_2
Your parent conversation ID is: 4454555e-8e94-46d7-b2c6-e12b4f18de76

MANDATORY: Read ORIGINAL_REQUEST.md first:
c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\ORIGINAL_REQUEST.md

Also read:
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\PROJECT.md
- Prior survey reports:
  - c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_2\survey_images_metadata.md
  - c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3\survey_env_infra.md
  - c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\spec_miner_survey_1\survey_spec.md

Scope: Milestone 1 — Covert Channel Detection Rules & Heuristic Risk Scoring
Task:
1. Formulate exact heuristic detection rules for `metadata_scanner.py`:
   - Identifying covert fields without brittle hardcoding (e.g. looking for command keywords, attack lifecycle prefixes like RECON/VULN/EXPLOIT/PERSIST/LATERAL/EXFIL, unusually long strings, high entropy, base64 patterns).
   - De-obfuscation algorithms: Base64 detection & decoding, standard EXIF 8-byte ASCII header stripping (`b'ASCII\x00\x00\x00'`), XML tag extraction.
   - Consistent, explainable heuristic risk scoring model (+10 confirmed covert message, +5 encoded/obfuscated value, +5 unusual carrier indicator like GPS or camera metadata on synthetic diagram), avoiding double-counting, yielding expected risk scores (10-15) and documented plain-English reasons.
2. Formulate the required CSV output format (`metadata_report.csv`) with the 7 required columns:
   `filename,format,metadata_fields,suspected_field,encoding,risk_score,reason`
3. Write `analysis.md` and `handoff.md` in your working directory and notify your parent.
Do NOT modify production files. Only write in your working directory.
