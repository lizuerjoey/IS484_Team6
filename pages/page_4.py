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
import openpyxl
from openpyxl import load_workbook
# from request import (get_num_format)

# if 1 pg -> display tables
    # check if more than 1 table

# if more than 1pg -> call from sakinah
    # check if more than 1 table

number = [            
            "Not Selected",
            "Thousand",
            "Million",
            "Billion",
            "Trillion",
            "Quadrillion"
        ]

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

def get_number_format (excel_path):
    num_array = []
    workbook = load_workbook(excel_path)
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        print(f"Title = {sheet.title}")
        for value in sheet.iter_rows(values_only=True):
            for cell in value:
                if cell is None:
                    continue
                if "thousand" in str(cell).lower():
                    num_array.append(1)
                if "million" in str(cell).lower():
                    num_array.append(2)
                if "billion" in str(cell).lower():
                    num_array.append(3)
                if "trillion" in str(cell).lower():
                    num_array.append(4)
                if "quadrillion" in str(cell).lower():
                    num_array.append(5)

    # get the first index because it is the first to retrieve
    return num_array[0]

def sort_num_list(index):
    format = number.pop(index)
    number.insert(0, format)

    return number

def extract_tables (tables):
    for i in range(len(tables)):
        tablenum = i + 1
        st.subheader('Extracted Table ' + str(tablenum))
        option = st.selectbox('Select a Financial Statement:', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), key=str(i))
        # st.write('You selected:', option)
        
        tables[i].to_excel(file_name + ".xlsx")
        num_format = get_number_format(file_name + ".xlsx")

        new_num_list = sort_num_list(num_format)
        selected = st.selectbox("Number Format:", new_num_list, key="x" + str(i))

        tables[i].to_csv(file_name + ".csv")
        df = pd.read_csv(file_name + ".csv")
        AgGrid(df, editable=True)

st.subheader('Currency')

# Initialization
if 'pg_input' not in st.session_state:
    st.session_state['pg_input'] = ''

if 'status' not in st.session_state:
    st.session_state['status'] = False

temp_path = "./temp_files"
dir = os.listdir(temp_path)

# if temp_files is not empty then extract
if len(dir) > 1:

    file_paths = glob.glob("./temp_files/*")
    count = 0
    for path in file_paths:
        file_type = get_file_type(path)

        # file is pdf
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

        # file is image
        # else:

