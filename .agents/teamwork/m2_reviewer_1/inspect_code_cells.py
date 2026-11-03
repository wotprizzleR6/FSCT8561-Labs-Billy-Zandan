import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("Lab6/Lab6.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        ec = cell.get('execution_count')
        print(f"\n========================================================")
        print(f"CELL {idx} [CODE] Execution Count: {ec}")
        print(f"========================================================")
        print("--- SOURCE ---")
        print("".join(cell.get('source', [])))
        print("--- OUTPUTS ---")
        for out in cell.get('outputs', []):
            otype = out.get('output_type')
            if otype == 'stream':
                print(f"[stream: {out.get('name')}]")
                print("".join(out.get('text', [])))
            elif otype in ('execute_result', 'display_data'):
                print(f"[{otype}]")
                for k, v in out.get('data', {}).items():
                    print(f"  ({k}): {''.join(v) if isinstance(v, list) else v}")
            else:
                print(f"[{otype}]: {out}")
