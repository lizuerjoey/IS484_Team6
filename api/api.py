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
                "data": results
            }
            if (len(results)==0):
                response["status"] = "No companies available"
            
    return response

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
    return {"message": "Added"}, 201

@app.get("/get_allFiles")
def get_allFiles():
    with connection:
        with connection.cursor() as cursor:
            sql = (
                """SELECT * FROM companies_files cf INNER JOIN companies c ON c.cid=cf.cid ;"""
            )
            cursor.execute(sql)
            results = cursor.fetchall()
            response = {
                "data": results
            }
            if (len(results)==0):
                response["status"] = "No files available"
    return response
    
if __name__ == '__main__':
    app.run(debug=True)