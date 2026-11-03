from pathlib import Path
from PIL import Image, ExifTags
import base64
import csv
import re
import xml.etree.ElementTree as ET

image_dir = Path("Lab6/Images")

LIFECYCLE_STAGE_PREFIXES = ("RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:")
THREAT_KEYWORDS = ("dns harvesting", "subdomain enumeration", "cve-2024-", "cve-", "sql injection", "reverse shell", "mimikatz", "dns covert channel", "domain controller", "cron job", "bypass waf", "payload")

results = []

for image_path in sorted(image_dir.glob("*.png")):
    with Image.open(image_path) as img:
        # Collect metadata field names across all layers
        field_names = list(img.info.keys())
        exif = img.getexif()
        if exif:
            for tag_id in exif:
                tname = ExifTags.TAGS.get(tag_id, str(tag_id))
                if tname in ("ImageDescription", "UserComment", "Copyright") and tname not in field_names:
                    field_names.append(tname)
            sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
            if sub_ifd and "UserComment" not in field_names:
                field_names.append("UserComment")
            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
            if gps_ifd and "GPSInfo" not in field_names:
                field_names.append("GPSInfo")

        candidates = []
        has_gps = bool(exif and exif.get_ifd(ExifTags.IFD.GPSInfo))
        has_camera = bool(exif and (exif.get(271) or exif.get(272) or "Make" in img.info or "Model" in img.info))
        has_xmp = "XML:com.adobe.xmp" in img.info or "xmp" in img.info

        # PNG text
        for k, v in img.info.items():
            if k in ("XML:com.adobe.xmp", "xmp"):
                raw_xmp = v.decode("utf-8", errors="replace") if isinstance(v, bytes) else str(v)
                raw_xmp = raw_xmp.lstrip("\ufeff")
                try:
                    root = ET.fromstring(raw_xmp)
                    for elem in root.iter():
                        if elem.tag.endswith("MakerNote") and elem.text:
                            candidates.append((f"{k} (exif:MakerNote)", elem.text))
                except Exception:
                    pass
            elif isinstance(v, str):
                candidates.append((k, v))

        # EXIF IFD0 & Sub-IFDs
        if exif:
            for tid, val in exif.items():
                tname = ExifTags.TAGS.get(tid, str(tid))
                candidates.append((tname, val))
            sub = exif.get_ifd(ExifTags.IFD.Exif)
            if sub:
                for tid, val in sub.items():
                    tname = ExifTags.TAGS.get(tid, str(tid))
                    candidates.append((tname, val))

        suspected_field = "None"
        encoding = "None"
        risk_score = 0
        reason = "No covert metadata detected."

        for fname, raw_val in candidates:
            cleaned = ""
            enc = "None (plain text)"
            is_enc = False

            if isinstance(raw_val, bytes) and raw_val.startswith(b"ASCII\x00\x00\x00"):
                cleaned = raw_val[8:].decode("utf-8", errors="replace").strip()
                enc = "EXIF ASCII header / plain text"
                is_enc = True
            elif isinstance(raw_val, str) and len(raw_val) >= 16 and len(raw_val) % 4 == 0 and re.match(r"^[A-Za-z0-9+/]+={0,2}$", raw_val.strip()):
                try:
                    dec = base64.b64decode(raw_val.strip(), validate=True).decode("utf-8")
                    if sum(1 for c in dec if c.isprintable()) / max(len(dec), 1) > 0.85:
                        cleaned = dec.strip()
                        enc = "Base64"
                        is_enc = True
                    else:
                        cleaned = raw_val.strip()
                except Exception:
                    cleaned = raw_val.strip()
            elif "MakerNote" in fname or "XML" in fname:
                cleaned = str(raw_val).strip()
                enc = "XML encapsulation / plain text"
            else:
                cleaned = raw_val.decode("utf-8", errors="replace").strip() if isinstance(raw_val, bytes) else str(raw_val).strip()

            is_covert = any(cleaned.startswith(p) for p in LIFECYCLE_STAGE_PREFIXES) or any(kw in cleaned.lower() for kw in THREAT_KEYWORDS)

            if is_covert:
                suspected_field = fname
                encoding = enc
                score = 10
                reasons = [f"Confirmed covert message in {fname} (+10)"]
                if enc == "Base64":
                    score += 5
                    reasons.append("obfuscated with Base64 encoding requiring decoding (+5)")
                elif has_gps and has_camera:
                    score += 5
                    reasons.append("camera hardware and GPS tags embedded in graphic (+5)")
                elif has_xmp and not (exif and len(exif) > 0):
                    score += 5
                    reasons.append("unusual container / embedded XMP packet (+5)")
                risk_score = score
                reason = "; ".join(reasons) + "."
                break

        results.append({
            "filename": image_path.name,
            "format": img.format or "PNG",
            "metadata_fields": ", ".join(field_names),
            "suspected_field": suspected_field,
            "encoding": encoding,
            "risk_score": risk_score,
            "reason": reason,
        })

print(f"Generated {len(results)} rows.")
with open("Lab6/metadata_report.csv", "r", encoding="utf-8") as f:
    existing_csv = f.read()

import io
s = io.StringIO()
w = csv.DictWriter(s, fieldnames=results[0].keys(), quoting=csv.QUOTE_MINIMAL)
w.writeheader()
w.writerows(results)
new_csv = s.getvalue()

print("Matches existing metadata_report.csv exactly?", existing_csv.strip() == new_csv.strip())
if existing_csv.strip() != new_csv.strip():
    print("Diff:\nExisting:\n", existing_csv, "\nNew:\n", new_csv)
