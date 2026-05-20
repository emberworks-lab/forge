---
name: zoom-out
description: Map the relevant modules and callers around unfamiliar code, using the project's domain vocabulary and surfacing any ADRs that constrain the area.
type: minimal
disable-model-invocation: true
---

I don't know this area of code well. Go up a layer of abstraction. Give me a map of all the relevant modules and callers, using the project's domain glossary vocabulary.

If this project uses a modular monolith structure (e.g. `lib/<domain>/{core,formulas,blocs,persistence,ui}/`), organize the map by domain and show how cross-domain interactions flow through barrel files (`lib/<domain>/<domain>.dart`). Identify which domain owns the code I'm looking at and which other domains depend on it.

Before summarizing, also check:
- `docs/04_tech/adr/*.md` — for architectural decisions that constrain how this module is used
- `docs/00_meta/decisions-log.md` — for recent decisions that may affect the area

Surface any relevant ADR or decision-log entry in the summary (one line each, with the key constraint). Don't re-litigate the decisions — just surface them so I understand the guard rails.
