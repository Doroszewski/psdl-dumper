import os
from PIL import Image
from utils.texture_formats import read_file as read_tex


def dump_textures(out_materials):
    if not os.path.exists("output/texture"): os.mkdir("output/texture") 
    for m in out_materials:
        if m["texture"] != "texture/.png":
            try:
                texname = m["texture"].replace(".png", ".tex")
                tex_data = read_tex(texname)
                print("converting: " + texname + ": " + str(len(tex_data)))
                out_tex = "png_texture/" + m["texture"]
                width = int.from_bytes(tex_data[4:8], 'little')
                height = int.from_bytes(tex_data[8:12], 'little')
                fmt = int.from_bytes(tex_data[12:16], 'little')
                mips = int.from_bytes(tex_data[16:20], 'little')
                if fmt not in [3, 4]: throw("invalid texture format: " + fmt)
                data_start = 20
                data_end = data_start + width * height * fmt
                data = tex_data[data_start:data_end]
                image_out = Image.new(mode=("RGB" if fmt==3 else "RGBA"), size=(width, height))
                pixels = [tuple([data[x*fmt+y] for y in range(fmt)]) for x in range(width*height)]
                image_out.putdata(pixels)
                image_out.save("output/" + m["texture"])
            except Exception as ex:
                print("error converting: " + m["texture"] + ": " + str(ex))
