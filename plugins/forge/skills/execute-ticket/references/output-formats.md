# Output formats for `forge:execute-ticket`

## Step 9 — manual test cases comment on the ticket

```markdown
## Manual test cases (<TICKET-REF>)

- <action 1>
- <action 2>
- <action 3>

(automated: <lint result>, <test result>; <files changed count> files)
```

The trailing line summarizes what was automatically verified.

## Step 12 — DONE summary (when `--commit`)

```
Ticket: <TICKET-REF> done
Files changed: <N>
Commit: <short SHA>
Manual cases: posted to tracker (see ticket comment)
```

## Step 12 — NO-COMMIT summary (standalone, default)

```
Ticket: <TICKET-REF> implemented (not committed)
Files changed: <N>
Lint: clean
Tests: passed (X tests)
Manual cases: posted to tracker (see ticket comment)
Next: review the diff, then `/commit <NUM>` if good
```

## Step 12 — HALTED summary

```
Ticket: <TICKET-REF> HALTED
Reason: <lint failed | build-validate failed | tests failed>
Details: <count> failures; see <log path or stdout>
No commit made.
Next: fix manually, or address the underlying issue
```
