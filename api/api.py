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


if __name__ == '__main__':
    app.run(debug=True)