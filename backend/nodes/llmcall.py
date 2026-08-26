from langchain.messages import SystemMessage
from tools.initialise_model import initialize_llama_model_with_tools
from states.state import MessagesState
system_message = """
You are a data extraction assistant for petrol station reports.

Extract all relevant information from the report using the available extraction tools.
Do not write to files, spreadsheets, or external systems.
When extraction is complete, return ONLY a valid JSON array containing dictionaries.
For one report, return one dictionary inside the array: [{"date": "YYYY-MM-DD", ...}]
Do not include markdown fences, explanations, or extra text.
"""

def llm_call(state: MessagesState) -> MessagesState:
    """Ask the LLM to extract report information as JSON."""
    model_with_tools = initialize_llama_model_with_tools()[0]


    return {
        "messages": [
            model_with_tools.invoke(
                [SystemMessage(content=system_message)]
                + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

