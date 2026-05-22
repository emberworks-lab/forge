# Forge Plugin — Test Tiers

The forge plugin has three test tiers with different cost and speed profiles.
Pick the right tier for the job; never run billable tiers on the inner dev loop.

---

## Tier 1 — Structural (fast gate, no model)

**What it does:** Runs `audit.sh` over every `plugins/forge/skills/*/SKILL.md`.
Checks front-matter, line caps, dangling `references/` pointers, and forbidden
patterns. Deterministic — no network, no model, no cost.

**When it runs:** Automatically on every `git push` and every pull-request via
the [forge-tests CI workflow](../../../.github/workflows/forge-tests.yml). Merge
is **blocked** if this job fails.

**Run locally:**

```bash
# From the repo root
bash plugins/forge/tests/structural/run-all.sh
```

Exit 0 = all skills pass. Exit 1 = one or more failed (details printed inline).
Exit 2 = setup error (audit.sh or skills directory not found).

---

## Tier 2 — Triggering (billable, on-demand / nightly)

**What it does:** Sends naive natural-language prompts to `claude -p` and
asserts that the correct `forge:<skill>` is triggered. Each case is one real
model invocation — takes 10–60 s and consumes API credit.

**When it runs:** Never on push/PR. Only via `workflow_dispatch` (manual trigger
with `run_billable = true`) or the nightly schedule (02:00 UTC). Requires the
`ANTHROPIC_API_KEY` CI secret (see [CI secrets](#ci-secrets) below).

**Run locally:**

```bash
# Run all triggering cases
bash plugins/forge/tests/triggering/run-all.sh

# Run a single case
bash plugins/forge/tests/triggering/run-test.sh <skill-name> <prompt-file> [max-turns]
# Example:
bash plugins/forge/tests/triggering/run-test.sh tdd plugins/forge/tests/triggering/prompts/tdd.txt
```

Prompts live in `plugins/forge/tests/triggering/prompts/<skill-name>.txt`.

---

## Tier 3 — Fixtures (billable, on-demand / nightly, gated behind `--live`)

**What it does:** Each fixture seeds a known input state, runs a forge skill via
`claude -p`, and asserts the output. Running the live mode is billable and slow
(60–300 s per fixture). Without `--live` (assertion-only mode), a fixture exits
with error 2 unless a `--result-dir` with pre-baked output is supplied.

**When it runs:** Same gate as Tier 2 — never on push/PR. Requires
`ANTHROPIC_API_KEY`. In CI the fixture runner uses assertion-only mode against
any pre-baked result directories; use `--live` for a full end-to-end run.

**Run locally:**

```bash
# Assertion-only against a pre-baked result dir
bash plugins/forge/tests/fixtures/simplify/run-fixture.sh --result-dir /path/to/result

# Full live run (billable — invokes claude -p)
bash plugins/forge/tests/fixtures/simplify/run-fixture.sh --live
```

Each fixture under `plugins/forge/tests/fixtures/<name>/run-fixture.sh` follows
the same `--live` / `--result-dir` interface.

---

## Fast gate vs billable — summary

| Tier | Triggers on push/PR | Model calls | Cost |
|------|---------------------|-------------|------|
| Structural | Yes — blocks merge | None | Free |
| Triggering | No | `claude -p` per case | Billable |
| Fixtures | No | `claude -p` (with `--live`) | Billable |

The fast gate (Tier 1) is the only tier that runs automatically on the
push/pull-request inner loop. Tiers 2 and 3 are intentionally kept off that
path to avoid surprise billing during normal development.

---

## CI secrets

The billable jobs in `.github/workflows/forge-tests.yml` require:

| Secret name | Scope | Purpose |
|-------------|-------|---------|
| `ANTHROPIC_API_KEY` | Repository secrets | Passed as `ANTHROPIC_API_KEY` env var to `claude -p` in both Tier 2 and Tier 3 jobs |

**How to set it:**
1. Go to the repo on GitHub → **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret**.
3. Name: `ANTHROPIC_API_KEY` — Value: your Anthropic API key.
4. Save.

The key is never printed in logs; do not hardcode it in scripts or workflow files.
The structural job (Tier 1) does **not** need this secret and works without it.
