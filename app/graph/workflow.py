

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    answerability_node,
    generate_node,
    no_answer_node,
    retrieve_node
)
from app.graph.state import RAGState
from app.graph.routers import route_after_answerability

graph = StateGraph(RAGState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("answerability", answerability_node)
graph.add_node("generate", generate_node)
graph.add_node("no_answer", no_answer_node)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "answerability")

graph.add_conditional_edges(
    "answerability",
    route_after_answerability,
    {
        "generate": "generate",
        "no_answer": "no_answer",
    }
)

graph.add_edge("generate", END)
graph.add_edge("no_answer", END)

compiled = graph.compile()

