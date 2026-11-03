import json
import re
from pathlib import Path

EXPECTED_IMAGES = [
    "Activation.png",
    "Brain-Channel.png",
    "Brain.png",
    "Chemicals.png",
    "Dopamine.png",
    "Music.png",
]

EXPECTED_STAGES = [
    "RECON",
    "VULN",
    "EXPLOIT",
    "PERSIST",
    "LATERAL",
    "EXFIL",
]

EXPECTED_SECRETS = {
    "Brain.png": "RECON: Perform DNS harvesting and Subdomain enumeration.",
    "Activation.png": "VULN: Identify unpatched CVE-2024-XXXX in web gateway.",
    "Chemicals.png": "EXPLOIT: Deploy SQL Injection payload to bypass WAF.",
    "Dopamine.png": "PERSIST: Establish reverse shell via obfuscated cron job.",
    "Brain-Channel.png": "LATERAL: Pivot to internal Domain Controller using Mimikatz.",
    "Music.png": "EXFIL: Tunnel compressed database dump via DNS Covert Channel.",
}

def verify_notebook(nb_path: Path):
    print(f"=== Verifying Notebook: {nb_path.name} ===")
    assert nb_path.exists(), f"Notebook file {nb_path} does not exist"
    
    with open(nb_path, "r", encoding="utf-8") as f:
        nb_data = json.load(f)
        
    # Check 1: JSON structure and nbformat
    assert nb_data.get("nbformat") == 4, f"Expected nbformat 4, got {nb_data.get('nbformat')}"
    assert "cells" in nb_data, "Missing 'cells' key in notebook"
    print("[PASS] Check 1: Notebook JSON structure is valid nbformat v4.")
    
    # Check 2: All code cells have non-null execution count
    code_cells = [c for c in nb_data["cells"] if c.get("cell_type") == "code"]
    non_empty_code_cells = [c for c in code_cells if "".join(c.get("source", "")).strip()]
    print(f"  Found {len(code_cells)} code cells ({len(non_empty_code_cells)} non-empty).")
    for idx, c in enumerate(non_empty_code_cells):
        ec = c.get("execution_count")
        assert ec is not None, f"Code cell {idx} execution_count is None"
        assert isinstance(ec, int) and ec > 0, f"Code cell {idx} execution_count is not positive int: {ec}"
    print(f"[PASS] Check 2: All {len(non_empty_code_cells)} non-empty code cells executed with valid execution_count.")
    
    # Check 3: No error outputs in any code cell
    error_count = 0
    for idx, c in enumerate(code_cells):
        for out in c.get("outputs", []):
            if out.get("output_type") == "error":
                print(f"  [ERROR] Cell {idx} failed with {out.get('ename')}: {out.get('evalue')}")
                error_count += 1
    assert error_count == 0, f"Found {error_count} error outputs in code cells"
    print("[PASS] Check 3: Zero unhandled exceptions or error outputs across all code cells.")
    
    # Check 4: Cell outputs contain all 6 stage strings
    all_output_text = ""
    for c in code_cells:
        for out in c.get("outputs", []):
            for line in out.get("text", []):
                all_output_text += line
    for stage in EXPECTED_STAGES:
        assert stage in all_output_text, f"Missing stage '{stage}' in notebook cell outputs"
    print(f"[PASS] Check 4: All 6 stage keywords ({', '.join(EXPECTED_STAGES)}) present in notebook outputs.")
    
    # Check 5: No placeholder strings "__________" in any cell
    all_text = " ".join("".join(c.get("source", [])) for c in nb_data["cells"])
    assert "__________" not in all_text, "Found unpopulated '__________' placeholders in notebook"
    print("[PASS] Check 5: No unpopulated '__________' placeholders in notebook text.")
    
    # Check 6: Evidence table contains all six images
    for img in EXPECTED_IMAGES:
        assert img in all_text, f"Image {img} not documented in notebook text"
    print("[PASS] Check 6: All six image names documented in notebook evidence table.")
    
    # Check 7: Reflection questions populated with substantive depth (>150 words)
    reflection_cell = None
    for cell in nb_data["cells"]:
        text = "".join(cell.get("source", []))
        if "Reflection questions" in text:
            reflection_cell = cell
            break
    assert reflection_cell is not None, "Reflection questions cell not found"
    ref_text = "".join(reflection_cell.get("source", []))
    word_count = len(ref_text.split())
    assert word_count > 150, f"Reflection word count {word_count} is too low (expected > 150)"
    print(f"[PASS] Check 7: Reflection questions thoroughly answered ({word_count} words).")
    
    print("\n=== ALL VERIFICATION CHECKS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    nb_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_explorer_3\prototype_Lab6.ipynb")
    verify_notebook(nb_path)
