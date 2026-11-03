# Handoff Report: Lab 6 Image Metadata Survey & Secret Reconstruction

**Agent Name:** `explorer_survey_2` (Teamwork Explorer)  
**Target Directory:** `Lab6/Images/`  
**Output Reference:** `.agents/teamwork/explorer_survey_2/survey_images_metadata.md`  
**Recipient:** Parent Agent (`4454555e-8e94-46d7-b2c6-e12b4f18de76`)  
**Date:** 2026-11-02  

---

## 1. Observation

All six target PNG images in `Lab6/Images/` were analyzed directly using custom Python inspection scripts leveraging Pillow, binary PNG chunk unpacking, and cryptographic hashing. The exact findings per image are:

### File 1: `Activation.png`
- **File properties:** 259,975 bytes; SHA-256: `1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904`.
- **PNG Chunks:** `IHDR`, `sRGB`, `gAMA`, `pHYs`, `eXIf`, `tEXt` (×4), `tIME`, `IDAT` (×4), `IEND`.
- **Metadata Layers:**
  - Standard EXIF 0th IFD contains tags: 271 (`Make: Nikon`), 272 (`Model: D750`), 305 (`Software: Adobe Lightroom 13.0`), 306 (`DateTime: 2025:02:02 10:15:00`), 34665 (`ExifOffset: 204`), 34853 (`GPSInfo: 396`).
  - SubIFD 0x8769 (`exif.get_ifd(0x8769)`) contains: Tag 37510 (`UserComment`):  
    `b'ASCII\x00\x00\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'`
  - SubIFD 0x8825 (`exif.get_ifd(0x8825)`) contains GPS coordinates: 40° 42' 46.08" N, 74° 0' 21.6" W.
  - Native PNG `tEXt` chunks: `Make`, `Model`, `Software`, `create-date` (`2025-02-02T10:15:00`).
  - Native PNG `tIME` chunk: `2025-02-02 10:15:00`.
- **Covert Field:** EXIF ExifOffset SubIFD Tag 37510 (`UserComment`).
- **Verbatim Recovered Fragment:** `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`

### File 2: `Brain-Channel.png`
- **File properties:** 201,685 bytes; SHA-256: `3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359`.
- **PNG Chunks:** `IHDR`, `sRGB`, `gAMA`, `pHYs`, `eXIf`, `IDAT` (×4), `IEND`.
- **Metadata Layers:**
  - EXIF 0th IFD contains Tag 270 (`ImageDescription`):  
    `'LATERAL: Pivot to internal Domain Controller using Mimikatz.'`
- **Covert Field:** EXIF Tag 270 (`ImageDescription`).
- **Verbatim Recovered Fragment:** `LATERAL: Pivot to internal Domain Controller using Mimikatz.`

### File 3: `Brain.png`
- **File properties:** 2,354,330 bytes; SHA-256: `5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e`.
- **PNG Chunks:** `IHDR`, `sRGB`, `gAMA`, `pHYs`, `tEXt`, `IDAT` (×36), `IEND`.
- **Metadata Layers:**
  - EXIF: 0 tags (`len(img.getexif()) == 0`; no `eXIf` chunk).
  - Native PNG `tEXt` chunk: Keyword `'Software'`, Value:  
    `'RECON: Perform DNS harvesting and Subdomain enumeration.'`
- **Covert Field:** PNG text chunk keyword `'Software'` (`img.info['Software']`).
- **Verbatim Recovered Fragment:** `RECON: Perform DNS harvesting and Subdomain enumeration.`

### File 4: `Chemicals.png`
- **File properties:** 561,245 bytes; SHA-256: `96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a`.
- **PNG Chunks:** `IHDR`, `tEXt`, `IDAT` (×9), `IEND`.
- **Metadata Layers:**
  - EXIF: 0 tags (`len(img.getexif()) == 0`; no `eXIf` chunk).
  - Native PNG `tEXt` chunk: Keyword `'ImageDescription'`, Value:  
    `'EXPLOIT: Deploy SQL Injection payload to bypass WAF.'`
- **Covert Field:** PNG text chunk keyword `'ImageDescription'` (`img.info['ImageDescription']`).
- **Verbatim Recovered Fragment:** `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`

