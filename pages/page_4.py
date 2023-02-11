import streamlit as st
# import camelot.io as camelot
import camelot
import PyPDF2
import os
from st_aggrid import AgGrid
import glob
import pandas as pd
import boto3
import io 
from PIL import Image

# if 1 pg -> display tables
    # check if more than 1 table

# if more than 1pg -> call from sakinah
    # check if more than 1 table

def get_file_name (file):
    filename = os.path.splitext(file)[0]
    return filename

def get_file_type (file):
    filetype = os.path.splitext(file)[1]
    return filetype

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

def extract_tables (tables):
    for i in range(len(tables)):
        tablenum = i + 1
        st.subheader('Extracted Table ' + str(tablenum))
        option = st.selectbox('Select a Financial Statement', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), label_visibility='collapsed', key=str(i))
        # st.write('You selected:', option)
        tables[i].to_csv(file_name + ".csv")
        df = pd.read_csv(file_name + ".csv")
        AgGrid(df, editable=True)

st.subheader('Number Format & Currency')

# Initialization
if 'pg_input' not in st.session_state:
    st.session_state['pg_input'] = ''

if 'status' not in st.session_state:
    st.session_state['status'] = False

temp_path = "./temp_files"
dir = os.listdir(temp_path)

# if temp_files is not empty then extract
if len(dir) > 1:

    # check if file type uploaded to temp files is a PDF
    file_paths = glob.glob("./temp_files/*")
    count = 0
    for path in file_paths:
        file_type = get_file_type(path)

        if file_type == '.pdf':
            file_path = glob.glob("./temp_files/*.pdf")[0]
            file_name = get_file_name(file_path)
            totalpages = get_total_pgs_PDF(file_path)

            # single page pdf
            if (totalpages == 1):
                tables = check_tables_single_PDF(file_path)
                extract_tables(tables)
            
            # multi page pdf
            else:
                pg_input = st.session_state.pg_input
                status = st.session_state.status

                # user input is successful on page 3
                if (status == True and pg_input != ''):
                    tables = check_tables_multi_PDF(file_path, str(pg_input))
                    extract_tables(tables)
                    
                else:
                    st.error("Please specify the pages you want to extract.", icon="🚨")

        # if uploaded file is image -> call aws
        #else:
