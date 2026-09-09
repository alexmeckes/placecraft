# Contributing

Start with a concrete failure or a new type of asset. Show the reference, brief,
before/after from the same view, source change and remaining limitations.
Preserve reference provenance and contribute only material you may distribute.

Workflow changes should explain the decision they improve. Avoid adding a fixed
number of steps, a universal bevel amount, or a special rule for every historical
mistake. Helpers should make repeated execution more reliable and stay portable.

Run the unittest suite. For geometry changes, build twice in clean directories,
inspect the source and GLB, record the Blender version and compare exports.
The bundled comparator checks a limited static uncompressed GLB contract; extend
its tests before extending that contract. Do not hide unsupported input as a pass.

Please keep large renders and models out of pull requests unless they provide
specific review evidence. Contributions are offered under the repository MIT
license; retain separate third-party notices.
