import requests 
import json
import os
from dotenv import load_dotenv

load_dotenv()
exchange_rate_api_key = os.getenv("EXCHANGE_RATE_API_KEY")

# GET REQUEST
def fetch(session, url):
    try:
        result = session.get(url)
        return result.json()
    except Exception:
        return {}

# POST REQUEST
def post(session, url, body):   
    try:
        result = session.post(url, json=body)
        return result.json()
    except Exception:
        return {}

########## Call HTTP REQUEST ########## 
# GET ALL COMPNIES NAMES
def get_all_companies():
    session = requests.Session()
    data = fetch(session, f"http://is484testing.pythonanywhere.com/get_companies")
    return data

# INSERT NEW COMPANY
def add_company(cid, com_name):
    session = requests.Session()
    body = {
        "cid": cid,
        "com_name": com_name,
    }
    
    data = post(session, f"http://is484testing.pythonanywhere.com/add_company", body)
    return data

# INSERT NEW FILE
def add_file(cid, file, type):
    session = requests.Session()
    body = {
        "cid": cid,
        "file": file,
        "type": type,
    }
    data = post(session, f"http://is484testing.pythonanywhere.com/insert_file", body)
    return data

# GET ALL COMPNIES FILES
def get_allFiles():
    session = requests.Session()
    data = fetch(session, f"http://is484testing.pythonanywhere.com/get_allFiles")
    return data

# INSERT EXTRACTED DATA
def insert_data(fid, cid, data):
    session = requests.Session()
    body = {
        "fid": fid,
        "cid": cid,
        "data": json.dumps(data)
    }
    
    data = post(session, f"http://is484testing.pythonanywhere.com/insert_data", body)
    return data

# RETRIEVE EXTRACTED DATA
def retrieve_data(cid):
    session = requests.Session()
    body = {
        "cid": cid,
    }
    data = post(session, f"http://is484testing.pythonanywhere.com/retrieve_data", body)
    return data

# GET SYMBOLS
def get_symbols():
    session = requests.Session()
    data = fetch(session, f"https://v6.exchangerate-api.com/v6/{exchange_rate_api_key}/codes")
    return_data = {}
    for codes in data["supported_codes"]:
        return_data[codes[0]] = codes[1]
    return return_data

# GET CURRENCIES
def get_currencies(base):
    session = requests.Session()
    data = fetch(session, f"https://v6.exchangerate-api.com/v6/{exchange_rate_api_key}/latest/{base}")
    return data

def get_months(mnth):
    month = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }
    return month[mnth]

# GET FINANCIAL WORDS
def get_financial_words_col(sheet):
    words = {
        "Income Statement": {
            "revenue": ["total revenue"],
            "cost": ["total cost"],
            "gross profit": ["earnings", "gross income"],
            "gross loss": [],
            "net profit": ["net income", "net earnings"],
            "net loss": [],
            "income tax": [],
            "interest": ["interest expense"],
            "depreciation": ["amortization", "depletion"],
        },
        "Balance Sheet": {
            "total equities": [],
            "total liabilities": [],
            "total current liabilties": [],
            "total non current liabitilies": [],
            "total assets": [],
            "total current assets": [],
            "total non current assets": [],
            "debt": [],
            "cash": [],
        },
        "Cash Flow": {
            "operating net cash flow": [],
            "investing net cash flow": [],
            "financing net cash flow": [],
        },
    }
    return words[sheet]

def get_financial_words_row(sheet):
    words = {
        "Income Statement": {
            "total": [],
        },
        "Balance Sheet": {
            "total": []
        },
        "Cash Flow": {
            "total": []
        },
    }
    return words[sheet]

# JSON FORMAT
def get_json_format():
    format = {
        "currency": "",
        "fiscal_start_month": [],
        "income_statement": [],
        "balance_sheet": [],
        "cash_flow": [],
        "other_metrics": [
            # {
            #     "year": "",
            #     "numberFormat": "", 
            #     "returnOnAsset": 0,
            #     "netInterestMargin": 0,
            #     "netInterestIncomeRatio": 0,
            #     "costIncomeRatio": 0,
            #     "ebidta": 0
            # }
        ]
    }
    return format

def get_json_financial_format(sheet):
    sheets = {
        "income_statement": {
            "year": "",
            "numberFormat": "", 
            "revenue": 0,
            "cost": 0,
            "grossProfit": 0,
            "grossLoss": 0,
            "netProfit": 0,
            "netLoss": 0,
            "incomeTax": 0,
            "interest": 0,
            "depreciation": 0,
        },
        "balance_sheet": {
            "year": "",
            "numberFormat": "", 
            "totalEquities": 0,
            "totalLiabilities": 0,
            "totalCurrentLiabilties": 0,
            "totalNonCurrentLiabitilies": 0,
            "totalAssets": 0,
            "totalCurrentAssets": 0,
            "totalNonCurrentAssets": 0,
            "debt": 0,
            "cash": 0
        },
        "cash_flow": {
            "year": "",
            "numberFormat": "", 
            "operatingNetCashFlow": 0,
            "investingNetCashFlow": 0,
            "financingNetCashFlow": 0
        }
    }
    return sheets[sheet]

# GET DICTIONARY
def get_dict():
    session = requests.Session()
    data = fetch(session, f"http://is484testing.pythonanywhere.com/get_dict")
    return data

# INSERT SYNONYM
def add_synonym(did, synonym):
    session = requests.Session()
    body = {
        "did": did,
        "synonym": json.dumps(synonym)
    }
    
    data = post(session, f"http://is484testing.pythonanywhere.com/add_synonym", body)
    return data