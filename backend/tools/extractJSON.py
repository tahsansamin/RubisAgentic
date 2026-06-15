from typing import TypedDict, Optional, List, Dict, Any
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI as Gemini
from langchain_groq import ChatGroq

from dotenv import load_dotenv
import os
import json
import re
load_dotenv()  # Load environment variables from .env file



class FuelReportInput(TypedDict):
    report: str

def clean_json(text: str) -> str:
    """Extract JSON from text that may contain extra content."""
    text = text.strip()
    if not text:
        return text

    # Remove markdown code fences if present.
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # If the whole response is valid JSON already, return it.
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Find balanced JSON objects while ignoring braces inside strings.
    candidates: list[str] = []
    depth = 0
    in_string = False
    escape = False
    start_idx: int | None = None

    for idx, ch in enumerate(text):
        if ch == '"' and not escape:
            in_string = not in_string
        if ch == '\\' and not escape:
            escape = True
        else:
            escape = False

        if in_string:
            continue

        if ch == '{':
            if depth == 0:
                start_idx = idx
            depth += 1
        elif ch == '}' and depth > 0:
            depth -= 1
            if depth == 0 and start_idx is not None:
                candidates.append(text[start_idx:idx + 1])
                start_idx = None

    for candidate in candidates:
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            continue

    # Fallback: return the widest brace-delimited section.
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx + 1].strip()

    return text



@tool
def extract_info_meter_sheet(report: str) -> Dict[str, Any]:
    """
    Extract pump opening, closing, and RTT data from a fuel station report.
    """

    llm = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0)

    system_prompt = """You are a fuel station data extraction engine.

CRITICAL: Output ONLY valid JSON. NO explanation, NO reasoning, NO comments, NO extra text.
Start with { and end with }. Nothing else.

RULES:
- Normalize all numbers (remove commas, spaces)
- Pump names may be misspelled — map them to: PMS 1, PMS 2, PMS 3, PMS 4, AGO 2, AGO 3, AGO 4
- If a value is missing or not mentioned, use null
- Do not guess or calculate values — only extract what is explicitly stated
- RTT means returns, transfers, or losses"""

    schema = {
        "date": None,
        "pumps": {
            "PMS 1": {"opening": None, "closing": None},
            "PMS 2": {"opening": None, "closing": None},
            "PMS 3": {"opening": None, "closing": None},
            "PMS 4": {"opening": None, "closing": None},
            "AGO 2": {"opening": None, "closing": None},
            "AGO 3": {"opening": None, "closing": None},
            "AGO 4": {"opening": None, "closing": None},
        },
        "rtt": {
            "PMS": None,
            "AGO": None
        }
    }

    prompt = f"""Extract data from this fuel station report and return ONLY valid JSON (no other text):

{report}

Return valid JSON in EXACT format (start with {{ and end with }}):
{json.dumps(schema, indent=2)}"""

    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])

    cleaned = clean_json(result.content)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Cleaned response: {cleaned}")
        raise


@tool
def extract_info_electronic_sales_sheet(report: str) -> Dict[str, Any]:
    """
    Extract electronic sales data (MomoPay, Airtel, Visa Card, Rubis Card, Rubis App)
    from a fuel station report.
    """

    llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

    system_prompt = """You are a fuel station data extraction engine.

CRITICAL: Output ONLY valid JSON. NO explanation, NO reasoning, NO comments, NO extra text.
Start with { and end with }. Nothing else.
CRITICAL: ONLY items under the ‘Expenses’ or ‘expenses:’ or equivalent heading are allowed
CRITICAL: HARD EXCLUSIONS (NEVER include these even if they look like expenses):
- STOCK
- LOSS AND GAIN
- TOTAL SALES
- LPG SALES
- LUBES SALES
- ELECTRONIC SALES
- BANKING 
- TOP UP
- WATER PRESENCE


RULES:
- Normalize all numbers (remove commas, spaces)
- Payment method names may be misspelled or abbreviated — map them to:
  MOMOPAY, AIRTEL, VISA CARD, RUBIS CARD, RUBIS APP
- If a value is missing or not mentioned, use null
- Do not guess or calculate values — only extract what is explicitly stated
- Values are in Uganda Shillings (UGX), always whole numbers"""

    schema = {
        "date": None,
        "electronic_sales": {
            "MOMOPAY":    None,
            "AIRTEL":     None,
            "VISA CARD":  None,
            "RUBIS CARD": None,
            "RUBIS APP":  None,
        }
    }

    prompt = f"""Extract electronic sales data from this fuel station report and return ONLY valid JSON (no other text):

{report}

Return valid JSON in EXACT format (start with {{ and end with }}):
{json.dumps(schema, indent=2)}"""

    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])

    cleaned = clean_json(result.content)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Cleaned response: {cleaned}")
        raise


@tool
def extract_expense(report: str):
    """
    Extract expense data from a fuel station report.
    """

    llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

    system_prompt = """You are a fuel station data extraction engine.

CRITICAL: Output ONLY valid JSON. NO explanation, NO reasoning, NO comments, NO extra text.
Start with { and end with }. Nothing else.

RULES:
- Normalize all numbers (remove commas, spaces)
- Do not guess or calculate values — only extract what is explicitly stated
- Values are in Uganda Shillings (UGX), always whole numbers"""

    schema = {
    "date": None,
    "expenses": [
        {
            "expense_name": None,
            "amount": None
        }
    ]
}

    prompt = f"""Extract expense data from this fuel station report and return ONLY valid JSON (no other text):

{report}

Return valid JSON in EXACT format (start with {{ and end with }}):
{json.dumps(schema, indent=2)}"""
    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])
    cleaned = clean_json(result.content)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Cleaned response: {cleaned}")
        raise




test_report = """04/06/2026
      Pump 1
PMS:1696506.241
PMS:674346.474
AG0:852073.232
AGO:545945.489

      PUMP 2
PMs:1387009.991
PMS. 346458.312
AGO:446305.630
AGO:292880.765

   STOCK
PMS: 9305.26
AGo:8000

     LOSS AND GAIN
PMS  -7
AGO. +5

TOTAL SALES
PMS: 1620.885
AGO:946.91


  LPG SALES:
6kg  (1)60000, burner (1)17000
     LUBES SALES  :  Gtx ½L (1)10000,GTX 1L(3)57000,GTX 4L (3)2160000, power  1(5)80000  coolant (1)18000,Edge w40 4L (1)190000, Edge w40 1L (1)50000, Edge w30 1L (1)55000, Magnetic 4L (1)125000,Multi 1L (5)100000, multi 5L (4)380000, filter 1001(1)8000
Expenses:
Tp to Bank 2000,
ELECTRONIC SALES:
Airtel money :1055808
Visa card:585000
Rubis card: 604200
Rubis App : 
Top up:

BANKING 15,622,000

Water presence 
Pms: little drops
Ago: little drops
Bik: Unmeasured droops """

# print(extract_info_electronic_sales_sheet(test_report))
# print(extract_info_meter_sheet(test_report))
print(extract_expense.invoke(test_report))