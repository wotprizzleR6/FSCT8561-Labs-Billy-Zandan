import json
import re
from pathlib import Path

test_nb_path = Path(".agents/teamwork/m2_explorer_2/executed_test_nb.ipynb")
with open(test_nb_path, "r", encoding="utf-8") as f:
    nb_data = json.load(f)

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

# 1. Check valid json
assert nb_data["nbformat"] == 4
assert len(nb_data["cells"]) >= 40
print("Check 1 (valid json & len >= 40): PASS")

# 2. Check all code cells executed
code_cells = [c for c in nb_data["cells"] if c["cell_type"] == "code" and "".join(c.get("source", "")).strip()]
assert len(code_cells) > 0
for idx, c in enumerate(code_cells):
    assert c.get("execution_count") is not None, f"Code cell {idx} not executed"
    assert isinstance(c.get("execution_count"), int)
    assert c.get("execution_count") > 0
print(f"Check 2 (all {len(code_cells)} code cells executed with valid positive count): PASS")

# 3. Check no unhandled exceptions
for idx, cell in enumerate(nb_data["cells"]):
    if cell["cell_type"] == "code":
        for out in cell.get("outputs", []):
            assert out.get("output_type") != "error", f"Error in cell {idx}: {out}"
print("Check 3 (no error outputs): PASS")

# 4. Check no unpopulated placeholders
all_text = " ".join("".join(c.get("source", [])) for c in nb_data["cells"])
assert "__________" not in all_text, "Found unpopulated placeholders"
for img in EXPECTED_IMAGES:
    assert img in all_text, f"Image {img} missing from markdown text"
print("Check 4 (no '__________' placeholders, all 6 images present in text): PASS")

# 5. Check reflection questions cell
reflection_cell = None
for cell in nb_data["cells"]:
    text = "".join(cell.get("source", []))
    if "Reflection questions" in text:
        reflection_cell = cell
        break
assert reflection_cell is not None, "Reflection questions cell not found"
ref_content = "".join(reflection_cell.get("source", []))
word_count = len(ref_content.split())
assert word_count > 150, f"Word count too small: {word_count}"
print(f"Check 5 (reflection questions answered with {word_count} words > 150): PASS")

# 6. Check cell outputs contain all stages
all_outputs = ""
for cell in nb_data["cells"]:
    for out in cell.get("outputs", []):
        for text_val in out.get("text", []):
            all_outputs += text_val
for stage in EXPECTED_STAGES:
    assert stage in all_outputs, f"Stage {stage} not present in cell outputs"
print("Check 6 (all 6 stages present in code cell outputs): PASS")

# 7. Check rubric prompts preserved
assert "Grading rubric" in all_text
assert "Reflection questions" in all_text
print("Check 7 (rubric and reflection prompts preserved): PASS")

print("\nALL VERIFICATION CHECKS PASSED PERFECTLY!")
