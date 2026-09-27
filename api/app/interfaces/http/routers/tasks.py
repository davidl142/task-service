import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.use_cases import (
    ActualizarTareaUseCase,
    CompletarTareaUseCase,
    CrearTareaUseCase,
    EliminarTareaUseCase,
    ListarTareasUseCase,
    ObtenerTareaUseCase,
    TareaNoEncontradaError,
)
from app.domain.ports import EventPublisher, TaskFilter, TaskRepository
from app.domain.task import EstadoTarea, Prioridad, TransicionInvalidaError
from app.infrastructure.security.jwt_handler import verificar_token
from app.interfaces.http.dependencies import get_event_publisher, get_task_repository
from app.interfaces.http.schemas import (
    ActualizarTareaRequest,
    CrearTareaRequest,
    TareaListResponse,
    TareaResponse,
)

router = APIRouter(prefix="/tasks", tags=["task"], dependencies=[Depends(verificar_token)])


def _error(status_code: int, code: str, message: str):
    raise HTTPException(status_code=status_code, detail={"code": code, "message": message})


@router.post("", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(body: CrearTareaRequest, repo: TaskRepository = Depends(get_task_repository)):
    tarea = CrearTareaUseCase(repo).execute(
        body.titulo, body.descripcion, body.prioridad, body.fecha_limite
    )
    return tarea


@router.get("", response_model=TareaListResponse)
def listar_tareas(
    estado: EstadoTarea | None = None,
    prioridad: Prioridad | None = None,
    desde: str | None = None,
    hasta: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    repo: TaskRepository = Depends(get_task_repository),
):
    filtro = TaskFilter(
        estado=estado, prioridad=prioridad, desde=desde, hasta=hasta, page=page, size=size
    )
    items, total = ListarTareasUseCase(repo).execute(filtro)
    return TareaListResponse(items=list(items), total=total, page=page, size=size)


@router.get("/{task_id}", response_model=TareaResponse)
def obtener_tarea(task_id: uuid.UUID, repo: TaskRepository = Depends(get_task_repository)):
    try:
        return ObtenerTareaUseCase(repo).execute(task_id)
    except TareaNoEncontradaError:
        _error(status.HTTP_404_NOT_FOUND, "TAREA_NO_ENCONTRADA", "La tarea no existe")


@router.put("/{task_id}", response_model=TareaResponse)
def actualizar_tarea(
    task_id: uuid.UUID,
    body: ActualizarTareaRequest,
    repo: TaskRepository = Depends(get_task_repository),
):
    try:
        return ActualizarTareaUseCase(repo).execute(task_id, **body.model_dump(exclude_unset=True))
    except TareaNoEncontradaError:
        _error(status.HTTP_404_NOT_FOUND, "TAREA_NO_ENCONTRADA", "La tarea no existe")


@router.patch("/{task_id}/completar", response_model=TareaResponse)
def completar_tarea(
    task_id: uuid.UUID,
    repo: TaskRepository = Depends(get_task_repository),
    publisher: EventPublisher = Depends(get_event_publisher),
):
    try:
        return CompletarTareaUseCase(repo, publisher).execute(task_id)
    except TareaNoEncontradaError:
        _error(status.HTTP_404_NOT_FOUND, "TAREA_NO_ENCONTRADA", "La tarea no existe")
    except TransicionInvalidaError as e:
        _error(status.HTTP_409_CONFLICT, "TRANSICION_INVALIDA", str(e))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(task_id: uuid.UUID, repo: TaskRepository = Depends(get_task_repository)):
    try:
        EliminarTareaUseCase(repo).execute(task_id)
    except TareaNoEncontradaError:
        _error(status.HTTP_404_NOT_FOUND, "TAREA_NO_ENCONTRADA", "La tarea no existe")
