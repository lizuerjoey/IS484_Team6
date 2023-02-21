import streamlit as st
# import camelot.io as camelot
import camelot
import PyPDF2
import os
import base64
from datetime import datetime
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import glob
import pandas as pd
from openpyxl import load_workbook
from request import (
        get_symbols,
        add_company,
        add_file,
    )
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

month = [
            "Not Selected",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
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

def get_currency_list():
    currency_acronyms = []
    symbols = get_symbols()
    for key in symbols:
        currency_acronyms.append(key + " (" + symbols[key] + ")")
    currency_acronyms.insert(0, "Not Selected")
    return currency_acronyms

def viewer_func(df, num, id):
    st.subheader('Extracted Table ' + str(num+1))

    # financial statement ddl
    option = st.selectbox('Select a Financial Statement:', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), key=id+str(num))

    df.to_excel("./temp_files/" + str(num) + ".xlsx")     
    num_format = get_number_format("./temp_files/" + str(num) + ".xlsx")

    col1, col2 = st.columns(2)

    # number format ddl
    with col1:
        new_num_list = sort_num_list(num_format)
        selected = st.selectbox("Number Format:", new_num_list, key="format -" + id + str(num))

    # fiscal month ddl
    with col2:
        selected = st.selectbox("Fiscal Month:", month, key="fiscalmnth -" + id + str(num))

    df.to_csv("./temp_files/" + str(num) + ".csv")
    dataframe = pd.read_csv("./temp_files/" + str(num) + ".csv")

    edit_table = st.checkbox("Edit Table", key="table -" + str(num))

    if edit_table:
        st.subheader("Edit Headers")
        st.caption("Enter new header name below:")

        col1, col2 = st.columns(2)

        col_index = 0
        for col in dataframe.columns:
            if col_index % 2 == 0:
                with col1:
                    column_name = st.text_input("Column", label_visibility="hidden", placeholder= col, key="table -" + str(num) + str(col_index))
                    delete_column = st.checkbox("Delete column", key="table -" + str(num) + " column -" +str(col_index))

                    # EDIT COL NAME
                    if column_name == "":
                        print(col)
                    else:
                        print(column_name)
                        dataframe.rename(columns = {col: column_name}, inplace = True) 

                    # DELETE COL
                    if delete_column:
                        dataframe.drop(col, axis=1, inplace = True)
                    
                    col_index +=1
            else:
                with col2:
                    column_name = st.text_input("Column", label_visibility="hidden", placeholder= col, key="table -" + str(num) + str(col_index))
                    delete_column = st.checkbox("Delete column", key="table -" + str(num) + " column -" +str(col_index))
                    
                    # EDIT COL NAME
                    if column_name == "":
                        print(col)
                    else:
                        print(column_name)
                        dataframe.rename(columns = {col: column_name}, inplace = True) 
                    
                    # DELETE COL
                    if delete_column:
                        dataframe.drop(col, axis=1, inplace = True)
                    
                    col_index +=1
                        
    is_df_empty = True
    if dataframe.empty:
        is_df_empty = True
    else:
        gd = GridOptionsBuilder.from_dataframe(dataframe)
        gd.configure_pagination(enabled=True)
        gd.configure_default_column(editable=True, groupable=True)
        #gd.configure_selection(selection_mode= 'multiple', use_checkbox=True)

        gridoptions = gd.build()
        #grid_table = AgGrid(dataframe, editable=True, gridOptions=gridoptions, update_mode=GridUpdateMode.SELECTION_CHANGED)
        AgGrid(dataframe, editable=True, gridOptions=gridoptions)

        # DELETE ROW 
        #selected_rows = grid_table['selected_rows']
        #st.write(selected_rows)
        # if selected_rows:
        #     selected_indices = [i['_selectedRowNodeInfo']
        #                         ['nodeRowIndex'] for i in selected_rows]
        #     #df_indices = st.session_state.df_for_grid.index[selected_indices]
        #     print("Row_index:" + str(selected_indices))

        #     drop_row_list = []
        #     for i in selected_indices:
        #         print("Row index " + str(i))
        #         drop_row_list.append(dataframe.index(i))

        #     dataframe = dataframe.drop(selected_indices, inplace=True, axis=0)

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
    print(is_df_empty) 
    print(accuracy)

def save_file (ID, uploaded_file, com_name):
    now = datetime.now()
    date_time = str(now.strftime("%d%m%Y%H%M%S"))

    # Upload into directory
    with open(os.path.join("upload_files",uploaded_file.name),"wb") as f: 
        f.write(uploaded_file.getbuffer())   

    # Change file name to directory before saving into DB
    old_path = os.path.join("upload_files",uploaded_file.name)
    new_file_name = com_name.replace(" ", "") +"_" + date_time +"_" + uploaded_file.name
    new_path = os.path.join("upload_files",new_file_name)
    os.rename(old_path, new_path)

    # Encode file details before saving in the database
    new_file_name = base64.b64encode(new_file_name.encode("ascii")).decode("ascii")

    # Call API
    add_com = add_file(ID, new_file_name, file_type)
    
    if (add_com["message"] == "Added"):
        st.success("Saved File", icon="✅")
    else:
        st.error('Error adding file. Please try again later', icon="🚨")

# Initialization
if 'pg_input' not in st.session_state:
    st.session_state['pg_input'] = ''

if 'status' not in st.session_state:
    st.session_state['status'] = False

if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = ''

com_name = st.session_state["com_name"]
com_id = st.session_state["com_id"]
selected_comName = st.session_state["selected_comName"]
selected_comID = st.session_state["selected_comID"]

if st.session_state["text_option"] == True:
    st.header(com_name)
else:
    st.header(selected_comName)

temp_path = "./temp_files"
dir = os.listdir(temp_path)

# if temp_files is not empty then extract
if len(dir) > 1:

    pg_input = st.session_state.pg_input
    status = st.session_state.status
    
    if (status == True and pg_input != ''):
        st.subheader('Currency')
        # currency
        currency_list = get_currency_list()
        option = st.selectbox('Select a Currency:', currency_list, key="currency")
    
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
            st.session_state["uploaded_file"] = file_path
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
                        print(is_df_empty)

    # # Save into DB
    # if st.session_state["text_option"] == True:
    #     if st.button('Submit'):
    #         if com_name:
    #             add_com = add_company(com_id, com_name)
    #             if (add_com["message"] == "Added"):
    #                 st.success("Company Added", icon="✅")
    #                 save_file(com_id, st.session_state["uploaded_file"], com_name)
    #             else:
    #                 st.error('Error adding company. Please try again later', icon="🚨")
    #         else:
    #             # If company name not entered
    #             st.error("Please enter a company name in Upload Report Page", icon="🚨")
    # else:
    #     if st.button('Submit'):
    #         save_file(selected_comID, st.session_state["uploaded_file"], selected_comName)

# no files was uploaded
else:
    st.error('Please upload a file for extraction.', icon="🚨")
