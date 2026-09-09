# Vegetation lessons and current limits

Treat foliage as an asset design problem before treating it as a scatter count.
Establish the trunk/branch silhouette, connected terminal growth and readable
canopy masses. Check the bare tree as well as the finished crown from multiple
angles. Random leaves around a volume can look detached even when they fill it.

Control canopy gaps, width and major branch hierarchy before leaf variation.
Leaf size, hue and shape variation should follow species and growth organization.
Too much independent variation becomes confetti. More seeds cannot fix a weak
base design. Keep small twigs/modules attached and visible supports plausible.

Choose geometry, cards, clusters or a hybrid for the actual camera and budget.
Measure cost by component and inspect LOD transitions/shadows in the runtime.
Alpha cards introduce their own sorting, normals, shadow and overdraw issues;
the original pipeline's source renders hid a browser foliage failure. Opaque
geometry avoids some problems but does not guarantee acceptable triangle cost.

For splotchy grass, inspect ground-color continuity, density falloff, normals and
per-blade shadows before adding blades. Prefer ecological clumps and graded
transitions over a uniformly speckled field. Keep ground texture color fields
separate from modeled silhouettes such as individual flowers or stones.

The historical oak was accepted provisionally. This repository does not ship a
production tree generator or claim that our vegetation problems are solved.
