"""Autenticación simplificada para la prueba técnica: emite un JWT para
cualquier 'usuario' recibido. En un entorno real esto validaría credenciales
contra un proveedor de identidad (Cognito, Auth0, IdP corporativo, etc.).
"""
from fastapi import APIRouter

from app.infrastructure.security.jwt_handler import crear_token
from app.interfaces.http.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    token = crear_token(subject=body.usuario)
    return LoginResponse(access_token=token)
