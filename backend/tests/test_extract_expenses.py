import json

import pytest

from tools import extractJSON


sample_report = '''04/06/2026
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
'''


def test_extract_expenses_sheet_real_groq():
    """Call the real Groq LLM via the tool. Skip test if call fails.

    This test intentionally uses the real `ChatGroq` from the module so it
    validates end-to-end behavior. If credentials/network are not available
    the test is skipped.
    """

    
    result = extractJSON.extract_info_expenses_sheet.invoke(sample_report)
   

    assert isinstance(result, dict)
    # Ensure date matches the report's leading date
    assert result.get("date") == "04/06/2026"
    assert "expenses" in result and isinstance(result["expenses"], dict)

    # Ensure 'Tp to Bank' expense exists and amount is 2000
    expenses = result["expenses"]
    found = False
    for v in expenses.values():
        if isinstance(v, dict):
            desc = (v.get("description") or "").lower()
            amt = v.get("amount")
            if ("tp" in desc or "trip" in desc) and "bank" in desc:
                assert amt == 2000, f"Expected Tp to Bank amount 2000, got {amt}"
                found = True
                break

    assert found, "Tp to Bank expense not found in extracted expenses"


