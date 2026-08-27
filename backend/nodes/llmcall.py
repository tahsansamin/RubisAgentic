from langchain.messages import SystemMessage
from tools.initialise_model import initialize_llama_model_with_tools
from states.state import MessagesState
system_message = """
You are a data extraction assistant for petrol station reports.

Extract all relevant information from the report using the available extraction tools.
Do not write to files, spreadsheets, or external systems.

When extraction is complete, return ONLY a valid JSON array containing exactly two
dictionaries, in this order:

1. Fuel meter data:
{
  "date": "YYYY-MM-DD",
  "pumps": {
    "<PUMP NAME>": {
      "opening": <number>,
      "closing": <number>
    }
  },
  "rtt": {
    "PMS": <number or null>,
    "AGO": <number or null>
  }
}

2. Electronic sales data:
{
  "date": "YYYY-MM-DD",
  "electronic_sales": {
    "MOMOPAY": <number or null>,
    "AIRTEL": <number or null>,
    "VISA CARD": <number or null>,
    "RUBIS CARD": <number or null>,
    "RUBIS APP": <number or null>
  }
}

Rules:
- Always include both dictionaries, even if one has all null values.
- Always include every listed key in "rtt" and "electronic_sales" — use null if not present in the report, never omit a key.
- "date" must be identical in both dictionaries.
- Do not include markdown fences (no ```), explanations, or any text outside the JSON array.
- Return exactly two elements in the array — no more, no fewer.
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

