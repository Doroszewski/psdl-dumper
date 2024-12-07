import numpy as np
from psdl.geometry_expander.common import *
from psdl.geometry_expander.divided_road import get_divided_road
from psdl.geometry_expander.junction_tunnel import get_junction_tunnel
from psdl.geometry_expander.road_tunnel import get_road_tunnel


def get_object(a, cVertices, mat_map, textures, perimeter, a2):



    if a["type"] == "road":
        rawVertices = [cVertices[i] for i in a["vertexRefs"]]
        totl = get_road_length(rawVertices, 4, 1)

        vertices = []
        uvs = []
        triangles0 = []
        triangles1 = []
        z = 0
        tw = get_road_width(rawVertices, 1)
        sww = get_road_width(rawVertices, 0)
        for i in range(0, len(rawVertices), 4):
            v0 = rawVertices[i]
            v1 = rawVertices[i + 1]
            v1H = [v1[0], v1[1] + 0.15, v1[2]]
            v2 = rawVertices[i + 2]
            v2H = [v2[0], v2[1] + 0.15, v2[2]]
            v3 = rawVertices[i + 3]
            vM = [p * 0.5 for p in [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]]
            u = z * 2 * max(1, round(totl / tw)) / totl
            us = z * 2 * max(1, round(totl / sww)) / totl
            uv0 = [u, 0]
            uv1 = [u, 1]
            uv0s = [us, 0]
            uv1s = [us, 1]
            vertices.extend([
                v0, v1H,
                v1H, v1,
                v1, vM,
                vM, v2,
                v2, v2H,
                v2H, v3
            ])
            uvs.extend([
                uv0s, uv1s,
                uv1s, uv1s,
                uv0, uv1,
                uv1, uv0,
                uv1s, uv1s,
                uv1s, uv0s
            ])
            if i < len(rawVertices) - 4:
                for j in range(0, 12, 2):
                    trianglesN = triangles0 if j in [4, 6] else triangles1
                    add_road_section_triangles(vertices, trianglesN, 12, 0, j)
                z += get_segment_length(rawVertices, i, 4, 1)
        mat0 = mat_map[textures[a["texRef"]]]
        mat1 = mat_map[textures[a["texRef"] + 1]]
        return construct_object(a, [triangles0, triangles1], vertices, uvs, [mat0, mat1])



    elif a["type"] == "walkway":
        vertices = [cVertices[i] for i in a["vertexRefs"]]
        uvs = []
        triangles = []
        totl = get_road_length(vertices, 2, 0)

        z = 0
        tw = get_road_width(vertices, 0)
        for i in range(0, len(vertices), 2):
            u = z * 2 * max(1, round(totl / tw)) / totl
            uv0 = [u, 0]
            uv1 = [u, 1]
            uvs.extend([uv0, uv1])
            if i < len(vertices) - 2:
                triangles.extend([
                    i, i + 1, i + 2,
                    i + 1, i + 3, i + 2
                ])
                z += get_segment_length(vertices, i, 2, 0)
        mat = mat_map[textures[a["texRef"]]]
        return construct_object(a, [triangles], vertices, uvs, [mat])



    elif a["type"] == "sidewalk_strip":
        vr = a["vertexRefs"]
        hasStart = False
        hasEnd = False
        if vr[0] == 0 and vr[0] == 0:
            hasStart = True
            vr = vr[2:]
        elif vr[0] == 1 and vr[0] == 1:
            hasEnd = True
            vr = vr[:-2]
        rawVertices = [cVertices[i] for i in vr]
        vertices = []
        uvs = []
        for i in range(0, len(rawVertices), 2):
            v0 = rawVertices[i + 1]
            v1 = rawVertices[i]
            v2 = [v1[0], v1[1] + 0.15, v1[2]]
            uv0 = [-0.25 * v0[0], -0.25 * v0[2]]
            uv1 = [-0.25 * v1[0], -0.25 * v1[2]]
            uv2 = uv1
            vertices.extend([v0, v2, v2, v1])
            uvs.extend([uv0, uv2, uv2, uv1])
        triangles = []
        for i in range(0, len(vertices) - 4, 4):
            triangles.extend([i, i + 5, i + 1])
            if vertices[i] != vertices[i + 4]: triangles.extend([i, i + 4, i + 5])
            triangles.extend([i + 2, i + 7, i + 3, i + 2, i + 6, i + 7])
        #TODO: start/end
        mat = mat_map[textures[a["texRef"] + 1]]
        return construct_object(a, [triangles], vertices, uvs, [mat])



    elif a["type"] == "sliver":
        return None
        left = cVertices[a["left"]]
        right = cVertices[a["right"]]
        topLeft = [left[0], a["top"], left[2]]
        topRight = [right[0], a["top"], right[2]]
        vertices = [left, right, topLeft, topRight]
        scale = a["textureScale"]
        d1 = np.linalg.norm(np.subtract(topLeft, topRight))
        d2 = np.linalg.norm(np.subtract(topLeft, left))
        d3 = np.linalg.norm(np.subtract(topRight, right))
        u = round(d1 * scale)
        v1 = d2 * scale
        v2 = d3 * scale
        uvs = [[0, v1], [u, v2], [0, 0], [u, 0]]
        triangles = [0, 1, 2, 1, 3, 2]
        mat = mat_map[textures[a["texRef"]]]
        return construct_object(a, [triangles], vertices, uvs, [mat])


    elif a["type"] == "crosswalk":
        vertices = [cVertices[i] for i in a["vertexRefs"]]
        cwl = np.linalg.norm(np.subtract(vertices[0], vertices[2]))
        cww = np.linalg.norm(np.subtract(vertices[0], vertices[1]))
        cwtl = cwl / cww
        adjv = max(1, round(cwtl))
        uvs = [[0, adjv], [1, adjv], [0, 0], [1, 0]]
        triangles = [0, 2, 1, 1, 2, 3]
        mat = mat_map[textures[a["texRef"] + 2]]
        return construct_object(a, [triangles], vertices, uvs, [mat])



    elif a["type"] == "triangle_fan" or a["type"] == "road_triangle_fan":
        vertices = [cVertices[i] for i in a["vertexRefs"]]
        uvs = [[-0.25 * v[0], -0.25 * v[2]] for v in vertices]
        triangles = []
        for i in range(1, len(vertices) - 1):
            triangles.extend([0, i, i + 1])
        mat = mat_map[textures[a["texRef"]]]
        return construct_object(a, [triangles], vertices, uvs, [mat])



    elif a["type"] == "divided_road":
        return get_divided_road(a, cVertices, mat_map, textures)



    elif a["type"] == "junction_tunnel":
        return get_junction_tunnel(a, cVertices, mat_map, textures, perimeter)



    elif a["type"] == "road_tunnel":
        return get_road_tunnel(a, cVertices, mat_map, textures, a2)



    elif a["type"] == "facade":
        return None
        rawLeft = cVertices[a["left"]]
        rawRight = cVertices[a["right"]]
        bottomLeft = [rawLeft[0], a["bottom"], rawLeft[2]]
        bottomRight = [rawRight[0], a["bottom"], rawRight[2]]
        topLeft = [rawLeft[0], a["top"], rawLeft[2]]
        topRight = [rawRight[0], a["top"], rawRight[2]]
        vertices = [bottomLeft, bottomRight, topLeft, topRight]
        uvs = [[0, a["vRepeat"]], [a["uRepeat"], a["vRepeat"]], [0, 0], [a["uRepeat"], 0]]
        triangles = [0, 1, 2, 1, 3, 2]
        mat = mat_map[textures[a["texRef"]]]
        return construct_object(a, [triangles], vertices, uvs, [mat])


    elif a["type"] == "roof_triangle_fan":
        return None
        rawVertices = [cVertices[i] for i in a["vertexRefs"]]
        vertices = [[v[0], a["height"], v[2]] for v in rawVertices]
        uvs = [[-0.25 * v[0], -0.25 * v[2]] for v in rawVertices]
        triangles = []
        for i in range(1, len(vertices) - 1):
            triangles.extend([0, i, i + 1])
        mat = mat_map[textures[a["texRef"]]]
        return construct_object(a, [triangles], vertices, uvs, [mat])


    else:
        return None
