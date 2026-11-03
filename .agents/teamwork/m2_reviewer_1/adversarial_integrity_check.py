import json
import csv
from pathlib import Path

with open("Lab6/Lab6.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# 1. Cell ID uniqueness
cell_ids = [c.get("id") for c in nb["cells"] if "id" in c]
print(f"Total cells with ID: {len(cell_ids)}, unique IDs: {len(set(cell_ids))}")
assert len(cell_ids) == len(set(cell_ids)), "Duplicate cell IDs found!"

# 2. Check metadata_report.csv vs Cell 39
with open("Lab6/metadata_report.csv", "r", encoding="utf-8") as f:
    csv_rows = list(csv.DictReader(f))

print(f"CSV report rows: {len(csv_rows)}")

# Check ground truth match
ground_truth = {
    "Activation.png": ("UserComment", 15, "VULN:"),
    "Brain-Channel.png": ("ImageDescription", 10, "LATERAL:"),
    "Brain.png": ("Software", 10, "RECON:"),
    "Chemicals.png": ("ImageDescription", 10, "EXPLOIT:"),
    "Dopamine.png": ("XML:com.adobe.xmp (exif:MakerNote)", 15, "PERSIST:"),
    "Music.png": ("Copyright", 15, "EXFIL:")
}

for row in csv_rows:
    fn = row["filename"]
    assert fn in ground_truth
    exp_field, exp_score, exp_stage = ground_truth[fn]
    assert exp_field in row["suspected_field"]
    assert int(row["risk_score"]) == exp_score
    print(f"Verified {fn}: field='{row['suspected_field']}', score={row['risk_score']}")

print("All integrity and consistency checks PASSED!")
