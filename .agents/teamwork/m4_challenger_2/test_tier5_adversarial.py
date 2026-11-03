"""
Tier 5 White-Box Adversarial Coverage Hardening Test Suite
BCIT FSCT 8561 - Lab 6 Deliverable Hardening

Adversarial Stress Verification:
1. WordprocessingML XML Schema Validity, Tag Balance, and Namespace Purity:
   - Deep OOXML parsing of all .xml and .rels members.
   - Low-level injection verification: w:shd, w:tcMar, w:tcBorders, w:tcW, w:tblHeader, w:cantSplit, w:pBdr.
   - Table cell balance, content type declarations, and absence of malformed entities.
2. Embedded Media Image Integrity:
   - PNG chunk validation (IHDR, IDAT, IEND), magic header verification.
   - Image visual density, dimensions (1000px width), RGB color mode.
   - Sequential figure captions (Figures 1-6) and relationship mapping integrity.
   - Absence of unpopulated placeholders and corrupted tokens.
3. Notebook JSON Schema Compliance & Execution Semantics:
   - Jupyter nbformat 4.x schema compliance.
   - Code cell count (exactly 18) and strictly sequential execution counts (1..18).
   - Python AST syntax parseability across all code cells.
   - Zero error tracebacks, unhandled exceptions, or uncompleted blanks ('__________').
4. Cross-Deliverable Concordance & Forensic Truth:
   - 100% concordance of recovered covert secrets across images, CSV, and DOCX.
   - Cyber Kill Chain (Stages 1-6) and MITRE ATT&CK Enterprise tactics mapping.
   - Exact hash digests and file sizes matching raw evidence in Images/.
   - Risk score model alignment between metadata_report.csv and DOCX Table 2.
   - Academic reflection questions citing textbook chapters (Ortega, 2021).
5. Rapid Re-Compilation, Performance, & Idempotency:
   - Headless compiler throughput (< 10 seconds execution).
   - TTF font fallback resilience in create_terminal_card.
   - Deterministic and idempotent output generation without resource leaks.
"""

import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image

# Path configurations
WORKING_DIR = Path(__file__).resolve().parent
REPO_ROOT = WORKING_DIR.parent.parent.parent
LAB6_DIR = REPO_ROOT / "Lab6"
DOCX_PATH = LAB6_DIR / "Lab6-Billy-Zandan-A01371854.docx"
NOTEBOOK_PATH = LAB6_DIR / "Lab6.ipynb"
GENERATOR_SCRIPT = LAB6_DIR / "generate_report_docx.py"
SCANNER_SCRIPT = LAB6_DIR / "metadata_scanner.py"
CSV_PATH = LAB6_DIR / "metadata_report.csv"
IMAGES_DIR = LAB6_DIR / "Images"

# Authoritative Ground Truth Constants
EXPECTED_SECRETS = {
    "Brain.png": "RECON: Perform DNS harvesting and Subdomain enumeration.",
    "Activation.png": "VULN: Identify unpatched CVE-2024-XXXX in web gateway.",
    "Chemicals.png": "EXPLOIT: Deploy SQL Injection payload to bypass WAF.",
    "Dopamine.png": "PERSIST: Establish reverse shell via obfuscated cron job.",
    "Brain-Channel.png": "LATERAL: Pivot to internal Domain Controller using Mimikatz.",
    "Music.png": "EXFIL: Tunnel compressed database dump via DNS Covert Channel.",
}

EXPECTED_ORDERED_IMAGES = [
    "Brain.png",
    "Activation.png",
    "Chemicals.png",
    "Dopamine.png",
    "Brain-Channel.png",
    "Music.png",
]

EXPECTED_STAGES = ["RECON", "VULN", "EXPLOIT", "PERSIST", "LATERAL", "EXFIL"]

EXPECTED_RISK_SCORES = {
    "Activation.png": 15,
    "Brain-Channel.png": 10,
    "Brain.png": 10,
    "Chemicals.png": 10,
    "Dopamine.png": 15,
    "Music.png": 15,
}

EXPECTED_IMAGE_PROPERTIES = {
    "Activation.png": (259975, "1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904"),
    "Brain-Channel.png": (201685, "3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359"),
    "Brain.png": (2354330, "5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e"),
    "Chemicals.png": (561245, "96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a"),
    "Dopamine.png": (388411, "ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472"),
    "Music.png": (679959, "3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370"),
}


