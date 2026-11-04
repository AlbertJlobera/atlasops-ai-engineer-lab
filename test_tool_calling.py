from app.tools.service_health import get_service_health
from app.models import llm


llm_with_tools = llm.bind_tools([
    get_service_health
])

response = llm_with_tools.invoke(
    "How is calculation-service doing right now?"
)

print(response.tool_calls)