import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module.js";
import { AllExceptionsFilter } from "./exceptions/all-exceptions.filter.js";

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule);

  app.useGlobalFilters(new AllExceptionsFilter());

  const port = parseInt(process.env["PORT"] ?? "3000", 10);
  await app.listen(port);
}

void bootstrap();
