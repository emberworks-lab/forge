import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
} from "@nestjs/common";
import { Request, Response } from "express";
import type { ErrorResponseDto } from "./error-response.dto.js";

/**
 * Global exception filter.  Normalises every thrown value into the
 * RFC 7807-style ErrorResponseDto envelope defined in error-response.dto.ts.
 *
 * Registration: app.useGlobalFilters(new AllExceptionsFilter()) in main.ts.
 *
 * Add new branches here when you introduce opt-in validation libraries
 * (e.g. nestjs-zod) so all error shapes stay consistent.
 */
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    // Prefer an explicit request-id header; fall back to express req.id if
    // a request-id middleware is present, otherwise mark as unknown.
    const requestId =
      (request.headers["x-request-id"] as string | undefined) ??
      (typeof (request as Request & { id?: string }).id === "string"
        ? (request as Request & { id?: string }).id
        : "unknown") ??
      "unknown";

    let statusCode: number;
    let code: string;
    let message: string;

    if (exception instanceof HttpException) {
      statusCode = exception.getStatus();
      const res = exception.getResponse();
      if (typeof res === "string") {
        code = exception.constructor.name;
        message = res;
      } else {
        const obj = res as Record<string, unknown>;
        code =
          typeof obj["code"] === "string"
            ? obj["code"]
            : exception.constructor.name;
        message =
          typeof obj["message"] === "string"
            ? obj["message"]
            : exception.message;
      }
    } else {
      statusCode = HttpStatus.INTERNAL_SERVER_ERROR;
      code = "internal_server_error";
      message =
        exception instanceof Error ? exception.message : "An error occurred";
    }

    const body: ErrorResponseDto = { code, message, requestId };

    response.status(statusCode).json(body);
  }
}
