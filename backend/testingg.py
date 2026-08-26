import json

from dotenv import load_dotenv
from langchain.messages import HumanMessage

from nodes.llmcall import llm_call
from nodes.toolnode import tool_node

load_dotenv()


test_report = """26th August 2026
Pump 1
PMS opening: 1696506.241
PMS closing: 1696746.474
AGO opening: 852073.232
AGO closing: 852545.489

Electronic sales:
Airtel money: 1055808
Visa card: 585000
Rubis card: 604200
"""


if __name__ == "__main__":
	state = {
		"messages": [HumanMessage(content=test_report)],
		"llm_calls": 0,
	}

	print("1. Calling the LLM...")
	llm_result = llm_call(state)
	ai_message = llm_result["messages"][0]
	print(f"LLM tool calls: {[call['name'] for call in ai_message.tool_calls]}")

	if not ai_message.tool_calls:
		print("The LLM returned no tool call.")
	else:
		print("2. Executing the LLM tool call(s)...")
		tool_result = tool_node({
			"messages": state["messages"] + llm_result["messages"],
		})

		print("Tool results:")
		for message in tool_result["messages"]:
			print(message.content)
