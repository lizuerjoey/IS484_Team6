import streamlit as st
import camelot.io as camelot
import PyPDF2
import os
from st_aggrid import AgGrid
import glob
import PyPDF2
import pandas as pd

pages = "1"
fname = ""

# if 1 pg -> display tables
    # check if more than 1 table

# if more than 1pg -> call from sakinah
    # check if more than 1 table

def get_total_pgs_PDF (file):
    file = open(file, 'rb')
    pdf = PyPDF2.PdfFileReader(file)
    pages = pdf.numPages
    return pages

def check_tables_single_PDF (file):
    tables = camelot.read_pdf(file, pages="1", flavor="stream", edge_tol=100, row_tol=10)
    return (tables)

def check_tables_multi_PDF (file, pages):
    tables = camelot.read_pdf(file, pages=pages, flavor="stream", edge_tol=100, row_tol=10)
    return (tables)

temp_path = "./temp_files"
dir = os.listdir(temp_path)

# if temp_files is not empty then extract
if len(dir) > 0:
    # retrieve the file from temp_files
    # get the first (because there will always be only one) pdf file in the list of all files of temp_files directory
    file_path = glob.glob("./temp_files/*.pdf")[0]

    totalpages = get_total_pgs_PDF(file_path)

    if (totalpages == 1):
        tables = check_tables_single_PDF(file_path)

        for i in range(len(tables)):
            tablenum = i + 1
            st.subheader('Extracted Table ' + str(tablenum))
            tables[i].to_csv(file_path + ".csv")
            df = pd.read_csv(file_path + ".csv")
            AgGrid(df, editable=True)
    
    # else:
        # get page number from sakinah
        # tables = check_tables_single_PDF(file_path)

