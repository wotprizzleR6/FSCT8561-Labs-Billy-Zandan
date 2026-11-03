"""
Test malformed XML behaviors.
"""
import re
import xml.etree.ElementTree as ET

# Case 1: unclosed exif:MakerNote
x1 = "<x:xmpmeta><exif:MakerNote>EXPLOIT: Malformed XML</x:xmpmeta>"
m1 = re.search(r"<exif:MakerNote>(.*?)</exif:MakerNote>", x1)
print("Case 1 (unclosed MakerNote) regex match:", m1)

# Case 2: XML syntax error elsewhere (unclosed other tag, bad entity, etc.)
x2 = "<x:xmpmeta><unclosed_tag><exif:MakerNote>EXPLOIT: Malformed XML</exif:MakerNote></x:xmpmeta>"
try:
    ET.fromstring(x2)
    print("Case 2 parsed with ET")
except Exception as e:
    print("Case 2 ET failed as expected:", e)
    m2 = re.search(r"<exif:MakerNote>(.*?)</exif:MakerNote>", x2)
    print("Case 2 regex match:", m2.group(1) if m2 else None)
