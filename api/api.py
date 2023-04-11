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
                "data": results,
                "code": 200
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

# RETREIVE EVERYTHING IN DICTIONARY DB
@app.get("/get_dict")
def get_dict():
    with connection:
        with connection.cursor() as cursor:
            dict = (
                """SELECT * FROM dictionary;"""
            )
            cursor.execute(dict)
            results = cursor.fetchall()
            response = {
                "data": results,
                "code": 200
            }
            if (len(results)==0):
                response["status"] = "No data available"
            
    return response


# RETRIEVE SYNONYM PER TYPE AND WORD
@app.post("/get_synonym")
def get_synonym():
    data = request.get_json()
    type = data["type"]
    word = data["word"]
    sql = ("""SELECT * FROM dictionary WHERE type=%s and financial_word = %s;""")
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, [type, word])
            results = cursor.fetchall()
    response = {"code": 200, "data": results}
    if (len(results)==0):
            response["status"] = "No data available"
            
    return response, 200

# INSERT SYNONYM 
@app.post("/add_synonym")
def add_synonym():
    data = request.get_json()
    did = data["did"]
    synonym = data["synonym"]    
    sql = (
        "UPDATE dictionary SET synonym = %s WHERE did=%s;"
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (synonym, did))
    return {"message": "Updated", "code": 200}, 200

# GET ALL DETAILS FROM NLP
@app.post("/get_all_from_nlp")
def get_all_from_nlp ():
    data = request.get_json()
    file_name = data["file_name"]
    sql = (
        "SELECT * FROM nlp WHERE fid = (SELECT fid FROM companies_files WHERE file = %s );"
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, [file_name])
            results = cursor.fetchall()
    response = {"code": 200, "data": results}
    if (len(results)==0):
            response["status"] = "No data available"
            
    return response, 200

# RETRIEVE FILE NAME FROM SPECIFIC COMPANY
@app.post("/get_file_name")
def get_file_name ():
    data = request.get_json()
    cid = data["cid"]
    sql = (
        "SELECT file FROM companies_files WHERE cid =  %s and file_type = 'pdf';"
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, [cid])
            results = cursor.fetchall()
    response = {"code": 200, "data": results}
    if (len(results)==0):
            response["status"] = "No data available"
            
    return response, 200


# INSERT EXTRACTED DATA NLP
@app.post("/insert_extracted_data_nlp")
def insert_extracted_data_nlp():
    data = request.get_json()
    fid = data["fid"]
    cid = data["cid"]
    string = data["data"]
    
    sql = (
    "INSERT INTO nlp (cid, fid, string) VALUES ( %s, %s, %s);"
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (cid, fid, string))
    return {"message": "Added", "code": 201}, 201


if __name__ == '__main__':
    app.run(debug=True)