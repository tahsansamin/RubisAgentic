from langchain.messages import ToolMessage
from tools.extractJSON import extract_info_meter_sheet
from tools.extractJSON import extract_info_electronic_sales_sheet

def tool_node(state: dict):
    """Execute extraction tool calls and return their JSON results."""

    tools = [
        extract_info_meter_sheet,
        extract_info_electronic_sales_sheet,
    ]
    tools_by_name = {tool.name: tool for tool in tools}

    result = []

    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])

        result.append(ToolMessage(
            content=str(observation),
            tool_call_id=tool_call["id"]
        ))

    return {"messages": result}