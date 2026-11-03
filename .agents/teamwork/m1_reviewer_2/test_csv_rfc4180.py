import csv
from pathlib import Path

csv_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\metadata_report.csv")
raw = csv_path.read_bytes()

print(f"Total bytes: {len(raw)}")
crlf_count = raw.count(b"\r\n")
lf_count = raw.count(b"\n")
lone_lf = lf_count - crlf_count
print(f"CRLF line terminators: {crlf_count}")
print(f"Lone LF line terminators: {lone_lf}")
assert crlf_count == 7, f"Expected 7 CRLF line terminators (RFC 4180), found {crlf_count}"
assert lone_lf == 0, f"Expected 0 lone LF line terminators, found {lone_lf}"

# Check for RFC 4180 quoting rules
# 1. Header has 7 fields
# 2. Each record on a separate line
# 3. Trailing CRLF optional/permitted
# 4. Each field containing comma enclosed in double quotes
with open(csv_path, "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    rows = list(reader)

for r_idx, row in enumerate(rows):
    assert len(row) == 7, f"Row {r_idx} does not have 7 fields"
    for f_idx, field in enumerate(row):
        # Verify no unprintable ASCII controls
        for ch in field:
            assert ord(ch) >= 32 or ch in "\t", f"Control char {ord(ch)} found in row {r_idx} field {f_idx}"

print("RFC 4180 verification passed cleanly!")
