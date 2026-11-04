from pydantic import BaseModel, Field
from langchain_core.messages import ToolMessage

from app.models import llm
from app.rag.context import build_context


class GroundednessResult(BaseModel):
    score: float = Field(
        ge=0,
        le=1,
        description="0 means unsupported, 1 means fully supported."
    )

    reasoning: str


def build_tool_evidence(messages) -> str:
    tool_messages = [
        message
        for message in messages
        if isinstance(message, ToolMessage)
    ]

    if not tool_messages:
        return "No tool evidence available."

    return "\n\n".join(
        f"Tool: {message.name}\n"
        f"Result: {message.content}"
        for message in tool_messages
    )


def evaluate_groundedness(
    question: str,
    answer: str,
    results: list,
    messages: list
) -> GroundednessResult:

    rag_evidence = build_context(results)

    tool_evidence = build_tool_evidence(
        messages
    )

    prompt = f"""
You are evaluating the groundedness of an AI assistant answer.

Groundedness means that factual claims in the answer must be
supported by the provided evidence.

Evaluate ONLY against the supplied evidence.
Do not use your own external knowledge.

Question:
{question}

Answer:
{answer}

RAG evidence:
{rag_evidence if rag_evidence else "No RAG evidence available."}

Tool evidence:
{tool_evidence}

Scoring:
- 1.0 = all important factual claims are supported
- 0.75 = mostly supported, with minor unsupported details
- 0.5 = partially supported
- 0.25 = mostly unsupported
- 0.0 = unsupported or contradictory

Return a score and a short explanation.
"""

    judge = llm.with_structured_output(
        GroundednessResult
    )

    return judge.invoke(prompt)

class RelevanceResult(BaseModel):
    score: float = Field(
        ge=0,
        le=1,
        description=(
            "0 means the answer is irrelevant, "
            "1 means it directly and completely answers the question."
        )
    )

    reasoning: str

def evaluate_relevance(
    question: str,
    answer: str
) -> RelevanceResult:

    prompt = f"""
You are evaluating the relevance of an AI assistant answer.

Relevance means that the answer directly addresses the user's
question and includes the information needed to satisfy the request.

Do NOT evaluate whether the answer is factually correct.
Do NOT evaluate whether claims are grounded in evidence.
Only evaluate whether the answer addresses the user's request.

Question:
{question}

Answer:
{answer}

Scoring:

- 1.0 = directly and completely answers the question
- 0.75 = mostly relevant but misses a minor part or contains some unnecessary information
- 0.5 = partially answers the question
- 0.25 = only slightly related to the question
- 0.0 = irrelevant or does not answer the question

Return a score and a short explanation.
"""

    judge = llm.with_structured_output(
        RelevanceResult
    )

    return judge.invoke(prompt)

class CorrectnessResult(BaseModel):
    score: float = Field(
        ge=0,
        le=1,
        description=(
            "0 means factually incorrect compared with the "
            "reference answer, 1 means fully correct."
        )
    )

    reasoning: str

def evaluate_correctness(
    question: str,
    answer: str,
    reference_answer: str
) -> CorrectnessResult:

    prompt = f"""
You are evaluating the correctness of an AI assistant answer.

Compare the assistant answer with the reference answer.

Evaluate whether the important factual information required
to answer the question is correct.

Do not require identical wording.
Equivalent wording should be considered correct.

Do not penalize harmless additional information unless it
contradicts the reference answer or introduces incorrect claims.

Question:
{question}

Reference answer:
{reference_answer}

Assistant answer:
{answer}

Scoring:

- 1.0 = fully correct
- 0.75 = mostly correct with a minor error or omission
- 0.5 = partially correct
- 0.25 = mostly incorrect
- 0.0 = incorrect or contradictory

Return a score and a short explanation.
"""

    judge = llm.with_structured_output(
        CorrectnessResult
    )

    return judge.invoke(prompt)
# if __name__ == "__main__":

#     fake_question = (
#         "How is calculation-service doing right now?"
#     )

#     fake_answer = (
#         "The calculation-service is degraded. "
#         "CPU usage is 91%. "
#         "The degradation was caused by a network outage."
#     )

#     fake_results = []

#     from langchain_core.messages import ToolMessage

#     fake_messages = [
#         ToolMessage(
#             content=(
#                 "{"
#                 "'service': 'calculation-service', "
#                 "'status': 'degraded', "
#                 "'cpu_percent': 91, "
#                 "'memory_percent': 72, "
#                 "'db_pool_usage_percent': 94, "
#                 "'error_rate_percent': 8.2"
#                 "}"
#             ),
#             tool_call_id="test-call",
#             name="get_service_health"
#         )
#     ]

#     result = evaluate_groundedness(
#         question=fake_question,
#         answer=fake_answer,
#         results=fake_results,
#         messages=fake_messages
#     )

#     print("Score:", result.score)
#     print("Reasoning:", result.reasoning)