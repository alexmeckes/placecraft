---
name: placecraft
description: Design and refine editable Blender environment assets and small scenes from visual references, using architectural planning, fixed-view critique, and actual export checks. Use for reference-led buildings, environment assembly, or visual refinement of these assets.
---

# Placecraft

Produce editable assets and coherent scenes with a visible record of design
decisions. Respect the user's art direction, tools, scope and review preferences.
The included study uses smooth painted fantasy; it is an example, not a universal
palette or modeling grammar. No other modeling skill is required.

## Establish the next decision

Inspect the existing brief, source, reference, current output and review record.
Identify whether the work needs a new architectural plan, a geometry correction,
a material pass, an assembly change, or export repair. Preserve accepted work
outside that scope. For a new project, record units, intended camera distance,
runtime target and whether interiors must be traversable.

For a new primary building, select a user-supplied reference or generate one
with an available image tool within the user's request. Use
[reference-design.md](references/reference-design.md) for prompt construction.
Save the exact prompt, image and provenance. Inspect the image before modeling;
distinguish visible evidence from assumptions about hidden elevations. A reference
anchors style and architecture; a world concept does not dictate terrain geometry.

## Build one convincing exemplar

Use [building.md](references/building.md) when creating or changing architecture.
Complete [building-brief.md](assets/building-brief.md): silhouette, footprint,
floor heights, all elevations, opening purpose, support and access relationships.
Reuse component tools after authoring the plan. Avoid turning a new building into
a recolored version of the first successful shell.

Separate massing, construction and finish decisions. Review massing against the
reference before investing in ornament. Keep shared corners, ridges and joints
under one owner. Vary free edges while preserving fitted contact and ground
datums. Tune asymmetry independently from bevels and surface smoothing.

After shape approval, refine broad material relationships, then sparse painted
accents. Read [materials.md](references/materials.md) for material/export traps.
Preserve a before-pass source and fixed cameras; material-only work should not
silently alter geometry. Keep source parts editable and export from a copy.

## Inspect, diagnose, change, inspect again

Review whole silhouette, both sides, rear, roof and relevant close-ups. Inspect
the **actual exported model in its target viewer**, as well as useful Blender
renders. A screenshot or numeric check alone does not establish quality.

Write each visible defect, likely cause, smallest useful change and recheck view
in [review.json](assets/review.json). Distinguish design, representation and export
problems. If another pass is rejected, revisit the responsible representation;
do not keep increasing noise, blur, bevels or density without a new diagnosis.
Retain unsuccessful passes as evidence, not as current production rules.

Use [review-export.md](references/review-export.md) for review, reproducibility
and runtime packaging. Numeric checks should test concrete relationships. Their
success cannot grant user approval. Save open defects and review scope honestly.

## Assemble a slice of a world

Use [scene.md](references/scene.md) when expanding beyond an asset. Plan activities,
entrances, circulation, terrain/water and biome transitions before scattering
props. Reserve working space around full asset envelopes. For stairs and angled
junctions, use the shared-surface and route checks in that scene guide. Establish
a small representative road/threshold/junction before extending it. Check real mesh contact: wheel/water, bridge/deck, prop/support, door/route.
Use [vegetation.md](references/vegetation.md) only when foliage needs work.

Review both an overview and activity areas at intended walking distance. For a
finite diorama, finish the ground edge and underside and preserve arrival-route
contact. Technical counters belong in QA, unless the user wants them visible.

## Helpers and example

Resolve these paths relative to this skill directory. Run `bpy` inside Blender.
`scripts/run.py` discovers Blender from `--blender`, `BLENDER`, PATH, or its macOS
app location. It runs an explicitly chosen script; it does not invent geometry.

```sh
python3 scripts/run.py assets/kiln-shelter/build.py -- --out /absolute/output --stage finish --render
python3 scripts/check_glb.py /absolute/output/model.glb
python3 scripts/check_glb.py /absolute/output/model.glb --compare /absolute/second/model.glb
python3 scripts/preview.py /absolute/output
```

The preview helper copies a local Three.js viewer and serves on loopback. It
does not capture screenshots or certify visual quality; use your host's browser
tools, or the repository's optional Chrome capture script. The Blender-side
`scripts/blender_review.py` provides fixed-view rendering and preview export.

The [kiln shelter brief](assets/kiln-shelter/brief.md) is a bounded worked example,
not a general-purpose architecture generator. Read only the needed source.

## Handoff

Deliver the brief, reference provenance, generator/spec/seed, editable source,
runtime export, review images and check results. Rebuild in a clean output
directory and compare actual content; report the comparator's limits. Keep asset
appearance, export checks, user acceptance, and engine integration separate.
Do not set `engine_ready` without target-engine physics, LOD/performance and
populated-scene evidence. Report a blocked tool or unresolved visual defect
instead of substituting an image for editable 3D or fabricating an acceptance.
