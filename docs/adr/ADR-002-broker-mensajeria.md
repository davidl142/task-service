# ADR-002: Broker de mensajería para el evento TareaCompletada

## Contexto
Al completar una tarea, la API debe publicar un evento de dominio que un
worker independiente consume para registrar auditoría (A4, A5). El
enunciado exige que el mecanismo sea intercambiable detrás de una interfaz.

## Decisión
Definir el puerto `EventPublisher` en el dominio, con dos adaptadores:
- `InMemoryEventPublisher`: usado en pruebas unitarias (sin infraestructura).
- `RedisEventPublisher`: usado en `docker-compose` (pub/sub de Redis) para
  la demo local, por su simplicidad de despliegue con un solo comando.

## Alternativas consideradas
- **RabbitMQ**: más robusto (colas durables, DLQ nativo), pero añade
  complejidad operativa innecesaria para el alcance de la prueba (10h).
- **Amazon SQS/SNS**: es la opción recomendada para producción en AWS
  (durabilidad, DLQ administrado, integración IAM), pero requiere
  credenciales de nube y complica la ejecución 100% local con
  `docker compose up`.
- **Kafka**: sobre-ingeniería para el volumen y alcance de esta prueba.

## Consecuencias
- (+) Cumple el requisito A4 de interfaz intercambiable: pasar a SQS/SNS en
  producción implica solo escribir `SqsEventPublisher` sin tocar casos de uso.
- (-) Redis pub/sub **no persiste mensajes**: si el worker está caído al
  publicarse el evento, el mensaje se pierde. Aceptable para el prototipo;
  en el "Camino a producción" se detalla la migración a SNS+SQS con DLQ.
