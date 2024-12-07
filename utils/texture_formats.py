# Decoder for Angel Studios TEX format, as described here: https://github.com/Dummiesman/angel-file-formats/blob/master/Midtown%20Madness%202/TEX.md
# extra info (MC2 DXT) from here: http://web.archive.org/web/20230513223648/https://wiki.xentax.com/index.php/Midnight_Club_TEX
import sys
import math

from utils.file_io import BinaryFileHelper


def read_mapped_pixels(f, length, color_map):
    data = f.read_bytes(length)
    return [color_map[data[i]] for i in range(length)]

def read_nibble_mapped_pixels(f, length, color_map):
    res = [None for i in range(length)]
    data = f.read_bytes(length)
    for i in range(0, length, 2):
        val = data[i/2]
        val1 = val & 0x0F
        val2 = (val >> 4) & 0x0F
        res[i] = color_map[val1]
        res[i + 1] = color_map[val2]
    return res

def read_pixels(f, length, typ, with_alpha):
    if typ == 0 and with_alpha: #palette - with alpha
        data = f.read_bytes(4*length)
        res = [bytes((data[i+2], data[i+1], data[i+0], data[i+3])) for i in range(0, length*4, 4)]
    elif typ == 0 and not with_alpha: #palette - without alpha
        data = f.read_bytes(4*length)
        res = [bytes((data[i+2], data[i+1], data[i+0])) for i in range(0, length*4, 4)]
    elif typ == 3: #rgb
        data = f.read_bytes(3*length)
        res = [data[i:i+3] for i in range(0, length*3, 3)]
    elif typ == 4: #rgba
        data = f.read_bytes(4*length)
        res = [data[i:i+4] for i in range(0, length*4, 4)]
    elif typ == 22: #dxt1
        res = f.read_bytes(4 * length)
    elif typ == 26: #dxt5
        res = f.read_bytes(8 * length)
    return res

def read_file(path):
    f = BinaryFileHelper(path, 'rb')
    width = f.read_uint16()
    height = f.read_uint16()
    typ = f.read_uint16()
    mips = f.read_uint16()
    unknown = f.read_uint16()
    bits = f.read_uint32()
    with_alpha = typ == 14 or typ == 16 or typ == 18
    dxt1 = typ == 22
    dxt5 = typ == 26
    if dxt1:
        fmt = 10 #DXT1
    elif dxt5:
        fmt = 12 #DXT5
    elif with_alpha:
        fmt = 4 #RGBA32
    else:
        fmt = 3 #RGB24

    #reported mips are wrong sometimes, check if too big
    if width > 0 and height > 0:
        max_mips = (int)(math.log(min(width, height), 2) + 1)
        if mips > max_mips: mips = max_mips


    unknown = typ not in [1, 14, 15, 16, 17, 18, 22, 26]
    if unknown: #unknown type, return empty texture
        width = 1
        height = 1
        fmt = 4
        mips = 1

    tex = bytearray(4)
    tex += width.to_bytes(4, 'little')
    tex += height.to_bytes(4, 'little')
    tex += fmt.to_bytes(4, 'little')
    tex += mips.to_bytes(4, 'little')

    if unknown: #unknown type, return empty texture
        f.close()
        p = 0
        tex += p.to_bytes(4, 'little')
        return tex

    if typ==1 or typ == 14:
        color_map = read_pixels(f, 256, 0, with_alpha)
    elif typ == 15 or typ == 16:
        color_map = read_pixels(f, 16, 0, with_alpha)
    for m in range(mips):
        w_m = width >> m
        h_m = height >> m
        if typ == 1 or typ == 14:
            pixels = read_mapped_pixels(f, w_m * h_m, color_map)
        elif typ == 15 or typ == 16:
            pixels = read_nibble_mapped_pixels(f, w_m * h_m, color_map)
        elif typ == 17:
            pixels = read_pixels(f, w_m * h_m, 3, with_alpha)
        elif typ == 18:
            pixels = read_pixels(f, w_m * h_m, 4, with_alpha)
        elif typ == 22 or typ == 26:
            pixels = read_pixels(f, w_m * h_m, typ, False)
        if typ == 22 or typ == 26:
            tex += pixels
        else:
            for y in range(h_m - 1, -1, -1):
                yw = y * w_m
                for x in range(w_m):
                    tex += pixels[yw + x]
    f.close()
    return tex
