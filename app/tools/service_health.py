from langchain_core.tools import tool

@tool
def get_service_health(service_name: str) -> dict:
    """
    Get the current operational health of a service.

    Use this tool when the user asks about the current status,
    CPU usage, memory usage, database pool usage, or error rate
    of a service.
    """
    return {
        "service": service_name,
        "status": "degraded",
        "cpu_percent": 91,
        "memory_percent": 72,
        "db_pool_usage_percent": 94,
        "error_rate_percent": 8.2,
    }