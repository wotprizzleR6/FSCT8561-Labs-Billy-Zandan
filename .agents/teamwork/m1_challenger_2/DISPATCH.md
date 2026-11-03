## 2026-11-02T21:11:16Z
You are a teamwork_challenger.
Your working directory is: c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m1_challenger_2
Your parent conversation ID is: 4454555e-8e94-46d7-b2c6-e12b4f18de76

MANDATORY: Read ORIGINAL_REQUEST.md first:
c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\ORIGINAL_REQUEST.md

Also read:
- c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\PROJECT.md
- Artifacts to challenge:
  - c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py
  - c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv

Task:
Differential Testing and Oracle Verification for Milestone 1:
1. Build an independent extraction oracle in your working directory using pure-Python libraries.
2. Compare the output of `metadata_scanner.py` against your independent oracle across:
   - Extracted metadata field lists
   - Suspected covert fields and extracted payload fragments
   - Detected encodings (Base64, ASCII, XML)
   - Computed risk scores and justification strings
3. Verify that the 6 images are mapped accurately to the 6 attack lifecycle stages (`RECON`, `VULN`, `EXPLOIT`, `PERSIST`, `LATERAL`, `EXFIL`).
4. Document your differential findings and explicit verdict (APPROVE or REQUEST_CHANGES) in `handoff.md`.
Send a completion message to your parent with your verdict and differential test results.
Do NOT modify production files. Only write in your working directory.
