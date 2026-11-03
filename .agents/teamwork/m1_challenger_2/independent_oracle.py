#!/usr/bin/env python3
"""
Independent Forensic Metadata Extraction Oracle & Attack Lifecycle Analyzer.

This oracle is independently implemented from first principles using pure-Python
binary structure parsing (PNG chunks, TIFF/EXIF IFD structures, XML XMP packets)
to serve as an adversarial ground truth oracle for differential testing against
Lab6/metadata_scanner.py.

Key Capabilities:
  - Raw binary PNG chunk iteration (IHDR, tEXt, zTXt, iTXt, eXIf, pHYs, etc.)
  - Native TIFF IFD byte parsing (Big-Endian 'MM' and Little-Endian 'II')
  - Tag resolution across TIFF Baseline, EXIF Private Sub-IFDs, and GPS tags
  - Adobe XMP XML packet parsing and namespace extraction
  - Base64, ASCII control code, and XML payload de-obfuscation
  - Independent risk scoring and heuristic classification
  - Cyber Kill Chain & MITRE ATT&CK incident lifecycle mapping
"""

import base64
import csv
import io
from pathlib import Path
import re
import struct
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import xml.etree.ElementTree as ET
import zlib

# TIFF Data Types (size in bytes, format char)
TIFF_TYPES = {
    1: (1, "B"),   # BYTE (8-bit unsigned integer)
    2: (1, "s"),   # ASCII (8-bit byte containing 7-bit ASCII; null-terminated)
    3: (2, "H"),   # SHORT (16-bit unsigned integer)
    4: (4, "I"),   # LONG (32-bit unsigned integer)
    5: (8, "II"),  # RATIONAL (two LONGs: numerator, denominator)
    7: (1, "B"),   # UNDEFINED (8-bit byte)
    9: (4, "i"),   # SLONG (32-bit signed integer)
    10: (8, "ii"), # SRATIONAL (two SLONGs)
}

TAG_NAMES = {
    # IFD0
    270: "ImageDescription",
    271: "Make",
    272: "Model",
    282: "XResolution",
    283: "YResolution",
    296: "ResolutionUnit",
    305: "Software",
    306: "DateTime",
    531: "YCbCrPositioning",
    33432: "Copyright",
    34665: "ExifOffset",
    34853: "GPSInfo",
    # Exif Sub-IFD
    36864: "ExifVersion",
    36867: "DateTimeOriginal",
    36868: "DateTimeDigitized",
    37121: "ComponentsConfiguration",
    37500: "MakerNote",
    37510: "UserComment",
    40960: "FlashPixVersion",
    40961: "ColorSpace",
    # GPS Sub-IFD
    0: "GPSVersionID",
    1: "GPSLatitudeRef",
    2: "GPSLatitude",
    3: "GPSLongitudeRef",
    4: "GPSLongitude",
}

LIFECYCLE_MAPPING = {
    "RECON": {
        "stage_num": 1,
        "name": "Reconnaissance",
        "description": "DNS harvesting and subdomain enumeration",
        "kill_chain": "Reconnaissance",
        "mitre_id": "TA0043 (Reconnaissance)",
    },
    "VULN": {
        "stage_num": 2,
        "name": "Vulnerability Analysis / Weaponization",
        "description": "Unpatched CVE identification in web gateway",
        "kill_chain": "Weaponization",
        "mitre_id": "TA0001 / TA0043 (Pre-Attack)",
    },
    "EXPLOIT": {
        "stage_num": 3,
        "name": "Exploitation",
        "description": "SQL Injection payload to bypass WAF",
        "kill_chain": "Exploitation",
        "mitre_id": "TA0002 (Execution) / T1190 (Exploit Public-Facing App)",
    },
    "PERSIST": {
        "stage_num": 4,
        "name": "Persistence",
        "description": "Reverse shell via obfuscated cron job",
        "kill_chain": "Persistence / Installation",
        "mitre_id": "TA0003 (Persistence) / T1053.003 (Cron)",
    },
    "LATERAL": {
        "stage_num": 5,
        "name": "Lateral Movement",
        "description": "Pivot to internal Domain Controller using Mimikatz",
        "kill_chain": "Lateral Movement",
        "mitre_id": "TA0008 (Lateral Movement) / T1003 (OS Credential Dumping)",
    },
    "EXFIL": {
        "stage_num": 6,
        "name": "Exfiltration",
        "description": "Compressed database dump tunnel via DNS covert channel",
        "kill_chain": "Actions on Objectives / Exfiltration",
        "mitre_id": "TA0010 (Exfiltration) / T1048.003 (DNS)",
    },
}


