---
name: kit-add-queue
description: "Use when adding a new background queue, async job, worker/processor, or a scheduled/repeatable job — work that runs outside the HTTP request path. Also use when a background job fails silently with no error alert."
---

# kit-add-queue

## When to use

- Triggers: "add a queue", "background job", "new worker / processor", "scheduled job", "cron job", `/kit-add-queue`.
- A job fails but nothing reaches your error-reporting seam — a processor is missing its failure hook.

Don't use for: synchronous request handling (`/kit-create-endpoint`).

## What it produces

- `src/queues/<name>/<name>-job.types.ts` — queue-name constant + payload union types
- `src/queues/<name>/<name>.queue.ts` — producer with retry policy
- `src/queues/<name>/<name>.processor.ts` — worker host + a `failed` event hook
- `src/queues/<name>/<name>-queue.module.ts` — module wiring
- The module registered in `AppModule` imports

## Required inputs

- Queue name in kebab-case (e.g. `email-delivery`, `report-export`)
- Job payload shape
- Retry policy (or accept the defaults below)
- Whether the queue needs a scheduled / repeatable job

## Step 0 — install your queue library

This template ships **no queue dependency**. Before Step 1, install your queue library and register the global module. Example using **BullMQ + Redis**:

```bash
npm install @nestjs/bullmq bullmq
```

In `AppModule`:
```ts
BullModule.forRoot({ connection: { host: process.env.REDIS_HOST, port: +process.env.REDIS_PORT } })
```

See "Swapping the queue provider" at the bottom for pg-boss and cloud alternatives.

## Steps

1. **Job types** — export `const <NAME>_QUEUE = "<name>"` and the payload type(s) in `<name>-job.types.ts`.
2. **Producer** — `<name>.queue.ts`: `@Injectable()` class with `@InjectQueue(<NAME>_QUEUE)`, verb-named `enqueue*` methods. Pass `DEFAULT_JOB_OPTIONS` (retry policy below).
3. **Processor** — `<name>.processor.ts`: `@Processor(<NAME>_QUEUE)` class extending `WorkerHost`, implement `process(job)`. **Add a `failed` event hook** (see "Failure reporting" below).
4. **Module** — `<name>-queue.module.ts`: register the queue, declare processor + producer as providers, export the producer.
5. Register the module in `AppModule` imports.
6. Run `npm run lint && npm test && npm run build`.

## Retry policy — required

Every queue must set `attempts` + `backoff`. A queue without them runs each job once — a transient failure is permanent:

```ts
// BullMQ example
const DEFAULT_JOB_OPTIONS: JobsOptions = {
  attempts: 3,
  backoff: { type: 'exponential', delay: 5_000 },
  removeOnComplete: { age: 3_600 },
  removeOnFail: false,  // keep failed jobs for inspection
};
```

Adjust `attempts` and `delay` based on the job's external dependency (email gateway, file store, etc.).

## Failure reporting — required

Workers run **outside the HTTP request path**. A throw inside `process()` never reaches `AllExceptionsFilter` — without an explicit hook a failed job is **silent**. Every processor must report failures to your error-reporting seam:

```ts
// BullMQ example — swap Sentry.captureException for your seam
@OnWorkerEvent('failed')
onFailed(job: Job<<Name>Payload> | undefined, error: Error): void {
  this.logger.error({ jobId: job?.id, error }, 'Job failed');
  // Replace with your error-reporting seam (Sentry, Datadog, custom sink):
  ErrorReporter.captureException(error, { tags: { queue: <NAME>_QUEUE } });
}
```

`ErrorReporter` is an abstract stand-in — inject your actual error-reporting service. It operates independently of any pipeline that may itself be the thing failing (e.g. email delivery).

## Scheduled / repeatable jobs

For recurring work, add a repeatable job with a cron pattern, registered once at module startup (not per request):

```ts
// BullMQ example
await this.queue.add('<name>', payload, {
  repeat: { pattern: '0 * * * *' },  // document the timezone assumption here
});
// or: await this.queue.upsertJobScheduler(...)
```

## Swapping the queue provider

This skill's worked example uses **BullMQ (Redis)**. The contract — producer / processor / retry policy / failure hook — maps onto other providers:

### pg-boss (Postgres)
- No Redis dependency; uses your existing Postgres as the queue store.
- Install: `npm install pg-boss`
- Job scheduling, retry, and failure callbacks map to `boss.work()` + `boss.on('error', ...)`.
- Wrap `pg-boss` in an `@Injectable()` service and expose the same producer/processor interface.

### Cloud queues (AWS SQS, GCP Pub/Sub, Azure Service Bus)
- Install the relevant SDK; wrap in an NestJS module that provides a producer and a consumer/listener.
- Retry policy is configured on the queue/topic resource itself (dead-letter queue); keep a local `MAX_ATTEMPTS` constant for early-exit logic in the processor.
- Failure hook: subscribe to the DLQ or the provider's failure event; forward to your error-reporting seam.

Regardless of provider: keep the job-types file (constants + payload types) and the module wiring pattern the same — only the transport implementation changes.

## Anti-patterns

- A processor with **no `failed` event hook** → failures vanish.
- A queue with **no retry policy** → one transient failure = permanent job loss.
- Hardcoding the queue connection per queue — use a global `BullModule.forRoot()` (or equivalent) in `AppModule`.
- Expecting `AllExceptionsFilter` or a global error handler to catch worker throws — it won't.
- Registering a repeatable job inside a request handler — it must be idempotent and registered at startup.

## References

- `src/queues/` — existing queues (reference pattern for retry policy + processor)
- `src/app.module.ts` — global queue provider registration
- `src/exceptions/all-exceptions.filter.ts` — why it does NOT catch worker throws
- `.env.example` — required queue env vars (connection strings, credentials)
