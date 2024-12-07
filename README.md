An importer for the PSDL file format used in Midtown Madness 2, at the moment it converts it to the glTF format, with an option to dump the textures to PNG and another option to dump a representation of the raw PSDL data to JSON.

Usage examples:
```
python psdl_import.py cityname.psdl
```
```
python psdl_import.py cityname.psdl -dump_json -dump_textures
```

Arguments:
- The PSDL file name (the PSDL will be converted to glTF, and saved in the "output" folder)

Flags:
- dump_json: if enabled, two JSON dumps will be generated in the output folder, one with the raw PSDL data (raw_json.psdl) and one with the expanded geometry (expanded_psdl.json)
- dump_textures: if enabled, the textures (which have to be in .tex format and placed in a "textures" folder next to the psdl file) will be exported to PNG in the output/textures folder)

TODO:
- Sidewalk strip start/end cap
- Road tunnels
- Junction tunnels
- Recalculate normals
- INST