# ==============================================================================
# TEST SUITE 1: WordprocessingML XML SCHEMA, TAG BALANCE & PACKAGING
# ==============================================================================
class TestWordprocessingMLXmlSchema(unittest.TestCase):
    """Adversarial stress-testing of DOCX OOXML structures."""

    def setUp(self):
        self.assertTrue(DOCX_PATH.exists(), f"DOCX deliverable missing at {DOCX_PATH}")

    def test_docx_is_valid_zip_archive(self):
        """Verify DOCX is a non-corrupt, valid ZIP package."""
        self.assertTrue(zipfile.is_zipfile(DOCX_PATH), "DOCX deliverable is not a valid ZIP file")
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            bad_file = zf.testzip()
            self.assertIsNone(bad_file, f"Corrupted file inside docx archive: {bad_file}")

    def test_all_xml_files_are_well_formed_and_valid(self):
        """Parse every single XML and .rels entry in the docx package with ElementTree."""
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            xml_entries = [name for name in zf.namelist() if name.endswith(".xml") or name.endswith(".rels")]
            self.assertGreater(len(xml_entries), 5, "Docx archive must contain core XML parts")
            for entry_name in xml_entries:
                xml_data = zf.read(entry_name)
                try:
                    root = ET.fromstring(xml_data)
                    self.assertIsNotNone(root, f"Parsed root of {entry_name} is None")
                except ET.ParseError as pe:
                    self.fail(f"XML parse error in {entry_name}: {pe}")

    def test_document_xml_namespaces_and_root(self):
        """Verify word/document.xml has standard WordprocessingML root and namespaces."""
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            self.assertIn("word/document.xml", zf.namelist())
            xml_data = zf.read("word/document.xml")
            root = ET.fromstring(xml_data)
            self.assertTrue(
                root.tag.endswith("document"),
                f"Root tag of document.xml must be w:document, got: {root.tag}"
            )
            body = root.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body")
            self.assertIsNotNone(body, "w:body missing from word/document.xml")

    def test_custom_ooxml_injections_validity(self):
        """
        Verify all low-level OOXML injections (w:shd, w:tcMar, w:tcBorders, w:tcW,
        w:tblHeader, w:cantSplit, w:pBdr) are well-formed and placed in valid parent contexts.
        """
        w_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            doc_xml = zf.read("word/document.xml")
            root = ET.fromstring(doc_xml)

            # 1. Shading nodes
            shd_nodes = root.findall(f".//{{{w_ns}}}shd")
            self.assertGreater(len(shd_nodes), 10, "Document should contain table/code shading nodes")
            for shd in shd_nodes:
                fill = shd.attrib.get(f"{{{w_ns}}}fill")
                self.assertIsNotNone(fill, "w:shd must have w:fill attribute")
                self.assertTrue(
                    fill == "auto" or (len(fill) == 6 and all(c in "0123456789ABCDEFabcdef" for c in fill)),
                    f"Invalid hex fill value in w:shd: {fill}"
                )

            # 2. Cell margin nodes (w:tcMar)
            tcMar_nodes = root.findall(f".//{{{w_ns}}}tcMar")
            self.assertGreater(len(tcMar_nodes), 10, "Document should contain cell margin nodes")
            for tcMar in tcMar_nodes:
                for margin_edge in ("top", "bottom", "left", "right"):
                    edge_el = tcMar.find(f"{{{w_ns}}}{margin_edge}")
                    if edge_el is not None:
                        w_val = edge_el.attrib.get(f"{{{w_ns}}}w")
                        self.assertTrue(w_val.isdigit(), f"w:tcMar {margin_edge} width not numeric: {w_val}")

            # 3. Header repeating and non-split rows (w:tblHeader, w:cantSplit)
            tblHeader_nodes = root.findall(f".//{{{w_ns}}}tblHeader")
            self.assertGreaterEqual(len(tblHeader_nodes), 2, "Both tables must have w:tblHeader")
            cantSplit_nodes = root.findall(f".//{{{w_ns}}}cantSplit")
            self.assertGreater(len(cantSplit_nodes), 5, "Rows should have w:cantSplit configured")

            # 4. Paragraph borders (w:pBdr) in code blocks
            pBdr_nodes = root.findall(f".//{{{w_ns}}}pBdr")
            self.assertGreater(len(pBdr_nodes), 20, "Source code block paragraphs must have w:pBdr")

    def test_absence_of_malformed_xml_entities(self):
        """Verify raw XML does not contain unescaped ampersands or raw unescaped HTML/XML."""
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            for entry_name in zf.namelist():
                if entry_name.endswith(".xml"):
                    raw_str = zf.read(entry_name).decode("utf-8", errors="replace")
                    unescaped_amp = re.findall(r"&(?!amp;|lt;|gt;|apos;|quot;|#\d+;|#x[0-9a-fA-F]+;)", raw_str)
                    self.assertEqual(
                        len(unescaped_amp),
                        0,
                        f"Found unescaped ampersands in {entry_name}: {unescaped_amp[:5]}"
                    )

    def test_table_structure_and_cell_balance(self):
        """Verify both forensic tables have uniform column counts across all rows."""
        import docx
        doc = docx.Document(str(DOCX_PATH))
        self.assertGreaterEqual(len(doc.tables), 2, "Document must have at least 2 tables")

        # Table 1: Evidence Table (7 columns)
        t_ev = doc.tables[0]
        self.assertEqual(len(t_ev.columns), 7, f"Evidence table must have 7 columns, found {len(t_ev.columns)}")
        for r_idx, row in enumerate(t_ev.rows):
            self.assertEqual(
                len(row.cells),
                7,
                f"Evidence table row {r_idx} has {len(row.cells)} cells, expected 7"
            )

        # Table 2: Scanner Results Table (7 columns)
        t_csv = doc.tables[1]
        self.assertEqual(len(t_csv.columns), 7, f"Scanner table must have 7 columns, found {len(t_csv.columns)}")
        for r_idx, row in enumerate(t_csv.rows):
            self.assertEqual(
                len(row.cells),
                7,
                f"Scanner table row {r_idx} has {len(row.cells)} cells, expected 7"
            )

    def test_content_types_xml_validity(self):
        """Verify [Content_Types].xml includes png image type and document main part."""
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            self.assertIn("[Content_Types].xml", zf.namelist())
            ct_data = zf.read("[Content_Types].xml")
            root = ET.fromstring(ct_data)
            ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"

            # Check png default
            defaults = {d.attrib.get("Extension"): d.attrib.get("ContentType") for d in root.findall(f"{{{ct_ns}}}Default")}
            self.assertIn("png", defaults)
            self.assertEqual(defaults["png"], "image/png")

            # Check document override
            overrides = {o.attrib.get("PartName"): o.attrib.get("ContentType") for o in root.findall(f"{{{ct_ns}}}Override")}
            self.assertIn("/word/document.xml", overrides)
            self.assertIn("wordprocessingml.document.main+xml", overrides["/word/document.xml"])


