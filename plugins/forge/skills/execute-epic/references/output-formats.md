# Output formats for `forge:execute-epic`

## Step 4 — plan preview

```
Execution plan for EMB-227:
1. EMB-228 [opus, A]
2. EMB-229 [opus, B-a]
3. parallel: EMB-230 [sonnet], EMB-231 [sonnet]
4. EMB-232 [sonnet, B-c]
```

## Step 7 — manual test cases comment on the epic

```markdown
## Manual test cases (epic <EPIC-ID>)

### <SUB-REF> — <title>
- <case 1>
- <case 2>

### <SUB-REF> — <title>
- <case 1>
- ...

(Automated checks: lint clean, <X> tests passed, <Y> commits, <Z> files changed)
```

## Step 8 — final summary to chat

```
Epic: <EPIC-ID> executed
Tickets done: <N>
Commits: <N>
Files changed: <N>
Lint: clean
Tests: passed (<X> tests)
Manual cases: posted to epic (<URL>)

Next:
1. Review commits: git log <base>..HEAD
2. Run manual test cases from the epic comment
3. When manual verification is done:
   - /epic-close <EPIC-ID> — squash + status update + docs sync
   - Optionally /pr-create <EPIC-ID> — create draft PR
```
