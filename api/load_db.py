import pandas as pd
import numpy as np
import os
import psycopg2

from dotenv import load_dotenv
dotenv = load_dotenv()
POSTGRESQL_CONNECTION_STRING = os.getenv("POSTGRESQL_CONNECTION_STRING")

from database import (
    Base,
    session_engine_from_connection_string,
    Companies,
    Companies_Files,
    Extracted_Data,
    Dictionary,
    convert_df_to_lst_of_table_objects
)

######### CREATE DB TABLES #########
# create session and engine
session, engine = session_engine_from_connection_string(POSTGRESQL_CONNECTION_STRING)

conn = engine.connect()

# tables to be created
table_objects = [
    Companies.__table__,
    Companies_Files.__table__,
    Extracted_Data.__table__,
    Dictionary.__table__,
]

# Drop All Tables
Base.metadata.drop_all(engine, table_objects)

# Create All Tables
Base.metadata.create_all(engine, table_objects)

# Insert Metrics into Dictionary 
connection = psycopg2.connect(POSTGRESQL_CONNECTION_STRING)
cursor = connection.cursor()
 
postgres_insert_query = """ INSERT INTO dictionary (type, sheet, financial_word, synonym) VALUES (%s,%s,%s,%s)"""

# income statement (col)
cursor.execute(postgres_insert_query, ('col','Income Statement', 'revenue', '["total revenue"]'))
cursor.execute(postgres_insert_query, ('col','Income Statement', 'cost', '["total cost"]'))
cursor.execute(postgres_insert_query, ('col','Income Statement', 'gross profit', '["earnings", "gross income"]'))
cursor.execute(postgres_insert_query, ('col','Income Statement', 'gross loss', ''))
cursor.execute(postgres_insert_query, ('col','Income Statement', 'net profit', '["net income", "net earnings"]'))
cursor.execute(postgres_insert_query, ('col','Income Statement', 'net loss', ''))
cursor.execute(postgres_insert_query, ('col','Income Statement', 'income tax', ''))
cursor.execute(postgres_insert_query, ('col','Income Statement', 'interest', '["interest expense"]'))
cursor.execute(postgres_insert_query, ('col','Income Statement', 'depreciation', '["amortization", "depletion"]'))

# balance sheet (col)
cursor.execute(postgres_insert_query, ('col','Balance Sheet', 'total equities', ''))
cursor.execute(postgres_insert_query, ('col','Balance Sheet', 'total liabilities', ''))
cursor.execute(postgres_insert_query, ('col','Balance Sheet', 'total current liabilties', ''))
cursor.execute(postgres_insert_query, ('col','Balance Sheet', 'total non current liabitilies', ''))
cursor.execute(postgres_insert_query, ('col','Balance Sheet', 'total assets', ''))
cursor.execute(postgres_insert_query, ('col','Balance Sheet', 'total current assets', ''))
cursor.execute(postgres_insert_query, ('col','Balance Sheet', 'total non current assets', ''))
cursor.execute(postgres_insert_query, ('col','Balance Sheet', 'debt', ''))
cursor.execute(postgres_insert_query, ('col','Balance Sheet', 'cash', ''))

# cash flow (col)
cursor.execute(postgres_insert_query, ('col','Cash Flow', 'operating net cash flow', ''))
cursor.execute(postgres_insert_query, ('col','Cash Flow', 'investing net cash flow', ''))
cursor.execute(postgres_insert_query, ('col','Cash Flow', 'financing net cash flow', ''))

# income statement (row)
cursor.execute(postgres_insert_query, ('row','Income Statement', 'total', ''))
cursor.execute(postgres_insert_query, ('row','Balance Sheet', 'total', ''))
cursor.execute(postgres_insert_query, ('row','Cash Flow', 'total', ''))

connection.commit()
# session.close()