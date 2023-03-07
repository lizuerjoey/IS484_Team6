
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.sql import select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker

import os
import pandas as pd
import numpy as np


########## DB Utility Functions ##########

# Create a base for the models to build upon.
Base = declarative_base()

# Session, Engine
def session_engine_from_connection_string(conn_string):
    '''
    Takes in a DB Connection String
    Return a tuple: (session, engine)

    e.g. session, engine = session_engine_from_connection_string(string)
    '''
    engine = create_engine(conn_string)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    return DBSession(), engine


# Convert DF into Table Objects
def convert_df_to_lst_of_table_objects(df, Table):
    '''
    Takes in a dataframe (each column name aligned to a DB table's column name)
    and convert it into a list of Table objects
    '''
    return [Table(**{k: v for k, v in row.items() if not np.array(pd.isnull(v)).any()}) for row in df.to_dict("records")]


########## DB Tables ##########

class Companies(Base):
    __tablename__ = "companies"

    cid = Column(String, primary_key=True)
    name = Column(String)

class Companies_Files(Base):
    __tablename__ = "companies_files"
    fid = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(String, ForeignKey("companies.cid"))
    file = Column(String)
    file_type = Column(String)
    created_date = Column(DateTime, server_default=func.now())


class Extracted_Data(Base):
    __tablename__ = "extracted_data"
    eid = Column(Integer, primary_key=True, autoincrement=True)
    fid = Column(Integer, ForeignKey("companies_files.fid"))
    cid = Column(String, ForeignKey("companies.cid"))
    data = Column(String)

class Dictionary(Base):
    __tablename__ = "dictionary"
    did = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    sheet = Column(String)
    financial_words = Column(String)
