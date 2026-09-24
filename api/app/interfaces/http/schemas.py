import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.domain.task import EstadoTarea, Prioridad


class CrearTareaRequest(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descripcion: str = ""
    prioridad: Prioridad
    fecha_limite: date


class ActualizarTareaRequest(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    descripcion: str | None = None
    prioridad: Prioridad | None = None
    fecha_limite: date | None = None
    estado: EstadoTarea | None = None


class TareaResponse(BaseModel):
    id: uuid.UUID
    titulo: str
    descripcion: str
    prioridad: Prioridad
    fecha_limite: date
    estado: EstadoTarea
    creada_en: datetime
    actualizada_en: datetime

    class Config:
        from_attributes = True


class TareaListResponse(BaseModel):
    items: list[TareaResponse]
    total: int
    page: int
    size: int


class ErrorResponse(BaseModel):
    error: dict


class LoginRequest(BaseModel):
    usuario: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
