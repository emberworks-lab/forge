# Testing — libraries / packages

Augments `00_general.md` for publishable packages (npm, pub.dev, PyPI, crates.io).

## Differences from app testing

A library has consumers you don't control. Testing priorities shift:

1. **API contract stability** — breaking changes must be intentional and signaled
2. **Cross-version compatibility** — works on the lowest declared peer/runtime version
3. **No incidental behavior** — anything observable is part of the contract, even if unintended
4. **Smaller surface, deeper coverage** — every public function needs unit tests; coverage target is HIGH

## Stack mapping

| Stack | Unit | Property | Cross-runtime | Type tests |
|---|---|---|---|---|
| **npm** (TS) | Vitest OR Jest | fast-check | `act` (npm-tarball install in N versions) | tsd OR expectType |
| **pub.dev** (Dart) | flutter_test (no Flutter dep) OR `package:test` | glados | melos / dart_test in matrix | analyzer-driven |
| **PyPI** | pytest | Hypothesis | tox (Python 3.9, 3.10, 3.11, 3.12) | mypy strict |
| **crates.io** | built-in `#[test]` | proptest | `cargo test` MSRV target | type-system inherent |

## What a library MUST test

- Every public API surface — at least one happy-path test per export
- Every documented edge case from the README
- Type contract — TypeScript types verified via `tsd` or `expect-type`; Dart types via analyzer
- Backward-compatibility on minor versions — snapshot the public API; PR diff signals breaking changes

## What a library should NOT test

- Internal helpers (mark `@internal` and let coverage drop there)
- Glue code with no logic
- Build tooling (bundler config, etc.)

## Property-based — strongly recommended for libraries

Libraries often expose pure functions with clean invariants. Property tests catch the "what about empty input / Unicode / very large numbers" classes of bugs.

Examples:
- Parser library: `parse(stringify(x)) === x` for all x in domain
- Validator: `validate(invalid) returns failure for all invalid in negative domain`
- Hash function: same input → same output (determinism); different inputs → different outputs (with high probability)

## Type tests (npm-specific)

```ts
import { expectType } from 'tsd';
import { parseQuery } from '../src';

expectType<{ q: string }>(parseQuery('?q=hello'));
expectType<{ q: string; n: number }>(parseQuery('?q=hello&n=1', { n: Number }));
```

## Multi-version matrix

CI runs tests against the minimum supported runtime + current LTS + current stable.

For Node libraries: `node-version: [18.x, 20.x, 22.x]` in GitHub Actions.
For Python: tox with `envlist = py39,py310,py311,py312`.
For Dart: `dart-version: [stable, beta, dev]` minimum, plus minimum SDK constraint.

## Snapshot of public API

Generate a snapshot of the public API (types + signatures) and check it into the repo. Any PR that changes the snapshot is a SemVer-relevant change.

- TS: `api-extractor` (Microsoft) generates `.api.md`
- Dart: `dart_api_diff` or hand-maintained `lib/<package>.dart` barrel review
- Rust: `cargo public-api`

## What "manual test cases" look like for a library

```markdown
## Manual test cases (LIB-7)

- In a fresh test project, `npm install <lib-name>@latest`
- Import the new export from the README example; verify it works
- Run the README's "advanced" example; verify the output matches the docs
- Run `npx <lib-name> --version`; verify it matches package.json
- Check published bundle: `npm pack`; inspect tarball; ensure no `.test.ts`, no source maps to private files, no `.env`
```

## Common pitfalls

- **Testing only the happy path** — library users will find every edge case you missed
- **Hardcoded paths or env vars** in tests — break for consumers who don't have them
- **Testing transpiled output** — test the source; CI also runs against the built artifact for catastrophic-bundle-breakage
- **Letting `peerDependencies` drift unchecked** — your tests pass on your version of React; users on theirs hit bugs. Multi-version matrix catches this
- **Skipping the multi-runtime matrix because "it works locally"** — you've tested ONE row of the matrix; the others find bugs
