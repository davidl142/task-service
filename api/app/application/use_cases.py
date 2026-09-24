from __future__ import annotations

import uuid
from datetime import date

from app.domain.ports import EventPublisher, TaskFilter, TaskRepository
from app.domain.task import EstadoTarea, Prioridad, Tarea

EVENTO_TAREA_COMPLETADA = "TareaCompletada"


class TareaNoEncontradaError(Exception):
    pass


class CrearTareaUseCase:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def execute(
        self, titulo: str, descripcion: str, prioridad: Prioridad, fecha_limite: date
    ) -> Tarea:
        tarea = Tarea(
            titulo=titulo,
            descripcion=descripcion,
            prioridad=prioridad,
            fecha_limite=fecha_limite,
        )
        self.repo.add(tarea)
        return tarea


class ObtenerTareaUseCase:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def execute(self, tarea_id: uuid.UUID) -> Tarea:
        tarea = self.repo.get(tarea_id)
        if tarea is None:
            raise TareaNoEncontradaError(str(tarea_id))
        return tarea


class ListarTareasUseCase:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def execute(self, filtro: TaskFilter):
        return self.repo.list(filtro)


class ActualizarTareaUseCase:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def execute(self, tarea_id: uuid.UUID, **cambios) -> Tarea:
        tarea = self.repo.get(tarea_id)
        if tarea is None:
            raise TareaNoEncontradaError(str(tarea_id))
        tarea.actualizar(**cambios)
        self.repo.update(tarea)
        return tarea


class CompletarTareaUseCase:
    """Al completar, publica el evento de dominio TareaCompletada (A4)."""

    def __init__(self, repo: TaskRepository, publisher: EventPublisher):
        self.repo = repo
        self.publisher = publisher

    def execute(self, tarea_id: uuid.UUID) -> Tarea:
        tarea = self.repo.get(tarea_id)
        if tarea is None:
            raise TareaNoEncontradaError(str(tarea_id))
        tarea.completar()
        self.repo.update(tarea)
        self.publisher.publish(
            EVENTO_TAREA_COMPLETADA,
            {
                "evento": EVENTO_TAREA_COMPLETADA,
                "tarea_id": str(tarea.id),
                "titulo": tarea.titulo,
                "completada_en": tarea.actualizada_en.isoformat(),
            },
        )
        return tarea


class EliminarTareaUseCase:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def execute(self, tarea_id: uuid.UUID) -> None:
        eliminada = self.repo.delete(tarea_id)
        if not eliminada:
            raise TareaNoEncontradaError(str(tarea_id))
