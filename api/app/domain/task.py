"""Entidades de dominio. Sin dependencias de frameworks (Clean/Hexagonal)."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum


class Prioridad(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class EstadoTarea(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"


class DomainError(Exception):
    """Error de negocio (se traduce a 4xx en la capa HTTP)."""


class TransicionInvalidaError(DomainError):
    pass


@dataclass
class Tarea:
    titulo: str
    descripcion: str
    prioridad: Prioridad
    fecha_limite: date
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    estado: EstadoTarea = EstadoTarea.PENDIENTE
    creada_en: datetime = field(default_factory=datetime.utcnow)
    actualizada_en: datetime = field(default_factory=datetime.utcnow)

    def completar(self) -> None:
        if self.estado == EstadoTarea.COMPLETADA:
            raise TransicionInvalidaError("La tarea ya está completada")
        self.estado = EstadoTarea.COMPLETADA
        self.actualizada_en = datetime.utcnow()

    def actualizar(
        self,
        titulo: str | None = None,
        descripcion: str | None = None,
        prioridad: Prioridad | None = None,
        fecha_limite: date | None = None,
        estado: EstadoTarea | None = None,
    ) -> None:
        if titulo is not None:
            self.titulo = titulo
        if descripcion is not None:
            self.descripcion = descripcion
        if prioridad is not None:
            self.prioridad = prioridad
        if fecha_limite is not None:
            self.fecha_limite = fecha_limite
        if estado is not None:
            self.estado = estado
        self.actualizada_en = datetime.utcnow()
