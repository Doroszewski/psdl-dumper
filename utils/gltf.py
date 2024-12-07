import pygltflib
from pygltflib import GLTF2
import numpy as np


def mesh_to_gltf(in_mesh, mi, offset0, buffer0):
    points = np.array(in_mesh["vertices"], dtype="float32")
    uvs = np.array(in_mesh["uvs"], dtype="float32")
    #normals = np.array(in_mesh["normals"], dtype="float32")
    points_binary_blob = points.tobytes()
    uvs_binary_blob = uvs.tobytes()
    #normals_binary_blob = normals.tobytes()
    primitives=[]
    idx_accessors = []
    idx_bufferViews = []
    offset1 = len(points_binary_blob) + len(uvs_binary_blob)
    full_triangles_binary_blob = b""
    for i in range(len(in_mesh["triangles"])):
        triangles = np.array(in_mesh["triangles"][i], dtype="uint16")
        triangles_binary_blob = triangles.tobytes()
        primitives.append(
            pygltflib.Primitive(
                attributes=pygltflib.Attributes(POSITION=buffer0, TEXCOORD_0=buffer0 + 1), indices=buffer0 + 2 + i, material=in_mesh["materials"][i]
            )
        )
        idx_accessors.append(
            pygltflib.Accessor(
                bufferView=buffer0 + 2 + i,
                componentType=pygltflib.UNSIGNED_SHORT,
                count=triangles.size,
                type=pygltflib.SCALAR,
                max=[int(triangles.max())],
                min=[int(triangles.min())],
            )
        )
        idx_bufferViews.append(
            pygltflib.BufferView(
                buffer=0,
                byteOffset=offset0 + offset1,
                byteLength=len(triangles_binary_blob),
                target=pygltflib.ELEMENT_ARRAY_BUFFER,
            )
        )
        offset1 = offset1 + len(triangles_binary_blob)
        full_triangles_binary_blob  = full_triangles_binary_blob + triangles_binary_blob
    mesh=pygltflib.Mesh(
        primitives=primitives
    )
    accessors=[
        pygltflib.Accessor(
            bufferView=buffer0,
            componentType=pygltflib.FLOAT,
            count=len(points),
            type=pygltflib.VEC3,
            max=points.max(axis=0).tolist(),
            min=points.min(axis=0).tolist(),
        ),
        #pygltflib.Accessor(
        #    bufferView=buffer0,
        #    componentType=pygltflib.FLOAT,
        #    count=len(normals),
        #    type=pygltflib.VEC3,
        #    max=normals.max(axis=0).tolist(),
        #    min=normals.min(axis=0).tolist(),
        #),
        pygltflib.Accessor(
            bufferView=buffer0 + 1,
            componentType=pygltflib.FLOAT,
            count=len(uvs),
            type=pygltflib.VEC2,
            max=uvs.max(axis=0).tolist(),
            min=uvs.min(axis=0).tolist(),
        ),
    ]
    accessors.extend(idx_accessors)

    bufferViews=[
        pygltflib.BufferView(
            buffer=0,
            byteOffset=offset0,
            byteLength=len(points_binary_blob),
            target=pygltflib.ARRAY_BUFFER,
        ),
        #pygltflib.BufferView(
        #    buffer=0,
        #    byteOffset=offset0 + len(points_binary_blob),
        #    byteLength=len(normals_binary_blob),
        #    target=pygltflib.ARRAY_BUFFER,
        #),
        pygltflib.BufferView(
            buffer=0,
            byteOffset=offset0 + len(points_binary_blob),
            byteLength=len(uvs_binary_blob),
            target=pygltflib.ARRAY_BUFFER,
        ),
    ]
    bufferViews.extend(idx_bufferViews)

    nodes = [pygltflib.Node(mesh=mi, name=in_mesh["name"])]
    return {
        "meshes": [mesh],
        "accessors": accessors,
        "bufferViews": bufferViews,
        "blob": points_binary_blob + uvs_binary_blob + full_triangles_binary_blob,
        "nodes": nodes
    }

def material_to_gltf(material, texMap):
    tn = material["texture"]
    tex = pygltflib.TextureInfo(index=texMap[tn])
    r = pygltflib.PbrMetallicRoughness(
        baseColorTexture=tex
    )
    return pygltflib.Material(
        pbrMetallicRoughness=r,
        name=material["name"],
        alphaCutoff=None,
    )

def to_gltf(meshes, materials):
    gltf = GLTF2()
    out_meshes = []
    out_accessors = []
    out_bufferViews = []
    out_buffers = []
    out_nodes = []
    blob = b""
    offset0 = 0
    buffer0 = 0
    i=0
    for mesh in meshes:
        res = mesh_to_gltf(mesh, i, offset0, buffer0)
        out_meshes.extend(res["meshes"])
        out_accessors.extend(res["accessors"])
        out_bufferViews.extend(res["bufferViews"])
        out_nodes.extend(res["nodes"])
        blob = blob + res["blob"]
        offset0 = len(blob)
        buffer0 = len(out_bufferViews)
        i += 1
    tex_map = {}
    out_textures = []
    out_images = []
    for m in materials:
        if m["texture"] not in tex_map:
            idx = len(out_textures)
            img = pygltflib.Image(uri=m["texture"])
            tex = pygltflib.Texture(source=idx)
            out_textures.append(tex)
            out_images.append(img)
            tex_map[m["texture"]] = idx
    out_materials = [material_to_gltf(m, tex_map) for m in materials]

    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[j for j in range(i)])],
        nodes=out_nodes,
        meshes=out_meshes,
        accessors=out_accessors,
        bufferViews=out_bufferViews,
        buffers=[
            pygltflib.Buffer(
                byteLength=len(blob)
            )
        ],
        images=out_images,
        textures=out_textures,
        materials=out_materials,
    )
    gltf.set_binary_blob(blob)
    return b"".join(gltf.save_to_bytes())
