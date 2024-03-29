import requests 
import json
import os
from dotenv import load_dotenv
import base64

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
    data = fetch(session, f"http://127.0.0.1:5000/get_companies")
    return data

# INSERT NEW COMPANY
def add_company(cid, com_name):
    session = requests.Session()
    body = {
        "cid": cid,
        "com_name": com_name,
    }
    
    data = post(session, f"http://127.0.0.1:5000/add_company", body)
    return data

# INSERT NEW FILE
def add_file(cid, file, type):
    session = requests.Session()
    body = {
        "cid": cid,
        "file": file,
        "type": type,
    }
    data = post(session, f"http://127.0.0.1:5000/insert_file", body)
    return data

# GET ALL COMPNIES FILES
def get_allFiles():
    session = requests.Session()
    data = fetch(session, f"http://127.0.0.1:5000/get_allFiles")
    return data

# INSERT EXTRACTED DATA
def insert_data(fid, cid, data):
    session = requests.Session()
    body = {
        "fid": fid,
        "cid": cid,
        "data": json.dumps(data)
    }
    
    data = post(session, f"http://127.0.0.1:5000/insert_data", body)
    return data

# RETRIEVE EXTRACTED DATA
def retrieve_data(cid):
    session = requests.Session()
    body = {
        "cid": cid,
    }
    data = post(session, f"http://127.0.0.1:5000/retrieve_data", body)
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
def get_financial_words_col(financial_sheet):
    words = {}

    session = requests.Session()
    result = fetch(session, f"http://127.0.0.1:5000/get_dict")
    for item in result["data"]:
        type = item[1]
        sheet = item[2]
        word = item[3]
        synonyms = item[4]

        if type == "col":
            if sheet == "Income Statement":
                if sheet not in words:
                    words[sheet] = {}
                if word not in words[sheet]:
                    words[sheet][word] = []
                if synonyms:
                    words[sheet][word].extend(eval(synonyms))
            elif sheet == "Balance Sheet":
                if sheet not in words:
                    words[sheet] = {}
                if word not in words[sheet]:
                    words[sheet][word] = []
                if synonyms:
                    words[sheet][word].extend(eval(synonyms))
            elif sheet == "Cash Flow":
                if sheet not in words:
                    words[sheet] = {}
                if word not in words[sheet]:
                    words[sheet][word] = []
                if synonyms:
                    words[sheet][word].extend(eval(synonyms))
    return words[financial_sheet]

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
        "other_metrics": []
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
    data = fetch(session, f"http://127.0.0.1:5000/get_dict")
    return data

# INSERT SYNONYM
def add_synonym(did, synonym):
    session = requests.Session()
    body = {
        "did": did,
        "synonym": json.dumps(synonym)
    }
    
    data = post(session, f"http://127.0.0.1:5000/add_synonym", body)
    return data

# RETRIEVE FILE DETAILS
def retrieve_details(file_name):
    session = requests.Session()
    body = {
        "file_name": base64.b64encode(file_name.encode("ascii")).decode("ascii"),
    }
    data = post(session, f"http://127.0.0.1:5000/get_all_from_nlp", body)
    return data

# RETRIEVE EXTRACTED DATA
def retrieve_file_name(cid):
    session = requests.Session()
    body = {
        "cid": cid,
    }
    datas = post(session, f"http://127.0.0.1:5000/get_file_name", body)
    return_data = []
    for data in datas["data"]:
        return_data.append(base64.b64decode(data[0].encode("ascii")).decode("ascii"))
    return return_data

# INSERT SYNONYM
def insert_extracted_data_nlp(fid, cid, data):
    session = requests.Session()
    body = {
        "fid": fid,
        "cid": cid,
        "data": json.dumps(data)
    }
    
    data = post(session, f"http://127.0.0.1:5000/insert_extracted_data_nlp", body)
    return data