### File 5: `Dopamine.png`
- **File properties:** 388,411 bytes; SHA-256: `ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472`.
- **PNG Chunks:** `IHDR`, `sRGB`, `gAMA`, `pHYs`, `iTXt`, `IDAT` (×6), `IEND`.
- **Metadata Layers:**
  - EXIF: 0 tags (`len(img.getexif()) == 0`; no `eXIf` chunk).
  - Native PNG `iTXt` chunk: Keyword `'XML:com.adobe.xmp'` (uncompressed UTF-8, length 421 bytes).
  - Contains XML element: `<exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>`.
- **Covert Field:** XMP element `<exif:MakerNote>` inside `img.info['XML:com.adobe.xmp']`.
- **Verbatim Recovered Fragment:** `PERSIST: Establish reverse shell via obfuscated cron job.`

### File 6: `Music.png`
- **File properties:** 679,959 bytes; SHA-256: `3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370`.
- **PNG Chunks:** `IHDR`, `sRGB`, `gAMA`, `pHYs`, `tEXt` (×4), `tIME`, `eXIf`, `IDAT` (×11), `IEND`.
- **Metadata Layers:**
  - EXIF Tag 33432 (`Copyright`): `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='`
  - PNG `tEXt` chunk `Copyright`: `'RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4='`
  - PNG `tIME` chunk & EXIF `DateTime`: `2025:02:06 11:11:00`.
- **Covert Field:** EXIF Tag 33432 & PNG Text `Copyright`.
- **Encoding:** RFC 4648 Base64 (84 ASCII characters, padded with `=`).
- **Verbatim Recovered Fragment:** `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`

---

## 2. Logic Chain

