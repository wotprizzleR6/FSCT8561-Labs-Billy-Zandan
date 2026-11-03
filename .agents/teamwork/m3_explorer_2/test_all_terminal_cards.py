"""
Test generation of all 6 forensic terminal evidence cards.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_terminal_card(title: str, lines: list, output_path: Path):
    width = 1000
    line_height = 24
    padding = 20
    header_height = 36
    total_height = header_height + padding * 2 + len(lines) * line_height

    img = Image.new("RGB", (width, total_height), color=(24, 24, 27)) # Dark zinc
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([(0, 0), (width, header_height)], fill=(39, 39, 42))
    # Window controls (macOS style dots)
    draw.ellipse([(14, 12), (24, 22)], fill=(239, 68, 68))   # Red
    draw.ellipse([(32, 12), (42, 22)], fill=(245, 158, 11))  # Amber
    draw.ellipse([(50, 12), (60, 22)], fill=(16, 185, 129))  # Emerald

    # Fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 13)
        font_body = ImageFont.truetype("consola.ttf", 13)
    except Exception:
        font_title = font_body = ImageFont.load_default()

    draw.text((75, 10), title, fill=(212, 212, 216), font=font_title)

    y = header_height + padding
    for line in lines:
        if line.startswith("$"):
            color = (52, 211, 153) # Mint green
        elif line.startswith("[+]"):
            color = (56, 189, 248) # Sky blue
        elif any(stage in line for stage in ("RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:")):
            color = (251, 191, 36) # Amber secret
        elif line.startswith("[-]"):
            color = (248, 113, 113) # Red alert
        elif line.strip().startswith(">>>"):
            color = (192, 132, 252) # Purple prompt
        else:
            color = (228, 228, 231) # Light gray
        draw.text((25, y), line, fill=color, font=font_body)
        y += line_height

    img.save(str(output_path), format="PNG")
    return output_path

def test_all():
    work_dir = Path(__file__).parent / "test_cards"
    work_dir.mkdir(parents=True, exist_ok=True)

    evidence_records = [
        {
            "img": "Brain.png",
            "title": "Terminal 1: Brain.png — PNG tEXt Chunk Extraction",
            "lines": [
                "$ python -c \"from PIL import Image; img = Image.open('Images/Brain.png'); print(img.info)\"",
                "[+] Target: Brain.png (2,354,330 bytes | SHA256: 5eeb270a...)",
                "    img.getexif() -> 0 tags (Standard EXIF container empty)",
                "[+] Native PNG Text Chunk Detected: img.info['Software']",
                "    RECON: Perform DNS harvesting and Subdomain enumeration.",
                "[+] Decoded Secret: RECON: Perform DNS harvesting and Subdomain enumeration.",
                "[+] Kill Chain Mapping: Stage 1 Reconnaissance confirmed.",
            ],
            "caption": "Figure 1: Forensic terminal output extracting Stage 1 Reconnaissance payload from Brain.png tEXt chunk."
        },
        {
            "img": "Activation.png",
            "title": "Terminal 2: Activation.png — EXIF Sub-IFD UserComment Extraction",
            "lines": [
                "$ python -c \"from PIL import Image, ExifTags; img = Image.open('Images/Activation.png'); ...\"",
                "[+] Target: Activation.png (259,975 bytes | SHA256: 1730dd61...)",
                "    Top-level IFD0 tag 34665 (ExifOffset) points to Sub-IFD",
                "[+] Sub-IFD Tag 37510 (UserComment) Detected:",
                "    b'ASCII\\x00\\x00\\x00VULN: Identify unpatched CVE-2024-XXXX in web gateway.'",
                "[+] De-obfuscation: Stripped 8-byte ASCII character code header",
                "[+] Decoded Secret: VULN: Identify unpatched CVE-2024-XXXX in web gateway.",
                "[+] Kill Chain Mapping: Stage 2 Vulnerability Identification confirmed.",
            ],
            "caption": "Figure 2: Forensic terminal output extracting and de-obfuscating Stage 2 payload from Activation.png Sub-IFD."
        },
        {
            "img": "Chemicals.png",
            "title": "Terminal 3: Chemicals.png — PNG tEXt ImageDescription Extraction",
            "lines": [
                "$ python -c \"from PIL import Image; img = Image.open('Images/Chemicals.png'); print(img.info)\"",
                "[+] Target: Chemicals.png (561,245 bytes | SHA256: 96e549e3...)",
                "    img.getexif() -> 0 tags (Standard EXIF absent)",
                "[+] Native PNG Text Chunk Detected: img.info['ImageDescription']",
                "    EXPLOIT: Deploy SQL Injection payload to bypass WAF.",
                "[+] Decoded Secret: EXPLOIT: Deploy SQL Injection payload to bypass WAF.",
                "[+] Kill Chain Mapping: Stage 3 Exploitation confirmed.",
            ],
            "caption": "Figure 3: Forensic terminal output extracting Stage 3 Exploitation payload from Chemicals.png tEXt chunk."
        },
        {
            "img": "Dopamine.png",
            "title": "Terminal 4: Dopamine.png — Adobe XMP XML MakerNote Extraction",
            "lines": [
                "$ python -c \"from PIL import Image; import xml.etree.ElementTree as ET; ...\"",
                "[+] Target: Dopamine.png (388,411 bytes | SHA256: ae5dcf7e...)",
                "    img.getexif() -> 0 tags | img.info['XML:com.adobe.xmp'] present",
                "[+] Parsed Adobe XMP XML Packet: <exif:MakerNote> element located",
                "    <exif:MakerNote>PERSIST: Establish reverse shell via obfuscated cron job.</exif:MakerNote>",
                "[+] Decoded Secret: PERSIST: Establish reverse shell via obfuscated cron job.",
                "[+] Kill Chain Mapping: Stage 4 Persistence confirmed.",
            ],
            "caption": "Figure 4: Forensic terminal output parsing Adobe XMP XML packet from Dopamine.png to uncover Stage 4 payload."
        },
        {
            "img": "Brain-Channel.png",
            "title": "Terminal 5: Brain-Channel.png — EXIF IFD0 ImageDescription Extraction",
            "lines": [
                "$ python -c \"from PIL import Image; img = Image.open('Images/Brain-Channel.png'); ...\"",
                "[+] Target: Brain-Channel.png (201,685 bytes | SHA256: 3c50c375...)",
                "    img.getexif() -> Tag 270 (ImageDescription) present",
                "[+] EXIF Tag 270 Discovered:",
                "    LATERAL: Pivot to internal Domain Controller using Mimikatz.",
                "[+] Decoded Secret: LATERAL: Pivot to internal Domain Controller using Mimikatz.",
                "[+] Kill Chain Mapping: Stage 5 Lateral Movement confirmed.",
            ],
            "caption": "Figure 5: Forensic terminal output extracting Stage 5 Lateral Movement payload from Brain-Channel.png EXIF IFD0."
        },
        {
            "img": "Music.png",
            "title": "Terminal 6: Music.png — Dual-Layer Base64 De-Obfuscation",
            "lines": [
                "$ python -c \"import base64; from PIL import Image; img = Image.open('Images/Music.png'); ...\"",
                "[+] Target: Music.png (679,959 bytes | SHA256: 3416149b...)",
                "    Dual-Container: Tag Copyright in both EXIF (33432) and PNG tEXt chunk",
                "[+] Raw Obfuscated String Discovered:",
                "    RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4=",
                "[+] Base64 RFC 4648 Computational Decoding Executed:",
                "    EXFIL: Tunnel compressed database dump via DNS Covert Channel.",
                "[+] Kill Chain Mapping: Stage 6 Exfiltration confirmed.",
            ],
            "caption": "Figure 6: Forensic terminal output demonstrating Base64 decoding of Stage 6 Exfiltration payload from Music.png."
        },
    ]

    doc = docx.Document()
    for rec in evidence_records:
        p = work_dir / f"term_{rec['img'].replace('.png', '')}.png"
        create_terminal_card(rec["title"], rec["lines"], p)
        print(f"Generated card: {p}")
        doc.add_picture(str(p), width=Inches(6.2))
        p_cap = doc.add_paragraph(rec["caption"])
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

    out = Path(__file__).parent / "test_all_cards.docx"
    doc.save(str(out))
    print(f"Saved complete cards docx at {out}")

if __name__ == "__main__":
    test_all()
