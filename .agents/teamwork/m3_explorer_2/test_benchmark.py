"""
Benchmark creating full 588 lines of code in python-docx with paragraph shading.
"""

import time
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def benchmark():
    t0 = time.time()
    scanner_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py")
    lines = scanner_path.read_text(encoding="utf-8").splitlines()

    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1.0)

    pPr_template = (
        f'<w:pPr {nsdecls("w")}>'
        f'<w:ind w:left="288" w:right="288"/>'
        f'<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
        f'<w:shd w:fill="F8FAFC"/>'
        f'<w:pBdr>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="8" w:color="002B49"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="single" w:sz="4" w:space="8" w:color="CBD5E1"/>'
        f'</w:pBdr>'
        f'</w:pPr>'
    )

    doc.add_heading("Section 5: Automated Scanner Implementation", level=1)
    doc.add_paragraph("Full verbatim source code of metadata_scanner.py:")

    for idx, line in enumerate(lines, 1):
        p = doc.add_paragraph()
        pPr = parse_xml(pPr_template)
        p._p.append(pPr)
        r_num = p.add_run(f"{idx:3d} | ")
        r_num.font.name = "Consolas"
        r_num.font.size = Pt(6.5)
        r_num.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

        r_code = p.add_run(line if line else " ")
        r_code.font.name = "Consolas"
        r_code.font.size = Pt(6.5)
        sline = line.strip()
        if sline.startswith("#") or sline.startswith('"""') or sline.startswith("'''"):
            r_code.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        elif any(sline.startswith(kw) for kw in ("def ", "class ", "import ", "from ", "return ", "if ", "elif ", "else:", "for ", "while ", "try:", "except")):
            r_code.font.color.rgb = RGBColor(0x00, 0x2B, 0x49)
            r_code.bold = True
        else:
            r_code.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    out = Path(__file__).parent / "test_benchmark.docx"
    doc.save(str(out))
    t1 = time.time()
    print(f"Generated {len(lines)} lines in {t1 - t0:.2f} seconds! File size: {out.stat().st_size} bytes")

if __name__ == "__main__":
    benchmark()
