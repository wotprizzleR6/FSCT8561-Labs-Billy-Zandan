import json
from pathlib import Path

nb_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx, cell in enumerate(nb["cells"]):
    ctype = cell.get("cell_type")
    if ctype == "code":
        ec = cell.get("execution_count")
        src = "".join(cell.get("source", []))
        outputs = cell.get("outputs", [])
        out_summary = []
        for o in outputs:
            otype = o.get("output_type")
            if otype == "stream":
                txt = "".join(o.get("text", []))
                out_summary.append(f"stream({len(txt)} chars, starts: {repr(txt[:60])})")
            elif otype == "execute_result":
                txt = repr(o.get("data", {}))
                out_summary.append(f"execute_result({len(txt)} chars)")
            elif otype == "error":
                out_summary.append(f"ERROR({o.get('ename')})")
            else:
                out_summary.append(otype)
        print(f"--- Code Cell {idx} [exec_count: {ec}] ---")
        first_lines = src.strip().split("\n")[:4]
        for l in first_lines:
            print(f"  src: {l}")
        print(f"  outputs: {out_summary}")
