# Backward tracing

When the error fires deep in the stack, the fix point is rarely where the exception surfaces. Trace backward to where the bad value was created, fix at the source, add defense-in-depth on the way down.

## When to use

- Stack trace is long and the failing call is several layers removed from any code you wrote.
- The failing parameter is "empty", "undefined", "null", or otherwise an obvious downstream casualty.
- You don't know which caller produced the bad input.

If the bug is shallow (one or two frames), just read the code; backward tracing is overkill.

## The process

### 1. Observe the symptom

```
Error: git init failed in /Users/me/project/packages/core
```

### 2. Find the immediate cause

What code directly triggers this?

```typescript
await execFile('git', ['init'], { cwd: projectDir });
```

`projectDir` is the suspect input.

### 3. Walk up the call chain

What called this with `projectDir`?

```
WorktreeManager.createSessionWorktree(projectDir, sessionId)
  ← Session.initializeWorkspace()
    ← Session.create()
      ← test setup at line 47
```

### 4. Inspect the value at each layer

What was `projectDir` at the moment of the call? `""` (empty string). An empty `cwd` resolves to `process.cwd()`, which is the source directory — hence `.git` ended up in `packages/core/`.

### 5. Find the original trigger

Where did the empty string come from?

```typescript
const context = setupCoreTest(); // returns { tempDir: '' } pre-beforeEach
Project.create('name', context.tempDir);
```

The test accessed `context.tempDir` before `beforeEach` had populated it. That's the root cause — not the missing validation in `WorktreeManager`.

### 6. Fix at the source

Make `tempDir` a getter that throws if accessed before initialization. The downstream code no longer needs to handle the empty case because the empty case can no longer exist.

## When manual tracing isn't enough

If the code path is too tangled to trace by reading, instrument:

```typescript
async function gitInit(directory: string) {
  if (!directory) {
    console.error('DEBUG empty git directory', {
      cwd: process.cwd(),
      env: process.env.NODE_ENV,
      stack: new Error().stack,
    });
  }
  await execFile('git', ['init'], { cwd: directory });
}
```

Run once, read the stack, find the test file + line that triggered the call. Same idea as boundary instrumentation, applied to a single value rather than a boundary crossing.

## After finding the source: defense in depth

Fix at the source AND add validation at each downstream layer the bad value would have passed through. Each layer that refuses the bad value is one more place the bug can never re-emerge:

- Project.create() validates the directory is non-empty.
- WorkspaceManager validates it points inside the expected tmp tree.
- A `NODE_ENV=test` guard refuses `git init` outside `$TMPDIR`.
- The git-init helper logs context before invoking.

If the source fix regresses, one of the layers below catches it.

## Anti-pattern: fixing at the symptom

```typescript
async function gitInit(directory: string) {
  if (!directory) return; // BAD — silently skip
  await execFile('git', ['init'], { cwd: directory });
}
```

This patches the visible symptom and hides the bug. The test that originally accessed `tempDir` early now silently produces a half-set-up project, which will fail somewhere else, possibly intermittently. Fix at the source.

## Stack trace tips

- In test environments, prefer `console.error` over your project logger; loggers are often suppressed by the test runner.
- Log *before* the dangerous operation. After-the-fact logging usually loses the context you need.
- Include cwd, env vars relevant to the operation, and a captured stack. The stack tells you who, not just what.
