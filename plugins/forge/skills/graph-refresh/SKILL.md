---
name: graph-refresh
description: Thin wrapper around `code-review-graph build --incremental`. Rebuilds the code-review graph for the current project and reports duration and node/edge count diff.
type: minimal
---

# Graph Refresh

Run an incremental rebuild of the code-review graph for the current project. Safe to call any time — idempotent.

## Steps

1. **Check tool availability.** Run `command -v code-review-graph`. If the command is not found, print:

   ```
   graph-refresh: code-review-graph not installed; skipping graph refresh. Install per docs/INSTALL.md
   ```

   Exit 0. Do not proceed further.

2. **Check project wiring.** Look for `.mcp.json` in the current working directory. If absent, print:

   ```
   graph-refresh: No .mcp.json in this project; graph not enabled. Run forge:project-init to wire it up.
   ```

   Exit 0. Do not proceed further.

3. **Run the incremental build.** Execute from the project root:

   ```bash
   code-review-graph build --incremental
   ```

   Capture stdout and stderr together.

4. **Parse output.** Scan the captured output for mentions of:
   - Files updated (e.g. `N file(s) updated`, `N files changed`)
   - Node count (e.g. `N nodes`)
   - Edge count (e.g. `N edges`)
   - Duration (e.g. `in Xs`, `Xs elapsed`, `took Xs`)

   Use 0 / unknown as fallback when a value is absent.

5. **Print compact summary.** Format:

   ```
   graph-refresh: <N> files updated, <N> nodes, <N> edges (<duration>)
   ```

   Example: `graph-refresh: 2 files updated, 41 nodes, 87 edges (3.2s)`

   If parsing fails entirely, relay the raw tool output instead.
