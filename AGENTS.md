# Repository guide

This is the public workflow extraction, not the private Worldwright scene engine.
Keep the plugin self-contained: installed skills cannot reach repository-level
docs or tools. Place operational resources inside the skill; repository docs
explain the history and evidence. Do not add private checkout dependencies.

Read the skill before altering its process. Preserve flexible design choices;
promote demonstrated decision criteria rather than universal numeric recipes.
Keep historical user review, current agent review and engine readiness distinct.
Never promote a case study's old pending status into user approval automatically.

Run `python3 -m unittest discover -s tests -v` after helper changes. Run the demo
and inspect actual browser output after Blender or viewer changes. Keep bulky
generated output ignored; checked-in evidence needs provenance. Preserve Three.js
license headers. Do not publish personal paths, credentials or private URLs.