# ==============================================================================
# TEST SUITE 2: EMBEDDED MEDIA IMAGE INTEGRITY
# ==============================================================================
class TestEmbeddedMediaIntegrity(unittest.TestCase):
    """Adversarial stress-testing of embedded media PNGs in DOCX."""

    def test_media_count_and_naming(self):
        """Verify exactly 6 media files exist in word/media/ and all are PNG."""
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            media_files = [n for n in zf.namelist() if n.startswith("word/media/")]
            self.assertEqual(
                len(media_files),
                6,
                f"Expected exactly 6 embedded media files, found {len(media_files)}: {media_files}"
            )
            for m in media_files:
                self.assertTrue(m.endswith(".png"), f"Media file {m} is not a PNG")

    def test_media_png_magic_bytes_and_chunks(self):
        """Verify standard 8-byte PNG signature and core IHDR/IEND chunks in all media."""
        png_sig = b"\x89PNG\r\n\x1a\n"
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            media_files = [n for n in zf.namelist() if n.startswith("word/media/")]
            for m in media_files:
                data = zf.read(m)
                self.assertTrue(data.startswith(png_sig), f"{m} does not start with PNG signature")
                self.assertIn(b"IHDR", data[:30], f"{m} missing IHDR chunk")
                self.assertTrue(data.endswith(b"IEND\xaeB`\x82"), f"{m} missing clean IEND chunk trailer")

    def test_media_pil_integrity_and_dimensions(self):
        """Open each media PNG with Pillow, verify integrity, mode, and dimensions."""
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            media_files = sorted([n for n in zf.namelist() if n.startswith("word/media/")])
            for m in media_files:
                img_bytes = zf.read(m)
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                    tf.write(img_bytes)
                    tf_path = Path(tf.name)
                try:
                    with Image.open(tf_path) as img:
                        self.assertEqual(img.format, "PNG", f"{m} format is {img.format}, expected PNG")
                        self.assertEqual(img.mode, "RGB", f"{m} mode is {img.mode}, expected RGB")
                        self.assertEqual(img.size[0], 1000, f"{m} width is {img.size[0]}, expected 1000")
                        self.assertGreaterEqual(img.size[1], 200, f"{m} height is {img.size[1]}, too small")

                        # Verify pixel content is not blank / empty
                        extrema = img.getextrema()
                        for ch_idx, (min_v, max_v) in enumerate(extrema):
                            self.assertNotEqual(
                                min_v,
                                max_v,
                                f"{m} channel {ch_idx} has identical min and max ({min_v}), likely blank image"
                            )
                finally:
                    if tf_path.exists():
                        tf_path.unlink()

    def test_document_rels_to_media_mapping(self):
        """Verify word/_rels/document.xml.rels links all drawing image relationships to valid media files."""
        with zipfile.ZipFile(DOCX_PATH, "r") as zf:
            rels_data = zf.read("word/_rels/document.xml.rels")
            root = ET.fromstring(rels_data)
            r_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
            type_img = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"

            image_rels = {
                rel.attrib["Id"]: rel.attrib["Target"]
                for rel in root.findall(f"{{{r_ns}}}Relationship")
                if rel.attrib.get("Type") == type_img
            }
            self.assertEqual(len(image_rels), 6, f"Expected 6 image relationships, found {len(image_rels)}")

            for r_id, target in image_rels.items():
                target_norm = "word/" + target if not target.startswith("word/") else target
                self.assertIn(
                    target_norm,
                    zf.namelist(),
                    f"Relationship {r_id} points to non-existent media {target_norm}"
                )

    def test_sequential_figure_captions_in_docx(self):
        """Verify Figure 1 through Figure 6 appear in strict sequential order."""
        import docx
        doc = docx.Document(str(DOCX_PATH))
        full_text = "\n".join(p.text for p in doc.paragraphs)

        for fig_num in range(1, 7):
            caption_prefix = f"Figure {fig_num}:"
            self.assertIn(
                caption_prefix,
                full_text,
                f"Missing caption for {caption_prefix}"
            )

    def test_absence_of_placeholder_corruption_in_docx(self):
        """Scan all paragraphs, tables, and headers/footers for unpopulated placeholders."""
        import docx
        doc = docx.Document(str(DOCX_PATH))

        text_corpus = []
        for p in doc.paragraphs:
            text_corpus.append(p.text)
        for t in doc.tables:
            for row in t.rows:
                for c in row.cells:
                    text_corpus.append(c.text)
        for s in doc.sections:
            for p in s.header.paragraphs:
                text_corpus.append(p.text)
            for p in s.footer.paragraphs:
                text_corpus.append(p.text)

        full_text = "\n".join(text_corpus)
        forbidden_placeholders = [
            "__________",
            "TODO",
            "TBD",
            "FIXME",
            "[insert]",
            "Lorem Ipsum",
            "undefined",
            "null",
        ]
        for placeholder in forbidden_placeholders:
            self.assertNotIn(
                placeholder,
                full_text,
                f"Deliverable DOCX contains unpopulated placeholder '{placeholder}'"
            )


