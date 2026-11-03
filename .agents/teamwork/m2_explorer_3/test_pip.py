import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

test_nb_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_explorer_3\test_pip.ipynb")
nb = nbformat.v4.new_notebook()
nb.cells.append(nbformat.v4.new_code_cell("%pip -q install Pillow"))
nb.cells.append(nbformat.v4.new_code_cell("from PIL import Image\nprint('Pillow imported successfully!')"))

ep = ExecutePreprocessor(timeout=60, kernel_name="python3")
ep.preprocess(nb, {"metadata": {"path": r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6"}})

with open(test_nb_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("Execution complete!")
for cell in nb.cells:
    for out in cell.outputs:
        print("OUT:", out.get("output_type"), out.get("text", out.get("ename", "")))
