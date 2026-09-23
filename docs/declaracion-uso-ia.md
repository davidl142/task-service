# Declaración de uso de IA

## Herramientas usadas y para qué
- **Claude (Anthropic)**: usado para (1) diseñar la estructura hexagonal
  inicial del proyecto, (2) generar el andamiaje de código (routers,
  esquemas, casos de uso, worker) a partir de los requisitos del enunciado,
  (3) redactar borradores del README y los ADR, (4) proponer casos de prueba
  unitarios e de integración.

## Qué validé o corregí
- Ejecuté todos los tests generados (`pytest`) y corregí ajustes de
  compatibilidad de versiones de librerías (SQLAlchemy 2.0, Pydantic v2)
  que la IA no siempre acierta a la primera.
- Revisé manualmente que el evento `TareaCompletada` solo se publique
  **después** de confirmar la transacción de base de datos, para evitar
  inconsistencias entre estado persistido y evento emitido.
- Verifiqué con un smoke test end-to-end (crear → completar → listar) que
  el flujo completo funciona antes de considerar el código como terminado.
- Revisé que ningún secreto (contraseñas, claves) quedara hardcodeado en el
  repositorio; todos se leen de variables de entorno con valores de ejemplo
  en `.env.example`.

## Una decisión en la que NO seguí la sugerencia de la IA
La IA sugirió inicialmente usar una API Key estática para el requisito A6
por ser más rápida de implementar. Decidí usar JWT en su lugar porque
permite demostrar mejor conceptos de expiración y claims de identidad, más
relevantes para la sustentación técnica (ver ADR-003 para el detalle
completo de esta decisión).
