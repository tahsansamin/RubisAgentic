from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator
from typing import Annotated, List


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
    processed_sheets: List[str]