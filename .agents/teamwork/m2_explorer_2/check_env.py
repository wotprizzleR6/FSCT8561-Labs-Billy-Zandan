import sys

modules = ['PIL', 'defusedxml', 'pandas', 'docx', 'nbformat', 'nbconvert', 'ipykernel', 'csv', 'base64', 'xml.etree.ElementTree']
for mod in modules:
    try:
        m = __import__(mod)
        ver = getattr(m, '__version__', 'builtin')
        print(f"{mod}: available ({ver})")
    except ImportError as e:
        print(f"{mod}: NOT available ({e})")

print("Python executable:", sys.executable)
print("Python version:", sys.version)
