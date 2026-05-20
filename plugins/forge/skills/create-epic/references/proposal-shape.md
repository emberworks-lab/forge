# Proposal shape (Step 4 of `forge:create-epic`)

The Step 4 proposal block is ONE compact chat message with three parts: epic title, epic body, and a bulleted sub-issue list.

## Epic title

Use phase prefix if the project convention requires it (e.g. `P1.1 — <title>`).

## Epic body — backend-conditional sections

GitHub and Linear surface parent / dependency relations natively (Issue Types + sub-issue API + `blockedBy` / `blocks`). Adding text-block duplicates is noise. Markdown lacks native UI, so its bodies keep the relation blocks.

- Native backends (`github`, `linear`) → skip `## Sub-issues` and `## Depends on` text blocks.
- Text-only backend (`markdown`) → keep them.

Required: `## What`, `## Acceptance`. Optional: include only when relevant.

```
## What                 (required)
2-3 sentences — goal, not how.

## Scope                (optional — include for refactors OR when extending existing functionality;
                                    skip for fully greenfield work)
- Keep: ...
- Change: ...
- Out of scope: ...

## Design               (optional — include only if a design artifact exists for the WHOLE epic
                                    that spans multiple sub-issues)
- Figma: <url>
- HTML mockup: <path or url>
- Description: <docs/design/<name>.md or other md path>
- ADR / RFC / sequence diagram: <path>
(any combination — list whichever apply; skip the section entirely if none)

## References           (optional — related issues, prior work, supporting docs)
- IF-XX
- docs/<path> §X

## Acceptance           (required)
- 5-8 verifiable bullets.

(## Sub-issues — added only for backends without native sub-issue UI; omitted for github / linear)
```

## Sub-issue list

After the body, a bullet list. For each sub-issue, indicate:

1. **Area** — only when multi-repo (see `multi-repo-detection.md`). Tag: `[<area-repo-short-name>]`, e.g. `[backend]`, `[mobile]`, `[tracker]`. Single-repo projects omit.
2. **Mode** — which `forge:create-ticket` body shape it will use:
   - `[A: docs/0X_<name>.md]` — doc-backed
   - `[B-a: inline steps]` — full inline plan
   - `[B-b: interview]` — body asks executor to interview the user
   - `[B-c: read-first]` — body lists files to read first
   - `[M: exec:manual]` — user-only manual steps; no code work
3. **Executor** — `[opus]` for new architecture, formula derivation, security-critical, design-heavy; `[sonnet]` for typical implementation by an existing plan, scaffolds, content additions, l10n, refactoring with clear scope. **Default `[sonnet]` if uncertain.** Reserve `[opus]` for genuinely thinking-heavy work. Manual-setup tickets (`[M]`) get `exec:manual` — no agent executes them.

### Example (single-repo)

```
- E1.1: Set up Supabase project + keys              [M: exec:manual]
- E1.2: Implement damage pipeline                   [A: docs/04_tech/combat-architecture.md] [opus]
- E1.3: Hit/crit/lucky formula                      [B-a: inline steps] [opus]
- E1.4: AP cycle state machine                      [B-c: read-first] [sonnet]
- E1.5: Combat UI live HP bars + damage numbers     [B-a: inline steps] [sonnet]
- E1.6: Combat formula property tests               [B-c: read-first] [sonnet]
```

### Example (multi-repo with `epics_repo`)

```
- E1.1: Provision external services + collect creds [tracker] [M: exec:manual]
- E1.2: Flutter project init via /project-init      [mobile]  [M: exec:manual]
- E1.3: NestJS scaffold + middleware + /health      [backend] [B-a: inline steps] [sonnet]
- E1.4: Prisma + Supabase wiring + DB healthcheck   [backend] [B-a: inline steps] [sonnet]
- E1.5: Fly.io deploy + Sentry + UptimeRobot        [backend] [B-a: inline steps] [sonnet]
```

**Manual-setup tickets ALWAYS appear FIRST** in the proposal list, and — for `markdown` backend — in the `## Sub-issues` body block, regardless of dependencies. They block `forge:execute-epic` until closed by the user.

**Do not show dependencies** in the proposal — the user doesn't want them in the planning view. You decide them silently in Step 6.

## Sub-issue numbering

GitHub doesn't surface sub-issue execution order well outside the parent's sidebar. A numbered title prefix (`E1.1:`, `E1.2:`, ...) makes priority obvious in every view.

Extract the epic number from the epic title (case-insensitive, first match wins):

- `Epic (\d+):` → e.g. `Epic 1: Foundation` → `1`
- `E(\d+) ` → e.g. `E1 — Foundation` → `1` (loose match)
- `P(\d+)\.\d+` → phase prefix → **skip auto-numbering** (phase prefix is the dominant convention).

If a leading epic number is found, auto-prefix every sub-issue title at creation time with `E<N>.<idx>:` where `<idx>` is the 1-based position in the proposed order. Manual-setup tickets keep their FIRST position, so they typically become `E<N>.1`, `E<N>.2`, etc.

If no epic number is detected, no prefix is added (backward-compatible).

Show the proposed prefixed titles in the Step 4 proposal so the user sees the final form before confirming.
