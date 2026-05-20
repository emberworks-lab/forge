# API Error Catalog

All errors follow the **RFC 7807** envelope shape. Every response with a 4xx
or 5xx status code returns a JSON body of the form:

```json
{
  "code": "snake_case_error_code",
  "message": "Human-readable description.",
  "requestId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

| Field       | Type   | Notes                                                  |
|-------------|--------|--------------------------------------------------------|
| `code`      | string | Stable machine-readable code. **Key off this.**        |
| `message`   | string | English description. May change between releases.      |
| `requestId` | string | Echo of `X-Request-Id`. Use for support correlation.  |

## Error codes

| HTTP | `code`                  | When thrown                                     |
|------|-------------------------|-------------------------------------------------|
| 400  | `BadRequestException`   | Malformed request body / query params           |
| 401  | `UnauthorizedException` | Missing or invalid auth token                   |
| 403  | `ForbiddenException`    | Authenticated but not allowed                   |
| 404  | `NotFoundException`     | Resource not found                              |
| 422  | `validation_error`      | Schema validation failure (pipes/guards)        |
| 429  | `ThrottlerException`    | Rate-limit exceeded                             |
| 500  | `internal_server_error` | Unhandled exception — check server logs         |

> Add project-specific codes to this table as you introduce new exceptions.
> Keep codes in `snake_case`; use the exception class name only as a fallback.
