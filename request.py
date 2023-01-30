import requests 
import json

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
        "type": type
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

#####DUMMY DATA -- NEEDS TO CHANGE
# GET SYMBOLS
def get_symbols():
    session = requests.Session()
    data = fetch(session, f"http://127.0.0.1:5000/get_symbols")
    return data

# GET CURRENCIES
def get_currencies(base):
    body = {
        "base": base
    }
    session = requests.Session()
    data = post(session, f"http://127.0.0.1:5000/get_currencies", body)
    return data

