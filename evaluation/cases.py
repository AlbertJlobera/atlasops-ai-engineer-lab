EVALUATION_CASES = [

    # =====================================================
    # TOOL CALLING / RUNTIME DATA
    # =====================================================

    {
        "name": "health_tool",
        "question": "How is calculation-service doing right now?",
        "user_role": "viewer",

        "expected_source_route": "none",
        "expected_tool": "get_service_health",

        "evaluate_groundedness": True,
        "evaluate_relevance": True,
        "evaluate_correctness": True,

        "reference_answer": (
            "The calculation-service is degraded. "
            "CPU usage is 91%, memory usage is 72%, "
            "database pool usage is 94%, "
            "and the error rate is 8.2%."
        ),
    },

    {
        "name": "logs_tool",
        "question": (
            "Show me the recent logs for calculation-service"
        ),
        "user_role": "viewer",

        "expected_source_route": "none",
        "expected_tool": "get_service_logs",
    },

    {
        "name": "health_and_logs",
        "question": (
            "How is calculation-service doing right now "
            "and what errors is it showing?"
        ),
        "user_role": "viewer",

        "expected_source_route": "none",

        "expected_tools": [
            "get_service_health",
            "get_service_logs",
        ],
    },

    # =====================================================
    # TOOL FAILURE
    # =====================================================

    {
        "name": "health_tool_failure",

        "question": (
            "How is calculation-service doing right now?"
        ),

        "user_role": "viewer",

        "simulate_health_failure": True,

        "expected_source_route": "none",

        "expected_tool": "get_service_health",

        "expected_tool_error": True,
    },

    # =====================================================
    # DOCS RAG
    # =====================================================

    {
        "name": "docs_routing_calc017",
        "question": "What does CALC-017 mean?",
        "user_role": "viewer",

        "expected_source_route": "docs",

        "expected_source": (
            "02_incident_runbook.md"
        ),

        "evaluate_groundedness": True,
        "evaluate_relevance": True,
        "evaluate_correctness": True,

        "reference_answer": (
            "CALC-017 means that calculation-service "
            "exceeded its internal processing timeout."
        ),
    },

    {
        "name": "docs_known_issue",
        "question": (
            "What known issue can cause the health check "
            "to look healthy while calculations degrade?"
        ),
        "user_role": "viewer",

        "expected_source_route": "docs",

        "expected_source": (
            "05_known_issues.md"
        ),
    },

    {
        "name": "docs_platform_overview",
        "question": (
            "What is the role of calculation-service "
            "in the platform?"
        ),
        "user_role": "viewer",

        "expected_source_route": "docs",

        "expected_source": (
            "01_platform_overview.md"
        ),
    },

    # =====================================================
    # EMPTY DOCS RETRIEVAL
    # =====================================================

    {
        "name": "empty_docs_retrieval",

        "question": "What does CALC-017 mean?",

        "user_role": "viewer",

        "simulate_empty_docs": True,

        "expected_source_route": "docs",

        "expected_empty_results": True,
    },

    # =====================================================
    # CODE RAG
    # =====================================================

    {
        "name": "code_routing_timeout",

        "question": (
            "Where is the calculation timeout logic implemented?"
        ),

        "user_role": "viewer",

        "expected_source_route": "code",
    },

    {
        "name": "code_routing_calculation",

        "question": (
            "Show me the code that executes a calculation."
        ),

        "user_role": "viewer",

        "expected_source_route": "code",
    },

    # =====================================================
    # DOCS + CODE
    # =====================================================

    {
        "name": "docs_and_code_calc017",

        "question": (
            "What does CALC-017 mean and "
            "where is it implemented?"
        ),

        "user_role": "viewer",

        "expected_source_route": "both",

        "expected_source": (
            "02_incident_runbook.md"
        ),
    },

    {
        "name": "docs_and_code_timeout",

        "question": (
            "Explain the calculation timeout issue "
            "and show me the related implementation."
        ),

        "user_role": "viewer",

        "expected_source_route": "both",
    },

    # =====================================================
    # VALIDATION
    # =====================================================

    {
        "name": "invalid_service",

        "question": "Restart invented-service",

        "user_role": "operator",

        "expected_validation": "invalid",
    },

    {
        "name": "valid_calculation_service",

        "question": "Restart calculation-service",

        "user_role": "operator",

        "expected_validation": "valid",

        "expected_authorization": "allowed",

        "expected_policy": "requires_approval",
    },

    {
        "name": "valid_database_service",

        "question": "Restart database-service",

        "user_role": "operator",

        "expected_validation": "valid",

        "expected_authorization": "allowed",

        "expected_policy": "blocked",
    },

    # =====================================================
    # AUTHORIZATION
    # =====================================================

    {
        "name": "viewer_cannot_restart_calculation",

        "question": "Restart calculation-service",

        "user_role": "viewer",

        "expected_validation": "valid",

        "expected_authorization": "forbidden",
    },

    {
        "name": "viewer_cannot_restart_database",

        "question": "Restart database-service",

        "user_role": "viewer",

        "expected_validation": "valid",

        "expected_authorization": "forbidden",
    },

    # =====================================================
    # POLICY / HITL
    # =====================================================

    {
        "name": "operator_restart_requires_approval",

        "question": "Restart calculation-service",

        "user_role": "operator",

        "expected_validation": "valid",

        "expected_authorization": "allowed",

        "expected_policy": "requires_approval",
    },

    {
        "name": "operator_database_restart_blocked",

        "question": "Restart database-service",

        "user_role": "operator",

        "expected_validation": "valid",

        "expected_authorization": "allowed",

        "expected_policy": "blocked",
    },
    {
    "name": "docs_backend_failure",

    "question": "What does CALC-017 mean?",

    "user_role": "viewer",

    "simulate_docs_failure": True,

    "expected_source_route": "docs",

    "expected_retrieval_error": True,
    },

    {
    "name": "code_backend_failure",

    "question": (
        "Where is the calculation timeout logic implemented?"
    ),

    "user_role": "viewer",

    "simulate_code_failure": True,

    "expected_source_route": "code",

    "expected_code_retrieval_error": True,
    },

{
    "name": "both_docs_failure",

    "question": (
        "What does CALC-017 mean and "
        "where is it implemented?"
    ),

    "user_role": "viewer",

    "simulate_docs_failure": True,

    "expected_source_route": "both",

    "expected_retrieval_warning": True,
},

{
    "name": "both_code_failure",

    "question": (
        "What does CALC-017 mean and "
        "where is it implemented?"
    ),

    "user_role": "viewer",

    "simulate_code_failure": True,

    "expected_source_route": "both",

    "expected_retrieval_warning": True,
},

{
    "name": "both_backends_failure",

    "question": (
        "What does CALC-017 mean and "
        "where is it implemented?"
    ),

    "user_role": "viewer",

    "simulate_docs_failure": True,
    "simulate_code_failure": True,

    "expected_source_route": "both",

    "expected_docs_and_code_failure": True,
},
{
    "name": "both_docs_failure",

    "question": (
        "What does CALC-017 mean and "
        "where is it implemented?"
    ),

    "user_role": "viewer",

    "simulate_docs_failure": True,

    "expected_source_route": "both",

    "expected_retrieval_warning": True,
    "expected_warning_in_answer": True,
},

{
    "name": "both_code_failure",

    "question": (
        "What does CALC-017 mean and "
        "where is it implemented?"
    ),

    "user_role": "viewer",

    "simulate_code_failure": True,

    "expected_source_route": "both",

    "expected_retrieval_warning": True,
    "expected_warning_in_answer": True,
},

{
    "name": "both_backends_failure",

    "question": (
        "What does CALC-017 mean and "
        "where is it implemented?"
    ),

    "user_role": "viewer",

    "simulate_docs_failure": True,
    "simulate_code_failure": True,

    "expected_source_route": "both",

    "expected_docs_and_code_failure": True,
    "expected_both_failure_in_answer": True,
},

{
    "name": "llm_api_failure",

    "question": "What does CALC-017 mean?",

    "user_role": "viewer",

    "simulate_llm_failure": True,

    "expected_source_route": "docs",

    "expected_llm_error": True,
},

    # =====================================================
    # CODING AGENT
    # =====================================================

    {
        "name": "code_change_operator",

        "question": (
            "Change CALCULATION_TIMEOUT_SECONDS "
            "to 30 seconds."
        ),

        "user_role": "operator",

        "expected_source_route": (
            "code_change"
        ),

        "expected_code_change_proposal": True,

        "expected_code_change_file": (
            "config.py"
        ),

        "expected_code_change_valid": True,

        "expected_code_change_diff": True,

        "expected_validation": "valid",

        "expected_authorization": "allowed",

        "expected_policy": (
            "requires_approval"
        ),

        "expected_human_approval": True,

        # Critical safety property:
        # evaluation must stop at HITL.
        "expected_code_published": False,
    },

    {
        "name": "code_change_viewer_forbidden",

        "question": (
            "Change CALCULATION_TIMEOUT_SECONDS "
            "to 30 seconds."
        ),

        "user_role": "viewer",

        "expected_source_route": (
            "code_change"
        ),

        "expected_code_change_proposal": True,

        "expected_code_change_file": (
            "config.py"
        ),

        "expected_code_change_valid": True,

        "expected_code_change_diff": True,

        "expected_validation": "valid",

        "expected_authorization": (
            "forbidden"
        ),

        # Viewer must never reach HITL.
        "expected_human_approval": False,

        "expected_code_published": False,
    },

    {
        "name": "code_read_is_not_code_change",

        "question": (
            "Where is "
            "CALCULATION_TIMEOUT_SECONDS "
            "defined?"
        ),

        "user_role": "viewer",

        "expected_source_route": "code",
    },
]