import os
from typing import Any, Dict, Tuple

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from .extractJSON import extract_fuel_report

load_dotenv()


def initialize_gemini_model_with_tools(
    model: str = "gemini-2.5-flash",
    model_provider: str = "google_genai",
    temperature: float = 0,
    tool_choice: str | bool = "auto",
    api_key: str | None = None,
    **kwargs: Any,
) -> Tuple[Any, Dict[str, Any]]:
    """Create a Gemini chat model and bind the extractJSON tool set to it."""

    api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY in environment")

    kwargs.setdefault("api_key", api_key)

    chat_model = init_chat_model(
        model,
        model_provider=model_provider,
        temperature=temperature,
        **kwargs,
    )

    tools = [extract_fuel_report]
    model_with_tools = chat_model.bind_tools(
        tools,
        tool_choice=tool_choice,
    )

    tools_by_name = {tool.name: tool for tool in tools}
    return model_with_tools, tools_by_name
