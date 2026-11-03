import argparse
import base64
import csv
from dataclasses import dataclass
import io
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image, ExifTags

# Safe XML parsing: prefer defusedxml if installed, fallback to standard xml.etree
try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


# CONSTANTS & GROUND-TRUTH PATTERNS

CSV_FIELDNAMES = [
    "filename",
    "format",
    "metadata_fields",
    "suspected_field",
    "encoding",
    "risk_score",
    "reason",
]

# Attack lifecycle stage markers
LIFECYCLE_STAGE_PREFIXES = (
    "RECON:",
    "VULN:",
    "EXPLOIT:",
    "PERSIST:",
    "LATERAL:",
    "EXFIL:",
)

# Operational threat keywords indicating covert incident payload
THREAT_KEYWORDS = (
    "dns harvesting",
    "subdomain enumeration",
    "cve-2024-",
    "cve-",
    "sql injection",
    "reverse shell",
    "mimikatz",
    "dns covert channel",
    "domain controller",
    "cron job",
    "bypass waf",
    "payload",
)

# Standard EXIF 8-byte ASCII prefix for UserComment (tag 37510)
EXIF_ASCII_PREFIX = b"ASCII\x00\x00\x00"



# DATA MODELS

@dataclass
class ImageScanResult:
    """Forensic scan result for a single image file."""

    filename: str
    format: str
    metadata_fields: str
    suspected_field: str
    encoding: str
    risk_score: int
    reason: str
    recovered_secret: str = ""

    def to_csv_dict(self) -> Dict[str, Any]:
        """Convert result to the exact 7-column schema required by the contract."""
        return {
            "filename": self.filename,
            "format": self.format,
            "metadata_fields": self.metadata_fields,
            "suspected_field": self.suspected_field,
            "encoding": self.encoding,
            "risk_score": self.risk_score,
            "reason": self.reason,
        }


# CONSOLE ENCODING HARDENING

