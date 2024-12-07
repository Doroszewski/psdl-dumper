#format info here: https://github.com/Dummiesman/angel-file-formats/blob/master/Midtown%20Madness%202/PSDL.md

import math, json, sys, os
from utils.file_io import BinaryFileHelper
from utils.gltf import to_gltf
from utils.tex_dumper import dump_textures
from psdl.attribute_parser import decode_attribute
from psdl.geometry_expander.main import get_object

# Process command line arguments
dump_json = False
with_textures = False
argv = sys.argv[1:]
if "-dump_json" in argv:
    dump_json = True
    argv.remove("-dump_json")

if "-dump_textures" in argv:
    with_textures = True
    argv.remove("-dump_textures")

if len(argv) != 1:
    print("arguments: psdl file, flags: -dump_json, -dump_textures")
    exit()

in_psdl_file = argv[0]

# Read the PSDL
print("reading psdl...")

def read_perimeter_point(file):
    vertex = file.read_uint16()
    room = file.read_uint16()
    return {"vertex": vertex, "room": room}

def read_room(file):
    nPerimeterPoints = file.read_uint32()
    attributeSize = file.read_uint32()
    perimeter = [read_perimeter_point(file) for i in range(nPerimeterPoints)]
    attributes = [file.read_uint16() for i in range(attributeSize)]
    return {"attributes": attributes, "perimeter": perimeter}

def read_paths(file):
    unknown4 = file.read_uint16()
    unknown5 = file.read_uint16()
    nFLanes = file.read_byte()
    nBLanes = file.read_byte()
    density = [file.read_float() for i in range(nFLanes + nBLanes)]
    unknown6 = file.read_uint16()
    startCrossroads = [file.read_uint16() for i in range(4)]
    endCrossroads = [file.read_uint16() for i in range(4)]
    nRoadBlocks = int(file.read_byte())
    roadBlocks = [file.read_uint16() for i in range(nRoadBlocks)]

file = BinaryFileHelper(in_psdl_file, 'rb')
header = str(file.file.read(4), 'utf-8')
if header != "PSD0":
    print("not a psdl file")
    exit()
targetsize = file.read_uint32()

nVertices = file.read_uint32()
cVertices = [file.read_vec3() for i in range(nVertices)]

nFloats = file.read_uint32()
floats = [file.read_float() for i in range(nFloats)]

nTextures = file.read_uint32() - 1
textures = [file.read_string()[:-1] for i in range(nTextures)]

nRooms = file.read_uint32()
unk0 = file.read_uint32()
rooms = [read_room(file) for i in range(nRooms - 1)]

roomFlags = [file.read_byte() for i in range(nRooms)]
propRule = [file.read_byte() for i in range(nRooms)]

vMin = file.read_vec3()
vMax = file.read_vec3()
center = file.read_vec3()
radius = file.read_float()

nPaths = file.read_uint32()
paths = [read_paths(file) for i in range(nPaths)]

file.close()

# Sort the materials
print("parsing psdl...")
mat_map = {}
out_materials = []
for tex in textures:
    if tex not in mat_map:
        idx = len(out_materials)
        texname = "texture/" + tex + ".png"
        mat = {"texture": texname, "name": tex}
        out_materials.append(mat)
        mat_map[tex] = idx

# Parse the PSDL attributes
rooms2 = [];
ri = 0
for room in rooms:
    a = room["attributes"]
    new_room = {"id": ri, "perimeter": room["perimeter"]}
    out_a = []
    cur_tex_ref = None
    if len(a) > 0:
        i = 0
        res = {"type": "start"}
        last = False
        while res["type"] != None and not last:
            tmp = decode_attribute(a, i, floats)
            i = tmp[1]
            res = tmp[0]
            if res["type"] == "texture_reference":
                cur_tex_ref = res
            elif cur_tex_ref != None:
                res["texRef"] = cur_tex_ref["value"]
                out_a.append(res)
            last = tmp[2]
    new_room["attributes"] = out_a
    rooms2.append(new_room)
    ri += 1

# Convert the PSDL attributes to meshes
print("expanding geometry...")

roomsGeo = []
for room in rooms2:
    roomGeo = {"id": room["id"]}
    filteredPerimeter = []
    for p in room["perimeter"]:
        if p["vertex"] not in filteredPerimeter:
            filteredPerimeter.append(p["vertex"])
    expandedPerimeter = [cVertices[i] for i in filteredPerimeter]
    roomGeo["perimeter"] = expandedPerimeter
    objects = []
    nAttr = len(room["attributes"])
    for i in range(nAttr):
        a = room["attributes"][i]
        a2 = room["attributes"][i + 1] if (i < nAttr - 1) else None
        obj = get_object(a, cVertices, mat_map, textures, room["perimeter"], a2)
        if obj: objects.append(obj)
    roomGeo["objects"] = objects
    roomsGeo.append(roomGeo)

# Export to file
print("exporting output...")

if not os.path.exists("output"): os.mkdir("output")

if dump_json:
    obj0 = {}
    obj0["vertices"] = cVertices
    obj0["textures"] = textures
    obj0["rooms"] = rooms2
    obj0s = json.dumps(obj0, indent=4)
    with open("output/raw_psdl.json", "w") as outf:
        outf.write(obj0s)

    obj1 = {}
    obj1["rooms"] = roomsGeo
    obj1s = json.dumps(obj1, indent=4) 
    with open("output/expanded_psdl.json", "w") as outf:
        outf.write(obj1s)

meshes = []
for room in roomsGeo:
    meshes.extend(room["objects"])

with open("output/city.gltf", "wb") as outf:
    outf.write(to_gltf(meshes, out_materials))

if with_textures: dump_textures(out_materials)
