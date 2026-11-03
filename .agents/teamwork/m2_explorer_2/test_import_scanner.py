from pathlib import Path
import sys

for p in [Path("."), Path("Lab6")]:
    if (p / "metadata_scanner.py").exists() and str(p.resolve()) not in sys.path:
        sys.path.insert(0, str(p.resolve()))

import metadata_scanner

image_dir = Path("Lab6/Images")
results = metadata_scanner.scan_directory(
    image_dir=image_dir,
    output_csv=Path("Lab6/test_out.csv"),
    verbose=False,
    quiet=False,
)

with open("Lab6/metadata_report.csv", "r", encoding="utf-8") as f1, open("Lab6/test_out.csv", "r", encoding="utf-8") as f2:
    print("Exact match with metadata_report.csv?", f1.read().strip() == f2.read().strip())

Path("Lab6/test_out.csv").unlink()