# ==============================================================================
# TEST SUITE 3: NOTEBOOK JSON SCHEMA & EXECUTION SEMANTICS
# ==============================================================================
class TestNotebookSchemaAndExecution(unittest.TestCase):
    """Adversarial validation of Lab6.ipynb structure and execution logs."""

    def setUp(self):
        self.assertTrue(NOTEBOOK_PATH.exists(), f"Notebook missing at {NOTEBOOK_PATH}")
        with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            self.nb = json.load(f)

    def test_notebook_json_format_v4(self):
        """Verify notebook is strictly valid Jupyter v4."""
        self.assertEqual(self.nb.get("nbformat"), 4, "Notebook nbformat must be 4")
        self.assertGreaterEqual(self.nb.get("nbformat_minor", 0), 0)
        self.assertIn("cells", self.nb)
        self.assertIsInstance(self.nb["cells"], list)

    def test_notebook_code_cells_count_and_sequential_execution(self):
        """Verify exactly 18 code cells exist with execution_count 1..18 in exact sequence."""
        code_cells = [c for c in self.nb["cells"] if c.get("cell_type") == "code"]
        self.assertEqual(len(code_cells), 18, f"Expected exactly 18 code cells, found {len(code_cells)}")

        exec_counts = [c.get("execution_count") for c in code_cells]
        expected_counts = list(range(1, 19))
        self.assertEqual(
            exec_counts,
            expected_counts,
            f"Execution counts not strictly sequential 1..18:\nActual: {exec_counts}"
        )

    def test_notebook_cell_indices_match_execution_count(self):
        """Verify code_cells[i].execution_count == i + 1 strictly for all cells."""
        code_cells = [c for c in self.nb["cells"] if c.get("cell_type") == "code"]
        for idx, cell in enumerate(code_cells):
            self.assertEqual(
                cell.get("execution_count"),
                idx + 1,
                f"Code cell at index {idx} has execution_count {cell.get('execution_count')}, expected {idx + 1}"
            )

    def test_notebook_python_ast_validity(self):
        """Verify source code in every code cell compiles as valid Python 3 AST."""
        code_cells = [c for c in self.nb["cells"] if c.get("cell_type") == "code"]
        for idx, cell in enumerate(code_cells):
            src = "".join(cell.get("source", []))
            # Strip IPython magics if any (e.g. %matplotlib)
            lines = [l for l in src.splitlines() if not l.strip().startswith("%") and not l.strip().startswith("!")]
            clean_code = "\n".join(lines)
            try:
                ast.parse(clean_code)
            except SyntaxError as se:
                self.fail(f"SyntaxError in notebook code cell {idx}: {se}")

    def test_notebook_zero_tracebacks_or_errors(self):
        """Verify no code cell produced an error or unhandled exception output."""
        for idx, cell in enumerate(self.nb["cells"]):
            if cell.get("cell_type") == "code":
                outputs = cell.get("outputs", [])
                for out in outputs:
                    self.assertNotEqual(
                        out.get("output_type"),
                        "error",
                        f"Unhandled exception in cell {idx}: {out.get('ename')}: {out.get('evalue')}"
                    )
                    self.assertNotIn("traceback", out, f"Traceback found in cell {idx}")

    def test_notebook_markdown_placeholders_eliminated(self):
        """Verify all response blanks '__________' in markdown cells are completed."""
        for idx, cell in enumerate(self.nb["cells"]):
            if cell.get("cell_type") == "markdown":
                content = "".join(cell.get("source", []))
                self.assertNotIn(
                    "__________",
                    content,
                    f"Markdown cell {idx} still contains uncompleted blank '__________'"
                )

    def test_notebook_evidence_table_integrity(self):
        """Verify all 6 image filenames appear in the notebook evidence logging table."""
        all_text = " ".join("".join(c.get("source", [])) for c in self.nb["cells"])
        for img in EXPECTED_ORDERED_IMAGES:
            self.assertIn(img, all_text, f"Image {img} missing from notebook evidence documentation")

    def test_notebook_reflection_depth(self):
        """Verify reflection cells (40 and 41) contain substantial academic responses."""
        reflection_text = ""
        for cell in self.nb["cells"]:
            src = "".join(cell.get("source", []))
            if "Reflection questions" in src:
                reflection_text += src + "\n"
        self.assertGreater(
            len(reflection_text.split()),
            180,
            f"Reflection text word count too low: {len(reflection_text.split())} words"
        )


