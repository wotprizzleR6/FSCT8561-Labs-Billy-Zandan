"""
Pure-Python stepic implementation conforming to standard Stepic specification.
"""
from PIL import Image

def encode_imdata(imdata, data):
    datalen = len(data)
    if datalen == 0:
        raise ValueError("data is empty")
    imdata = iter(imdata)
    for i in range(datalen):
        p1 = list(next(imdata))
        p2 = list(next(imdata))
        p3 = list(next(imdata))
        channels = [c & ~1 for c in (p1[:3] + p2[:3] + p3[:3])]
        byte = data[i] if isinstance(data[i], int) else ord(data[i])
        for j in range(7, -1, -1):
            channels[j] |= (byte & 1)
            byte >>= 1
        if i == datalen - 1:
            channels[8] |= 1
        yield tuple(channels[0:3] + p1[3:])
        yield tuple(channels[3:6] + p2[3:])
        yield tuple(channels[6:9] + p3[3:])

def encode(image, data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    pixels = list(image.getdata())
    needed_pixels = len(data) * 3
    if needed_pixels > len(pixels):
        raise ValueError(f"Payload requires {needed_pixels} pixels, but image only has {len(pixels)}")
    
    encoded_gen = encode_imdata(pixels, data)
    new_pixels = list(encoded_gen)
    # Remaining unchanged pixels
    new_pixels.extend(pixels[len(new_pixels):])
    
    out = Image.new(image.mode, image.size)
    out.putdata(new_pixels)
    return out

def decode(image):
    imdata = iter(image.getdata())
    res = bytearray()
    while True:
        try:
            p1 = next(imdata)
            p2 = next(imdata)
            p3 = next(imdata)
        except StopIteration:
            break
        channels = list(p1[:3] + p2[:3] + p3[:3])
        byte = 0
        for c in range(7):
            byte |= (channels[c] & 1)
            byte <<= 1
        byte |= (channels[7] & 1)
        res.append(byte)
        if channels[8] & 1:
            break
    return bytes(res)
