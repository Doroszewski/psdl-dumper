import numpy as np
from psdl.geometry_expander.common import *


def add_cap(vertices, uvs, triangles_d, ics, i0, invert):
    vc0 = len(vertices)
    for ic in ics:
        vertices.append(vertices[i0 + ic])
    uvs.extend([
        [0, 1], [0, 0], [1, 0], [1, 1],
    ])
    if not invert:
        triangles_d[3].extend([
            vc0, vc0 + 1, vc0 + 2,
            vc0 + 1, vc0 + 3, vc0 + 2
        ])
    else:
        triangles_d[3].extend([
            vc0, vc0 + 2, vc0 + 1,
            vc0 + 1, vc0 + 2, vc0 + 3
        ])

def get_divided_road(a, cVertices, mat_map, textures):
        rawVertices = [cVertices[i] for i in a["vertexRefs"]]
        totl = get_road_length(rawVertices, 6, 2)
        
        vertices = []
        uvs = []
        triangles0 = []
        triangles1 = []
        triangles_d = [[], [], [], []]
        z = 0
        tw = get_road_width(rawVertices, 1)
        sww = get_road_width(rawVertices, 0)
        vps0 = 12
        vpsd = 0
        if a["dividerType"] == 1: vpsd = 2
        elif a["dividerType"] == 2: vpsd = 10
        elif a["dividerType"] == 3: vpsd = 6
        vps = vps0 + vpsd
        for i in range(0, len(rawVertices), 6):
            v0 = rawVertices[i]
            v1 = rawVertices[i + 1]
            v1H = [v1[0], v1[1] + 0.15, v1[2]]
            v2 = rawVertices[i + 2]
            v3 = rawVertices[i + 3]
            v4 = rawVertices[i + 4]
            v4H = [v4[0], v4[1] + 0.15, v4[2]]
            v5 = rawVertices[i + 5]

            u = z * max(1, round(totl / tw)) / totl
            us = z * max(1, round(totl / sww)) / totl
            ud = z * max(1, round(totl)) / totl
            uv0 = [u, 0]
            uv1 = [u, 1]
            uv0s = [us, 0]
            uv1s = [us, 1]
            
            # the road
            vertices.extend([
                v0, v1H,
                v1H, v1,
                v1, v2,
                v3, v4,
                v4, v4H,
                v4H, v5
            ])
            uvs.extend([
                uv0s, uv1s,
                uv1s, uv1s,
                uv0, uv1,
                uv1, uv0,
                uv1s, uv1s,
                uv1s, uv0s
            ])
            if i < len(rawVertices) - 6:
                for j in range(0, 12, 2):
                    trianglesN = triangles0 if j in [4, 6] else triangles1
                    add_road_section_triangles(vertices, trianglesN, vps, vpsd, j)
                z += get_segment_length(rawVertices, i, 6, 2)

            vdir = np.subtract(v3, v2)
            vdir = vdir / np.linalg.norm(vdir)

            # the divider
            if a["dividerType"] == 1: # flat
                vd0 = v2
                vd1 = v3
                vertices.extend([vd0, vd1])
                uvd0 = [ud, 0]
                uvd1 = [ud, a["value"]]
                uvs.extend([uvd0, uvd1])
                if i < len(rawVertices) - 6:
                    add_road_section_triangles(vertices, triangles_d[1], vps, vps0, 0)
            
            elif a["dividerType"] == 2: # elevated
                vd0 = v2
                vd0H = [vd0[0], vd0[1] + a["value"], vd0[2]]
                vd0I = list(np.add(vd0H, vdir * a["value"]))
                vd1 = v3
                vd1H = [vd1[0], vd1[1] + a["value"], vd1[2]]          
                vd1I = list(np.add(vd1H, -vdir * a["value"]))
                vertices.extend([
                    vd0, vd0H,
                    vd0H, vd0I,
                    vd0I, vd1I,
                    vd1I, vd1H,
                    vd1H, vd1,
                ])
                uvd0 = [ud, 0]
                uvd1 = [ud, 1]
                uvs.extend([
                    uvd0, uvd1,
                    uvd0, uvd1,
                    uvd0, uvd1,
                    uvd0, uvd1,
                    uvd0, uvd1,
                ])
                if i < len(rawVertices) - 6:
                    for j in range(0, 10, 2):
                        if j in [0, 8]: dm = 0
                        elif j in [2, 6]: dm = 1
                        elif j in [4]: dm = 2
                        add_road_section_triangles(vertices, triangles_d[dm], vps, vps0, j)
                vc0 = len(vertices)
                if a["closeStart"] and i == len(rawVertices) - 6:
                    add_cap(vertices, uvs, triangles_d, [12, 21, 13, 20], 0, False)
                if a["closeEnd"] and i == len(rawVertices) - 6:
                    add_cap(vertices, uvs, triangles_d, [12, 21, 13, 20], vc0 - vps, True)
            
            elif a["dividerType"] == 3: # wedged
                vd0 = v2
                vd0I = list(np.add([vd0[0], vd0[1] + 1, vd0[2]], vdir * 0.5))
                vd1 = v3       
                vd1I = list(np.add([vd1[0], vd1[1] + 1, vd1[2]], -vdir * 0.5))
                vertices.extend([
                    vd0, vd0I,
                    vd0I, vd1I,
                    vd1I, vd1,
                ])
                uvd0 = [ud, 0]
                uvd1 = [ud, 1]
                uvs.extend([
                    uvd0, uvd1,
                    uvd0, uvd1,
                    uvd0, uvd1,
                ])
                if i < len(rawVertices) - 6:
                    for j in range(0, 6, 2):
                        if j in [0, 4]: dm = 1
                        elif j in [2]: dm = 2
                        add_road_section_triangles(vertices, triangles_d[dm], vps, vps0, j)
                vc0 = len(vertices)
                if a["closeStart"] and i == len(rawVertices) - 6:
                    add_cap(vertices, uvs, triangles_d, [12, 17, 13, 16], 0, False)
                if a["closeEnd"] and i == len(rawVertices) - 6:
                    add_cap(vertices, uvs, triangles_d, [12, 17, 13, 16], vc0 - vps, True)

        mat0 = mat_map[textures[a["texRef"]]]
        mat1 = mat_map[textures[a["texRef"] + 1]]
        full_mats = [mat0, mat1]
        full_tris = [triangles0, triangles1]

        if a["dividerType"] == 2:
            mat_d0 = mat_map[textures[a["tex"]]]
            full_mats.append(mat_d0)
            full_tris.append(triangles_d[0])

        if a["dividerType"] > 0:
            mat_d1 = mat_map[textures[a["tex"] + 1]]
            full_mats.append(mat_d1)
            full_tris.append(triangles_d[1])

        if a["dividerType"] > 1:
            mat_d2 = mat_map[textures[a["tex"] + 2]]
            full_mats.append(mat_d2)
            full_tris.append(triangles_d[2])

        if (a["closeStart"] or a["closeEnd"]) and a["dividerType"] > 1:
            mat_d3 = mat_map[textures[a["tex"] + 3]]
            full_mats.append(mat_d3)
            full_tris.append(triangles_d[3])

        return construct_object(a, full_tris, vertices, uvs, full_mats)
