# WebSocket / Real-time Events

> **Note:** This file refers to the `asyncapi.yaml` skeleton at the project
> root.  When you add NestJS Gateways, document each channel here and keep
> `asyncapi.yaml` in sync.

## Overview

_(No real-time events yet. Remove this note once gateways are added.)_

## Channel reference

See `asyncapi.yaml` for machine-readable channel/message schemas.

| Channel | Direction | Payload type | Description |
|---------|-----------|--------------|-------------|
| _(none)_ | — | — | — |

## Gateway implementation notes

- Gateways live in `src/<feature>/<feature>.gateway.ts`.
- Use `@WebSocketGateway({ namespace: '/<ns>' })` to scope channels.
- Each new gateway must add its channels to this file **and** to
  `asyncapi.yaml` in the same PR (enforced by `CLAUDE.md` rule).
