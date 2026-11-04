import os
import anyio

from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.workflow import build_workflow

from evaluation.cases import EVALUATION_CASES

from evaluation.evaluators import (
    get_called_tools,
    has_tool_error,
    has_empty_results,
    has_retrieval_error,
    has_code_retrieval_error,
    has_retrieval_warning,
    has_docs_and_code_failure,
    answer_contains_warning,
    answer_mentions_both_retrieval_failures,
    has_llm_error,
)

from evaluation.semantic_evaluators import (
    evaluate_groundedness,
    evaluate_relevance,
    evaluate_correctness,
)


def accuracy(
    correct: int,
    total: int
):
    if total == 0:
        return None

    return correct / total * 100


async def main():

    server_path = Path(
        "mcp_servers/operations_server.py"
    )

    # =========================================================
    # GLOBAL METRICS
    # =========================================================

    metrics = {

        # Cases
        "cases_total": 0,
        "cases_passed": 0,

        # Source routing
        "source_route_total": 0,
        "source_route_correct": 0,

        # Tool selection
        "tool_total": 0,
        "tool_correct": 0,

        # Tool failure
        "tool_error_total": 0,
        "tool_error_correct": 0,

        # Empty retrieval
        "empty_results_total": 0,
        "empty_results_correct": 0,

        # Docs backend failure
        "retrieval_error_total": 0,
        "retrieval_error_correct": 0,

        # Code backend failure
        "code_retrieval_error_total": 0,
        "code_retrieval_error_correct": 0,

        # Partial retrieval degradation
        "retrieval_warning_total": 0,
        "retrieval_warning_correct": 0,

        # Warning propagated to final answer
        "warning_answer_total": 0,
        "warning_answer_correct": 0,

        # Both retrieval backends fail
        "both_failure_total": 0,
        "both_failure_correct": 0,

        # Both failures correctly communicated
        "both_failure_answer_total": 0,
        "both_failure_answer_correct": 0,

        # LLM failure
        "llm_error_total": 0,
        "llm_error_correct": 0,

        # Validation
        "validation_total": 0,
        "validation_correct": 0,

        # Authorization
        "authorization_total": 0,
        "authorization_correct": 0,

        # Policy
        "policy_total": 0,
        "policy_correct": 0,

        # Retrieval Hit@K
        "retrieval_total": 0,
        "retrieval_correct": 0,

        # Semantic evaluation
        "groundedness_total": 0,
        "groundedness_score_sum": 0.0,

        "relevance_total": 0,
        "relevance_score_sum": 0.0,

        "correctness_total": 0,
        "correctness_score_sum": 0.0,
    }

    # =========================================================
    # RUN CASES
    # =========================================================

    for i, case in enumerate(
        EVALUATION_CASES,
        start=1
    ):

        metrics["cases_total"] += 1

        # =====================================================
        # LOCAL FAILURE SIMULATION
        # =====================================================

        os.environ[
            "SIMULATE_EMPTY_DOCS"
        ] = (
            "true"
            if case.get(
                "simulate_empty_docs",
                False
            )
            else "false"
        )

        os.environ[
            "SIMULATE_DOCS_FAILURE"
        ] = (
            "true"
            if case.get(
                "simulate_docs_failure",
                False
            )
            else "false"
        )

        os.environ[
            "SIMULATE_CODE_FAILURE"
        ] = (
            "true"
            if case.get(
                "simulate_code_failure",
                False
            )
            else "false"
        )

        os.environ[
            "SIMULATE_LLM_FAILURE"
        ] = (
            "true"
            if case.get(
                "simulate_llm_failure",
                False
            )
            else "false"
        )

        # =====================================================
        # MCP ENVIRONMENT
        # =====================================================

        mcp_env = os.environ.copy()

        mcp_env[
            "SIMULATE_HEALTH_FAILURE"
        ] = (
            "true"
            if case.get(
                "simulate_health_failure",
                False
            )
            else "false"
        )

        # =====================================================
        # MCP TRANSPORT
        # =====================================================

        transport = PythonStdioTransport(
            str(server_path),
            env=mcp_env
        )

        client = Client(
            transport
        )

        # Cada test tiene memoria independiente
        checkpointer = InMemorySaver()

        # =====================================================
        # EXECUTE CASE
        # =====================================================

        async with MCPAdapter(
            client
        ) as adapter:

            mcp_tools = (
                await adapter.list_tools()
            )

            compiled = build_workflow(
                mcp_tools,
                checkpointer
            )

            config = {
                "configurable": {
                    "thread_id": (
                        f"evaluation-{i}"
                    )
                }
            }

            result = await compiled.ainvoke(
                {
                    "question": (
                        case["question"]
                    ),

                    "user_role": case.get(
                        "user_role",
                        "viewer"
                    ),
                },

                config=config
            )

        # =====================================================
        # CASE HEADER
        # =====================================================

        print(
            "\n================================"
        )

        print(
            case["name"]
        )

        print(
            "================================"
        )

        passed = True

        # =====================================================
        # SOURCE ROUTING
        # =====================================================

        if "expected_source_route" in case:

            actual = result.get(
                "source_route"
            )

            expected = case[
                "expected_source_route"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "source_route_total"
            ] += 1

            if ok:
                metrics[
                    "source_route_correct"
                ] += 1

            print(
                f"source_route: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

        # =====================================================
        # SINGLE TOOL SELECTION
        # =====================================================

        if "expected_tool" in case:

            called_tools = (
                get_called_tools(
                    result.get(
                        "messages",
                        []
                    )
                )
            )

            expected = case[
                "expected_tool"
            ]

            ok = (
                expected
                in called_tools
            )

            passed = (
                passed and ok
            )

            metrics[
                "tool_total"
            ] += 1

            if ok:
                metrics[
                    "tool_correct"
                ] += 1

            print(
                f"tool: "
                f"{called_tools} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

        # =====================================================
        # MULTIPLE TOOL SELECTION
        # =====================================================

        if "expected_tools" in case:

            called_tools = (
                get_called_tools(
                    result.get(
                        "messages",
                        []
                    )
                )
            )

            expected_tools = case[
                "expected_tools"
            ]

            ok = all(
                tool in called_tools
                for tool in expected_tools
            )

            passed = (
                passed and ok
            )

            metrics[
                "tool_total"
            ] += 1

            if ok:
                metrics[
                    "tool_correct"
                ] += 1

            print(
                f"tools: "
                f"{called_tools} | "
                f"expected={expected_tools} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

        # =====================================================
        # TOOL FAILURE
        # =====================================================

        if "expected_tool_error" in case:

            actual = (
                has_tool_error(
                    result.get(
                        "messages",
                        []
                    )
                )
            )

            expected = case[
                "expected_tool_error"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "tool_error_total"
            ] += 1

            if ok:
                metrics[
                    "tool_error_correct"
                ] += 1

            print(
                f"tool_error: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

        # =====================================================
        # EMPTY RETRIEVAL
        # =====================================================

        if "expected_empty_results" in case:

            actual = (
                has_empty_results(
                    result.get(
                        "results",
                        []
                    )
                )
            )

            expected = case[
                "expected_empty_results"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "empty_results_total"
            ] += 1

            if ok:
                metrics[
                    "empty_results_correct"
                ] += 1

            print(
                f"empty_results: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

            print(
                f"answer: "
                f"{result.get('answer', '')}"
            )

        # =====================================================
        # DOCS RETRIEVAL FAILURE
        # =====================================================

        if "expected_retrieval_error" in case:

            actual = (
                has_retrieval_error(
                    result
                )
            )

            expected = case[
                "expected_retrieval_error"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "retrieval_error_total"
            ] += 1

            if ok:
                metrics[
                    "retrieval_error_correct"
                ] += 1

            print(
                f"docs_retrieval_error: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

            print(
                f"answer: "
                f"{result.get('answer', '')}"
            )

        # =====================================================
        # CODE RETRIEVAL FAILURE
        # =====================================================

        if "expected_code_retrieval_error" in case:

            actual = (
                has_code_retrieval_error(
                    result
                )
            )

            expected = case[
                "expected_code_retrieval_error"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "code_retrieval_error_total"
            ] += 1

            if ok:
                metrics[
                    "code_retrieval_error_correct"
                ] += 1

            print(
                f"code_retrieval_error: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

            print(
                f"answer: "
                f"{result.get('answer', '')}"
            )

        # =====================================================
        # PARTIAL RETRIEVAL WARNING
        # =====================================================

        if "expected_retrieval_warning" in case:

            actual = (
                has_retrieval_warning(
                    result
                )
            )

            expected = case[
                "expected_retrieval_warning"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "retrieval_warning_total"
            ] += 1

            if ok:
                metrics[
                    "retrieval_warning_correct"
                ] += 1

            print(
                f"retrieval_warning: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

            print(
                f"warning: "
                f"{result.get('retrieval_warning', '')}"
            )

        # =====================================================
        # WARNING MUST APPEAR IN FINAL ANSWER
        # =====================================================

        if "expected_warning_in_answer" in case:

            actual = (
                answer_contains_warning(
                    result
                )
            )

            expected = case[
                "expected_warning_in_answer"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "warning_answer_total"
            ] += 1

            if ok:
                metrics[
                    "warning_answer_correct"
                ] += 1

            print(
                f"warning_in_answer: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

            print(
                f"answer: "
                f"{result.get('answer', '')}"
            )

        # =====================================================
        # BOTH DOCS + CODE FAILURE
        # =====================================================

        if "expected_docs_and_code_failure" in case:

            actual = (
                has_docs_and_code_failure(
                    result
                )
            )

            expected = case[
                "expected_docs_and_code_failure"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "both_failure_total"
            ] += 1

            if ok:
                metrics[
                    "both_failure_correct"
                ] += 1

            print(
                f"docs_and_code_failure: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

        # =====================================================
        # BOTH FAILURE MUST BE COMMUNICATED
        # =====================================================

        if "expected_both_failure_in_answer" in case:

            actual = (
                answer_mentions_both_retrieval_failures(
                    result
                )
            )

            expected = case[
                "expected_both_failure_in_answer"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "both_failure_answer_total"
            ] += 1

            if ok:
                metrics[
                    "both_failure_answer_correct"
                ] += 1

            print(
                f"both_failure_in_answer: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

            print(
                f"answer: "
                f"{result.get('answer', '')}"
            )

        # =====================================================
        # LLM FAILURE
        # =====================================================

        if "expected_llm_error" in case:

            actual = (
                has_llm_error(
                    result
                )
            )

            expected = case[
                "expected_llm_error"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "llm_error_total"
            ] += 1

            if ok:
                metrics[
                    "llm_error_correct"
                ] += 1

            print(
                f"llm_error: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

            print(
                f"answer: "
                f"{result.get('answer', '')}"
            )

        # =====================================================
        # VALIDATION
        # =====================================================

        if "expected_validation" in case:

            actual = result.get(
                "validation_decision"
            )

            expected = case[
                "expected_validation"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "validation_total"
            ] += 1

            if ok:
                metrics[
                    "validation_correct"
                ] += 1

            print(
                f"validation: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

        # =====================================================
        # AUTHORIZATION
        # =====================================================

        if "expected_authorization" in case:

            actual = result.get(
                "authorization_decision"
            )

            expected = case[
                "expected_authorization"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "authorization_total"
            ] += 1

            if ok:
                metrics[
                    "authorization_correct"
                ] += 1

            print(
                f"authorization: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

        # =====================================================
        # POLICY
        # =====================================================

        if "expected_policy" in case:

            actual = result.get(
                "policy_decision"
            )

            expected = case[
                "expected_policy"
            ]

            ok = (
                actual == expected
            )

            passed = (
                passed and ok
            )

            metrics[
                "policy_total"
            ] += 1

            if ok:
                metrics[
                    "policy_correct"
                ] += 1

            print(
                f"policy: "
                f"{actual} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

        # =====================================================
        # RETRIEVAL HIT@K
        # =====================================================

        if "expected_source" in case:

            sources = result.get(
                "sources",
                []
            )

            source_names = [
                source["source"]
                for source in sources
            ]

            expected = case[
                "expected_source"
            ]

            ok = (
                expected
                in source_names
            )

            passed = (
                passed and ok
            )

            metrics[
                "retrieval_total"
            ] += 1

            if ok:
                metrics[
                    "retrieval_correct"
                ] += 1

            print(
                f"retrieval: "
                f"{source_names} | "
                f"expected={expected} | "
                f"{'PASS' if ok else 'FAIL'}"
            )

        # =====================================================
        # GROUNDEDNESS
        # =====================================================

        if case.get(
            "evaluate_groundedness",
            False
        ):

            groundedness_result = (
                evaluate_groundedness(
                    question=(
                        case["question"]
                    ),

                    answer=result.get(
                        "answer",
                        ""
                    ),

                    results=result.get(
                        "results",
                        []
                    ),

                    messages=result.get(
                        "messages",
                        []
                    ),
                )
            )

            metrics[
                "groundedness_total"
            ] += 1

            metrics[
                "groundedness_score_sum"
            ] += (
                groundedness_result.score
            )

            print(
                f"groundedness: "
                f"{groundedness_result.score:.2f}"
            )

            print(
                f"groundedness reasoning: "
                f"{groundedness_result.reasoning}"
            )

        # =====================================================
        # RELEVANCE
        # =====================================================

        if case.get(
            "evaluate_relevance",
            False
        ):

            relevance_result = (
                evaluate_relevance(
                    question=(
                        case["question"]
                    ),

                    answer=result.get(
                        "answer",
                        ""
                    ),
                )
            )

            metrics[
                "relevance_total"
            ] += 1

            metrics[
                "relevance_score_sum"
            ] += (
                relevance_result.score
            )

            print(
                f"relevance: "
                f"{relevance_result.score:.2f}"
            )

            print(
                f"relevance reasoning: "
                f"{relevance_result.reasoning}"
            )

        # =====================================================
        # CORRECTNESS
        # =====================================================

        if case.get(
            "evaluate_correctness",
            False
        ):

            reference_answer = (
                case.get(
                    "reference_answer"
                )
            )

            if not reference_answer:
                raise ValueError(
                    f"Case '{case['name']}' "
                    "has evaluate_correctness=True "
                    "but no reference_answer."
                )

            correctness_result = (
                evaluate_correctness(
                    question=(
                        case["question"]
                    ),

                    answer=result.get(
                        "answer",
                        ""
                    ),

                    reference_answer=(
                        reference_answer
                    ),
                )
            )

            metrics[
                "correctness_total"
            ] += 1

            metrics[
                "correctness_score_sum"
            ] += (
                correctness_result.score
            )

            print(
                f"correctness: "
                f"{correctness_result.score:.2f}"
            )

            print(
                f"correctness reasoning: "
                f"{correctness_result.reasoning}"
            )

        # =====================================================
        # CASE RESULT
        # =====================================================

        if passed:
            metrics[
                "cases_passed"
            ] += 1

        print(
            "\nRESULT:",
            (
                "PASS"
                if passed
                else "FAIL"
            )
        )

    # =========================================================
    # CLEAN ENVIRONMENT
    # =========================================================

    os.environ.pop(
        "SIMULATE_EMPTY_DOCS",
        None
    )

    os.environ.pop(
        "SIMULATE_DOCS_FAILURE",
        None
    )

    os.environ.pop(
        "SIMULATE_CODE_FAILURE",
        None
    )

    os.environ.pop(
        "SIMULATE_LLM_FAILURE",
        None
    )

    # =========================================================
    # SUMMARY
    # =========================================================

    print(
        "\n\n================================"
    )

    print(
        "EVALUATION SUMMARY"
    )

    print(
        "================================"
    )

    cases_rate = accuracy(
        metrics[
            "cases_passed"
        ],
        metrics[
            "cases_total"
        ],
    )

    print(
        f"Cases passed: "
        f"{metrics['cases_passed']}/"
        f"{metrics['cases_total']}"
    )

    if cases_rate is not None:

        print(
            f"Overall pass rate: "
            f"{cases_rate:.1f}%"
        )

    print()

    # =========================================================
    # DETERMINISTIC METRICS
    # =========================================================

    metric_pairs = [

        (
            "Source routing accuracy",
            "source_route_correct",
            "source_route_total",
        ),

        (
            "Tool selection accuracy",
            "tool_correct",
            "tool_total",
        ),

        (
            "Tool error handling accuracy",
            "tool_error_correct",
            "tool_error_total",
        ),

        (
            "Empty retrieval handling",
            "empty_results_correct",
            "empty_results_total",
        ),

        (
            "Docs retrieval failure handling",
            "retrieval_error_correct",
            "retrieval_error_total",
        ),

        (
            "Code retrieval failure handling",
            "code_retrieval_error_correct",
            "code_retrieval_error_total",
        ),

        (
            "Partial retrieval degradation",
            "retrieval_warning_correct",
            "retrieval_warning_total",
        ),

        (
            "Retrieval warning communication",
            "warning_answer_correct",
            "warning_answer_total",
        ),

        (
            "Both retrieval backends failure",
            "both_failure_correct",
            "both_failure_total",
        ),

        (
            "Both retrieval failures communication",
            "both_failure_answer_correct",
            "both_failure_answer_total",
        ),

        (
            "LLM failure handling",
            "llm_error_correct",
            "llm_error_total",
        ),

        (
            "Validation accuracy",
            "validation_correct",
            "validation_total",
        ),

        (
            "Authorization accuracy",
            "authorization_correct",
            "authorization_total",
        ),

        (
            "Policy accuracy",
            "policy_correct",
            "policy_total",
        ),

        (
            "Retrieval Hit@3",
            "retrieval_correct",
            "retrieval_total",
        ),
    ]

    for (
        label,
        correct_key,
        total_key,
    ) in metric_pairs:

        value = accuracy(
            metrics[
                correct_key
            ],
            metrics[
                total_key
            ],
        )

        if value is not None:

            correct = metrics[
                correct_key
            ]

            total = metrics[
                total_key
            ]

            print(
                f"{label}: "
                f"{value:.1f}% "
                f"({correct}/{total})"
            )

    # =========================================================
    # SEMANTIC METRICS
    # =========================================================

    if (
        metrics[
            "groundedness_total"
        ]
        > 0
    ):

        average_groundedness = (
            metrics[
                "groundedness_score_sum"
            ]
            / metrics[
                "groundedness_total"
            ]
        )

        print()

        print(
            f"Average groundedness: "
            f"{average_groundedness:.2f} "
            f"({metrics['groundedness_total']} cases)"
        )

    if (
        metrics[
            "relevance_total"
        ]
        > 0
    ):

        average_relevance = (
            metrics[
                "relevance_score_sum"
            ]
            / metrics[
                "relevance_total"
            ]
        )

        print(
            f"Average relevance: "
            f"{average_relevance:.2f} "
            f"({metrics['relevance_total']} cases)"
        )

    if (
        metrics[
            "correctness_total"
        ]
        > 0
    ):

        average_correctness = (
            metrics[
                "correctness_score_sum"
            ]
            / metrics[
                "correctness_total"
            ]
        )

        print(
            f"Average correctness: "
            f"{average_correctness:.2f} "
            f"({metrics['correctness_total']} cases)"
        )


if __name__ == "__main__":
    anyio.run(main)