def configure_utf8_streams() -> None:
    """Ensure standard stdout and stderr streams support UTF-8 on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure") and stream.encoding and stream.encoding.lower() not in ("utf-8", "utf8"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, io.UnsupportedOperation):
                pass



# MULTI-LAYER METADATA EXTRACTION

def collect_metadata_field_names(img: Image.Image) -> List[str]:
    """
    Collect unique, ordered metadata field names present across all layers.

    Extracts keys from native PNG text chunks (img.info), EXIF IFD0 tags,
    Exif Sub-IFD tags (e.g. UserComment), and GPS IFD tags.
    """
    field_names: List[str] = list(img.info.keys())

    exif = img.getexif()
    if exif:
        # Inspect primary IFD0 tags
        for tag_id in exif:
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            if tag_name in ("ImageDescription", "UserComment", "Copyright") and tag_name not in field_names:
                field_names.append(tag_name)

        # Inspect Exif Sub-IFD (tag 34665 / 0x8769)
        sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
        if sub_ifd:
            for sub_tag_id in sub_ifd:
                sub_tag_name = ExifTags.TAGS.get(sub_tag_id, str(sub_tag_id))
                if sub_tag_name in ("UserComment",) and sub_tag_name not in field_names:
                    field_names.append(sub_tag_name)

        # Inspect GPS Sub-IFD (tag 34853 / 0x8825)
        gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
        if gps_ifd and "GPSInfo" not in field_names:
            field_names.append("GPSInfo")

    return field_names


def extract_metadata_candidates(img: Image.Image) -> Tuple[List[Tuple[str, Any]], Dict[str, Any]]:
    """
    Extract candidate metadata key-value pairs across EXIF, PNG, and XMP.

    Returns:
        candidates: List of (field_name, raw_value) tuples
        context: Dictionary containing environmental metadata (GPS, Camera, XMP presence)
    """
    candidates: List[Tuple[str, Any]] = []
    context: Dict[str, Any] = {
        "has_gps": False,
        "has_camera": False,
        "has_xmp": False,
    }

    # 1. Native PNG Text Chunks & XMP packets in img.info
    for key, val in img.info.items():
        if key in ("XML:com.adobe.xmp", "xmp"):
            context["has_xmp"] = True
            # Parse Adobe XMP XML packet
            xmp_str = val if isinstance(val, str) else val.decode("utf-8", errors="replace")
            xmp_str = xmp_str.lstrip("\ufeff")  # Strip UTF-8 BOM if present
            try:
                root = ET.fromstring(xmp_str)
                for elem in root.iter():
                    tag_local = elem.tag.split("}")[-1]
                    if elem.text and elem.text.strip():
                        if tag_local == "MakerNote":
                            field_label = "XML:com.adobe.xmp (exif:MakerNote)"
                        else:
                            field_label = f"XML:com.adobe.xmp ({tag_local})"
                        candidates.append((field_label, elem.text.strip()))
            except Exception:
                # Robust regex fallback if XML is partially malformed
                match = re.search(r"<exif:MakerNote>(.*?)</exif:MakerNote>", xmp_str)
                if match:
                    candidates.append(("XML:com.adobe.xmp (exif:MakerNote)", match.group(1).strip()))
        elif key != "exif":
            # Native PNG textual chunk (e.g. Software, ImageDescription, Copyright)
            if isinstance(val, (str, bytes)):
                candidates.append((key, val))

    # 2. EXIF Multi-IFD structure
    exif = img.getexif()
    if exif:
        # Check camera hardware tags
        if 271 in exif or 272 in exif:  # Make or Model
            context["has_camera"] = True

        # IFD0 tags
        for tag_id, val in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            candidates.append((tag_name, val))

        # Exif Sub-IFD (tag 34665 / 0x8769)
        sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
        if sub_ifd:
            for sub_tag_id, val in sub_ifd.items():
                sub_tag_name = ExifTags.TAGS.get(sub_tag_id, str(sub_tag_id))
                candidates.append((sub_tag_name, val))

        # GPS Sub-IFD (tag 34853 / 0x8825)
        gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
        if gps_ifd and len(gps_ifd) > 0:
            context["has_gps"] = True

    return candidates, context



# DE-OBFUSCATION & HEURISTIC DETECTION


def analyze_and_deobfuscate(field_name: str, raw_val: Any) -> Tuple[str, str, bool, bool]:
    """
    De-obfuscate raw metadata candidate and test for covert channel indicators.

    Returns:
        cleaned_text: De-obfuscated or plaintext string
        encoding_name: Human-readable encoding type description
        is_covert: True if text matches incident stage or threat keywords
        is_encoded: True if computational decoding was required
    """
    cleaned_text = ""
    encoding_name = "None (plain text)"
    is_encoded = False

    # 1. Check for standard EXIF UserComment 8-byte ASCII header
    if isinstance(raw_val, bytes) and raw_val.startswith(EXIF_ASCII_PREFIX):
        cleaned_text = raw_val[len(EXIF_ASCII_PREFIX):].decode("utf-8", errors="replace").strip()
        encoding_name = "EXIF ASCII header / plain text"
        is_encoded = True

    # 2. Check for RFC 4648 Base64 encoding
    elif isinstance(raw_val, str) and len(raw_val) >= 16 and len(raw_val) % 4 == 0 and re.match(r"^[A-Za-z0-9+/]+={0,2}$", raw_val.strip()):
        try:
            decoded_bytes = base64.b64decode(raw_val.strip(), validate=True)
            decoded_str = decoded_bytes.decode("utf-8")
            # Verify printable distribution
            printable_ratio = sum(1 for c in decoded_str if c.isprintable()) / max(len(decoded_str), 1)
            if printable_ratio > 0.85:
                cleaned_text = decoded_str.strip()
                encoding_name = "Base64"
                is_encoded = True
            else:
                cleaned_text = raw_val.strip()
        except Exception:
            cleaned_text = raw_val.strip()

    # 3. Check for XMP XML element encapsulation
    elif "MakerNote" in field_name or "XML" in field_name:
        cleaned_text = str(raw_val).strip()
        encoding_name = "XML encapsulation / plain text"
        is_encoded = False

    # 4. Standard plain text
    else:
        if isinstance(raw_val, bytes):
            cleaned_text = raw_val.decode("utf-8", errors="replace").strip()
        else:
            cleaned_text = str(raw_val).strip()
        encoding_name = "None (plain text)"
        is_encoded = False

    # Heuristic covert message matching
    is_covert = any(cleaned_text.startswith(p) for p in LIFECYCLE_STAGE_PREFIXES) or any(
        kw in cleaned_text.lower() for kw in THREAT_KEYWORDS
    )

    return cleaned_text, encoding_name, is_covert, is_encoded



# RISK SCORING ENGINE

def calculate_risk_score(
    suspected_field: str,
    encoding: str,
    is_covert: bool,
    is_encoded: bool,
    context: Dict[str, Any],
) -> Tuple[int, str]:
    """
    Calculate explainable risk score and justification text per lab rubric.

    Scoring Model:
      +10: Confirmed covert message detected in metadata
      +5:  Encoded or obfuscated payload requiring computational decoding
      +5:  Anomalous metadata indicator (camera/GPS on graphic, or isolated XMP)
      Guard: Double-counting prevented (maximum single score addition capped at +5).
    """
    if not is_covert:
        return 0, "No covert metadata detected."

    score = 10
    reasons = [f"Confirmed covert message in {suspected_field} (+10)"]

    # Rule 2: Suspicious encoding requiring decoding (+5)
    if encoding == "Base64":
        score += 5
        reasons.append("obfuscated with Base64 encoding requiring decoding (+5)")

    # Rule 3: Anomalous container or metadata indicator (+5)
    elif context.get("has_gps") and context.get("has_camera"):
        score += 5
        reasons.append("camera hardware and GPS tags embedded in graphic (+5)")

    elif "XML" in suspected_field or "MakerNote" in suspected_field:
        score += 5
        reasons.append("unusual container / embedded XMP packet (+5)")

    reason_str = "; ".join(reasons) + "."
    return score, reason_str



# SINGLE IMAGE & DIRECTORY SCAN PIPELINE

def scan_single_image(image_path: Path) -> ImageScanResult:
    """
    Execute complete forensic scan on a single image file.

    Extracts multi-layer metadata, detects covert channels, de-obfuscates,
    and assigns an explainable risk score.
    """
    filename = image_path.name

    with Image.open(image_path) as img:
        img_format = img.format or "PNG"
        fields = collect_metadata_field_names(img)
        metadata_fields_str = ", ".join(fields)

        candidates, context = extract_metadata_candidates(img)

        suspected_field = "None"
        encoding = "None"
        risk_score = 0
        reason = "No covert metadata detected."
        recovered_secret = ""

        for field_name, raw_val in candidates:
            cleaned_text, enc_name, is_covert, is_encoded = analyze_and_deobfuscate(field_name, raw_val)
            if is_covert:
                suspected_field = field_name
                encoding = enc_name
                recovered_secret = cleaned_text
                risk_score, reason = calculate_risk_score(
                    suspected_field=field_name,
                    encoding=enc_name,
                    is_covert=True,
                    is_encoded=is_encoded,
                    context=context,
                )
                break

    return ImageScanResult(
        filename=filename,
        format=img_format,
        metadata_fields=metadata_fields_str,
        suspected_field=suspected_field,
        encoding=encoding,
        risk_score=risk_score,
        reason=reason,
        recovered_secret=recovered_secret,
    )


def scan_directory(
    image_dir: Union[str, Path],
    output_csv: Optional[Union[str, Path]] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> List[Dict[str, Any]]:
    """
    Scan all PNG images in image_dir and export findings to CSV if specified.

    Returns:
        List of result dictionaries conforming to the 7-column schema.
    """
    img_dir_path = Path(image_dir)
    if not img_dir_path.exists() or not img_dir_path.is_dir():
        raise FileNotFoundError(f"Image directory does not exist: {img_dir_path}")

    # Discover and sort all PNG image files
    png_files = sorted(
        [p for p in img_dir_path.iterdir() if p.is_file() and p.suffix.lower() == ".png"],
        key=lambda p: p.name.lower(),
    )

    if not quiet:
        print(f"Scanning directory: {img_dir_path.resolve()}")
        print(f"Found {len(png_files)} PNG image(s) to inspect.\n")

    results: List[ImageScanResult] = []

    for idx, p in enumerate(png_files, 1):
        try:
            res = scan_single_image(p)
            results.append(res)
            if not quiet:
                print(f"[{idx}/{len(png_files)}] Scanned {res.filename}")
                if verbose or not quiet:
                    print(f"      Suspected Field : {res.suspected_field}")
                    print(f"      Encoding        : {res.encoding}")
                    print(f"      Risk Score      : {res.risk_score}")
                    print(f"      Reason          : {res.reason}")
                    if verbose and res.recovered_secret:
                        print(f"      Recovered Secret: {res.recovered_secret}")
                    print()
        except Exception as e:
            sys.stderr.write(f"Error scanning {p.name}: {e}\n")

    dict_rows = [res.to_csv_dict() for res in results]

    # Write CSV report if output path specified
    if output_csv is not None:
        out_path = Path(output_csv)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=CSV_FIELDNAMES,
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writeheader()
            for row in dict_rows:
                writer.writerow(row)

        if not quiet:
            print("=" * 80)
            print(f"Scan complete. Exported {len(dict_rows)} record(s) to: {out_path.resolve()}")
            print("=" * 80)

    return dict_rows



# PATH RESOLUTION & CLI ENTRY POINT

def resolve_paths(images_arg: str, output_arg: str) -> Tuple[Path, Path]:
    """
    Dynamically resolve target image directory and CSV output path.

    Supports execution from both repository root and Lab6 subfolder.
    """
    script_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()

    # Resolve image directory
    candidate_img = Path(images_arg)
    if candidate_img.is_absolute():
        resolved_img = candidate_img
    elif candidate_img.exists() and candidate_img.is_dir():
        resolved_img = candidate_img.resolve()
    elif (cwd / candidate_img).exists() and (cwd / candidate_img).is_dir():
        resolved_img = (cwd / candidate_img).resolve()
    elif (script_dir / candidate_img).exists() and (script_dir / candidate_img).is_dir():
        resolved_img = (script_dir / candidate_img).resolve()
    elif images_arg == "Images" and (script_dir / "Images").exists():
        resolved_img = (script_dir / "Images").resolve()
    else:
        resolved_img = (cwd / candidate_img).resolve()

    # Resolve output CSV path
    candidate_out = Path(output_arg)
    if candidate_out.is_absolute():
        resolved_out = candidate_out
    elif output_arg == "metadata_report.csv":
        # Default report path: place alongside script if in Lab6
        if (cwd / "metadata_scanner.py").exists():
            resolved_out = (cwd / "metadata_report.csv").resolve()
        else:
            resolved_out = (script_dir / "metadata_report.csv").resolve()
    else:
        resolved_out = (cwd / candidate_out).resolve()

    return resolved_img, resolved_out


def parse_arguments(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Automated Image Metadata Covert Channel Scanner (FSCT 8561 Lab 6)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--images",
        "--image-dir",
        "-d",
        dest="images",
        default="Images",
        help="Path to directory containing target PNG images (default: 'Images').",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-csv",
        dest="output",
        default="metadata_report.csv",
        help="Output path for the generated 7-column CSV report (default: 'metadata_report.csv').",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed diagnostic stdout reporting during scan.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress console progress messages and table output.",
    )
    return parser.parse_args(argv)


def main() -> None:
    """CLI execution entry point."""
    configure_utf8_streams()
    args = parse_arguments()

    images_dir, output_csv = resolve_paths(args.images, args.output)

    if not images_dir.exists() or not images_dir.is_dir():
        sys.stderr.write(f"Error: Target image directory not found: {images_dir}\n")
        sys.exit(1)

    try:
        scan_directory(
            image_dir=images_dir,
            output_csv=output_csv,
            verbose=args.verbose,
            quiet=args.quiet,
        )
    except Exception as e:
        sys.stderr.write(f"Fatal error during metadata scan: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
