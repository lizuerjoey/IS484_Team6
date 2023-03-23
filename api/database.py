
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.sql import select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker

import os
import pandas as pd


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
    financial_word = Column(String)
    synonym = Column(String)

class NLP(Base):
    __tablename__ = "nlp"
    nid = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(String, ForeignKey("companies.cid"))
    fid = Column(Integer, ForeignKey("companies_files.fid"))
    string = Column(String)