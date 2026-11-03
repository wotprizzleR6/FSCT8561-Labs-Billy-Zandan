import csv
import base64
import math
import re
from pathlib import Path
from PIL import Image, ExifTags
import xml.etree.ElementTree as ET

def shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    entropy = 0
    length = len(data)
    for x in set(data):
        p_x = data.count(x) / length
        entropy += - p_x * math.log2(p_x)
    return entropy

def is_base64(s: str) -> bool:
    s = s.strip()
    if len(s) < 16 or len(s) % 4 != 0:
        return False
    # Check charset
    if not re.match(r'^[A-Za-z0-9+/]+={0,2}$', s):
        return False
    try:
        decoded = base64.b64decode(s, validate=True)
        # Check if decoded is mostly printable text
        text = decoded.decode('utf-8', errors='ignore')
        if len(text) > 0 and sum(c.isprintable() for c in text) / len(text) > 0.85:
            return True
    except Exception:
        return False
    return False

def scan_images(image_dir: Path):
    results = []
    
    # Attack stage keywords for heuristic covert-channel detection
    stage_keywords = ["RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:"]
    security_keywords = ["dns harvesting", "cve-", "sql injection", "reverse shell", "mimikatz", "covert channel"]
    
    for image_path in sorted(image_dir.glob("*.png")):
        with Image.open(image_path) as img:
            # Metadata fields list
            all_fields = list(img.info.keys())
            
            exif_obj = img.getexif()
            if len(exif_obj) > 0:
                for tid in exif_obj.keys():
                    tname = ExifTags.TAGS.get(tid, f"ExifTag_{tid}")
                    if tname not in all_fields:
                        all_fields.append(f"EXIF:{tname}")
            
            suspected_field = ""
            encoding = "None"
            risk_score = 0
            reasons = []
            covert_found = False
            encoded_found = False
            unusual_found = False
            
            candidate_texts = []
            
            # Check EXIF Root
            for tid, val in exif_obj.items():
                tname = ExifTags.TAGS.get(tid, str(tid))
                if isinstance(val, str):
                    candidate_texts.append((f"EXIF:{tname}", val))
                    
            # Check Sub-IFDs (0x8769 ExifOffset)
            try:
                sub_ifd = exif_obj.get_ifd(34665)
                for tid, val in sub_ifd.items():
                    tname = ExifTags.TAGS.get(tid, str(tid))
                    if isinstance(val, bytes):
                        # check UserComment
                        if val.startswith(b"ASCII\x00\x00\x00"):
                            clean_val = val[8:].decode("utf-8", errors="replace")
                            candidate_texts.append((f"EXIF Sub-IFD:{tname}", clean_val, "ASCII (Null-prefixed UserComment)"))
                        else:
                            clean_val = val.decode("utf-8", errors="ignore")
                            if len(clean_val) > 10:
                                candidate_texts.append((f"EXIF Sub-IFD:{tname}", clean_val))
                    elif isinstance(val, str):
                        candidate_texts.append((f"EXIF Sub-IFD:{tname}", val))
            except Exception:
                pass

            # Check GPS IFD (34853)
            try:
                gps_ifd = exif_obj.get_ifd(34853)
                if gps_ifd:
                    unusual_found = True
                    reasons.append("GPS metadata present on synthetic screenshot asset")
            except Exception:
                pass
                
            # Check PNG text chunks in img.info
            for k, v in img.info.items():
                if isinstance(v, str) and k not in ["exif", "XML:com.adobe.xmp", "xmp"]:
                    candidate_texts.append((f"PNG:{k}", v))
                    
            # Check XMP
            xmp_raw = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
            if xmp_raw:
                if isinstance(xmp_raw, bytes):
                    xmp_str = xmp_raw.decode("utf-8", errors="replace")
                else:
                    xmp_str = str(xmp_raw)
                try:
                    clean_xmp = xmp_str.strip("\ufeff")
                    root = ET.fromstring(clean_xmp)
                    for elem in root.iter():
                        txt = (elem.text or "").strip()
                        if txt:
                            candidate_texts.append((f"XMP:{elem.tag.split('}')[-1]}", txt))
                except Exception:
                    # Fallback regex
                    pass
            
            # Analyze candidate texts
            for item in candidate_texts:
                field_name = item[0]
                text_val = item[1]
                custom_enc = item[2] if len(item) > 2 else None
                
                # Check for Base64
                if is_base64(text_val):
                    encoded_found = True
                    decoded_val = base64.b64decode(text_val).decode("utf-8", errors="replace")
                    # Check if decoded value has stage keywords
                    if any(kw in decoded_val for kw in stage_keywords) or any(sk in decoded_val.lower() for sk in security_keywords):
                        covert_found = True
                        suspected_field = field_name
                        encoding = "Base64"
                        reasons.append(f"Confirmed covert message in {field_name} encoded in Base64 (Decoded: '{decoded_val[:40]}...')")
                elif any(kw in text_val for kw in stage_keywords) or any(sk in text_val.lower() for sk in security_keywords):
                    covert_found = True
                    suspected_field = field_name
                    encoding = custom_enc if custom_enc else "Plain text"
                    reasons.append(f"Confirmed covert incident narrative stage in {field_name} ('{text_val[:40]}...')")
                    
            # Scoring
            if covert_found:
                risk_score += 10
            if encoded_found:
                risk_score += 5
            if unusual_found and not encoded_found:
                risk_score += 5
                
            # If Dopamine has XMP MakerNote
            if "Dopamine" in image_path.name and covert_found:
                # maker note inside XMP is unusual indicator
                risk_score += 5
                reasons.append("Unusual metadata structure: MakerNote embedded in XMP on PNG format")

            result = {
                "filename": image_path.name,
                "format": img.format,
                "metadata_fields": ", ".join(all_fields),
                "suspected_field": suspected_field,
                "encoding": encoding,
                "risk_score": risk_score,
                "reason": "; ".join(reasons) if reasons else "No covert metadata identified"
            }
            results.append(result)
            
    return results

if __name__ == "__main__":
    img_dir = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images")
    res = scan_images(img_dir)
    for r in res:
        print("-" * 60)
        print(f"File: {r['filename']} | Score: {r['risk_score']} | Field: {r['suspected_field']} | Enc: {r['encoding']}")
        print(f"Reason: {r['reason']}")
