import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc = docx.Document()

# Set standard margins
sections = doc.sections
for section in sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Helper for cell shading
def set_cell_shading(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

# Helper for cell borders
def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

# Title
p_title = doc.add_paragraph()
r_title = p_title.add_run("LAB 6: COVERT CHANNELS IN IMAGE METADATA")
r_title.bold = True
r_title.font.size = Pt(20)
r_title.font.color.rgb = RGBColor(0x00, 0x2B, 0x49) # BCIT Navy

# Table test
table = doc.add_table(rows=2, cols=3)
table.autofit = False

headers = ["Image Filename", "Metadata Type", "Risk Score"]
for i, h in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = h
    set_cell_shading(cell, "002B49")
    set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
    for p in cell.paragraphs:
        for r in p.runs:
            r.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            r.font.size = Pt(10)

doc.save(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3\test_doc.docx")
print("Saved test_doc.docx successfully!")
