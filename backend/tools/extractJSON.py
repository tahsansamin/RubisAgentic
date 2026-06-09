from typing import TypedDict, Optional, List, Dict, Any
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI as Gemini
from dotenv import load_dotenv
import os
import json
import re
load_dotenv()  # Load environment variables from .env file



class FuelReportInput(TypedDict):
    report: str

def clean_json(text: str) -> str:
    # remove ```json and ```
    text = text.strip()
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()


@tool
def extract_fuel_report(report: str) -> Dict[str, Any]:
    """
    Extract structured fuel station report data from messy SMS/log text.
    """

    llm = Gemini(model="gemini-2.5-flash", temperature=0)

    system_prompt = """
You are a fuel station data extraction engine.

Extract structured JSON from messy station reports.

RULES:
- Normalize numbers (remove commas)
- PMS/AGO may be misspelled (PMS, PMs, PMS., AG0, AGo, AGO)
- If missing, use null
- Do not guess values
- Output ONLY valid JSON matching schema
"""

    schema = {
        "date": None,
        "pumps": [
            {
                "pump_id": "",
                "products": {
                    "PMS": None,
                    "AGO": None
                }
            }
        ],
        "stock": {"PMS": None, "AGO": None},
        "loss_and_gain": {"PMS": None, "AGO": None},
        "total_sales": {"PMS": None, "AGO": None},
        "lpg_sales": [],
        "lubricants_sales": [],
        "expenses": [],
        "electronic_sales": {
            "airtel_money": None,
            "visa_card": None,
            "rubis_card": None,
            "rubis_app": None,
            "top_up": None
        },
        "banking_total": None,
        "water_presence": {
            "pms": None,
            "ago": None,
            "bik": None
        }
    }

    prompt = f"""
Extract data from this report:

{report}

Return JSON in EXACT format:
{schema}
"""

    result = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])
    cleaned = clean_json(result.content)

    return json.loads(cleaned)




# test_report = """04/06/2026
#       Pump 1
# PMS:1696506.241
# PMS:674346.474
# AG0:852073.232
# AGO:545945.489

#       PUMP 2
# PMs:1387009.991
# PMS. 346458.312
# AGO:446305.630
# AGO:292880.765

#    STOCK
# PMS: 9305.26
# AGo:8000

#      LOSS AND GAIN
# PMS  -7
# AGO. +5

# TOTAL SALES
# PMS: 1620.885
# AGO:946.91


#   LPG SALES:
# 6kg  (1)60000, burner (1)17000
#      LUBES SALES  :  Gtx ½L (1)10000,GTX 1L(3)57000,GTX 4L (3)2160000, power  1(5)80000  coolant (1)18000,Edge w40 4L (1)190000, Edge w40 1L (1)50000, Edge w30 1L (1)55000, Magnetic 4L (1)125000,Multi 1L (5)100000, multi 5L (4)380000, filter 1001(1)8000
#  Expenses:
#  Tp to Bank 2000,
#  ELECTRONIC SALES:
# Airtel money :1055808
# Visa card:585000
# Rubis card: 604200
# Rubis App : 
# Top up:

# BANKING 15,622,000

# Water presence 
# Pms: little drops
# Ago: little drops
# Bik: Unmeasured droops """

# print(extract_fuel_report(test_report))