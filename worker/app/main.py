"""Worker independiente (A5): se suscribe al topic TareaCompletada y
registra una traza de auditoría / notificación simulada.

Se ejecuta como proceso/contenedor separado de la API, comunicándose
únicamente a través del broker de eventos (desacoplamiento total).
"""
import json
import logging
import os
import time
import uuid
from datetime import datetime

import redis
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("task-worker")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://tasks:tasks@localhost:5432/tasks"
)
TOPIC = "TareaCompletada"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS auditoria (
    id UUID PRIMARY KEY,
    tarea_id UUID NOT NULL,
    evento VARCHAR(100) NOT NULL,
    detalle TEXT NOT NULL,
    procesado_en TIMESTAMP NOT NULL
);
"""

# Deduplicación simple en memoria de eventos ya procesados (idempotencia,
# elemento diferenciador). En producción se persistiría el event_id.
_procesados: set[str] = set()


def registrar_auditoria(engine, payload: dict) -> None:
    tarea_id = payload["tarea_id"]
    if tarea_id in _procesados:
        logger.info("evento_duplicado_ignorado tarea_id=%s", tarea_id)
        return
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO auditoria (id, tarea_id, evento, detalle, procesado_en) "
                "VALUES (:id, :tarea_id, :evento, :detalle, :procesado_en)"
            ),
            {
                "id": str(uuid.uuid4()),
                "tarea_id": tarea_id,
                "evento": TOPIC,
                "detalle": json.dumps(payload),
                "procesado_en": datetime.utcnow(),
            },
        )
    _procesados.add(tarea_id)
    logger.info("auditoria_registrada tarea_id=%s", tarea_id)


def main():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as conn:
        conn.execute(text(CREATE_TABLE_SQL))

    client = redis.Redis.from_url(REDIS_URL)
    pubsub = client.pubsub()
    pubsub.subscribe(TOPIC)
    logger.info("worker_iniciado topic=%s", TOPIC)

    for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            payload = json.loads(message["data"])
            registrar_auditoria(engine, payload)
        except Exception:
            logger.exception("error_procesando_evento")
            time.sleep(1)  # backoff simple ante fallos (reintento básico)


if __name__ == "__main__":
    main()
