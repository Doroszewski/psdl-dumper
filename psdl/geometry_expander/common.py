import numpy as np


def construct_object(a, triangles, vertices, uvs, materials):
    if len(triangles) == 0:
        return None
    else:
        for t in triangles:
            if len(t) == 0:
                return None
    return {
        "name": a["type"],
        "triangles": triangles,
        "vertices": vertices,
        "uvs": uvs,
        "materials": materials
    }

def get_road_length(rawVertices, vps, i0):
    totl = 0
    for i in range(0, len(rawVertices) - vps, vps):
        l1 = np.linalg.norm(np.subtract(rawVertices[i + i0], rawVertices[i + i0 + vps]))
        l2 = np.linalg.norm(np.subtract(rawVertices[i + i0 + 1], rawVertices[i + i0 + 1 + vps]))
        lr = (l1 + l2) * 0.5
        totl += lr
    return totl

def get_road_width(rawVertices, i0):
    tw = np.linalg.norm(np.subtract(rawVertices[i0], rawVertices[i0 + 1]))
    if tw == 0: tw = 1
    return tw

def get_segment_length(rawVertices, i, vps, i0):
    l1 = np.linalg.norm(np.subtract(rawVertices[i + i0], rawVertices[i + i0 + vps]))
    l2 = np.linalg.norm(np.subtract(rawVertices[i + i0 + 1], rawVertices[i + i0 + 1 + vps]))
    lr = (l1 + l2) * 0.5
    return lr

def add_road_section_triangles(vertices, triangles, vps, offset, j):
    i2 = len(vertices) - vps + offset
    triangles.extend([
        i2 + j,
        i2 + 1 + j,
        i2 + vps + j,
        i2 + 1 + j,
        i2 + vps + 1 + j,
        i2 + vps + j
    ])
