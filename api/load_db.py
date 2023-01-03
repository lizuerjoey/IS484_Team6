import pandas as pd
import numpy as np
import os

from dotenv import load_dotenv
dotenv = load_dotenv()
POSTGRESQL_CONNECTION_STRING = os.getenv("POSTGRESQL_CONNECTION_STRING")

from database import (
    Base,
    session_engine_from_connection_string,
    Companies,
    Companies_Files,
    Extracted_Data,
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
]

# Drop All Tables
Base.metadata.drop_all(engine, table_objects)

# Create All Tables
Base.metadata.create_all(engine, table_objects)
# session.close()