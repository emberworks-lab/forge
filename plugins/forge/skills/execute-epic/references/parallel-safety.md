# Parallel safety checklist

REQUIRED if `--parallel` was passed. Walk this explicitly before dispatching N subagents in parallel for any group.

- [ ] Each ticket touches DIFFERENT files (no overlap by exact path; confirm via `## Files` or `## Steps`)
- [ ] No shared in-memory state between tickets (no shared mocks, shared fixtures being mutated, shared singletons being initialized)
- [ ] No sequential dependencies (`A blocks B` relations resolved; `## Depends on` cleared)
- [ ] Each subagent receives full context (no inheriting from controller — controller curates a fresh prompt per subagent)
- [ ] Controller curates the prompt per subagent (NOT "here's a list of tickets, pick one and go" — each subagent gets its specific ticket + its specific plan slice)
- [ ] Codegen-dependent tickets (Drift / freezed / build_runner) NOT in the same parallel group as tickets that depend on the regenerated output

If ANY box unchecked → fall back to sequential execution for this group. Tell the user:

```
Parallel safety check failed for group [EMB-X, EMB-Y]: <reason — file overlap on lib/foo.dart / shared fixture in test/util>.
Falling back to sequential.
```

This rule is conservative on purpose. False sequentialism wastes time but never corrupts output; false parallelism corrupts output and burns more time on cleanup. Default to safe.