1. **Identification of Covert Content:**
   - In each of the six images, inspecting non-pixel metadata revealed exactly one human- or machine-decodable string marked with a capitalized cybersecurity incident stage keyword: `RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, and `EXFIL:`.
   - Five fragments were in plain text (though stored across different containers: EXIF 0th IFD, EXIF SubIFD, PNG `tEXt`, and XMP XML).
   - In `Music.png`, the value `RVhGSUw6...` matches Base64 syntax (length divisible by 4, ending with `=`, valid alphabet). Decoding via `base64.b64decode` yielded the readable string prefixed with `EXFIL:`.
2. **Reconstruction of Chronological Sequence:**
   - **Step 1 (Stage 1 — `RECON` / `Brain.png`):** An adversary begins with external reconnaissance (DNS harvesting and subdomain enumeration) to identify attack surfaces before any interaction with target systems.
   - **Step 2 (Stage 2 — `VULN` / `Activation.png`):** Having identified external endpoints, the adversary audits perimeter infrastructure to locate an exploitable vulnerability (`CVE-2024-XXXX` in the web gateway).
   - **Step 3 (Stage 3 — `EXPLOIT` / `Chemicals.png`):** Armed with knowledge of the vulnerability, the attacker launches an exploit (SQL Injection payload designed to bypass the WAF) to achieve initial access.
   - **Step 4 (Stage 4 — `PERSIST` / `Dopamine.png`):** Once inside, the adversary solidifies control by establishing persistence (a scheduled reverse shell via an obfuscated cron job) to survive server restarts and session interruptions.
   - **Step 5 (Stage 5 — `LATERAL` / `Brain-Channel.png`):** With persistent local access, the attacker dumps credentials using Mimikatz and moves laterally across the internal subnet to compromise the core Windows Active Directory Domain Controller.
   - **Step 6 (Stage 6 — `EXFIL` / `Music.png`):** After achieving domain dominance and accessing critical databases, the adversary completes their objective: compressing database dumps and exfiltrating them over a covert DNS channel.
3. **Corroborating Timestamp Evidence:**
   - `Activation.png` (Stage 2) embeds creation timestamps of `2025-02-02 10:15:00 UTC`.
   - `Music.png` (Stage 6) embeds creation timestamps of `2025-02-06 11:11:00 UTC`.
   - This provides empirical proof of a multi-day timeline where initial vulnerability staging preceded final data exfiltration by 4 days.

---

## 3. Caveats

- **Filesystem Timestamps:** File system modification timestamps (`mtime`) on disk reflect when files were unpacked/written locally and do not represent the original incident timeline. Only embedded metadata timestamps (`tIME`, `DateTime`, `DateTimeOriginal`) provide forensic historical value.
- **Scope of Obfuscation:** Only `Music.png` utilized character-level encoding (Base64). The other five images utilized structural/container obfuscation (placing data in PNG `tEXt` chunks or XMP where `getexif()` returns 0 tags, or hiding in SubIFDs) rather than cryptographic encryption.
- **No Residual Slack Data:** Inspection of all six PNG files confirmed that no data was appended after the `IEND` chunk (0 bytes of trailing overlay).

---

## 4. Conclusion

1. **Covert Message Retrieval:** All six image metadata covert fragments were successfully extracted, decoded, and forensically validated:
   - Stage 1: `Brain.png` → `RECON: Perform DNS harvesting and Subdomain enumeration.`
   - Stage 2: `Activation.png` → `VULN: Identify unpatched CVE-2024-XXXX in web gateway.`
   - Stage 3: `Chemicals.png` → `EXPLOIT: Deploy SQL Injection payload to bypass WAF.`
   - Stage 4: `Dopamine.png` → `PERSIST: Establish reverse shell via obfuscated cron job.`
   - Stage 5: `Brain-Channel.png` → `LATERAL: Pivot to internal Domain Controller using Mimikatz.`
   - Stage 6: `Music.png` → `EXFIL: Tunnel compressed database dump via DNS Covert Channel.`
2. **Assembled Incident Narrative:**
   > *"RECON: Perform DNS harvesting and Subdomain enumeration. VULN: Identify unpatched CVE-2024-XXXX in web gateway. EXPLOIT: Deploy SQL Injection payload to bypass WAF. PERSIST: Establish reverse shell via obfuscated cron job. LATERAL: Pivot to internal Domain Controller using Mimikatz. EXFIL: Tunnel compressed database dump via DNS Covert Channel."*
3. **Sequence Justification:** The reconstructed order adheres strictly to the Lockheed Martin Cyber Kill Chain and MITRE ATT&CK framework progression (Reconnaissance → Vulnerability Identification → Exploitation → Persistence → Lateral Movement → Exfiltration), corroborated by embedded image timestamps showing a Feb 2 → Feb 6 chronological interval.
4. **Tooling & Implementation Readiness:** Detailed forensic documentation, field identifiers, and risk-scoring analysis have been documented in `survey_images_metadata.md`, fully enabling the implementation of `metadata_report.csv`, notebook updates (`Lab6.ipynb`), and the Word document report (`Lab6-Billy-Zandan-A01371854.docx`).

---

## 5. Verification Method

To independently verify the observations and extracted strings, execute the following PowerShell command in the workspace root:

```powershell
python -c "
import base64
from PIL import Image

def get_secret(path):
    with Image.open(path) as img:
        # Check EXIF
        exif = img.getexif()
        if 270 in exif: return exif[270]
        if 33432 in exif: return base64.b64decode(exif[33432]).decode('utf-8')
        try:
            sub = exif.get_ifd(0x8769)
            if 37510 in sub:
                val = sub[37510]
                return val[8:].decode('utf-8') if val.startswith(b'ASCII\x00\x00\x00') else str(val)
        except Exception: pass
        # Check PNG info
        for k in ['Software', 'ImageDescription']:
            if k in img.info: return img.info[k]
        if 'XML:com.adobe.xmp' in img.info:
            import re
            m = re.search(r'<exif:MakerNote>(.*?)</exif:MakerNote>', img.info['XML:com.adobe.xmp'])
            if m: return m.group(1)
    return 'None'

files = ['Brain.png', 'Activation.png', 'Chemicals.png', 'Dopamine.png', 'Brain-Channel.png', 'Music.png']
for i, f in enumerate(files, 1):
    print(f'Stage {i} ({f}):', get_secret(f'Lab6/Images/{f}'))
"
```

**Invalidation Conditions:**
- If running the command outputs anything other than the exact six-stage sequence (`RECON:`, `VULN:`, `EXPLOIT:`, `PERSIST:`, `LATERAL:`, `EXFIL:`), this handoff is invalidated.
- If SHA-256 hashes of the files in `Lab6/Images/` do not match the values in Section 1, the files have been modified.
