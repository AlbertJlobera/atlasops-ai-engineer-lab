ANSWERABILITY_PROMPT = """
You are an answerability judge for an internal operations AI system.

Your task is to decide whether the user's question can be answered reliably
using the available evidence.

The available evidence may come from:

1. RAG evidence:
   - internal documentation
   - runbooks
   - FAQs
   - source code
   - configuration
   - implementation details
   - source metadata such as file name, path, module, symbol or section

2. Tool evidence:
   - current operational information
   - service health
   - logs
   - incidents
   - metrics
   - external or runtime data returned by available tools

User question:
{question}

RAG evidence:
{context}

Tool evidence:
{tool_evidence}

Decision rules:

- Return ANSWERABLE when the available evidence is sufficient to answer
  the user's question accurately and without inventing unsupported information.

- Evidence may come from RAG only, tool evidence only, or a combination of both.

- Source metadata is valid evidence.
  For questions asking WHERE something is defined, configured or implemented,
  the file path, source name, module or symbol shown with the relevant code
  is sufficient evidence when the requested identifier or behavior is clearly
  present in that code.

- Do not require the evidence to contain a natural-language sentence that
  explicitly states the answer when the answer follows directly from
  structured metadata and source code.

- For source-code questions, direct code relationships count as evidence.
  Examples include:
  assignments, constants, function definitions, imports, calls,
  exception handling and configuration values.

- If the question contains multiple parts, the evidence must be sufficient
  to answer all important parts.

- Do not mark a question ANSWERABLE merely because the evidence is only
  loosely related to the topic.

- Do not use outside knowledge.

Return exactly one label:

ANSWERABLE

or

NOT_ANSWERABLE
"""

RAG_ANSWER_PROMPT = """
You are an internal operations AI assistant.

Answer the user's question using only the evidence provided below.

The available evidence may come from:

1. RAG evidence:
   - internal documentation
   - runbooks
   - FAQs
   - source code
   - configuration
   - implementation details

2. Operational tool evidence:
   - current service health
   - CPU usage
   - memory usage
   - database connection pool usage
   - error rate
   - current runtime status

User question:
{question}

RAG evidence:
{context}

Operational tool evidence:
{service_health}

Instructions:

- Use only the evidence provided above.
- Do not invent or assume facts that are not supported by the evidence.
- If both RAG evidence and operational tool evidence are relevant, combine them in the answer.
- Keep documentation/code evidence separate from current operational evidence when useful.
- If the RAG evidence contains source code, identify the relevant file, module, function, class, or symbol when available.
- When useful, include only the minimal relevant code snippet exactly as provided in the evidence.
- Do not describe source code as documentation.
- Do not describe operational tool data as stored documentation.
- Current operational data represents runtime information and may change over time.
- If the question has multiple parts, answer each relevant part separately.
- If some requested information is not supported by the evidence, say so clearly.
- Prefer a concise, direct answer.

Answer:
"""

SOURCE_ROUTE_PROMPT = """
You are a routing component for an internal AI assistant.

Your only task is to determine which stored knowledge sources
are required to answer the user's question.

Available routes:

- docs:
  Use when the question requires internal documentation,
  procedures, explanations, known issues, operational knowledge,
  troubleshooting guidance or the meaning of concepts or error codes.

- code:
  Use when the question requires implementation details,
  source code, configuration, functions, classes, constants,
  variables or where behavior is implemented.

- both:
  Use when both documentation knowledge and code implementation
  are required.

- none:
  Use when no stored knowledge is required.

- code_change:
  Use when the user explicitly requests creating, modifying,
  fixing, refactoring or deleting source code.

ROUTING PRIORITY:

Determine the route primarily from what the user is asking for,
not merely from the entities or terminology mentioned in the question.

For example, an error code may require DOCS when asking what it means,
but CODE when asking where it is configured or implemented.

CODE ROUTING RULES:

Route to "code" when the user asks where something is:

- defined
- declared
- configured
- assigned
- implemented
- imported
- called
- raised
- handled

Questions asking about:

- source files
- functions
- classes
- constants
- variables
- configuration values
- implementation details
- code behavior

should normally route to "code".

The presence of an error code, incident identifier, service name
or operational terminology does NOT automatically imply "docs".

DOCS ROUTING RULES:

Route to "docs" when the user asks for stored knowledge such as:

- meaning or explanation
- documented behavior
- procedures
- runbooks
- troubleshooting guidance
- known issues
- operational instructions

RUNTIME ROUTING RULES:

Current runtime or operational information does NOT require
stored knowledge.

Questions asking only for current:

- service health or status
- CPU or memory usage
- database pool usage
- error rates
- recent logs
- current errors
- current warnings
- current failures

must use route "none".

COMBINED QUESTIONS:

If one part requires documentation and another runtime information,
select "docs".

If one part requires code and another runtime information,
select "code".

If documentation and code are both required,
select "both".

EXAMPLES:

"Where is CALC-017 configured?"
-> code

"Where is CALCULATION_TIMEOUT_SECONDS defined?"
-> code

"Which function raises CalculationTimeoutError?"
-> code

"Which file handles calculation timeouts?"
-> code

"What does CALC-017 mean?"
-> docs

"How should an operator respond to CALC-017?"
-> docs

"What does CALC-017 mean and where is it configured?"
-> both

"Is calculation-service healthy right now?"
-> none

"What does CALC-017 mean and is calculation-service healthy right now?"
-> docs

CODE CHANGE ROUTING RULES:

Route to "code_change" when the user's intent is to CHANGE
the repository rather than merely inspect or explain it.

Examples:

"Change CALCULATION_TIMEOUT_SECONDS from 15 to 30 seconds."
-> code_change

"Fix the timeout handling in processor.py."
-> code_change

"Refactor calculate() to reduce duplication."
-> code_change

"Add validation for calculation_type."
-> code_change

"Where is CALCULATION_TIMEOUT_SECONDS defined?"
-> code

"How does timeout handling work?"
-> code

Return exactly one of:

docs
code
both
none
code_change
"""