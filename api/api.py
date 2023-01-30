import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()
app = Flask(__name__)
######## DB CONNECTION ########
url = os.environ.get("POSTGRESQL_CONNECTION_STRING")
connection = psycopg2.connect(url)

######## APIs ########
@app.get("/get_companies")
def get_companies():
    with connection:
        with connection.cursor() as cursor:
            companies = (
                """SELECT * FROM companies;"""
            )
            cursor.execute(companies)
            results = cursor.fetchall()
            response = {
                "data": results,
                "code": 200
            }
            if (len(results)==0):
                response["status"] = "No companies available"
            
    return response

@app.post("/add_company")
def add_company():
    data = request.get_json()
    cid = data["cid"]
    com_name = data["com_name"]
    sql = (
    "INSERT INTO companies (cid, name) VALUES (%s,  %s);"
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (cid, com_name))
    return {"message": "Added", "code": 201}, 201

@app.post("/insert_file")
def insert_file():
    data = request.get_json()
    cid = data["cid"]
    file = data["file"]
    file_type = data["type"]
    sql = (
    "INSERT INTO companies_files (cid, file, file_type) VALUES (%s, %s, %s);"
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (cid, file, file_type))
    return {"message": "Added", "code": 201}, 201

@app.get("/get_allFiles")
def get_allFiles():
    with connection:
        with connection.cursor() as cursor:
            sql = (
                """SELECT cf.fid, c.name, cf.file, cf.file_type FROM companies c INNER JOIN companies_files cf ON cf.cid=c.cid ;"""
            )
            cursor.execute(sql)
            results = cursor.fetchall()
            response = {
                "data": results
            }
            if (len(results)==0):
                response["status"] = "No files available"
    return response

# INSERT EXTRACTED DATA
@app.post("/insert_data")
def insert_data():
    data = request.get_json()
    fid = data["fid"]
    cid = data["cid"]
    extracted_data = data["data"]
    
    sql = (
    "INSERT INTO extracted_data (fid, cid, data) VALUES (%s, %s, %s);"
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (fid, cid, extracted_data))
    return {"message": "Added", "code": 201}, 201

# RETRIEVE EXTRACTED DATA
@app.post("/retrieve_data")
def retrieve_data():
    data = request.get_json()
    cid = data["cid"]
    print(cid)
    sql = ("""SELECT * FROM extracted_data WHERE cid = %s;""")
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, [cid])
            results = cursor.fetchall()
    return {"message": "Added", "code": 200, "data": results}, 200

# Dummy Data
@app.get("/get_symbols")
def get_symbols():
    symbols = {
        "symbols": {
        "AUD": "Australian",
        "CAD": "Canada",
        "CHF": "Swiss Franc",
        "CNY": "Chinese Yuan",
        "JPY": "Japanese Yen",
        "USD": "United States"
        }
    }
    return symbols

@app.post("/get_currencies")
def get_currencies():
    data = request.get_json()
    base = data["base"]
    currencies = {
        "rates": {
            "AUD": 1.566015,
            "CAD": 1.560132,
            "CHF": 1.154727,
            "CNY": 7.827874,
            "JPY": 132.360679,
            "USD": 1.23396,
        }
    }
    return currencies

if __name__ == '__main__':
    app.run(debug=True)