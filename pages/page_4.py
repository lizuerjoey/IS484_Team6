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

def viewer_func(df, num, id):
    st.subheader('Extracted Table ' + str(num+1))
    option = st.selectbox('Select a Financial Statement:', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), key=id+str(num))

    df.to_excel("./temp_files/" + str(num) + ".xlsx")     
    num_format = get_number_format("./temp_files/" + str(num) + ".xlsx")

    new_num_list = sort_num_list(num_format)
    selected = st.selectbox("Number Format:", new_num_list, key="format -" + id + str(num))

    df.to_csv("./temp_files/" + str(num) + ".csv")
    dataframe = pd.read_csv("./temp_files/" + str(num) + ".csv")
    
    is_df_empty = True
    if dataframe.empty:
        is_df_empty = True
    else:
        AgGrid(dataframe, editable=True)

    return (option, selected, is_df_empty)


def extract_tables (tables):
    # CHECK ACCURACY
    accuracy = []
    for i in range(len(tables)):
        accuracy.append(tables[i].parsing_report["accuracy"])
    if (any(i < 75 for i in accuracy)):
        print(accuracy)
        dfs = convert_file()
        for i in range(len(dfs)):
            statement, format, is_df_empty = viewer_func(dfs[i][0], i, "pdfimg")
    else:
        for i in range(len(tables)):
            statement, format, is_df_empty = viewer_func(tables[i], i, 'camelot')
    print(statement)
    print(format) 
    print (is_df_empty) 
    print(accuracy)

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
            button_clicked = False
            btn_placeholder = st.empty()
            with btn_placeholder.container():
                if st.session_state["status"]:
                    if (st.button("Try AWS")):
                        button_clicked = True
                        btn_placeholder.empty()
                
            file_path = glob.glob("./temp_files/*.pdf")[0]
            file_name = get_file_name(file_path)
            totalpages = get_total_pgs_PDF(file_path)

            # single page pdf
            if (totalpages == 1):
                tables = check_tables_single_PDF(file_path)
                extraction_container = st.empty()
                with extraction_container.container():
                    extract_tables(tables)
            
            # multi page pdf
            else:
                pg_input = st.session_state.pg_input
                status = st.session_state.status

                # user input is successful on page 3
                if (status == True and pg_input != ''):
                    tables = check_tables_multi_PDF(file_path, str(pg_input))
                    extraction_container = st.empty()
                    with extraction_container.container():
                        extract_tables(tables)
                    
                else:
                    st.error("Please specify the pages you want to extract.", icon="🚨")
            if button_clicked:
                extraction_container.empty()
                next_extraction = st.empty()
                with next_extraction.container():
                    dfs = convert_file()
                    for i in range(len(dfs)):
                        statement, format, is_df_empty = viewer_func(dfs[i][0], i, "btnclicked")

        # file is image
        elif file_type == '.png' or file_type == '.jpg' or file_type == '.jpeg' and file_type != '.txt':
            file_path = glob.glob("./temp_files/*" + file_type)[0]
            file_name = get_file_name(file_path)

    
            dataframes = image_extraction(file_path)
            # check if dataframe is empty
            if len(dataframes) < 1:
                st.error('Please upload an image with a table.', icon="🚨")

            else:
                extraction_container = st.empty()
                with extraction_container.container():
                    for i in range(len(dataframes)):
                        # if dataframe is not empty (manage to extract some things out)        
                        statement, format, is_df_empty = viewer_func(dataframes[i], i, 'img') 
                        print(statement)
                        print(format) 
                        print (is_df_empty)

# no files was uploaded
else:
    st.error('Please upload a file for extraction.', icon="🚨")
