import sys
import importlib.util

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")

packages = [
    ("PIL (Pillow)", "PIL"),
    ("Pillow", "pillow"),
    ("exifread", "exifread"),
    ("piexif", "piexif"),
    ("exiftool / PyExifTool", "exiftool"),
    ("xmltodict", "xmltodict"),
    ("defusedxml", "defusedxml"),
    ("python-docx", "docx"),
    ("pandas", "pandas"),
    ("jupyter", "jupyter"),
    ("nbformat", "nbformat"),
    ("nbconvert", "nbconvert"),
    ("ipykernel", "ipykernel"),
]

for display_name, mod_name in packages:
    spec = importlib.util.find_spec(mod_name)
    if spec is not None:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "installed")
            print(f"[FOUND] {display_name}: version {ver}")
        except Exception as e:
            print(f"[ERROR importing] {display_name}: {e}")
    else:
        print(f"[NOT FOUND] {display_name}")
