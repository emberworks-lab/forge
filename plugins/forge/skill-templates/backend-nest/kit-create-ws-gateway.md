---
name: kit-create-ws-gateway
description: "Use when adding real-time WebSocket functionality to the backend — a Socket.io gateway, a streaming response, live chat, or any persistent bidirectional connection."
---

# kit-create-ws-gateway

## When to use

- Triggers: "WebSocket", "Socket.io", "real-time", "streaming response", "live updates", "gateway", `/kit-create-ws-gateway`.

Don't use for: request/response HTTP (`/kit-create-endpoint`) or background jobs (`/kit-add-queue`).

## What it produces

- `@nestjs/websockets` + `socket.io` dependencies installed (Step 1)
- A `@WebSocketGateway()` class for the feature
- Authenticated handshakes (JWT verified via an injected auth seam)
- A streaming pattern using an injected domain service
- Persisted message/event history (via a Prisma model from `/kit-add-prisma-model`)

## Required inputs

- Feature name (snake_case, e.g. `chat`, `live-feed`)
- Auth seam: which injectable service verifies tokens for the handshake
- Domain/streaming seam: which injectable service produces the stream
- Session key: what uniquely identifies a connection session (e.g. `userId`, `userId + resourceId`)
- Whether message history must survive reconnect (usually yes)

## Steps

1. **Install** (skip if `@nestjs/websockets` is already installed):
   ```bash
   npm install @nestjs/websockets @nestjs/platform-socket.io socket.io
   ```
2. **Gateway** — create `src/modules/<feature>/<feature>.gateway.ts` with `@WebSocketGateway({ cors: { origin: process.env.ALLOWED_ORIGINS?.split(',') ?? '*' } })`. Implement `handleConnection`, `handleDisconnect`, and `@SubscribeMessage(...)` handlers.
3. **Authenticate the handshake.** Read the JWT from `client.handshake.auth.token`. Inject your **auth seam** (`AuthVerifier` or equivalent) — do **not** re-implement JWT verification in the gateway. Reject the connection (`client.disconnect()`) on an invalid or expired token. Store the resolved `userId` (or session identity) on the socket data.
4. **Bind the session** — associate the socket with its domain key (e.g. `userId`, or `(userId, resourceId)`). Use socket rooms or a local Map for routing server-initiated events.
5. **Stream via the domain service seam.** Inject your domain/streaming service; call its stream method and emit chunks as they arrive (`client.emit('chunk', { data })`). The gateway's job is transport only — no business logic here.
6. **Persist history** — if the feature requires history across reconnect, store messages/events in a Prisma model (create it with `/kit-add-prisma-model`). Load and replay on reconnect.
7. **Error handling** — emit a structured error *event* to the client on expected failures (`client.emit('error', { code: 'snake_case', message: '...' })`); never let a throw kill the socket. Send unexpected errors to your error-reporting seam (`ErrorReporter.captureException`) — gateway exceptions bypass `AllExceptionsFilter`.
8. **Doc-sync** — after implementing, update `docs/api/websockets.md` (event catalog: name, direction, payload shape, description) and `asyncapi.yaml` (machine-readable spec). See the Doc-sync note below.
9. Run `npm run lint && npm test && npm run build`.

## Conventions

- One gateway per real-time feature.
- The auth seam and the domain/streaming seam are **always injected** — never instantiated inside the gateway. This makes the gateway testable and swappable.
- Keep the gateway thin: transport + auth + routing only; all business logic lives in the domain service.
- Handle reconnect gracefully: the client re-authenticates with a fresh token; the gateway accepts it without losing persisted session state.
- Socket.io is the default transport. If the project uses native WebSockets (`ws`) instead, the pattern is the same; only the decorator options and event API change.

## Doc-sync note

Every PR that adds or changes a gateway MUST update:

| Doc | Content |
|---|---|
| `docs/api/websockets.md` | Event catalog: name, direction (client→server / server→client), payload shape, description |
| `asyncapi.yaml` | Machine-readable AsyncAPI spec; HTML view is generated from this, never hand-edited |

Reviewers reject gateway PRs without these updates.

## Anti-patterns

- Re-implementing JWT / token verification inside the gateway instead of calling the auth seam.
- Accepting a connection without verifying the handshake token.
- Holding event history only in memory — it must persist (reconnect, server restart).
- Blocking the event loop inside a streaming handler (use `async`/`await` correctly; never `while(true)` without yielding).
- Letting a throw inside a handler crash the socket or escape unreported.
- Hard-coding any concrete domain service name directly in the gateway — always inject seams through the constructor.

## Example

```ts
// chat.gateway.ts
@WebSocketGateway({ cors: { origin: process.env.ALLOWED_ORIGINS ?? '*' } })
export class ChatGateway implements OnGatewayConnection, OnGatewayDisconnect {
  constructor(
    private readonly authVerifier: AuthVerifier,        // injected auth seam
    private readonly streamService: ChatStreamService,  // injected domain seam
  ) {}

  async handleConnection(client: Socket): Promise<void> {
    const token = client.handshake.auth?.token;
    const identity = await this.authVerifier.verify(token).catch(() => null);
    if (!identity) { client.disconnect(); return; }
    client.data.userId = identity.userId;
  }

  handleDisconnect(client: Socket): void {
    // clean up rooms / local state
  }

  @SubscribeMessage('start-stream')
  async onStartStream(
    client: Socket,
    payload: { resourceId: string },
  ): Promise<void> {
    const { userId } = client.data;
    try {
      for await (const chunk of this.streamService.stream(userId, payload.resourceId)) {
        client.emit('chunk', { data: chunk });
      }
      client.emit('stream-end');
    } catch (err) {
      client.emit('error', { code: 'stream_failed', message: 'Stream interrupted' });
      ErrorReporter.captureException(err);
    }
  }
}
```

## References

- `src/modules/<feature>/<feature>.gateway.ts` — gateway implementation
- `docs/api/websockets.md` — event catalog (hand-maintained)
- `asyncapi.yaml` — machine-readable WebSocket spec
- NestJS WebSockets docs — verify the current `@WebSocketGateway` API at implementation time
