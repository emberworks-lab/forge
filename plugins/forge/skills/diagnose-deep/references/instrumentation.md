# Boundary instrumentation

When a defect crosses component boundaries, the cheapest way to localize it is to log what enters and exits each boundary before forming any hypothesis. This is Phase 1, step 4 of `diagnose-deep`.

## The principle

Multi-component systems fail because data, config, or environment doesn't propagate across a boundary the way you think it does. Reading code rarely catches this; observing runtime data does. The cost of one instrumented run is small; the cost of three wrong-hypothesis fixes is large.

## The pattern

For each boundary in the chain:

1. Log what data enters the component.
2. Log what data exits.
3. Verify environment / config / secrets are present.
4. Verify state at each layer (keychain, db, file system, env vars).

Run once. Read the output top-to-bottom. The boundary where "expected" turns into "missing" or "wrong" is your failing component.

## Example: CI signing pipeline

A macOS app signs in CI but fails locally — or the reverse. The chain is: workflow secrets → build script env → signing script → `codesign`. Each boundary is a potential drop point.

```bash
# Layer 1: workflow secrets reachable?
echo "=== workflow ==="
echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

# Layer 2: env vars survived into the build script?
echo "=== build script env ==="
env | grep IDENTITY || echo "IDENTITY missing from environment"

# Layer 3: keychain populated?
echo "=== keychain ==="
security list-keychains
security find-identity -v

# Layer 4: actual signing
codesign --sign "$IDENTITY" --verbose=4 "$APP"
```

One run, and the output tells you whether the secret was missing in the workflow, dropped between workflow and build script, never written to the keychain, or refused by `codesign`. Each of those is a different fix.

## Example: API → service → DB

Same pattern, different stack:

```python
# Layer 1: handler entry
log.info("api.request", path=req.path, user_id=req.user_id, body_size=len(req.body))

# Layer 2: service call
log.info("service.fetch_user", user_id=user_id)
user = repo.get_user(user_id)
log.info("service.fetch_user.result", found=user is not None)

# Layer 3: repository
log.info("repo.query", sql=sql, params=params)
rows = db.execute(sql, params)
log.info("repo.query.result", row_count=len(rows))
```

You now know whether the user_id reached the service, whether the SQL was right, and whether the DB returned rows. Three boundaries, three hypotheses pre-tested in one run.

## Rules

- **Log before the dangerous operation, not after it fails.** "Why did this fail?" needs context that's already gone by the time the exception fires.
- **Include context.** Inputs, environment, time, request ID. Anything you'd ask about when the report comes in.
- **Use `console.error` or stderr in test runs.** Test runners often suppress stdout but pass stderr through.
- **Capture stack traces in deep stacks.** `new Error().stack` (JS) / `traceback.format_stack()` (Python) / `runtime.Stack` (Go) — shows who called the failing operation, often the real culprit.
- **Don't leave instrumentation in.** Strip it when the root cause is found, or move it to permanent structured logs if the boundary is one you'll debug again.

## When this doesn't help

- Single-component bugs (one file, one function). Just read the code.
- Bugs already reproducible in a one-line script. Skip instrumentation; the reproducer is your evidence.
- Bugs in code you didn't write and can't modify. Use external tracing (strace, dtrace, network capture, sidecar logs) instead of source-level prints.
