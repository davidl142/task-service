# ADR-001: Elección de base de datos para persistencia de tareas

## Contexto
El servicio necesita persistir tareas con campos estructurados (título,
prioridad, fecha límite, estado) y soportar filtros combinados (estado +
prioridad + rango de fechas) con paginación (A2). No hay requisito de
esquema flexible ni de escritura masiva no estructurada.

## Decisión
Usar **PostgreSQL** como motor de persistencia, accedido vía SQLAlchemy
detrás del puerto `TaskRepository`.

## Alternativas consideradas
- **MongoDB (NoSQL documental)**: flexible para evolución de esquema, pero
  el dominio es completamente estructurado y los filtros combinados con
  paginación son más naturales y eficientes en SQL (índices compuestos).
- **DynamoDB**: excelente para escalar en AWS sin gestión de servidores,
  pero sus patrones de acceso (particionamiento por clave) complican
  consultas ad-hoc con múltiples filtros opcionales, que aquí son un
  requisito explícito (A2).

## Consecuencias
- (+) Consultas de filtrado expresivas y con integridad referencial para
  futuras entidades relacionadas (usuarios, auditoría).
- (+) SQLAlchemy permite cambiar de motor SQL (ej. a Aurora PostgreSQL en
  AWS) sin reescribir la capa de dominio, gracias al puerto `TaskRepository`.
- (-) Requiere gestionar migraciones de esquema al evolucionar el modelo
  (mitigado a futuro con Alembic; ver "Camino a producción").
