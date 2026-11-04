from langchain_core.tools import tool


@tool
def get_service_logs(service_name: str) -> dict:
    """
    Get recent logs for a service.

    Use this tool when the user asks about recent errors,
    warnings, failures, or log messages from a service.
    """
    return {
        "service": service_name,
        "logs": [
            {
                "timestamp": "2026-10-27T09:41:12",
                "level": "ERROR",
                "error_code": "CALC-017",
                "message": "Calculation exceeded processing timeout."
            },
            {
                "timestamp": "2026-10-27T09:42:03",
                "level": "ERROR",
                "error_code": "CALC-017",
                "message": "Calculation exceeded processing timeout."
            },
            {
                "timestamp": "2026-10-27T09:43:20",
                "level": "WARNING",
                "error_code": None,
                "message": "Database connection pool usage above 90%."
            },
            {
                "timestamp": "2026-10-27T09:44:11",
                "level": "INFO",
                "error_code": None,
                "message": "Calculation request received."
            }
        ]
    }