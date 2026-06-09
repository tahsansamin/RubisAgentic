from states.state import MessagesState
from nodes.llmcall import llm_call
from nodes.shouldcontinue import should_continue
from nodes.toolnode import tool_node
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display


def build_agent():
    """Build and compile the agent graph."""
    agent_builder = StateGraph(MessagesState)

    # Add nodes
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)

    # Add edges to connect nodes
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges(
        "llm_call",
        should_continue,
        ["tool_node", END]
    )
    agent_builder.add_edge("tool_node", "llm_call")

    # Compile the agent
    return agent_builder.compile()


def display_agent(agent):
    """Display the agent graph visualization."""
    graph = agent.get_graph(xray=True).draw_mermaid_png()
    display(Image(graph))
    # with open("graph.png", "wb") as f:
    #     f.write(graph)

