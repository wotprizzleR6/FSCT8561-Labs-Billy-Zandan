import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

nb_path = r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3\test_nb.ipynb"

with open(nb_path, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
ep.preprocess(nb, {"metadata": {"path": r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3"}})

with open(nb_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("Notebook programmatically executed and saved successfully!")
