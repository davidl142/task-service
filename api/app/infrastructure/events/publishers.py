"""Implementaciones intercambiables de EventPublisher (requisito A4).

- InMemoryEventPublisher: usada en tests unitarios y como fallback local.
- RedisEventPublisher: usada en docker-compose para comunicar API <-> worker
  en procesos/contenedores distintos.

Cambiar de broker (a SQS/SNS, RabbitMQ, Kafka) implica solo agregar una nueva
clase que cumpla el Protocol `EventPublisher`; el resto del código no cambia.
"""
from __future__ import annotations

import json
import logging
import os

logger = logging.getLogger(__name__)


class InMemoryEventPublisher:
    def __init__(self):
        self.published: list[tuple[str, dict]] = []

    def publish(self, topic: str, payload: dict) -> None:
        self.published.append((topic, payload))
        logger.info("evento_en_memoria", extra={"topic": topic, "payload": payload})


class RedisEventPublisher:
    def __init__(self, redis_url: str | None = None):
        import redis  # import diferido: no requerido si se usa InMemory

        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client = redis.Redis.from_url(self.redis_url)

    def publish(self, topic: str, payload: dict) -> None:
        self._client.publish(topic, json.dumps(payload))
        logger.info("evento_publicado_redis", extra={"topic": topic})


def build_event_publisher():
    """Factory: decide el broker según configuración (patrón puerto/adaptador)."""
    broker = os.getenv("EVENT_BROKER", "redis")
    if broker == "memory":
        return InMemoryEventPublisher()
    return RedisEventPublisher()
