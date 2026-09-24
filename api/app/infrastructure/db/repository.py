from __future__ import annotations

import uuid
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.ports import TaskFilter, TaskRepository
from app.domain.task import EstadoTarea, Prioridad, Tarea
from app.infrastructure.db.models import TareaORM


def _to_domain(row: TareaORM) -> Tarea:
    return Tarea(
        id=row.id,
        titulo=row.titulo,
        descripcion=row.descripcion,
        prioridad=row.prioridad,
        fecha_limite=row.fecha_limite,
        estado=row.estado,
        creada_en=row.creada_en,
        actualizada_en=row.actualizada_en,
    )


class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, tarea: Tarea) -> None:
        row = TareaORM(
            id=tarea.id,
            titulo=tarea.titulo,
            descripcion=tarea.descripcion,
            prioridad=tarea.prioridad,
            fecha_limite=tarea.fecha_limite,
            estado=tarea.estado,
            creada_en=tarea.creada_en,
            actualizada_en=tarea.actualizada_en,
        )
        self.session.add(row)
        self.session.commit()

    def get(self, tarea_id: uuid.UUID) -> Tarea | None:
        row = self.session.get(TareaORM, tarea_id)
        return _to_domain(row) if row else None

    def list(self, filtro: TaskFilter) -> tuple[Iterable[Tarea], int]:
        stmt = select(TareaORM)
        if filtro.estado:
            stmt = stmt.where(TareaORM.estado == filtro.estado)
        if filtro.prioridad:
            stmt = stmt.where(TareaORM.prioridad == filtro.prioridad)
        if filtro.desde:
            stmt = stmt.where(TareaORM.fecha_limite >= filtro.desde)
        if filtro.hasta:
            stmt = stmt.where(TareaORM.fecha_limite <= filtro.hasta)

        total = self.session.scalar(
            select(func.count()).select_from(stmt.subquery())
        )
        stmt = stmt.offset((filtro.page - 1) * filtro.size).limit(filtro.size)
        rows = self.session.scalars(stmt).all()
        return [_to_domain(r) for r in rows], total or 0

    def update(self, tarea: Tarea) -> None:
        row = self.session.get(TareaORM, tarea.id)
        if row is None:
            return
        row.titulo = tarea.titulo
        row.descripcion = tarea.descripcion
        row.prioridad = tarea.prioridad
        row.fecha_limite = tarea.fecha_limite
        row.estado = tarea.estado
        row.actualizada_en = tarea.actualizada_en
        self.session.commit()

    def delete(self, tarea_id: uuid.UUID) -> bool:
        row = self.session.get(TareaORM, tarea_id)
        if row is None:
            return False
        self.session.delete(row)
        self.session.commit()
        return True
