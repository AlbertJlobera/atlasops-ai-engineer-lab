from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from app.tools.service_health import get_service_health
from app.models import llm


llm_with_tools = llm.bind_tools([
    get_service_health
])


def agent_node(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }


graph = StateGraph(MessagesState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode([
    get_service_health
]))

graph.add_edge(START, "agent")

graph.add_conditional_edges(
    "agent",
    tools_condition
)

graph.add_edge("tools", "agent")

compiled = graph.compile()


result = compiled.invoke({
    "messages": [
        {
            "role": "user",
            "content": "How is calculation-service doing right now?"
        }
    ]
})

print(result["messages"])