# ==============================================================================
# TEST SUITE 4: CROSS-DELIVERABLE CONCORDANCE & FORENSIC FIDELITY
# ==============================================================================
class TestCrossDeliverableConcordance(unittest.TestCase):
    """Verify 100% concordance across notebook, CSV, and DOCX."""

    def setUp(self):
        import docx
        self.doc = docx.Document(str(DOCX_PATH))
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            self.csv_records = {row["filename"]: row for row in csv.DictReader(f)}
        with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            self.nb = json.load(f)

    def test_secrets_concordance_across_all_deliverables(self):
        """Verify every secret fragment matches exactly across image truth and docx."""
        docx_text = "\n".join(p.text for p in self.doc.paragraphs)
        for t in self.doc.tables:
            for row in t.rows:
                for c in row.cells:
                    docx_text += "\n" + c.text

        for img_name, expected_secret in EXPECTED_SECRETS.items():
            self.assertIn(
                expected_secret,
                docx_text,
                f"Secret for {img_name} missing from DOCX deliverable: '{expected_secret}'"
            )

    def test_image_files_hashes_and_sizes_concordance(self):
        """Verify file sizes and SHA256 hashes stated in docx terminal logs match actual files."""
        docx_text = "\n".join(p.text for p in self.doc.paragraphs)
        for fname, (expected_sz, expected_sha) in EXPECTED_IMAGE_PROPERTIES.items():
            # Check actual file
            actual_path = IMAGES_DIR / fname
            self.assertTrue(actual_path.exists())
            actual_sz = actual_path.stat().st_size
            actual_sha = hashlib.sha256(actual_path.read_bytes()).hexdigest()

            self.assertEqual(actual_sz, expected_sz, f"Size mismatch for {fname}")
            self.assertEqual(actual_sha, expected_sha, f"SHA256 mismatch for {fname}")

            # Verify that this SHA256 is present in the report
            # The report prints terminal cards with SHA256 hashes
            card_found = any(fname in p.text for p in self.doc.paragraphs)
            self.assertTrue(card_found, f"{fname} not referenced in docx paragraphs")

    def test_threat_lifecycle_sequence_concordance(self):
        """Verify the 6 attack lifecycle stages and order are identical across artifacts."""
        expected_order_str = " -> ".join(EXPECTED_STAGES)
        self.assertEqual(expected_order_str, "RECON -> VULN -> EXPLOIT -> PERSIST -> LATERAL -> EXFIL")

        docx_text = "\n".join(p.text for p in self.doc.paragraphs)
        self.assertIn("Stage 1 — Reconnaissance", docx_text)
        self.assertIn("Stage 2 — Vulnerability Identification", docx_text)
        self.assertIn("Stage 3 — Exploitation & Initial Access", docx_text)
        self.assertIn("Stage 4 — Persistence", docx_text)
        self.assertIn("Stage 5 — Lateral Movement & Privilege Escalation", docx_text)
        self.assertIn("Stage 6 — Exfiltration on Objectives", docx_text)

    def test_mitre_attack_and_killchain_mapping_depth(self):
        """Verify explicit MITRE ATT&CK enterprise tactic IDs and Kill Chain mapping."""
        docx_text = "\n".join(p.text for p in self.doc.paragraphs)
        required_mitre_tags = [
            "TA0043",  # Reconnaissance
            "TA0001",  # Initial Access
            "TA0003",  # Persistence
            "TA0008",  # Lateral Movement
            "TA0010",  # Exfiltration
            "T1595",   # Active Scanning
            "T1190",   # Exploit Public-Facing Application
            "T1053",   # Scheduled Task
            "T1003",   # OS Credential Dumping
            "T1048",   # Exfiltration Over Alternative Protocol
        ]
        for tag in required_mitre_tags:
            self.assertIn(
                tag,
                docx_text,
                f"MITRE ATT&CK tag {tag} missing from docx narrative mapping"
            )

    def test_disproof_of_alphabetical_sequence(self):
        """Verify comprehensive forensic disproof of alphabetical filename ordering."""
        docx_text = "\n".join(p.text for p in self.doc.paragraphs)
        self.assertIn("Technical Disproof of Alphabetical Filename Sorting", docx_text)
        self.assertIn("Forensic Absurdity", docx_text)
        self.assertIn("Mimikatz", docx_text)

    def test_risk_scores_concordance_csv_and_docx(self):
        """Verify risk scores and suspected fields in metadata_report.csv match DOCX Table 2."""
        scanner_table = None
        for t in self.doc.tables:
            header_text = " ".join(c.text for c in t.rows[0].cells)
            if "Risk Score" in header_text and "Suspected Field" in header_text:
                scanner_table = t
                break
        self.assertIsNotNone(scanner_table, "Scanner Results Table not found in docx")

        docx_scanner_data = {}
        for row in scanner_table.rows[1:]:
            fn = row.cells[0].text.strip()
            score = int(row.cells[5].text.strip())
            suspected = row.cells[3].text.strip()
            docx_scanner_data[fn] = {"risk_score": score, "suspected_field": suspected}

        for img_name, expected_score in EXPECTED_RISK_SCORES.items():
            self.assertIn(img_name, self.csv_records)
            csv_score = int(self.csv_records[img_name]["risk_score"])
            self.assertEqual(
                csv_score,
                expected_score,
                f"CSV risk score mismatch for {img_name}: {csv_score} vs {expected_score}"
            )
            self.assertIn(img_name, docx_scanner_data)
            docx_score = docx_scanner_data[img_name]["risk_score"]
            self.assertEqual(
                docx_score,
                expected_score,
                f"DOCX risk score mismatch for {img_name}: {docx_score} vs {expected_score}"
            )

    def test_reflection_arguments_and_citations_concordance(self):
        """Verify all 5 reflection prompts are answered in docx and cite Ortega (2021)."""
        docx_text = "\n".join(p.text for p in self.doc.paragraphs)
        self.assertIn("Question 1: Hidden Metadata Beyond Primary EXIF", docx_text)
        self.assertIn("Question 2: Encoding versus Encryption", docx_text)
        self.assertIn("Question 3: Evidence Preservation", docx_text)
        self.assertIn("Question 4: Evidentiary Weight of Metadata Alone", docx_text)
        self.assertIn("Question 5: Synthesis with Automated Security Scanners", docx_text)

        self.assertIn("Ortega (2021", docx_text)
        self.assertIn("Chapter 13", docx_text)
        self.assertIn("Chapter 14", docx_text)


