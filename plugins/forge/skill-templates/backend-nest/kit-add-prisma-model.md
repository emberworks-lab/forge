---
name: kit-add-prisma-model
description: "Use when adding or changing a Prisma model, table, column, enum, index, or relation in prisma/schema.prisma — and therefore creating a database migration."
---

# kit-add-prisma-model

## When to use

- Triggers: "add a model", "new table", "add a column / field / enum / index", "new migration", `/kit-add-prisma-model`.

Don't use for: querying existing models (that's repository code), or schema-less changes.

## What it produces

- An edited `prisma/schema.prisma`
- A new committed migration directory under `prisma/migrations/`
- A regenerated Prisma client
- A repository class (`<entity>.repository.ts`) wrapping Prisma access for that model

## Required inputs

- Model name in PascalCase (e.g. `Order`, `LineItem`)
- Fields with types, nullability, and default values
- Any relations to existing models
- Feature module the model belongs to (determines where the repository lives)

## Steps

1. **Edit `prisma/schema.prisma`** — add the model / field / enum. Use `@id @default(cuid())` for IDs and `@default(now())` / `@updatedAt` for timestamps, consistent with existing models.
2. **Create the migration:**
   ```bash
   npx prisma migrate dev --name <snake_case_description>
   ```
   This runs **locally against your development database**. It writes the SQL to `prisma/migrations/`, applies it, and regenerates the Prisma client.
3. **Commit the migration** directory together with the `schema.prisma` change in the same commit. `prisma/migrations/` is tracked in git — it is the source of truth for DB state.
4. **Add a repository** — `src/modules/<feature>/<entity>.repository.ts`: an `@Injectable()` class that injects `PrismaService` and exposes verb-named methods (`findById`, `create`, `update`, `delete`). Keep raw `prisma.*` calls inside the repository; services and controllers never call `PrismaService` directly.
5. **Register the repository** as a provider in the owning feature module.
6. Run `npm run lint && npm test && npm run build`.

## Migration rules

| Rule | Why |
|---|---|
| `migrate dev` runs on your **local machine only** | It mutates the connected database; never run it in CI or production |
| `migrate deploy` runs in the **deployment environment only** | Production migrations are applied at deploy time, not by hand |
| **Never hand-edit** files in `prisma/migrations/` | They are generated; fix a bad migration with a new one |
| **One migration per logical change** | Keeps history reviewable; don't bundle unrelated schema changes |
| Commit every migration | The directory is the authoritative DB history |

`DATABASE_URL` is the runtime connection (typically pooled); `DIRECT_URL` is the direct connection that migrations require. The exact env-var names depend on your deployment setup — check `.env.example`.

## Conventions

- IDs: `@id @default(cuid())` unless the project convention differs.
- Timestamps: `createdAt DateTime @default(now())` and `updatedAt DateTime @updatedAt`.
- Repository methods are verbs (`findById`, `create`, `markArchived`), never nouns.
- Repository return types are Prisma model types or mapped domain types — never raw `prisma.*` calls exposed to callers.

## Anti-patterns

- Running `prisma migrate dev` in CI or against a shared staging database without coordination.
- `prisma db push` — it skips migration history; this project is migration-tracked.
- Editing a generated `migration.sql` by hand.
- Returning Prisma `*CreateInput` / `*UpdateInput` objects from a repository — map to domain types inside.
- Bundling two unrelated schema changes into one migration.

## Example

```ts
// order.repository.ts
@Injectable()
export class OrderRepository {
  constructor(private readonly prisma: PrismaService) {}

  findById(id: string): Promise<Order | null> {
    return this.prisma.order.findUnique({ where: { id } });
  }

  create(data: { userId: string; total: number }): Promise<Order> {
    return this.prisma.order.create({ data });
  }
}
```

## References

- `prisma/schema.prisma` — current models, ID/timestamp conventions
- `prisma/migrations/` — existing migration history
- `src/prisma/prisma.service.ts` (or equivalent) — the injectable Prisma client
- `src/modules/<feature>/` — feature module that owns the repository
