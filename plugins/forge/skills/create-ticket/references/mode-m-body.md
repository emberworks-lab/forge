# Mode M — manual-setup body

Use when the work is something the USER must do by hand: create a Supabase project, register an OAuth app, generate API keys, set up a Stripe account, configure DNS, etc. No code work; the agent's job is to wait until the user marks the ticket DONE.

## Template

```markdown
## What
<what the user must do manually before code work can begin — 1-2 sentences>

## User actions
1. <e.g. Go to https://supabase.com/dashboard → New project>
2. <e.g. Set project name "embergard-dev"; choose region eu-west>
3. <e.g. Wait for provisioning (~2 min)>
4. <e.g. Copy the anon public key + service_role key from Project Settings → API>
5. <e.g. Save SUPABASE_URL and SUPABASE_ANON_KEY into .env.dev (gitignored)>

## Acceptance
- <verifiable end state, e.g. ".env.dev contains SUPABASE_URL and SUPABASE_ANON_KEY">
- <e.g. "supabase login completed; CLI authenticated">
```

## Rules

Mode M tickets:

- ALWAYS get the `exec:manual` label
- Are placed FIRST in the parent epic — both in native sub-issue UI order (github / linear) and, for `markdown` backend, in the epic's `## Sub-issues` body block (handled by `forge:create-epic`)
- Do NOT get an opus/sonnet label (no agent executes them)
- Block `forge:execute-epic` until the user marks them DONE
