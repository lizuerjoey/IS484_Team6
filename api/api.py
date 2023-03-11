import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request

api_folder = os.path.expanduser('~/mysite')
load_dotenv(os.path.join(api_folder, '.env'))

######## DB CONNECTION ########
url = os.environ.get("POSTGRESQL_CONNECTION_STRING")

# connection = psycopg2.connect(url)
# print(connection)

app = Flask(__name__)

# ######## APIs ########

@app.get("/get_companies")
def get_companies():
    connection = psycopg2.connect(url)
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

    connection.close()
    return response

@app.post("/add_company")
def add_company():
    connection = psycopg2.connect(url)
    data = request.get_json()
    cid = data["cid"]
    com_name = data["com_name"]
    sql = (
    "INSERT INTO companies (cid, name) VALUES (%s,  %s);"
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (cid, com_name))

    connection.close()
    return {"message": "Added", "code": 201}, 201

@app.post("/insert_file")
def insert_file():
    connection = psycopg2.connect(url)
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

    connection.close()
    return {"message": "Added", "code": 201}, 201

@app.get("/get_allFiles")
def get_allFiles():
    connection = psycopg2.connect(url)
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

    connection.close()
    return response

# INSERT EXTRACTED DATA
@app.post("/insert_data")
def insert_data():
    connection = psycopg2.connect(url)
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

    connection.close()
    return {"message": "Added", "code": 201}, 201

# RETRIEVE EXTRACTED DATA
@app.post("/retrieve_data")
def retrieve_data():
    connection = psycopg2.connect(url)
    data = request.get_json()
    cid = data["cid"]
    print(cid)
    sql = ("""SELECT * FROM extracted_data WHERE cid = %s;""")
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, [cid])
            results = cursor.fetchall()

    connection.close()
    return {"message": "Added", "code": 200, "data": results}, 200

# RETREIVE EVERYTHING IN DICTIONARY DB
@app.get("/get_dict")
def get_dict():
    connection = psycopg2.connect(url)
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

    connection.close()
    return response

# RETRIEVE SYNONYM PER TYPE AND WORD
@app.post("/get_synonym")
def get_synonym():
    connection = psycopg2.connect(url)
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

    connection.close()
    return response, 200

# INSERT SYNONYM
@app.post("/add_synonym")
def add_synonym():
    connection = psycopg2.connect(url)
    data = request.get_json()
    did = data["did"]
    synonym = data["synonym"]
    sql = (
        "UPDATE dictionary SET synonym = %s WHERE did=%s;"
    )
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (synonym, did))

    connection.close()
    return {"message": "Updated", "code": 200}, 200