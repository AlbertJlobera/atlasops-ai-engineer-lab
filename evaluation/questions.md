# Fase 1 — Preguntas iniciales de evaluación

Estas preguntas se usarán para comprobar el RAG. No optimices el sistema escribiendo reglas específicas para ellas.

## Preguntas con respuesta documental
1. ¿Qué significa el error CALC-017 y qué comprobaciones debo hacer primero?
2. ¿Debo reiniciar calculation-service en cuanto aparezca CALC-017?
3. ¿Cuándo se escala CALC-017 al owner del servicio?
4. ¿En qué condiciones puede producirse un rollback automático?
5. ¿Se puede hacer rollback automático si hay una migración no compatible hacia atrás?
6. ¿Puede un usuario Support-L1 reiniciar servicios en producción?
7. ¿Puede Support-L2 modificar directamente registros de PostgreSQL?
8. Si Redis y PostgreSQL muestran estados diferentes, ¿cuál debo considerar correcto?
9. ¿Qué debo revisar si el consumer group acumula más de 5.000 mensajes durante más de 10 minutos?
10. ¿Qué endpoint puedo consultar para comprobar la salud de calculation-service?
11. ¿Qué debe hacerse si la documentación no cubre una pregunta?
12. ¿Se pueden guardar tokens de producción en el repositorio?

## Preguntas que requieren combinar información
13. El health check de calculation-service devuelve 200, pero siguen aumentando los CALC-017 para un único tipo de cálculo. ¿Es suficiente el health check para descartar un problema?
14. Tras un despliegue aumenta el HTTP 5xx al 8% durante seis minutos y no hubo migraciones incompatibles. ¿Qué mecanismo podría activarse?
15. El event-worker tiene lag alto y PostgreSQL está saturado. ¿Debería escalar workers inmediatamente?

## Preguntas sin soporte suficiente
16. ¿Cuál es la región AWS donde se ejecuta producción?
17. ¿Cuánto cuesta mensualmente la infraestructura?
18. ¿Cuál es el teléfono del responsable de guardia?
19. ¿Qué versión exacta de PostgreSQL se utiliza?
20. ¿Cuál es el SLA contractual con los clientes?
