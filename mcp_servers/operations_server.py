from mcp.server import MCPServer
from typing import Any
import os


mcp = MCPServer("AtlasOps Operations")


# @mcp.tool()
# def get_service_health(service_name: str) -> dict[str, Any]:
#     """
#     Get the current operational health of a service.
#     """
#     return {
#         "service": service_name,
#         "status": "degraded",
#         "cpu_percent": 91,
#         "memory_percent": 72,
#         "db_pool_usage_percent": 94,
#         "error_rate_percent": 8.2,
#     }

@mcp.tool()
def get_service_health(service_name: str) -> dict[str, Any]:

    simulate_failure = (
        os.getenv("SIMULATE_HEALTH_FAILURE", "false").lower()
        == "true"
    )

    if simulate_failure:
        raise RuntimeError(
            "Health backend is temporarily unavailable."
        )

    return {
        "service": service_name,
        "status": "degraded",
        "cpu_percent": 91,
        "memory_percent": 72,
        "db_pool_usage_percent": 94,
        "error_rate_percent": 8.2,
    }

@mcp.tool()
def get_service_logs(service_name: str) -> dict[str, Any]:
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

@mcp.tool()
def restart_service(service_name: str) -> dict[str, Any]:
    """
    Restart a service.

    Use this tool when the user explicitly requests
    restarting a service.
    """
    return {
        "service": service_name,
        "action": "restart",
        "status": "restarted"
    }


if __name__ == "__main__":
    mcp.run()