from langchain.messages import ToolMessage
from tools.extractJSON import extract_info_meter_sheet
from tools.extractJSON import extract_info_electronic_sales_sheet
from tools.writefuelmeter import write_fuel_meter_sheet
from tools.write_electronic_sales import write_electronic_sales_sheet
# from tools.write_expenses import write_expenses_to_excel        # add as you build them
# from tools.write_momo import write_momo_to_excel
# from tools.write_balancing import write_balancing_to_excel
# from tools.write_p_and_l import write_p_and_l_to_excel

# Map tool name → sheet name for tracking
TOOL_TO_SHEET = {
    "extract_info_meter_sheet":        None,          # extraction step, not a sheet
    "extract_info_electronic_sales_sheet": None,          # extraction step, not a sheet
    "write_fuel_meter_sheet": "METER",
    # "write_expenses_to_excel":  "EXPENSES",    # uncomment as you build
    "write_electronic_sales_sheet":      "MOMO,AIRTEL,CARDS",
    # "write_balancing_to_excel": "BALANCING",
    # "write_p_and_l_to_excel":   "P_AND_L",
}

def tool_node(state: dict):
    """Performs the tool call and tracks which sheets have been processed."""

    tools = [
        extract_info_meter_sheet,
        extract_info_electronic_sales_sheet,
        write_fuel_meter_sheet,
        write_electronic_sales_sheet,

        # write_expenses_to_excel,     # uncomment as you build
        # write_momo_to_excel,
        # write_balancing_to_excel,
        # write_p_and_l_to_excel,
    ]
    tools_by_name = {tool.name: tool for tool in tools}

    result = []
    processed_sheets = list(state.get("processed_sheets", []))

    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])

        result.append(ToolMessage(
            content=str(observation),
            tool_call_id=tool_call["id"]
        ))

        # Mark sheet as done if this tool corresponds to a sheet
        sheet = TOOL_TO_SHEET.get(tool_call["name"])
        if sheet and sheet not in processed_sheets:
            processed_sheets.append(sheet)

    return {
        "messages": result,
        "processed_sheets": processed_sheets
    }