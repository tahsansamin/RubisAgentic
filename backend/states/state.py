from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator
from typing import Annotated


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int