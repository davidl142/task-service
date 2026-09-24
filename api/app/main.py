import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.infrastructure.db.session import Base, engine
from app.interfaces.http.routers import auth, tasks

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="Servicio de Gestión de Tareas",
    description="API orientada a eventos para gestión de tareas (Opción A - Prueba técnica)",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.on_event("startup")
def on_startup():
    # Para la prueba técnica se usa create_all; en producción se usarían
    # migraciones versionadas (Alembic). Ver ADR-002.
    Base.metadata.create_all(bind=engine)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.exception("Error no controlado")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "ERROR_INTERNO", "message": "Ocurrió un error inesperado"}},
    )


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
