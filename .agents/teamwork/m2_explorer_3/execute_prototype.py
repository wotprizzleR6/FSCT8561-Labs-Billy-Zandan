import sys
import asyncio
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

LAB6_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6")
WORK_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_explorer_3")
NB_PATH = WORK_DIR / "prototype_Lab6.ipynb"

print(f"Reading notebook from: {NB_PATH}")
with open(NB_PATH, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

print("Starting in-place execution via ExecutePreprocessor...")
ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
ep.preprocess(nb, {"metadata": {"path": str(LAB6_DIR)}})

print("Saving executed notebook in place...")
with open(NB_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("Execution completed successfully!")
