import uuid
from datetime import date

import pytest

from app.application.use_cases import (
    CompletarTareaUseCase,
    CrearTareaUseCase,
    TareaNoEncontradaError,
)
from app.domain.ports import TaskFilter, TaskRepository
from app.domain.task import Prioridad, Tarea
from app.infrastructure.events.publishers import InMemoryEventPublisher


class FakeTaskRepository(TaskRepository):
    """Fake en memoria: permite testear casos de uso sin base de datos real."""

    def __init__(self):
        self._data: dict[uuid.UUID, Tarea] = {}

    def add(self, tarea):
        self._data[tarea.id] = tarea

    def get(self, tarea_id):
        return self._data.get(tarea_id)

    def list(self, filtro: TaskFilter):
        items = list(self._data.values())
        return items, len(items)

    def update(self, tarea):
        self._data[tarea.id] = tarea

    def delete(self, tarea_id):
        return self._data.pop(tarea_id, None) is not None


def test_crear_tarea_la_persiste():
    repo = FakeTaskRepository()
    tarea = CrearTareaUseCase(repo).execute(
        "Título", "Descripción", Prioridad.MEDIA, date(2026, 1, 1)
    )
    assert repo.get(tarea.id) is not None


def test_completar_tarea_publica_evento():
    repo = FakeTaskRepository()
    publisher = InMemoryEventPublisher()
    tarea = CrearTareaUseCase(repo).execute(
        "Título", "Descripción", Prioridad.ALTA, date(2026, 1, 1)
    )

    CompletarTareaUseCase(repo, publisher).execute(tarea.id)

    assert len(publisher.published) == 1
    topic, payload = publisher.published[0]
    assert topic == "TareaCompletada"
    assert payload["tarea_id"] == str(tarea.id)


def test_completar_tarea_inexistente_lanza_error():
    repo = FakeTaskRepository()
    publisher = InMemoryEventPublisher()
    with pytest.raises(TareaNoEncontradaError):
        CompletarTareaUseCase(repo, publisher).execute(uuid.uuid4())
