# Placecraft

Build small worlds with Blender and AI.

Start with a reference image, build one convincing asset, then grow it into a
scene. The agent writes Blender code; you guide the result through renders,
feedback and refinement. Buildings, terrain and props stay editable.

![Brookside hamlet](docs/images/brookside-final.png)

This repo shares the process behind **Brookside**, **Sunwell** and **Frostpass**:
what worked, what looked wrong, and how we fixed it. It includes a Codex skill,
Blender helpers and a runnable kiln-shelter example. The larger scenes are
[illustrated case studies](docs/case-studies.md).

## Use it

You'll need Codex, local Blender and Python 3.10+.

```sh
codex plugin marketplace add alexmeckes/placecraft
codex plugin add placecraft@placecraft
```

In a new task:

> Use $placecraft to build a small riverside workshop. Start with a reference
> image and refine one building before expanding the scene.

The workflow is simple: **reference → plan → build → look → refine**. Get the
building right before multiplying it. Check the actual exported scene as well
as the Blender renders.

[Read the process](docs/process.md) ·
[See the before/after lessons](docs/lessons.md) ·
[Run the example](docs/quickstart.md)

[MIT license](LICENSE) · [Credits](THIRD_PARTY_NOTICES.md) ·
[Contributing](CONTRIBUTING.md) · [Validation](docs/validation.md)
