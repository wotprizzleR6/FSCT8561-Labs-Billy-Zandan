from PIL import Image, ImageDraw, ImageFont

def create_terminal_screenshot(title, lines, output_path):
    width = 900
    line_height = 24
    padding = 20
    header_height = 40
    total_height = header_height + padding * 2 + len(lines) * line_height

    img = Image.new("RGB", (width, total_height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Header bar (macOS / Linux terminal style)
    draw.rectangle([(0, 0), (width, header_height)], fill=(45, 45, 45))
    # Window buttons
    draw.ellipse([(15, 14), (27, 26)], fill=(255, 95, 86))
    draw.ellipse([(35, 14), (47, 26)], fill=(255, 189, 46))
    draw.ellipse([(55, 14), (67, 26)], fill=(39, 201, 63))

    # Header title
    try:
        font_title = ImageFont.truetype("arial.ttf", 14)
        font_body = ImageFont.truetype("consola.ttf", 14)
    except:
        font_title = font_body = ImageFont.load_default()

    draw.text((80, 12), title, fill=(200, 200, 200), font=font_title)

    # Body lines
    y = header_height + padding
    for line in lines:
        if line.startswith("$") or line.startswith(">>>"):
            color = (80, 250, 123) # Green prompt
        elif "LATERAL" in line or "RECON" in line or "EXPLOIT" in line or "PERSIST" in line or "EXFIL" in line or "VULN" in line:
            color = (255, 184, 108) # Yellow/Orange secret
        elif line.startswith("[-]"):
            color = (255, 85, 85) # Red
        else:
            color = (248, 248, 242) # White
        draw.text((25, y), line, fill=color, font=font_body)
        y += line_height

    img.save(output_path)
    print(f"Created screenshot: {output_path}")

lines = [
    "$ python -c \"from PIL import Image, ExifTags; ...\"",
    "Image: Brain-Channel.png",
    "EXIF tags count: 5",
    "  ImageDescription : LATERAL: Pivot to internal Domain Controller using Mimikatz.",
    "  ResolutionUnit : 2",
    "  YCbCrPositioning : 1",
    "[+] Recovered Stage 5 Fragment: LATERAL Movement payload confirmed."
]

create_terminal_screenshot("Terminal - Brain-Channel.png EXIF Extraction", lines, r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3\terminal_sample.png")
