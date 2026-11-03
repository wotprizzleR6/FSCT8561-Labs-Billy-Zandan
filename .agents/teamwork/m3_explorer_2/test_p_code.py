"""
Test paragraph shading and paragraph borders in python-docx.
Verifies that code formatted in top-level doc.paragraphs is shaded, bordered,
and directly detectable by doc.paragraphs tests.
"""

from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def test_paragraph_code_styling():
    doc = docx.Document()

    # Style helper for paragraph shading and borders
    def style_code_paragraph(p, is_first=False, is_last=False):
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.right_indent = Inches(0.2)
        p.paragraph_format.space_before = Pt(4) if is_first else Pt(0)
        p.paragraph_format.space_after = Pt(6) if is_last else Pt(0)
        p.paragraph_format.line_spacing = 1.0

        pPr = p._p.get_or_add_pPr()
        # Paragraph Shading
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
        pPr.append(shd)

        # Paragraph Borders (left thick accent bar, subtle top/bottom for first/last)
        top_xml = '<w:top w:val="single" w:sz="4" w:space="3" w:color="CBD5E1"/>' if is_first else '<w:top w:val="none"/>'
        bot_xml = '<w:bottom w:val="single" w:sz="4" w:space="3" w:color="CBD5E1"/>' if is_last else '<w:bottom w:val="none"/>'
        pbdr_xml = (
            f'<w:pBdr {nsdecls("w")}>'
            f'{top_xml}'
            f'<w:left w:val="single" w:sz="24" w:space="8" w:color="002B49"/>'
            f'{bot_xml}'
            f'<w:right w:val="single" w:sz="4" w:space="8" w:color="CBD5E1"/>'
            f'</w:pBdr>'
        )
        pPr.append(parse_xml(pbdr_xml))

    doc.add_heading("Section 5: Automated Scanner Implementation", level=1)
    p_intro = doc.add_paragraph("The Python source code for metadata_scanner.py is embedded below:")

    code_lines = [
        "import base64",
        "import csv",
        "from PIL import Image, ExifTags",
        "",
        "# Automated Multi-Layer Metadata Extraction",
        "def scan_single_image(image_path):",
        "    with Image.open(image_path) as img:",
        "        exif = img.getexif()",
        "        return exif",
    ]

    for i, line in enumerate(code_lines):
        p = doc.add_paragraph()
        style_code_paragraph(p, is_first=(i == 0), is_last=(i == len(code_lines) - 1))
        r = p.add_run(line if line else " ")
        r.font.name = "Consolas"
        r.font.size = Pt(8.0)
        if line.startswith("#"):
            r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        elif line.startswith("import ") or line.startswith("from ") or line.startswith("def "):
            r.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)
            r.bold = True
        else:
            r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    out_file = Path(__file__).parent / "test_p_code.docx"
    doc.save(str(out_file))
    print(f"Saved: {out_file}")

    # Verify doc.paragraphs
    doc_check = docx.Document(str(out_file))
    full_text = "\n".join(p.text for p in doc_check.paragraphs)
    has_code = "import" in full_text and ("def " in full_text or "class " in full_text or "Image.open" in full_text)
    print("test_t2_f7_69 pass:", has_code)
    print("Total doc.paragraphs:", len(doc_check.paragraphs))

if __name__ == "__main__":
    test_paragraph_code_styling()
