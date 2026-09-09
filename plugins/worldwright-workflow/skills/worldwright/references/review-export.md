# Review, reproducibility and runtime limits

Keep the reviewed source, exported GLB, generator/spec/seed and review views tied
together by hashes. Save the source before rendering so review-only cameras and
lights are not mistaken for runtime meshes. Export copies if you batch or reduce
geometry. Preserve source editability.

## Visual loop

Use consistent front/rear/side/roof/overview cameras and one close-up of the
current defect. Record: visible problem, suspected layer, change, same-view
result, regressions, unresolved issues. Different lighting/cameras can obscure
whether an iteration helped. Reject stale renders from another build.

Inspect the final exported asset in the actual viewer. Numeric checks support
visual judgment, not replace it. When browser inspection is unavailable, record
that gap and stop short of declaring export appearance accepted.

## Technical evidence

Choose checks for the intended behavior: upward road normals, continuous deck,
clear entrance, feet on support, water visible at the wheel. Check a wider region
when a local fix could damage surrounding geometry. Bounds alone do not prove
these contracts. Keep budgets separate from measured frame rate.

Rebuild into a clean directory from the same inputs. File size alone is not a
reproducibility check. The included checker validates uncompressed, static GLB
structure and compares JSON content plus embedded binary bytes, ignoring only
container generator metadata. It is intentionally strict and ordering-sensitive.
It rejects unsupported external buffers, compressed/sparse accessors, skins,
animations and morph targets. It does not prove geometric equivalence under
reordering and does not validate engine collision. Different Blender versions
can export different ordering; do not loosen checks silently to get a pass.

Source studies sometimes needed a geometry-aware comparator with a documented
one-tangent-quantization tolerance. That is distinct from byte identity. State
which comparator and tolerances actually passed.

## Acceptance and packaging

Maintain separate statuses for agent visual review, user appearance approval,
export validation, rebuild reproducibility and engine integration. Historical
pending review files stay historical; later user acceptance needs its own scope.

For game delivery, author LODs/collision for the target, preserve openings and
ground datum during reduction, and test transitions and player access there.
COL_ names in GLB do not configure an engine's physics importer automatically.
Keep engine_ready false until target-engine evidence exists.
