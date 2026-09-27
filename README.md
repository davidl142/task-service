# Servicio de Gestión de Tareas Orientado a Eventos

Prueba técnica — Opción A — Ingeniero de Soluciones TI.

API REST de gestión de tareas que publica el evento de dominio `TareaCompletada`
al broker de mensajería cuando una tarea se marca como completada. Un
**worker independiente** consume ese evento y registra una traza de auditoría,
sin que la API conozca su existencia (desacoplamiento total vía eventos).

## Arquitectura resumida

```
┌─────────────┐      HTTP       ┌──────────────┐
│   Cliente   │ ───────────────▶│   task-api    │
└─────────────┘                 │ (FastAPI)     │
                                 └──────┬────────┘
                                        │ publica evento
                                        │ "TareaCompletada"
                                        ▼
                                 ┌──────────────┐
                                 │    Redis     │◀── pub/sub
                                 │ (pub/sub)    │
                                 └──────┬────────┘
                                        │ consume
                                        ▼
                                 ┌──────────────┐        ┌────────────┐
                                 │ task-worker   │ ─────▶│ PostgreSQL │
                                 │ (auditoría)   │        │ (auditoria)│
                                 └──────────────┘        └────────────┘
                                        ▲
                                        │
                                 ┌──────┴────────┐
                                 │  task-api      │
                                 │  (tareas)      │──────▶ PostgreSQL (tareas)
                                 └────────────────┘
```

- **Arquitectura hexagonal / Clean**: `domain` (entidades y puertos) →
  `application` (casos de uso) → `infrastructure` (SQLAlchemy, Redis, JWT) →
  `interfaces/http` (FastAPI, routers, schemas).
- **Broker intercambiable (A4)**: `EventPublisher` es un puerto (`domain/ports.py`)
  con dos adaptadores: `InMemoryEventPublisher` (tests) y `RedisEventPublisher`
  (docker-compose). Cambiar a SQS/SNS/RabbitMQ/Kafka solo requiere una nueva
  clase que implemente el mismo contrato.
- Ver diagrama C4 completo y ADRs en [`docs/`](./docs).

## Cómo ejecutar localmente

Requisitos: Docker y Docker Compose.

```bash
cp .env.example .env   # ajustar JWT_SECRET si se desea
docker compose up --build
```

- API disponible en: `http://localhost:8000`
- Documentación OpenAPI/Swagger: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Flujo de prueba manual

```bash
# 1. Obtener token (autenticación simplificada para la prueba)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"usuario":"demo"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 2. Crear una tarea
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"titulo":"Revisar reporte","descripcion":"Reporte mensual","prioridad":"alta","fecha_limite":"2026-12-31"}'

# 3. Completar la tarea (dispara el evento TareaCompletada)
curl -X PATCH http://localhost:8000/tasks/<id>/completar -H "Authorization: Bearer $TOKEN"

# 4. Verificar la auditoría generada por el worker
docker compose exec db psql -U tasks -d tasks -c "SELECT * FROM auditoria;"
```

## Cómo ejecutar las pruebas

```bash
cd api
pip install -r requirements.txt -r requirements-dev.txt

# Unitarias (no requieren Docker)
python -m pytest tests/unit -v --cov=app

# Integración (requiere Docker corriendo, usa testcontainers)
python -m pytest tests/integration -v
```

Reporte de cobertura: se genera en consola y como `coverage.xml` (también
publicado como artefacto en el pipeline de CI).

## URL de la aplicación desplegada

> _Completar tras el despliegue:_ `https://<pendiente>`
> Credenciales de prueba: usuario `demo` (ver endpoint `/auth/login`, no requiere contraseña real — ver ADR-003).

## Estructura del proyecto

```
api/
  app/
    domain/            # Entidades y puertos (sin dependencias externas)
    application/        # Casos de uso (orquestan el dominio)
    infrastructure/      # Adaptadores: DB (SQLAlchemy), eventos (Redis), JWT
    interfaces/http/     # FastAPI: routers, schemas, dependencias
  tests/
    unit/               # Prueban dominio y casos de uso con fakes
    integration/         # API + PostgreSQL real (testcontainers)
worker/
  app/main.py           # Consumidor independiente (A5)
docs/
  adr/                  # Registros de decisiones de arquitectura
  solucion.pdf          # Documento de solución (C4, NFRs, riesgos, etc.)
.github/workflows/ci.yml # Pipeline: build, test, SAST, SCA, secret scanning
docker-compose.yml       # Levanta api + worker + db + redis con un comando
```

## Decisiones y supuestos documentados

- Se asumió que "autenticación simple" (A6) permite un login sin verificación
  de contraseña real, enfocado en emitir/validar JWT — ver ADR-003.
- Se usó `create_all` de SQLAlchemy en vez de migraciones Alembic para
  simplificar el arranque en 10h; en producción se usarían migraciones
  versionadas (ver Camino a producción en el documento de solución).
- El broker por defecto en `docker-compose` es Redis pub/sub (sin persistencia
  de mensajes); para AWS en producción se propone SNS+SQS con DLQ (ver ADR-002
  y sección "Camino a producción").

## Declaración de uso de IA

Ver [`docs/declaracion-uso-ia.md`](./docs/declaracion-uso-ia.md).
