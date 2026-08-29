from typing import List

from agent import build_agent, display_agent
from langchain.messages import HumanMessage
from tools.writefuelmeter import write_fuel_meter_sheet
from tools.write_electronic_sales import write_electronic_sales_sheet
from tools.extractJSON import normalize_fuel_meter_data
import json


myagent = build_agent()
test_input = """
26th August 2026
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
Bik: Unmeasured droops
"""
    
def return_dictionary(report: str) -> List[dict]:
    """Return a dictionary containing the extracted information from the report."""
    messages = [HumanMessage(content=report)]
    messages = myagent.invoke({"messages": messages})
    final_content = messages["messages"][-1].content
    try:
        output = json.loads(final_content)
        if isinstance(output, list):
            for index, item in enumerate(output):
                if isinstance(item, dict) and "pumps" in item:
                    output[index] = normalize_fuel_meter_data(item)
        return output
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON: {e}")


def write_extracted_information(extracted: dict) -> None:
    """Write the extracted fuel and electronic-sales data to their sheets."""
    
    electronic_result = write_electronic_sales_sheet.invoke(json.dumps(extracted[1]))
    meter_result = write_fuel_meter_sheet.invoke(json.dumps(extracted[0]))
    print("success")

def combine_and_write(report: str) -> None:
    """Combine the extraction and writing process."""
    try:
        myagent = build_agent()
    except Exception as e:
        print(f"Error occurred during agent building: {e}")
        return
    try:
        extracted_info = return_dictionary(report)
    except ValueError as e:
        print(f"Error occurred during extraction: {e}")
    try:
        write_extracted_information(extracted_info)

    except ValueError as e:
        print(f"Error occurred during writing: {e}")
