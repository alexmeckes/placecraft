# Run the kiln-shelter example

Requirements: Python 3.10+, a local Blender executable, and a modern WebGL browser.
Validated on Blender 5.1.1 on macOS. Other Blender versions/platforms are not yet
certified; set `BLENDER` to the executable if automatic discovery does not find it.
No provider keys, private source checkout, npm install or network assets are needed
for the example build or interactive viewer.

Clone the repository first:

```sh
git clone https://github.com/alexmeckes/placecraft.git
cd placecraft
```

Run commands from this repository root. Output paths are explicit so review
checkpoints stay separate:

```sh
python3 tools/demo.py build --stage massing --out out/massing --render
python3 tools/demo.py build --stage construction --out out/construction --render
python3 tools/demo.py build --stage finish --out out/kiln-shelter --render
python3 tools/demo.py check
python3 tools/demo.py serve
```

Open http://127.0.0.1:8770/. Drag to orbit, scroll to zoom, or select a fixed view.
The viewer uses bundled Three.js files; it reports loading failures visibly.
Each build produces `source.blend`, `model.glb`, `manifest.json`, source contact
checks and the viewer. `--render` adds six fixed-view PNGs. Rebuilding the same
output folder replaces that checkpoint; choose a new folder to preserve a pass.
Blender may retain its normal `.blend1` backup.

[Brief and reference observations](../plugins/placecraft/skills/placecraft/assets/kiln-shelter/brief.md)
explain the fixed layout. The seed changes surface variation, not the footprint.
The supplied reference was generated once through the built-in image tool; the
build uses authored geometry and does not invoke image-to-3D reconstruction.

## Repeatability and exported contacts

```sh
python3 tools/demo.py build --out out/repeat
python3 tools/demo.py check --compare out/repeat
python3 plugins/placecraft/skills/placecraft/scripts/run.py   plugins/placecraft/skills/placecraft/scripts/check_contacts.py --   out/kiln-shelter/model.glb   plugins/placecraft/skills/placecraft/assets/kiln-shelter/contacts.json   --report out/kiln-shelter/export-contacts.json
```

The GLB comparator is strict: static, uncompressed, embedded-buffer models only;
JSON scene content and binary payload must agree, ignoring the exporter generator
string. It rejects unsupported geometry features rather than passing silently.
The contact helper imports the actual GLB into Blender and probes specified rays
in Z-up meters. These sampled relationships are not a collision/navigation system.

## Capture browser evidence

Optional: Node 22+ and installed Chrome/Chromium. The capture helper uses an
isolated browser profile and only opens loopback URLs. It has no npm dependencies.
On macOS it locates Google Chrome; elsewhere set `CHROME` to your executable.
Start the preview server above, then in another terminal:

```sh
node tools/capture.mjs http://127.0.0.1:8770/ out/kiln-shelter/browser
```

Inspect all six images. The helper checks loading/errors and the rotation control,
but does not judge art quality. Close the server with Ctrl-C when finished.

## Use only the installed skill

The repository wrapper is optional. Inside the installed skill folder:

```sh
python3 scripts/run.py assets/kiln-shelter/build.py -- --out /absolute/output --stage finish --render
python3 scripts/check_glb.py /absolute/output/model.glb
python3 scripts/preview.py /absolute/output
```

To make a different building, start with the brief and a new reference/layout.
The kiln is a teaching example, not a universal building generator. The public
starter is simpler than its reference and the historical hero scenes; see the
[validation record](validation.md) for what the fresh exercise established.

## Install the skill without a plugin

Copy `plugins/placecraft/skills/placecraft` into your project's
`.agents/skills/placecraft` directory. Keep its scripts, assets and references
together. In a new task, invoke `$placecraft`.

The plugin ships local scripts, not a hosted Blender service. Image generation
uses an available image tool; user-supplied references work too. The bundled
example already includes its reference and needs no image API key.

## Existing Worldwright Workflow installations

The public project is now Placecraft. The original Worldwright development
project and historical review records keep their names. For an old plugin install,
remove `worldwright-workflow@worldwright`, add the `alexmeckes/placecraft`
marketplace, then install `placecraft@placecraft`. Existing source assets and
outputs do not need rebuilding for this naming change.
