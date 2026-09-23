# ADR-003: Estrategia de autenticación de la API

## Contexto
El requisito A6 pide "autenticación simple (JWT o API key)" para proteger
los endpoints de tareas.

## Decisión
Usar **JWT** emitido por un endpoint `/auth/login` que, para efectos de esta
prueba técnica, no valida credenciales contra una base de usuarios real:
recibe un `usuario` y devuelve un token firmado con HS256, válido 60 minutos.
Todos los endpoints de `/tareas` requieren `Authorization: Bearer <token>`.

## Alternativas consideradas
- **API Key estática**: más simple de implementar, pero no permite expresar
  identidad del solicitante ni expiración — menos representativo de un
  esquema real de autorización.
- **Integración con un IdP real (Cognito/Auth0)**: es el camino correcto
  para producción, pero excede el alcance y tiempo de la prueba, y
  añadiría una dependencia externa no gratuita/gestionable en 10h.

## Decisión que NO seguí de la IA (ver también declaración de uso de IA)
La sugerencia inicial de la IA fue usar API Key estática por simplicidad.
Se descartó porque JWT permite demostrar mejor el manejo de expiración,
claims (`sub`) y el patrón de verificación como dependencia de FastAPI,
que es más representativo de un esquema de autenticación real y evaluable
en la sustentación.

## Consecuencias
- (+) Demuestra manejo de expiración, verificación de firma y claims.
- (-) No hay gestión real de usuarios/contraseñas ni revocación de tokens;
  documentado como fuera de alcance. En producción se integraría con un IdP
  corporativo (ver "Camino a producción" en el documento de solución).
