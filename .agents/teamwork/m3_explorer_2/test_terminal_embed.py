"""
Test script to verify PIL terminal screenshot generator and docx image embedding.
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

    # Title centered or next to controls
    draw.text((75, 10), title, fill=(212, 212, 216), font=font_title)

    # Lines
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

def test_embed():
    temp_img = Path(__file__).parent / "test_term.png"
    lines = [
        "$ python -c \"from PIL import Image; img = Image.open('Images/Brain-Channel.png'); print(img.getexif()[270])\"",
        "[+] Target: Brain-Channel.png (201,685 bytes)",
        "[+] EXIF Primary IFD0 Tag 270 (ImageDescription) Detected:",
        "    LATERAL: Pivot to internal Domain Controller using Mimikatz.",
        "[+] Stage Verification: Cyber Kill Chain Stage 5 (Lateral Movement) Confirmed.",
    ]
    create_terminal_card("Terminal: Brain-Channel.png EXIF Extraction", lines, temp_img)

    doc = docx.Document()
    doc.add_heading("Terminal Evidence Verification", level=1)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(str(temp_img), width=Inches(6.2))
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_cap.add_run("Figure 1: Forensic CLI extraction terminal verifying Stage 5 covert channel.")
    r_cap.italic = True
    r_cap.font.size = Pt(8.5)
    r_cap.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    out_docx = Path(__file__).parent / "test_embed_output.docx"
    doc.save(str(out_docx))
    print(f"Successfully created docx with embedded picture at {out_docx}")

if __name__ == "__main__":
    test_embed()
