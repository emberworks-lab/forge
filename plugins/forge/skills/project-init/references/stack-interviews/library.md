# library / package interview

For npm / pub / pip / crates publishable libraries.

## Ask about

- **Target runtimes** — Node versions, browsers, Dart versions, Python versions, Rust toolchain.
- **Build tooling** — `tsup` / `unbuild` / `rollup` / `dart pub` / `maturin` / `cargo`.
- **Testing approach** — Vitest / Jest / `package:test` / pytest / `cargo test`.
- **Publishing target** — npm / pub.dev / PyPI / crates.io / GitHub Packages / private registry.

## Generate

- `kit-add-feature.md` — lighter than the app variant; no UI scaffold.
- `kit-add-test.md` — test file + matcher conventions.
- `kit-publish.md` — version bump + tag + registry publish for the chosen target.

## Notes

- Libraries usually do not need `kit-deploy.md` — replace with `kit-publish.md`.
- API surface stability is a recurring concern; consider adding a `kit-add-changeset.md` if the user uses Changesets or a similar tool.
