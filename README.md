# AI Engineer Lab — Proyecto incremental

## Contexto
Eres AI Engineer en **AtlasOps**, una empresa ficticia que ofrece una plataforma SaaS para equipos de operaciones y soporte técnico.

El equipo de soporte interno tiene documentación dispersa sobre:
- arquitectura y servicios,
- gestión de incidencias,
- despliegues,
- permisos,
- procedimientos operativos,
- errores conocidos.

El objetivo inicial es construir un **asistente RAG interno** que responda preguntas basándose exclusivamente en esta documentación y cite las fuentes utilizadas.

Este proyecto evolucionará más adelante hacia un sistema agentic con LangGraph, tools, MCP, memory, HITL, guardrails, evals, observabilidad, FastAPI, Docker, CI/CD y AWS/AgentCore.

## Fase actual
**Fase 1 — RAG**

En esta fase NO hay agentes, MCP, tools externas ni memoria persistente.

Tu objetivo es diseñar y construir el pipeline RAG.

## Regla principal
No se evalúa solo que “funcione”.

Debes poder explicar:
- cómo cargas los documentos,
- cómo los divides,
- qué metadata conservas,
- qué embeddings utilizas,
- qué vector store eliges,
- cómo recuperas contexto,
- cómo construyes el prompt,
- cómo evitas responder sin evidencia,
- cómo citas la fuente,
- cómo comprobarías si el retrieval es bueno o malo.

## Restricción
El asistente debe responder únicamente con información respaldada por la base documental. Si no encuentra evidencia suficiente, debe indicarlo claramente.

## Punto de partida
Lee primero:
1. `PROJECT_BRIEF.md`
2. los documentos de `knowledge_base/`
3. `evaluation/questions.md`

No empieces programando inmediatamente. Primero diseña tu solución y justifica tus decisiones.