class BinaryTiffParser:
    """Pure-Python TIFF binary parser for raw eXIf chunks."""

    def __init__(self, raw_data: bytes):
        self.data = raw_data
        if len(raw_data) < 8:
            raise ValueError("TIFF data too short")
        endian_marker = raw_data[:2]
        if endian_marker == b"II":
            self.endian = "<"
        elif endian_marker == b"MM":
            self.endian = ">"
        else:
            raise ValueError(f"Invalid TIFF endian marker: {endian_marker!r}")

        magic = struct.unpack(f"{self.endian}H", raw_data[2:4])[0]
        if magic != 42:
            raise ValueError(f"Invalid TIFF magic number: {magic}")

        self.ifd0_offset = struct.unpack(f"{self.endian}I", raw_data[4:8])[0]

    def read_value(self, type_id: int, count: int, value_or_offset: bytes) -> Any:
        if type_id not in TIFF_TYPES:
            return value_or_offset

        type_size, fmt_char = TIFF_TYPES[type_id]
        total_size = type_size * count

        if total_size <= 4:
            val_bytes = value_or_offset[:total_size]
        else:
            offset = struct.unpack(f"{self.endian}I", value_or_offset)[0]
            if offset + total_size > len(self.data):
                return None
            val_bytes = self.data[offset:offset + total_size]

        if type_id == 2:  # ASCII
            try:
                return val_bytes.rstrip(b"\x00").decode("latin-1")
            except Exception:
                return val_bytes
        elif type_id == 3:  # SHORT
            return struct.unpack(f"{self.endian}{count}H", val_bytes) if count > 1 else struct.unpack(f"{self.endian}H", val_bytes)[0]
        elif type_id == 4:  # LONG
            return struct.unpack(f"{self.endian}{count}I", val_bytes) if count > 1 else struct.unpack(f"{self.endian}I", val_bytes)[0]
        elif type_id == 5:  # RATIONAL
            rats = []
            for i in range(count):
                num, den = struct.unpack(f"{self.endian}2I", val_bytes[i*8:(i+1)*8])
                rats.append((num, den))
            return tuple(rats) if count > 1 else rats[0]
        elif type_id == 7:  # UNDEFINED
            return val_bytes
        else:
            return val_bytes

    def parse_ifd(self, offset: int) -> Dict[int, Tuple[str, Any]]:
        if offset + 2 > len(self.data):
            return {}
        num_entries = struct.unpack(f"{self.endian}H", self.data[offset:offset+2])[0]
        entries: Dict[int, Tuple[str, Any]] = {}
        curr = offset + 2

        for _ in range(num_entries):
            if curr + 12 > len(self.data):
                break
            entry_bytes = self.data[curr:curr+12]
            tag_id = struct.unpack(f"{self.endian}H", entry_bytes[0:2])[0]
            type_id = struct.unpack(f"{self.endian}H", entry_bytes[2:4])[0]
            count = struct.unpack(f"{self.endian}I", entry_bytes[4:8])[0]
            val_or_off = entry_bytes[8:12]

            val = self.read_value(type_id, count, val_or_off)
            tag_name = TAG_NAMES.get(tag_id, f"Tag_{tag_id}")
            entries[tag_id] = (tag_name, val)
            curr += 12

        return entries


