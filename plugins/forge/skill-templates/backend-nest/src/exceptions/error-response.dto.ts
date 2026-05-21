/**
 * RFC 7807-style error envelope returned by AllExceptionsFilter.
 *
 * Clients key off `code` (stable machine-readable string) rather than
 * HTTP status text or exception class names.
 *
 * See docs/api/errors.md for the full error catalog.
 */
export interface ErrorResponseDto {
  /** Machine-readable error code (snake_case). */
  code: string;
  /** Human-readable description (may change between releases). */
  message: string;
  /** Echo of X-Request-Id / request.id for correlation. */
  requestId: string;
}
