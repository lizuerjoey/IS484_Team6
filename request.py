import requests 

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