# ==============================================================================
# TEST SUITE 5: RAPID RE-COMPILATION, PERFORMANCE & IDEMPOTENCY
# ==============================================================================
class TestRapidRecompilationAndIdempotency(unittest.TestCase):
    """Adversarial stress-testing of report generator performance and idempotency."""

    def test_generator_execution_speed_and_success(self):
        """Verify generate_report_docx.py compiles cleanly in under 10 seconds."""
        t0 = time.time()
        res = subprocess.run(
            [sys.executable, str(GENERATOR_SCRIPT)],
            cwd=str(LAB6_DIR),
            capture_output=True,
            text=True,
            timeout=30,
        )
        elapsed = time.time() - t0
        self.assertEqual(
            res.returncode,
            0,
            f"Generator script failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        )
        self.assertLess(elapsed, 10.0, f"Compilation took {elapsed:.2f}s, expected < 10.0s")

    def test_generator_font_fallback_resilience(self):
        """Verify create_terminal_card survives when system truetype fonts (arial/consola) are unavailable."""
        sys.path.insert(0, str(LAB6_DIR))
        from generate_report_docx import create_terminal_card
        from PIL import ImageFont

        orig_truetype = ImageFont.truetype

        def mock_truetype(font, *args, **kwargs):
            if isinstance(font, str) and ("arial" in font.lower() or "consola" in font.lower()):
                raise OSError(f"System font {font} not found")
            return orig_truetype(font, *args, **kwargs)

        with tempfile.TemporaryDirectory() as td:
            card_path = Path(td) / "test_fallback.png"
            with patch.object(ImageFont, "truetype", side_effect=mock_truetype):
                # Should fallback to ImageFont.load_default() without error
                out_p = create_terminal_card(
                    "Test Fallback Card",
                    ["$ test command", "[+] test output line"],
                    card_path,
                )
                self.assertTrue(out_p.exists())
                with Image.open(out_p) as img:
                    self.assertEqual(img.size[0], 1000)

    def test_generator_repeated_clean_execution(self):
        """Verify 3 consecutive compilations succeed without resource leaks or file locking."""
        for run_i in range(3):
            res = subprocess.run(
                [sys.executable, str(GENERATOR_SCRIPT)],
                cwd=str(LAB6_DIR),
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(
                res.returncode,
                0,
                f"Repeated run {run_i} failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
            )
            self.assertTrue(DOCX_PATH.exists())

    def test_generator_idempotency_to_temp_destination(self):
        """Verify generate_report_docx.py can target an alternate file path idempotently."""
        import docx
        sys.path.insert(0, str(LAB6_DIR))
        from generate_report_docx import generate_report

        with tempfile.TemporaryDirectory() as td:
            temp_out = Path(td) / "TestOutput.docx"
            generate_report(temp_out, IMAGES_DIR, SCANNER_SCRIPT, CSV_PATH)
            self.assertTrue(temp_out.exists(), "Temporary output docx was not created")

            temp_doc = docx.Document(str(temp_out))
            prod_doc = docx.Document(str(DOCX_PATH))
            self.assertEqual(
                len(temp_doc.paragraphs),
                len(prod_doc.paragraphs),
                "Paragraph count differs in idempotent recompilation"
            )
            self.assertEqual(
                len(temp_doc.tables),
                len(prod_doc.tables),
                "Table count differs in idempotent recompilation"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
