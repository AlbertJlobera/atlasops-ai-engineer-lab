# Project Brief — AtlasOps Knowledge Assistant

## Problema
Los ingenieros de soporte de AtlasOps pierden tiempo buscando procedimientos y soluciones en documentación interna.

La empresa quiere un primer prototipo de asistente que permita hacer preguntas en lenguaje natural y recuperar respuestas verificables desde documentación interna.

## Usuario objetivo
Ingenieros de soporte L1/L2 y desarrolladores de guardia.

## Ejemplos de consultas
- ¿Qué debo comprobar si el servicio de cálculo devuelve `CALC-017`?
- ¿Cuándo se puede hacer rollback automático?
- ¿Quién puede ejecutar una operación administrativa en producción?
- ¿Qué endpoint se utiliza para comprobar la salud del servicio?
- ¿Qué hago si el consumidor Kafka acumula lag?

## Requisitos funcionales de la Fase 1
1. Ingerir los documentos entregados.
2. Crear un índice consultable semánticamente.
3. Recuperar contexto relevante ante una pregunta.
4. Generar una respuesta utilizando solo dicho contexto.
5. Mostrar las fuentes/documentos que respaldan la respuesta.
6. Rechazar o reconocer preguntas para las que no haya evidencia suficiente.
7. Permitir ejecutar varias preguntas sin reconstruir todo el índice innecesariamente.

## Requisitos no funcionales
- Python.
- Código organizado y entendible.
- Configuración sensible fuera del código.
- Persistencia del vector store si la tecnología elegida lo permite.
- Logging básico.
- Diseño que pueda evolucionar posteriormente.
- No es necesario crear frontend todavía.

## Fuera de alcance en esta fase
- LangGraph.
- agentes autónomos.
- MCP.
- llamadas a sistemas reales.
- modificación de incidencias.
- autenticación.
- despliegue AWS.
- FastAPI.
- Docker.
- CI/CD.

Se añadirán progresivamente.

## Criterios de evaluación
Se valorará especialmente:
- calidad del retrieval,
- razonamiento sobre chunking,
- uso correcto de metadata,
- groundedness de las respuestas,
- manejo de información insuficiente,
- capacidad para depurar fallos,
- claridad para defender las decisiones técnicas.

## Entregable de esta fase
Un repositorio ejecutable desde local que permita realizar preguntas contra la documentación y observar:
- pregunta,
- documentos/chunks recuperados,
- score o información equivalente si está disponible,
- respuesta final,
- fuentes.
