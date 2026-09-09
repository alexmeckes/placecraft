# How the process evolved

Placecraft was first published as Worldwright Workflow. Historical project and
review names below refer to that earlier work.

The starting point was Terraingen's world-generation experiment, inspired by the
WorldClaw paper discussed in that repository. The original pipeline planned a
world, generated composition/reference images, reconstructed assets through
image-to-3D providers, placed them on terrain and reviewed the result. This public
extraction is an account of our alternative workflow, not a reproduction claim or
a new evaluation of that paper.

We kept the goal: a coherent, editable, explorable slice of a world. We shifted
many asset classes to code-authored Blender geometry. An agent could design a
part, build it, inspect the result, diagnose the defect and modify the construction
rule directly. That made correction and variation more explicit, but it also
required architectural judgment and repeated art direction.

## The production loop

```mermaid
flowchart LR
    A[Written brief] --> B[Reference and observations]
    B --> C[Architecture and massing]
    C --> D[Editable construction]
    D --> E[Materials and export]
    E --> F[Fixed-view visual review]
    F -->|Targeted correction| C
    F --> G[Small scene and functional contacts]
    G -->|Repair the responsible layer| D
    G --> H[Rebuild evidence and scoped acceptance]
```

1. **Reference and brief.** Generate or select a strong primary image, inspect it,
   and translate observable architecture into a plan. Record unseen elevations as
   assumptions. A reference for an object and a concept for an entire world serve
   different purposes.
2. **One exemplar.** Review silhouette before ornament. A new type needs its own
   layout. Reuse component construction and material methods after the plan exists.
3. **Construction.** Give each shared post, corner and roof joint one owner.
   Model openings, support and access as relationships. Keep source parts editable.
4. **Surface refinement.** Apply controlled asymmetry to free edges. Tune edge
   softness separately. After geometry selection, compare an independent material
   pass with sparse accents and quiet surfaces.
5. **Actual export review.** Revisit fixed front, rear, side, roof and detail
   views in Blender and the browser. Name the defect, cause, change and result.
   Diagnose repeated rejection at the design, representation or export layer.
6. **Scene assembly.** Plan activities, circulation, terrain/water interfaces and
   biome transitions. Prototype difficult road/shoreline interfaces before spreading
   them across the scene. Add dressing where the activity gives it a purpose.
7. **Evidence and acceptance.** Compare a clean regeneration, check actual mesh
   contacts, retain screenshots and state the limits of each result. Keep user
   appearance selection separate from agent review and engine integration.

## What the agent did, and what the person did

Astra wrote procedural builders, inspected renders, researched methods when
needed, generated design references through an image tool, assembled scenes,
and implemented fixes. Alex selected directions and repeatedly identified visual
problems: foliage density, unnatural materials, over-reused cottage shapes,
misaligned structure, roads, excessive blending and incomplete scene composition.

The loop worked because those corrections changed the next construction decision.
It would be misleading to describe the historical results as one-shot autonomous
world generation. The new kiln example tests the extracted package on a bounded
fresh asset; it is a same-agent exercise, not an independent-agent benchmark.

## Scope of reuse

The reusable unit is a family recipe plus its constraints and review evidence.
The workflow supports authoring a new recipe when the next building differs.
A seed can vary approved surfaces or proportions within stated limits; it cannot
supply the missing design of a new architectural type.

The public skill contains the decision process and a few portable helpers. The
historical private application also has catalogs, scene plans and larger bespoke
builders. We have intentionally not represented those private modules as features
of this downloadable plugin. The finished scene screenshots are case studies;
the small kiln is the executable example shipped here.