class PurePngParser:
    """Pure-Python binary PNG chunk parser."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.chunks: List[Tuple[str, bytes]] = []
        self.text_chunks: Dict[str, str] = {}
        self.exif_chunks: List[bytes] = []
        self._parse()

    def _parse(self):
        with open(self.file_path, "rb") as f:
            sig = f.read(8)
            if sig != b"\x89PNG\r\n\x1a\n":
                raise ValueError(f"{self.file_path.name} is not a valid PNG file.")

            while True:
                len_bytes = f.read(4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                chunk_len = struct.unpack(">I", len_bytes)[0]
                chunk_type = f.read(4).decode("latin-1")
                chunk_data = f.read(chunk_len)
                crc = f.read(4)

                self.chunks.append((chunk_type, chunk_data))

                if chunk_type == "tEXt":
                    parts = chunk_data.split(b"\x00", 1)
                    key = parts[0].decode("latin-1")
                    val = parts[1].decode("latin-1") if len(parts) > 1 else ""
                    self.text_chunks[key] = val
                elif chunk_type == "zTXt":
                    parts = chunk_data.split(b"\x00", 1)
                    key = parts[0].decode("latin-1")
                    rest = parts[1]
                    decomp = zlib.decompress(rest[1:]).decode("latin-1")
                    self.text_chunks[key] = decomp
                elif chunk_type == "iTXt":
                    parts = chunk_data.split(b"\x00", 1)
                    key = parts[0].decode("utf-8", errors="replace")
                    rest = parts[1]
                    comp_flag = rest[0]
                    sub = rest[2:].split(b"\x00", 2)
                    text_bytes = sub[2]
                    if comp_flag == 1:
                        text = zlib.decompress(text_bytes).decode("utf-8", errors="replace")
                    else:
                        text = text_bytes.decode("utf-8", errors="replace")
                    self.text_chunks[key] = text
                elif chunk_type == "eXIf":
                    self.exif_chunks.append(chunk_data)


class IndependentMetadataOracle:
    """Ground-truth metadata analyzer and risk evaluator."""

    def __init__(self, image_path: Path):
        self.path = image_path
        self.filename = image_path.name
        self.png = PurePngParser(image_path)
        self.metadata_items: List[Tuple[str, str, Any]] = []  # (layer, key, value)
        self.context: Dict[str, Any] = {
            "has_gps": False,
            "has_camera": False,
            "has_xmp": False,
        }
        self._extract_all()

    def _extract_all(self):
        # 1. Native PNG Text Chunks
        for k, v in self.png.text_chunks.items():
            self.metadata_items.append(("PNG", k, v))
            if "xmp" in k.lower():
                self.context["has_xmp"] = True
                self._parse_xmp(k, v)

        # 2. Binary EXIF chunks
        for exif_raw in self.png.exif_chunks:
            try:
                parser = BinaryTiffParser(exif_raw)
                ifd0 = parser.parse_ifd(parser.ifd0_offset)

                if 271 in ifd0 or 272 in ifd0:  # Make or Model
                    self.context["has_camera"] = True

                for tag_id, (tag_name, val) in ifd0.items():
                    self.metadata_items.append(("EXIF_IFD0", tag_name, val))

                    # Follow ExifOffset
                    if tag_id == 34665 and isinstance(val, int):
                        sub_ifd = parser.parse_ifd(val)
                        for stag_id, (stag_name, sval) in sub_ifd.items():
                            self.metadata_items.append(("EXIF_SubIFD", stag_name, sval))

                    # Follow GPSInfo
                    elif tag_id == 34853 and isinstance(val, int):
                        gps_ifd = parser.parse_ifd(val)
                        if gps_ifd:
                            self.context["has_gps"] = True
                        for gtag_id, (gtag_name, gval) in gps_ifd.items():
                            self.metadata_items.append(("EXIF_GPS", gtag_name, gval))
            except Exception as e:
                self.metadata_items.append(("EXIF_ERROR", "Error", str(e)))

    def _parse_xmp(self, layer_key: str, xml_content: str):
        clean_xml = xml_content.lstrip("\ufeff")
        try:
            root = ET.fromstring(clean_xml)
            for elem in root.iter():
                tag_local = elem.tag.split("}")[-1]
                if elem.text and elem.text.strip():
                    self.metadata_items.append(("XMP", f"{layer_key} ({tag_local})", elem.text.strip()))
        except Exception:
            m = re.search(r"<exif:MakerNote>(.*?)</exif:MakerNote>", clean_xml)
            if m:
                self.metadata_items.append(("XMP", f"{layer_key} (exif:MakerNote)", m.group(1).strip()))

    def analyze(self) -> Dict[str, Any]:
        """Analyze extracted metadata and compute ground-truth findings."""
        suspected_field = "None"
        raw_payload = ""
        recovered_secret = ""
        encoding = "None"
        lifecycle_stage = None
        risk_score = 0
        reasons = []

        # Find covert channel candidates
        for layer, key, val in self.metadata_items:
            # Test for Base64
            if isinstance(val, str) and len(val) >= 16 and len(val) % 4 == 0 and re.match(r"^[A-Za-z0-9+/]+={0,2}$", val.strip()):
                try:
                    dec = base64.b64decode(val.strip(), validate=True).decode("utf-8")
                    if any(dec.startswith(p) for p in ("RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:")):
                        suspected_field = key
                        raw_payload = val
                        recovered_secret = dec.strip()
                        encoding = "Base64"
                        break
                except Exception:
                    pass

            # Test for EXIF ASCII header
            elif isinstance(val, bytes) and val.startswith(b"ASCII\x00\x00\x00"):
                dec = val[8:].decode("utf-8", errors="replace").strip()
                if any(dec.startswith(p) for p in ("RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:")):
                    suspected_field = key
                    raw_payload = repr(val)
                    recovered_secret = dec
                    encoding = "EXIF ASCII header / plain text"
                    break

            # Test for XML encapsulation
            elif "MakerNote" in key or layer == "XMP":
                sval = str(val).strip()
                if any(sval.startswith(p) for p in ("RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:")):
                    suspected_field = key
                    raw_payload = sval
                    recovered_secret = sval
                    encoding = "XML encapsulation / plain text"
                    break

            # Test for plain text
            else:
                sval = val.decode("utf-8", errors="replace").strip() if isinstance(val, bytes) else str(val).strip()
                if any(sval.startswith(p) for p in ("RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:")):
                    suspected_field = key
                    raw_payload = sval
                    recovered_secret = sval
                    encoding = "None (plain text)"
                    break

        # Stage classification
        if recovered_secret:
            for stage_code, stage_info in LIFECYCLE_MAPPING.items():
                if recovered_secret.startswith(f"{stage_code}:"):
                    lifecycle_stage = stage_code
                    break

            # Score computation
            risk_score = 10
            reasons.append(f"Confirmed covert message in {suspected_field} (+10)")

            if encoding == "Base64":
                risk_score += 5
                reasons.append("obfuscated with Base64 encoding requiring decoding (+5)")
            elif self.context["has_gps"] and self.context["has_camera"]:
                risk_score += 5
                reasons.append("camera hardware and GPS tags embedded in graphic (+5)")
            elif "XML" in suspected_field or "MakerNote" in suspected_field:
                risk_score += 5
                reasons.append("unusual container / embedded XMP packet (+5)")

        reason_str = "; ".join(reasons) + "." if reasons else "No covert metadata detected."

        # Unique field names present across all chunks
        unique_fields = []
        for _, k, _ in self.metadata_items:
            if k not in unique_fields:
                unique_fields.append(k)

        return {
            "filename": self.filename,
            "format": "PNG",
            "metadata_fields": ", ".join(unique_fields),
            "suspected_field": suspected_field,
            "encoding": encoding,
            "risk_score": risk_score,
            "reason": reason_str,
            "raw_payload": raw_payload,
            "recovered_secret": recovered_secret,
            "lifecycle_stage": lifecycle_stage,
            "stage_info": LIFECYCLE_MAPPING.get(lifecycle_stage),
            "context": self.context,
        }


def run_oracle_scan(images_dir: Path) -> List[Dict[str, Any]]:
    results = []
    for p in sorted(images_dir.glob("*.png")):
        oracle = IndependentMetadataOracle(p)
        results.append(oracle.analyze())
    return results


if __name__ == "__main__":
    img_dir = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images")
    res = run_oracle_scan(img_dir)
    print(f"Independent Oracle scanned {len(res)} images successfully.")
    for r in res:
        print(f"[{r['filename']}] Stage={r['lifecycle_stage']} Field={r['suspected_field']} Score={r['risk_score']} Enc={r['encoding']}")
        print(f"    Secret: {r['recovered_secret']}")
