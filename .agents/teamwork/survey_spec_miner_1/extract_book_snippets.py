import pypdf
from pathlib import Path

lab6_dir = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6")

# Inspect Ortega's book around pages 798-825
ortega_pdf = list(lab6_dir.glob("Mastering Python*"))[0]
reader1 = pypdf.PdfReader(str(ortega_pdf))
print("=== ORTEGA: CHAPTER & CONTENT AROUND PAGES 798-825 ===")
for p in range(798, 822):
    txt = reader1.pages[p].extract_text()
    first_few_lines = "\n".join([line for line in txt.splitlines()[:5] if line.strip()])
    print(f"--- Page {p+1} ---")
    print(first_few_lines)
    if "def " in txt or "import " in txt or "class " in txt:
        print("  [Contains Code Snippets]")

# Inspect Sarwar's book table of contents
sarwar_pdf = list(lab6_dir.glob("Python Ethical Hacking*"))[0]
reader2 = pypdf.PdfReader(str(sarwar_pdf))
print("\n=== SARWAR: TABLE OF CONTENTS / CHAPTERS ===")
for p in range(0, 20):
    txt = reader2.pages[p].extract_text()
    if "Chapter" in txt or "Contents" in txt or "Table" in txt:
        print(f"--- Page {p+1} ---")
        for line in txt.splitlines():
            if any(term in line.lower() for term in ["chapter", "forensic", "crypto", "attack", "recon", "dns", "sniff", "payload", "shell", "covert"]):
                print(" ", line.strip())
