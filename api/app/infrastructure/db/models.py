import uuid

from sqlalchemy import Column, Date, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.domain.task import EstadoTarea, Prioridad
from app.infrastructure.db.session import Base


class TareaORM(Base):
    __tablename__ = "tareas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False, default="")
    prioridad = Column(Enum(Prioridad), nullable=False)
    fecha_limite = Column(Date, nullable=False)
    estado = Column(Enum(EstadoTarea), nullable=False, default=EstadoTarea.PENDIENTE)
    creada_en = Column(DateTime, nullable=False)
    actualizada_en = Column(DateTime, nullable=False)


class AuditoriaORM(Base):
    """Usada por el worker (A5) para registrar la traza de auditoría."""

    __tablename__ = "auditoria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tarea_id = Column(UUID(as_uuid=True), nullable=False)
    evento = Column(String(100), nullable=False)
    detalle = Column(Text, nullable=False)
    procesado_en = Column(DateTime, nullable=False)
