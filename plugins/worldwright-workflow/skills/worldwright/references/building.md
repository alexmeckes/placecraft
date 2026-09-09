# Architectural construction decisions

## Plan before components

Record dimensions in meters, origin, front direction, floor levels, purpose and
camera distance. Plan all elevations, even those hidden by the reference.
Give windows an interior use. Distinguish a dark doorway recess from a complete
traversable interior. Model deliberate wall thickness and roof relationships.

Inspect silhouette with plain materials first. If the plan cannot express the
reference's dominant forms, author another layout or builder before adding wear.

## Shared ownership

Assign one owner to each shared corner, ridge, post and roof junction. Adjacent
facades consume that plan instead of independently generating corner members.
Check actual endpoints and dimensions for paired beams. Define valley/roof
termination before laying shingles. A stable sweep frame prevents twisting on
curved roof beams; for a planar curve a fixed plane normal can be appropriate.

Cut real wall openings and add a recessed frame or a real void. Reserve clearance
for the whole frame. Check supports, stairs, thresholds and the approach. Props
need supports too: a hoist needs an axle, support, rope route and useful reach.

## Shape and surface

Keep editable named source components. Use bounded, seeded variation; preserve
mating faces, the ground datum and load paths. Deform appropriate free edges,
stone faces and tile toes rather than independently moving every vertex.

Natural asymmetry is not broad smoothing. Sunwell became too clay-like after
aggressive union/remesh/smoothing. Firm buttress planes and fitted decorated trim
needed protection, while dome asymmetry could remain. Calibrate both controls
independently at the asset's scale; the historical voxel numbers are not defaults.

When deforming touching surfaces, ensure comparable sampling density. A finely
sampled wall can intersect a coarsely sampled roof despite sharing a formula.
Keep shallow trim out of broad swelling. Check new vertex paint after Booleans:
zeroed colors can masquerade as black shadow patches.
