import hashlib
import json
import os
import sys
import tempfile
import shutil
import ast
from pathlib import Path

# Paths
REPO_ROOT = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan")
LAB6_DIR = REPO_ROOT / "Lab6"
NOTEBOOK_PATH = LAB6_DIR / "Lab6.ipynb"
IMAGES_DIR = LAB6_DIR / "Images"

EXPECTED_HASHES = {
    "Activation.png": "1730dd6126823fad076525d816d825e41817f824fe9fd865e5b5908445b81904",
    "Brain-Channel.png": "3c50c3751221ebe33d7638f0006258727988fec5525c3c968105dbad74120359",
    "Brain.png": "5eeb270a3281efe74c48c3114bb4c48a1f6848007d61adbb05e34a70d1bc792e",
    "Chemicals.png": "96e549e35a1ba22500b1a53fa51b2aacb33a2bf553d2559378a9ca096f77e30a",
    "Dopamine.png": "ae5dcf7e7a71c6db771349b6e2f208d28a450db630cf386da7dd26a53b65d472",
    "Music.png": "3416149b1aaa35ce306cf0f642cac251dec1e1398f8b215626123bef1cdf6370"
}

def check_image_hashes():
    print("=== CHECK 1: Cryptographic Hashes of Evidence Images ===")
    all_match = True
    actual_hashes = {}
    for filename, expected in EXPECTED_HASHES.items():
        filepath = IMAGES_DIR / filename
        if not filepath.exists():
            print(f"[FAIL] Missing image file: {filename}")
            all_match = False
            continue
        h = hashlib.sha256(filepath.read_bytes()).hexdigest().lower()
        actual_hashes[filename] = h
        if h == expected.lower():
            print(f"[PASS] {filename}: {h} MATCH")
        else:
            print(f"[FAIL] {filename}: expected {expected}, got {h}")
            all_match = False
    return all_match, actual_hashes

def analyze_notebook_cells():
    print("\n=== CHECK 2: Static Analysis of Lab6.ipynb ===")
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb_data = json.load(f)
    
    cells = nb_data.get("cells", [])
    print(f"Total cells: {len(cells)}")
    
    code_cells = [c for c in cells if c.get("cell_type") == "code"]
    markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]
    print(f"Code cells: {len(code_cells)}, Markdown cells: {len(markdown_cells)}")
    
    exec_counts = []
    has_errors = False
    facade_detected = False
    canned_print_detected = False
    
    for idx, cell in enumerate(cells):
        ctype = cell.get("cell_type")
        source = "".join(cell.get("source", []))
        
        if ctype == "code":
            ec = cell.get("execution_count")
            exec_counts.append(ec)
            outputs = cell.get("outputs", [])
            
            # Check for error outputs
            for out in outputs:
                if out.get("output_type") == "error":
                    print(f"[FAIL] Cell {idx} has error output: {out.get('ename')}: {out.get('evalue')}")
                    has_errors = True
            
            # Parse Python AST to inspect statements
            try:
                tree = ast.parse(source)
                # Check for facade: function that only returns constant
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # check if body is just a Return with constant
                        if len(node.body) == 1 and isinstance(node.body[0], ast.Return):
                            val = node.body[0].value
                            if isinstance(val, (ast.Constant, ast.Str)):
                                print(f"[WARN/FLAG] Cell {idx} function {node.name} is a facade returning constant: {ast.dump(val)}")
                                facade_detected = True
            except Exception as e:
                # Syntax error or IPython magic
                print(f"[NOTE] Cell {idx} ast parse notice: {e}")
                
            # Check if cell prints covert text without actually loading/opening images or libraries
            # e.g., print("RECON: ...") without Image or Path or open
            stage_tokens = ["RECON:", "VULN:", "EXPLOIT:", "PERSIST:", "LATERAL:", "EXFIL:"]
            has_stage_in_source = any(st in source for st in stage_tokens)
            has_img_access = any(k in source for k in ["Image.open", "open(", "Path(", "Images", "metadata_scanner"])
            if has_stage_in_source and not has_img_access:
                # Is it just printing hardcoded string?
                print(f"[FLAG] Cell {idx} contains stage token in source code without image access: {source[:100]}...")
                canned_print_detected = True
                
    print(f"Execution counts: {exec_counts}")
    is_sequential = exec_counts == list(range(1, len(code_cells) + 1))
    print(f"Execution counts strictly sequential (1..{len(code_cells)}): {is_sequential}")
    
    return {
        "total_cells": len(cells),
        "code_cells": len(code_cells),
        "markdown_cells": len(markdown_cells),
        "is_sequential": is_sequential,
        "has_errors": has_errors,
        "facade_detected": facade_detected,
        "canned_print_detected": canned_print_detected,
    }

if __name__ == "__main__":
    h_ok, hashes = check_image_hashes()
    nb_res = analyze_notebook_cells()
    print("\nSummary:", {"hashes_ok": h_ok, "nb_res": nb_res})
