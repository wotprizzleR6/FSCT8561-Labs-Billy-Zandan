"""
Static AST and Source Code Forensic Audit of Lab6/metadata_scanner.py
"""

import ast
import re
from pathlib import Path

scanner_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_scanner.py")

with open(scanner_path, "r", encoding="utf-8") as f:
    source_code = f.read()

tree = ast.parse(source_code, filename=str(scanner_path))

print(f"=== AST Audit of {scanner_path.name} ===")
print(f"File size: {len(source_code)} bytes, lines: {len(source_code.splitlines())}")

# 1. Search for hardcoded image filenames
target_images = [
    "Activation.png", "Brain-Channel.png", "Brain.png",
    "Chemicals.png", "Dopamine.png", "Music.png",
    "Activation", "Brain-Channel", "Brain",
    "Chemicals", "Dopamine", "Music"
]

found_references = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        val = node.value
        for img in target_images:
            if img.lower() == val.lower():
                found_references.append((node.lineno, val))

print(f"\n1. Direct image filename string literals found: {len(found_references)}")
for lineno, val in found_references:
    print(f"   Line {lineno}: '{val}'")

# 2. Search for all string constants that might contain hardcoded secret fragments or outputs
print("\n2. Checking string constants against secret narrative contents:")
suspicious_secret_strings = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        val = node.value
        if any(kw in val.lower() for kw in ["dns harvesting", "subdomain enumeration", "cve-2024", "mimikatz", "cron job", "waf"]):
            # Check if this is within THREAT_KEYWORDS or somewhere else
            suspicious_secret_strings.append((node.lineno, val))

for lineno, val in suspicious_secret_strings:
    print(f"   Line {lineno}: {repr(val)}")

# 3. Search for function definitions and check if any return constant without computation (facades)
print("\n3. Inspecting all functions for facade / dummy implementations:")
functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
for fn in functions:
    body_nodes = fn.body
    # Check if docstring is first
    non_doc = [b for b in body_nodes if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant) and isinstance(b.value.value, str))]
    is_facade = False
    if len(non_doc) == 1 and isinstance(non_doc[0], ast.Return) and isinstance(non_doc[0].value, ast.Constant):
        is_facade = True
    elif len(non_doc) == 1 and isinstance(non_doc[0], ast.Pass):
        is_facade = True
    elif len(non_doc) == 1 and isinstance(non_doc[0], ast.Raise):
        if isinstance(non_doc[0].exc, ast.Call) and getattr(non_doc[0].exc.func, "id", "") == "NotImplementedError":
            is_facade = True
    print(f"   Function '{fn.name}' (lines {fn.lineno}-{fn.end_lineno}): {len(body_nodes)} statements, Facade={is_facade}")

# 4. Check for dictionary lookups keyed by filename
print("\n4. Checking for dictionary mappings that could act as lookup tables:")
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        keys = []
        for k in node.keys:
            if isinstance(k, ast.Constant):
                keys.append(str(k.value))
        if any(any(img in k for img in ["Activation", "Brain", "Chemicals", "Dopamine", "Music"]) for k in keys):
            print(f"   Line {node.lineno}: Suspicious Dict keyed by image names: {keys}")
