"""Puertos (interfaces) que la capa de aplicación necesita.
La infraestructura implementa estos contratos (Inversión de Dependencias).
"""
from __future__ import annotations

import abc
import uuid
from datetime import date
from typing import Iterable, Protocol

from app.domain.task import EstadoTarea, Prioridad, Tarea


class TaskFilter:
    def __init__(
        self,
        estado: EstadoTarea | None = None,
        prioridad: Prioridad | None = None,
        desde: date | None = None,
        hasta: date | None = None,
        page: int = 1,
        size: int = 20,
    ):
        self.estado = estado
        self.prioridad = prioridad
        self.desde = desde
        self.hasta = hasta
        self.page = page
        self.size = size


class TaskRepository(abc.ABC):
    """Puerto de persistencia. Cualquier motor (SQL/NoSQL) puede implementarlo."""

    @abc.abstractmethod
    def add(self, tarea: Tarea) -> None: ...

    @abc.abstractmethod
    def get(self, tarea_id: uuid.UUID) -> Tarea | None: ...

    @abc.abstractmethod
    def list(self, filtro: TaskFilter) -> tuple[Iterable[Tarea], int]: ...

    @abc.abstractmethod
    def update(self, tarea: Tarea) -> None: ...

    @abc.abstractmethod
    def delete(self, tarea_id: uuid.UUID) -> bool: ...


class EventPublisher(Protocol):
    """Puerto de mensajería. Permite cambiar de broker sin tocar la lógica
    de negocio (requisito A4): en memoria, Redis, SQS/SNS, RabbitMQ, Kafka...
    """

    def publish(self, topic: str, payload: dict) -> None: ...
