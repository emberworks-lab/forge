# Manual VM-service coverage workflow

Use this path when the default `dart run coverage:test_with_coverage` is insufficient — typically because the task requires branch coverage, function coverage, or fine-grained control over isolate pausing.

## Task progress checklist

- [ ] 1. Run tests with VM service enabled (paused-on-exit).
- [ ] 2. Collect raw JSON coverage.
- [ ] 3. Format JSON to LCOV.

## 1. Run tests with VM service

Execute tests while pausing isolates on exit and exposing the VM service on a known port (e.g. 8181). Background the process so the collector can attach:

```bash
dart run --pause-isolates-on-exit --disable-service-auth-codes --enable-vm-service=8181 test &
```

## 2. Collect raw coverage

Attach the collector to the running VM service and write JSON:

```bash
dart run coverage:collect_coverage \
  --wait-paused \
  --uri=http://127.0.0.1:8181/ \
  -o coverage/coverage.json \
  --resume-isolates
```

Optional flags (Dart VM 2.17.0+):

- `--function-coverage` — per-function hit counts.
- `--branch-coverage` — per-branch hit counts.

## 3. Format to LCOV

Convert the raw JSON to LCOV, honoring inline ignore directives:

```bash
dart run coverage:format_coverage \
  --packages=.dart_tool/package_config.json \
  --lcov \
  -i coverage/coverage.json \
  -o coverage/lcov.info \
  --check-ignore
```

## Gotchas

- If the VM service port is already bound, change `--enable-vm-service=<port>` and the matching `--uri` flag.
- `--check-ignore` is required for `coverage:ignore-file` / `ignore-start` directives to take effect at format time.
- Branch / function coverage flags require a recent Dart VM; older SDKs silently drop them.
