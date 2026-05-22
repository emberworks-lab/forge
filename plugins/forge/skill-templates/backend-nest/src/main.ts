import { NestFactory } from "@nestjs/core";
import { DocumentBuilder, SwaggerModule } from "@nestjs/swagger";
import { AppModule } from "./app.module.js";
import { AllExceptionsFilter } from "./exceptions/all-exceptions.filter.js";

// Build the OpenAPI document. Shared by the running server (Swagger UI at /docs)
// and the docs:api generator (scripts/gen-openapi.ts) so both use one source.
export function buildOpenApiConfig() {
  return new DocumentBuilder()
    .setTitle(process.env["APP_NAME"] ?? "API")
    .setVersion(process.env["APP_VERSION"] ?? "0.0.1")
    .build();
}

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule);

  app.useGlobalFilters(new AllExceptionsFilter());

  // Interactive Swagger UI (generated from decorators) — never hand-written.
  const document = SwaggerModule.createDocument(app, buildOpenApiConfig());
  SwaggerModule.setup("docs", app, document);

  const port = parseInt(process.env["PORT"] ?? "3000", 10);
  await app.listen(port);
}

void bootstrap();
