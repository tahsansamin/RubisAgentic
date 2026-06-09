from langchain.messages import SystemMessage

from tools.initialise_model import initialize_gemini_model_with_tools
from states.state import MessagesState

system_message = """
You are a helpful assistant who helps in the book keeping for petrol station businesses. You must extract information from the user's messages. Only extract relevant numerical information in JSON.
You MUST respond with ONLY a valid JSON object.
Do NOT include any explanation, markdown, code fences, or prose.
Your entire response must be parseable by json.loads().
"""
def llm_call(state: MessagesState) -> MessagesState:
    """LLM decides whether to call a tool or not"""
    model_with_tools = initialize_gemini_model_with_tools()[0]

    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content=system_message
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }