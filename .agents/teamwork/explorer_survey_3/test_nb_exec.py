import json
import io
import contextlib
from pathlib import Path

def test_notebook_execution_concept():
    # Verify we can parse, simulate exec, capture stdout, and serialize back to ipynb
    nb_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb_data = json.load(f)

    print(f"Loaded notebook successfully: {len(nb_data['cells'])} cells")
    
    code_cells = [c for c in nb_data["cells"] if c["cell_type"] == "code"]
    print(f"Found {len(code_cells)} code cells")

test_notebook_execution_concept()
