[OPEN: opt-in choice for team structure] Rewrite the provided answers to all five reflection questions from Lab 6 to be as concise and direct as possible.

Working directory: [OPEN: target directory or file destination]
Integrity mode: [OPEN: integrity mode based on restrictions]

## Requirements

### R1. Concise and Direct Answers
Condense the answers to all five reflection questions to be as concise and direct as possible, eliminating unnecessary verbosity while preserving technical accuracy.
[OPEN: preferred format, length constraints, or delivery destination]

### R2. Technical Preservation
Retain the essential technical points from each answer:
- Question 1 (Hidden message vs getexif): Why getexif() returns empty for non-EXIF chunks (PNG native tEXt, zTXt, iTXt chunks, XMP vs TIFF IFD/eXIf chunk).
- Question 2 (Encoding vs encryption & Base64): Base64 provides zero confidentiality/trivial obfuscation; encoding is open and reversible without keys, whereas encryption requires secret keys.
- Question 3 (Preserving files & recording hashes): Metadata fragility/spoliation, cryptographic chain of custody/tamper-evidence, scientific reproducibility.
- Question 4 (Metadata alone proving incident & corroboration): Metadata is easily forged/unauthenticated; requires independent telemetry (network, host/OS, EDR/memory, filesystem logs).
- Question 5 (Connection to Labs 4 & 5 automation): Scalability/automation vs manual inspection, normalization of heterogeneous data into a unified schema, and SIEM/SOAR ingestion.

## Acceptance Criteria

### Completeness and Quality
- [ ] All 5 reflection questions are answered concisely and directly.
- [ ] The key technical distinctions and terminology for each question are retained.
- [ ] [OPEN: verification and rubric criteria]
