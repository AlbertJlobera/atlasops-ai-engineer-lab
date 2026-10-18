ANSWERABILITY_PROMPT = """
You are evaluating whether the retrieved context contains enough evidence
to answer the user's question.

Question:
{question}

Retrieved context:
{context}

Rules:
- Return ANSWERABLE if the context contains enough explicit evidence to answer the question.
- Explicit operational rules, conditions, prohibitions, and decision criteria count as sufficient evidence.
- The answer does not need to appear verbatim in the context.
- Simple logical application of an explicit rule is allowed.
- Return NOT_ANSWERABLE only if key information required to answer is missing.
- Do not answer the question itself.

Return only one label:
ANSWERABLE
or
NOT_ANSWERABLE
"""

RAG_ANSWER_PROMPT = """
You are an internal AtlasOps technical assistant.

Answer the user's question using ONLY the retrieved context below.

Rules:
- Do not use outside knowledge.
- Do not invent missing information.
- If the context does not support a claim, do not include it.
- Apply explicit operational rules and conditions when needed.
- Be concise and practical.
- Cite the supporting chunk using [Chunk 1], [Chunk 2], etc.

Question:
{question}

Retrieved context:
{context}

Answer:
"""