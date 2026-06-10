from langchain.messages import SystemMessage
from tools.initialise_model import initialize_llama_model_with_tools
from states.state import MessagesState
from tools.writefuelmeter import write_fuel_meter_sheet
#add more sheet names to system message and remaining variable definition as you go on building them.
system_message = """
You are a bookkeeping assistant for petrol station businesses.

You will receive a single report message that contains data for multiple sheets.
You must process the sheets ONE AT A TIME in this strict order:
1. METER — pump openings, closings, RTT
2. MOMO,AIRTEL,CARDS — mobile money transactions, card payments




RULES:
- Check the state to see which sheets have already been processed
- Always call the tool for the NEXT unprocessed sheet
- Extract ONLY the data relevant to that sheet from the message
- Do not process a sheet that is already marked as done
- When all sheets are done, stop
"""

def llm_call(state: MessagesState) -> MessagesState:
    """LLM decides which sheet tool to call next based on what has been processed."""
    model_with_tools = initialize_llama_model_with_tools()[0]

    # Build a status summary so the LLM knows what's been done
    processed = state.get("processed_sheets", [])
    remaining = [s for s in ["METER","MOMO,AIRTEL,CARDS"] 
                 if s not in processed]

    status_message = SystemMessage(content=f"""
Sheets already processed: {processed if processed else "None"}
Sheets still to process: {remaining}
Next sheet to process: {remaining[0] if remaining else "ALL DONE — do not call any tool"}
""")

    return {
        "messages": [
            model_with_tools.invoke(
                [SystemMessage(content=system_message), status_message]
                + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


