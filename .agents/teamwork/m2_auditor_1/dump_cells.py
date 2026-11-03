import json
from pathlib import Path

nb_path = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Lab6.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

out_log = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_auditor_1\code_cells_dump.txt")

with open(out_log, "w", encoding="utf-8") as out:
    for idx, cell in enumerate(nb["cells"]):
        ctype = cell.get("cell_type")
        if ctype == "code":
            ec = cell.get("execution_count")
            src = "".join(cell.get("source", []))
            outputs = cell.get("outputs", [])
            out.write(f"======================================================================\n")
            out.write(f"CELL {idx} [exec_count: {ec}]\n")
            out.write(f"----------------------------- SOURCE ---------------------------------\n")
            out.write(src + "\n")
            out.write(f"----------------------------- OUTPUTS --------------------------------\n")
            for o_idx, o in enumerate(outputs):
                otype = o.get("output_type")
                out.write(f"  [Output {o_idx}: {otype}]\n")
                if otype == "stream":
                    out.write("".join(o.get("text", [])) + "\n")
                elif otype == "execute_result":
                    out.write(json.dumps(o.get("data", {}), indent=2) + "\n")
                elif otype == "error":
                    out.write(f"ERROR: {o.get('ename')}: {o.get('evalue')}\n")
                    for tr in o.get("traceback", []):
                        out.write(f"    {tr}\n")
                else:
                    out.write(str(o) + "\n")
            out.write("\n")

print(f"Dumped code cells to {out_log}")
