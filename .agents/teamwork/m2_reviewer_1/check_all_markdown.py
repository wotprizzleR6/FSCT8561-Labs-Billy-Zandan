import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Lab6/Lab6.ipynb', encoding='utf-8') as f:
    nb = json.load(f)

for idx, c in enumerate(nb['cells']):
    src = ''.join(c.get('source', []))
    if c['cell_type'] == 'markdown':
        lines = [line.strip() for line in src.splitlines() if line.strip()]
        last_line = lines[-1] if lines else "EMPTY"
        first_line = lines[0] if lines else "EMPTY"
        print(f"MD Cell {idx:02d} (len {len(src):5d}) | First: {first_line[:40]:40s} | Last: {last_line[:40]}")
