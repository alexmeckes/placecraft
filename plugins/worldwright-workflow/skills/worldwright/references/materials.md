# Painted materials and export behavior

Set broad value/color relationships first. Leave quiet surfaces between accents.
Grain follows the member; linen, hay, fruit and roofing keep distinct material
behavior. A palette alone does not make unrelated surfaces the same substance.

After geometry acceptance, save the before-pass source and change materials as
a separate experiment. Use identical light and camera for comparison. Sparse
paired scuffs, partial edge wear and a few varied component treatments read
better than equally bright outlines on every stone or uniform noise everywhere.

Compare both close-up and intended camera distance. Exportable vertex color or
baked textures are useful choices, not mandatory styles. A Blender shader graph
may not survive glTF. Know which properties are exported and inspect that file.
Color images need correct sRGB treatment; normal maps use non-color data. Check
the active UV layer and required tangents. Do not multiply a baked ground color
by old vertex paint accidentally. White or zeroed COLOR_0 can change the result.

For material-only work, compare positions/indices/transforms separately from
changed UVs and textures. The bundled strict comparator checks whole static GLB
content, so an intended material change will fail it; use a targeted geometry
comparison when the question is geometry preservation.

A browser can expose backface culling, foliage shading, water clipping or shadow
artifacts absent from a source render. Repair flipped open paving faces in the
generator rather than hiding the defect by disabling all backface culling.
