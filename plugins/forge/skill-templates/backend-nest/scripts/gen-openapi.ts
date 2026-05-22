// Generate openapi.json from the Nest app's decorators without starting a server.
// Consumed by `npm run docs:api`, which then renders it to docs/api/endpoints.md (Markdown).
// The Markdown is the committed source; any HTML view (Swagger UI / Redoc) is generated
// from this same openapi.json and is never hand-edited.
import { writeFileSync } from "node:fs";
import { NestFactory } from "@nestjs/core";
import { SwaggerModule } from "@nestjs/swagger";
import { AppModule } from "../src/app.module.js";
import { buildOpenApiConfig } from "../src/main.js";

async function main(): Promise<void> {
  const app = await NestFactory.create(AppModule, { logger: false });
  const document = SwaggerModule.createDocument(app, buildOpenApiConfig());
  writeFileSync("openapi.json", JSON.stringify(document, null, 2));
  await app.close();
  // eslint-disable-next-line no-console
  console.log("openapi.json written");
}

void main();
