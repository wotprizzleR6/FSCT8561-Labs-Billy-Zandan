import subprocess
import os

interpreters = [
    r"C:\Users\BillyZ\AppData\Local\Programs\Python\Python314\python.exe",
    r"C:\Users\BillyZ\anaconda3\python.exe",
    r"C:\Users\BillyZ\miniconda3\python.exe",
    r"C:\Users\BillyZ\miniconda3\envs\whisper-env\python.exe",
]

script = r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\explorer_survey_3\check_env.py"

for py in interpreters:
    print("=" * 60)
    print("Testing:", py)
    if os.path.exists(py):
        res = subprocess.run([py, script], capture_output=True, text=True)
        print(res.stdout)
        if res.stderr:
            print("STDERR:", res.stderr)
    else:
        print("Path does not exist.")
