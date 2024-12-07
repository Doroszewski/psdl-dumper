#info here: https://github.com/Dummiesman/angel-file-formats/blob/master/Midtown%20Madness%202/Room_attributes.md


def decode_attribute(a, i, floats):
    res = {"type": None}
    typ = (a[i] & 120) >> 3
    subtyp = (a[i] & 7)
    last = (a[i] & 128) > 0
    i += 1



    if typ == 0:
        res["type"] = "road"
        if subtyp > 0:
            nSections = subtyp
        else:
            nSections = a[i]
            i += 1
        vertexRefs = [a[i + j] for j in range(nSections * 4)]
        i += nSections * 4
        res["nSections"] = nSections
        res["vertexRefs"] = vertexRefs



    elif typ == 1 or typ == 2:
        res["type"] = "walkway" if typ == 2 else "sidewalk_strip"
        if subtyp > 1:
            nSections = subtyp
        else:
            nSections = a[i]
            i += 1
        vertexRefs = [a[i + j] for j in range(nSections * 2)]
        i += nSections * 2
        res["nSections"] = nSections
        res["vertexRefs"] = vertexRefs



    elif typ == 3:
        res["type"] = "sliver"
        for k in ["top", "textureScale", "left", "right"]:
            res[k] = a[i]
            i += 1
        for k in ["top", "textureScale"]:
            res[k] = floats[res[k]]



    elif typ == 4:
        res["type"] = "crosswalk"
        vertexRefs = [a[i + j] for j in range(subtyp)]
        i += subtyp
        res["nVertices"] = subtyp
        res["vertexRefs"] = vertexRefs



    elif typ == 5 or typ == 6:
        res["type"] = "triangle_fan" if typ == 6 else "road_triangle_fan"
        nTriangles = subtyp
        if nTriangles == 0:
            nTriangles = a[i]
            i += 1
        vertexRefs = [a[i + j] for j in range(nTriangles + 2)]
        i += nTriangles + 2
        res["nTriangles"] = nTriangles
        res["vertexRefs"] = vertexRefs



    elif typ == 7:
        res["type"] = "facade_bound"
        for k in ["angle", "top", "left", "right"]:
            res[k] = a[i]
            i += 1
        for k in ["top"]:
            res[k] = floats[res[k]]



    elif typ == 8:
        res["type"] = "divided_road"
        if subtyp > 0:
            nSections = subtyp
        else:
            nSections = a[i]
            i += 1
        data = a[i]
        i += 1
        
        divFlags = (data & 248) >> 3
        res["closeStart"] = (divFlags & 8) > 0
        res["closeEnd"] = (divFlags & 16) > 0
        res["dividerType"] = (data & 7)
        res["tex"] = ((data & 65280) >> 8) - 1
        res["value"] = a[i] / 256.0
        i += 1
        vertexRefs = [a[i + j] for j in range(nSections * 6)]
        i += nSections * 6
        res["vertexRefs"] = vertexRefs



    elif typ == 9:
        if subtyp == 0:
            res["type"] = "junction_tunnel"
            nSize = a[i]
            i += 1
        else:
            res["type"] = "road_tunnel"
        ks = ["data", "height"]
        if subtyp != 2: ks.append("unknown")
        for k in ks:
            res[k] = a[i]
            i += 1
        res["height"] = res["height"] / 256.0
        if subtyp == 0:
            res["unknown3"] = a[i]
            i += 1
            enabledWalls = [a[i + j] for j in range(nSize - 4)]
            i += nSize - 4
            enWallsBits = []
            for bi in range((nSize - 4)):
                for bj in range(16):
                    enWallsBits.append((enabledWalls[bi] & 2**bj) > 0)
            res["enabledWalls"] = enWallsBits
        bits = [
            "leftSide", "rightSide", "style", "flatCeiling",
            "closedStartLeft", "closedLeftEnd", "closedStartRight", "closedEndRight",
            "curvedCeiling", "offsetStartLeft", "offsetEndLeft", "offsetStartRight",
            "offsetEndRight", "curvedSides", "culled", "unknown1",
        ]
        for bi in range(len(bits)):
            res[bits[bi]] = ((res["data"] & 2**bi) > 0)



    elif typ == 10:
        res["type"] = "texture_reference"
        res["value"] = a[i] + (256 * subtyp) - 1
        i += 1



    elif typ == 11:
        res["type"] = "facade"
        for k in ["bottom", "top", "uRepeat", "vRepeat", "left", "right"]:
            res[k] = a[i]
            i += 1
        for k in ["top", "bottom"]:
            res[k] = floats[res[k]]



    elif typ == 12:
        res["type"] = "roof_triangle_fan"
        if subtyp > 1:
            nVertices = subtyp
        else:
            nVertices = a[i]
            i += 1
        heightRef = a[i]
        i += 1
        vertexRefs = [a[i + j] for j in range(nVertices + 1)]
        i += nVertices + 1
        res["nVertices"] = nVertices
        res["height"] = floats[heightRef]
        res["vertexRefs"] = vertexRefs



    return [res, i, last]
