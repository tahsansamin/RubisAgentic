import os
from typing import Any, Dict, Tuple

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_groq import ChatGroq

from .extractJSON import extract_info_meter_sheet, extract_info_electronic_sales_sheet
from .writefuelmeter import write_fuel_meter_sheet
from .write_electronic_sales import write_electronic_sales_sheet

load_dotenv()


def initialize_llama_model_with_tools(
    model: str = "qwen/qwen3-32b",
    model_provider: str = "groq",
    temperature: float = 0,
    tool_choice: str | bool = "auto",
    api_key: str | None = None,
    **kwargs: Any,
) -> Tuple[Any, Dict[str, Any]]:
    """Create a Llama chat model and bind the extractJSON tool set to it."""

    api_key = api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY in environment")


    chat_model = init_chat_model(
        model=model,
        model_provider=model_provider,
        api_key=api_key,
        temperature=temperature,
        **kwargs,
    )

    tools = [extract_info_meter_sheet, extract_info_electronic_sales_sheet, write_fuel_meter_sheet, write_electronic_sales_sheet]
    model_with_tools = chat_model.bind_tools(
        tools,
        tool_choice=tool_choice,
    )

    tools_by_name = {tool.name: tool for tool in tools}
    return model_with_tools, tools_by_name
