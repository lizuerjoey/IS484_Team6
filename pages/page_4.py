import streamlit as st
# import camelot.io as camelot
import camelot
import PyPDF2
import os
from st_aggrid import AgGrid
import glob
import pandas as pd
from openpyxl import load_workbook
from extraction.pdf_to_image import (convert_file)
from extraction.aws_image import (image_extraction)


number = [            
            "Unable to Determine",
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

                # # if cannot find any
                # if "thousand" not in str(cell).lower() and "million" in str(cell).lower() and "billion" in str(cell).lower() and "trillion" in str(cell).lower() and "quadrillion" in str(cell).lower():
                #     print("IN")
                #     num_array.append(0)
    
    index = 0
    if len(num_array) > 0:
        # get the first index because it is the first to retrieve
        index = num_array[0]
    else:
        index = 0 # unable to determine
    
    return index

def sort_num_list(index):
    format = number.pop(index)
    number.insert(0, format)
    return number

def extract_tables (tables):
    is_df_empty = False
    # CHECK ACCURACY
    accuracy = []
    for i in range(len(tables)):
        accuracy.append(tables[i].parsing_report["accuracy"])
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

        if df.empty:
            is_df_empty = True
            break
        else:
            AgGrid(df, editable=True)
   
    # TESTING REQUIRED
    if (any(i < 75 for i in accuracy) and is_df_empty):
        dfs = convert_file()
        for df in dfs:
            AgGrid(df, editable=True)
    

# Initialization
if 'pg_input' not in st.session_state:
    st.session_state['pg_input'] = ''

if 'status' not in st.session_state:
    st.session_state['status'] = False

temp_path = "./temp_files"
dir = os.listdir(temp_path)

# if temp_files is not empty then extract
if len(dir) > 1:
    st.subheader('Currency')

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
        elif file_type == '.png' or file_type == '.jpg' or file_type == '.jpeg' and file_type != '.txt':
            file_path = glob.glob("./temp_files/*" + file_type)[0]
            file_name = get_file_name(file_path)

    
            dataframes = image_extraction(file_path)
            # check if dataframe is empty
            if len(dataframes) < 1:
                st.error('Please upload an image with a table.', icon="🚨")

            else:
               for i in range(len(dataframes)):
                    # if dataframe is not empty (manage to extract some things out)
                    st.subheader('Extracted Table 1')
                    option = st.selectbox('Select a Financial Statement:', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), key=str(i))
                    dataframes[i].to_excel(file_name + ".xlsx")
                    num_format = get_number_format(file_name + ".xlsx")
                    new_num_list = sort_num_list(num_format)
                    selected = st.selectbox("Number Format:", new_num_list, key="x" + str(i))
                    
                    AgGrid(dataframes[i], editable=True)

# no files was uploaded
else:
    st.error('Please upload a file for extraction.', icon="🚨")
