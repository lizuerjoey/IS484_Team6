import streamlit as st
# import camelot.io as camelot
import camelot
import PyPDF2
import os
import base64
from datetime import datetime
from streamlit import session_state
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import glob
import pandas as pd
from openpyxl import load_workbook
import shutil
from request import (
        get_symbols,
        add_company,
        add_file,
        get_financial_words_col,
        get_financial_words_row,
        get_json_financial_format,
        get_json_format
    )
from extraction.pdf_to_image import (convert_file)
from extraction.aws_image import (image_extraction)

# Initialization
if 'pg_input' not in session_state:
    session_state['pg_input'] = ''

if 'status' not in session_state:
    session_state['status'] = False

if 'uploaded_file' not in session_state:
    session_state['uploaded_file'] = ''

currency = ""
fiscal_month = ""
confirm_headers_list = []
confirm_rows_list = []
financial_format =[]
number_format = []
dataframe_list = []
is_df_empty_list = []
button_clicked = False

if 'dataframes' not in session_state:
    session_state['dataframes'] = []

if 'column_input' not in st.session_state:
    st.session_state['column_input'] = False

if 'column_del' not in st.session_state:
    st.session_state['column_del'] = False

if "upload_file_status" not in st.session_state:
    session_state['upload_file_status'] = True

# re-initalise again to update previous false
session_state['upload_file_status'] = True

if ("com_name" and "selected_comName" and "com_id" and "selected_comID") not in st.session_state:
    st.session_state['com_name'] = ""
    st.session_state['com_id'] = ""
    st.session_state['selected_comName'] = ""
    session_state['selected_comID'] = ""
    session_state['upload_file_status'] = False
    st.error("No file was uploaded", icon="🚨")

if "text_option" not in st.session_state:
    session_state['text_option'] = False

# retrieve from upload files page
com_name = session_state["com_name"]
com_id = session_state["com_id"]
selected_comName = session_state["selected_comName"]
selected_comID = session_state["selected_comID"]

temp_path = "./temp_files"
dir = os.listdir(temp_path)

# check if file was uploaded
if st.session_state['text_option'] == True and session_state['upload_file_status'] and len(dir) > 1:
    st.header(com_name)
else:
    st.header(selected_comName)

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
    return tables

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

def list_all_lower(my_list):
    return [x.lower() for x in my_list]

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

    # to loop through and search for number format
    df.to_excel("./temp_files/" + str(num) + ".xlsx")    

    # for displaying in aggrid 
    df.to_csv("./temp_files/" + str(num) + ".csv")
    dataframe = pd.read_csv("./temp_files/" + str(num) + ".csv")

    option = ""
    selected = ""

    col1, col2 = st.columns(2)
                       
    c1,c2 = st.columns([3,1])
    with c1:
        st.subheader('Extracted Table ' + str(num+1))

    # check if an empty dataframe is extracted
    if dataframe.empty:
        is_df_empty = True
        is_df_empty_list.append(True)
        df_empty_msg = "Empty dataframe, please upload a pdf with a filled table or Try AWS."
        st.error(df_empty_msg, icon="🚨")
    else:
        is_df_empty = False
        is_df_empty_list.append(False)
        
        col1, col2 = st.columns(2)

        # financial statement ddl
        with col1:
            option = st.selectbox('Select a Financial Statement:', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), key=id+str(num))
            
            if option != "Not Selected":
                financial_format.append(option)
            else:
                st.warning("Financial Statement is a required field", icon="⭐")
        
        # number format ddl
        with col2:
            num_format = get_number_format("./temp_files/" + str(num) + ".xlsx")
            new_num_list = sort_num_list(num_format)
            options = list(range(len(new_num_list)))
            i = st.selectbox("Number Format:", options, format_func=lambda x: new_num_list[int(x)], key="format -" + id + str(num))
            if new_num_list[i] != "Unable to Determine":
                number_format.append(new_num_list[i])
            else:
                st.warning("Number Format is a required field.", icon="⭐")
        
        st.subheader("Edit Headers")

        col1, col2 = st.columns(2)

        with col1:
            options = st.multiselect('Select Columns to Delete:', list(dataframe.columns), key="coldelete -" + id + str(num))
            st.session_state['column_del'] = True
                
            for col_option in options:
                dataframe.drop(col_option, axis=1, inplace=True)

                
        with col2:
            renamecol_tooltip = "Column headers must be unique and strictly years or years+quarters. For yearly statements, you can rename columns which falls under a specified year as 2020_1, 2020_2 etc. For quarterly statements, you can rename the headers as 2020 Q1, 2020 Q2 etc. If there are other columns which falls under 2020 Q1 for instance, you can rename it as 2020 Q1_1"
            options = st.multiselect('Select Column Header(s) to Rename:', list(dataframe.columns), help=renamecol_tooltip, key="colrename -" + id + str(num))
            
            for i in range(len(options)):
                old_name = options[i]
                column_name = st.text_input("Enter New Header Name for "+ str(options[i]), value=options[i], key="table -" + str(num) + str(i))
                st.session_state['column_input'] = True
                
                if column_name in (dataframe.columns) and old_name !=column_name:
                    st.error("Header name already exisit. Try a different name")
                else:
                    dataframe.rename(columns = {options[i]: column_name}, inplace = True) 


        # get column headers
        column_headers = list(dataframe.columns)
        confirm_headers_tooltip = "Select the columns with all rows consisting of financial keywords in your word dictionary e.g. Revenue, Liabilities, Operating Net Cash Flow etc."
        confirm_headers = st.multiselect(
        'Select the Column(s) with Financial Statement Keywords:',
        column_headers,
        column_headers[0], help=confirm_headers_tooltip ,key="confirm_headers -" + id + str(num))

        confirm_headers_list.append(confirm_headers)
        
        if len(confirm_headers_list[num]) < 1:
            st.error("You need to select at least 1 column headers", icon="🚨")

        delete_row = JsCode("""
            function(e) {
                let api = e.api;
                let sel = api.getSelectedRows();
                api.applyTransaction({remove: sel})    
            };
            """)  

        string_to_add_row = "\n\n function(e) { \n \
        let api = e.api; \n \
        let rowIndex = e.rowIndex + 1; \n \
        api.applyTransaction({addIndex: rowIndex, add: [{}]}); \n \
            }; \n \n"
        
        cell_button_add = JsCode('''
            class BtnAddCellRenderer {
                init(params) {
                    this.params = params;
                    this.eGui = document.createElement('div');
                    this.eGui.innerHTML = `
                    <span>
                        <style>
                        .btn_add {
                        border: none;
                        color: black;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 10px;
                        font-weight: bold;
                        height: 2.5em;
                        width: 8em;
                        cursor: pointer;
                        }

                        .btn_add :hover {
                        background-color: #05d588;
                        }
                        </style>
                        <button id='click-button' 
                            class="btn_add" 
                            >Add Row Below</button>
                    </span>
                `;
                }

                getGui() {
                    return this.eGui;
                }

            };
            ''')
        
        st.info('To Delete Row(s): Click the checkbox', icon="ℹ️")

        gd = GridOptionsBuilder.from_dataframe(dataframe)
        gd.configure_default_column(editable=True,groupable=True)
        gd.configure_column("", onCellClicked=JsCode(string_to_add_row), cellRenderer=cell_button_add, editable=False, autoHeight=True,lockPosition='left')
        gd.configure_selection(selection_mode= 'multiple', use_checkbox=True)
        gd.configure_grid_options(onRowSelected = delete_row, pre_selected_rows=[])

        gridOptions = gd.build()
        grid_table = AgGrid(dataframe, 
                    gridOptions = gridOptions, 
                    enable_enterprise_modules = True,
                    fit_columns_on_grid_load = True,
                    update_mode = GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
                    editable = True,
                    height= 450,
                    allow_unsafe_jscode=True)    
        
        # st.info("Total Rows :" + str(len(grid_table['data']))) 
        # print("Selected row: " + str(grid_table["selected_rows"]))

        # ----- SAVE EDIT BUTTON HERE -----
        # done_button = st.button("Save Edit", key="done -" + str(num))
        # if done_button:
        new_df = grid_table['data']
        dataframe_list.append(new_df)
        # st.success("Table saved successfully")

        # get updated row id
        row_list = list(new_df.index)
        confirm_rows_tooltip = "Select the rows if there are rows below column headers which consist of text e.g. Total"
        confirm_rows = st.multiselect(
        'Select the Row(s) with Keywords:',
            row_list, help=confirm_rows_tooltip, key="confirm_rows -" + id + str(num))
        confirm_rows_list.append(confirm_rows)

    return (option, selected, is_df_empty)

def total_num_tables(df):
    session_state["total_num_tables"] = len(df)
    return session_state["total_num_tables"]

def extract_tables (tables):
    # CHECK ACCURACY
    accuracy = []
    financial_format = []
    number_format = []
    confirm_headers_list = []
    confirm_rows_list = []
    if len(tables) == 0:
        st.error('Please upload a pdf with a table.', icon="🚨")
    else:
        for i in range(len(tables)):
            accuracy.append(tables[i].parsing_report["accuracy"])
        if (any(i < 75 for i in accuracy)):
            print(accuracy)
            dfs = convert_file()
            for i in range(len(dfs[0])):
                statement, format, is_df_empty = viewer_func(dfs[0][i], i, "pdfimg")
        else:
            for i in range(len(tables)):
                statement, format, is_df_empty = viewer_func(tables[i], i, 'camelot')

def concat_lists(lists):
    result = []
    for items in zip(*lists):
        result.append(" ".join(str(item) for item in items if not pd.isnull(item)))
    return result

def merge_col_cells(confirm_headers_table, table):
    # check each column selected for merged cells
    if colname in confirm_headers_table:
        # check if each cell is blank
        empty = 0
        keyword = 0
        replace_keyword = ""
        index = -1
        colvalues = dataframe_list[table][colname].values
        
        for cell in colvalues:
            index += 1
            
            # first few cells is empty
            if keyword == 0 and (pd.isnull(cell) == True or str(cell) == "None" or str(cell) == " "):
                empty += 1

            # first few cells is empty but a cell with keyword is found
            elif empty > 0 and pd.isnull(cell) == False and str(cell) != "None" and str(cell) != " " and str(cell) != "":
                replace_keyword = str(cell)
                keyword += 1
                empty = 0

            # first cell contains a keyword and not empty
            elif empty == 0 and str(cell) != "None" and str(cell) != " " and str(cell) != "":
                replace_keyword = str(cell)
                keyword += 1

            # check if cell below keyword is another keyword
            elif keyword > 0 and empty == 0:
                # another keyword or edited and became empty string or None                             
                if pd.isnull(cell) == False and str(cell) != "None" and str(cell) != " " and str(cell) != "":
                    keyword += 1
                    replace_keyword = str(cell)
                
                # empty cell
                if str(cell) == "None" or str(cell) == " " or str(cell) == "":
                    colvalues[index] = replace_keyword
        
        new_col_list.append(colvalues)
        
    return new_col_list

def merge_row_cells(confirm_row_table, table):
    # didn't check for empty cells because if it is a merged cell, it will be difficult to fill it horizontally wise                        
    for row_index in confirm_row_table:
        new_row_list.append(list(dataframe_list[table].iloc[row_index]))
    new_row_list.insert(0, list(dataframe_list[table].columns))
    
    big_row = concat_lists(new_row_list)
    return big_row

def remove_space_caps_next_letter(key):
    new_key = "".join(word.capitalize() for word in key.split())
    first_letter = key[0].lower()
    new_key = first_letter + new_key[1:]
    return new_key

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

# make sure a file was being uploaded first
if session_state['upload_file_status'] == True:
    # if temp_files is not empty then extract
    if len(dir) > 1:

        pg_input = session_state.pg_input
        status = session_state.status
        
        file_paths = glob.glob("./temp_files/*")
        count = 0
        for path in file_paths:
            file_type = get_file_type(path)

            # file is pdf
            if file_type == '.pdf':                
                file_path = glob.glob("./temp_files/*.pdf")[0]
                session_state["uploaded_file"] = file_path
                file_name = get_file_name(file_path)
                totalpages = get_total_pgs_PDF(file_path)

                # at least 1 page
                if (totalpages > 0):
                    
                    st.subheader('Basic Form Data')
                    col1, col2 = st.columns(2)
                    
                    # with col1:
                        # currency
                        # currency_list = get_currency_list()
                        # option = st.selectbox('Select a Currency:', currency_list, key="currency_singlepg_pdf")
                        # if option != "Not Selected":
                        #     currency = option
                        # else:
                        #     st.warning("Currency is a required field", icon="⭐")
                    
                    # fiscal month ddl
                    with col2:
                        month_list = list(range(len(month)))
                        selected = st.selectbox("Fiscal Start Month:", month_list, format_func=lambda x: month[int(x)], key="fiscalmnth")
                        if selected != 0:
                            fiscal_month = selected
                        else:
                            st.warning("Fiscal Start Month is a required field.", icon="⭐")

                # single page pdf
                if (totalpages == 1):

                    # try aws button
                    button_clicked = False
                    btn_placeholder = st.empty()
                    with btn_placeholder.container():
                        # if session_state["status"]:
                            if (st.button("Try AWS", key="aws_singlepg_pdf")):
                                origin = './temp_files/'
                                target = './selected_files/'
                                files = os.listdir(origin)
                                files_target = os.listdir(target)
                                for file in files_target:
                                    if file=="file.pdf":
                                        os.remove(target+file)
                                for file in files:
                                    if file!="test.txt" and file.endswith(".pdf"):
                                        file_type = get_file_type(file)
                                        shutil.copy(origin+file, target)
                                        os.rename(target+file, target+"file"+file_type)

                                button_clicked = True
                                btn_placeholder.empty()
                        
                    tables = check_tables_single_PDF(file_path)
                    extraction_container = st.empty()
                    with extraction_container.container():
                        extract_tables(tables)
                
                # multi page pdf
                else:
                    # user input is successful on page 3
                    if (status == True and pg_input != ''):
                        # try aws button 
                        button_clicked = False
                        btn_placeholder = st.empty()
                        with btn_placeholder.container():
                            if session_state["status"]:
                                if (st.button("Try AWS", key="aws_multipg_pdf")):
                                    button_clicked = True
                                    btn_placeholder.empty()

                        tables = check_tables_multi_PDF(file_path, str(pg_input))
                        extraction_container = st.empty()
                        with extraction_container.container():
                            extract_tables(tables)
                        
                    else:
                        if (session_state['upload_file_status'] == True):
                            st.error("Please specify the pages you want to extract.", icon="🚨")
                
                if button_clicked:
                    extraction_container.empty()
                    next_extraction = st.empty()
                    with next_extraction.container():
                        dfs = convert_file()
                        for i in range(len(dfs[0])):
                            statement, format, is_df_empty = viewer_func(dfs[0][i], i, "btnclicked")

            #file is image
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

        # if at least 1 dataframe is not empty
        if False in is_df_empty_list:
            # show extract button
            if st.button("Extract", key="extract"):            
                save_status = False
                total_num_tables = total_num_tables(dataframe_list)
                big_col = []
                big_row = []
                header_big_row = []
                new_col_list = []
                new_row_list = []
                yr_qtr = []
                matched_column_headers = []
                matched_list_row = []
                matched_dict_col = {}

                # below are required fields; if at least one field is not correct -> cannot save to json
                if ((currency == 'Not Selected') or (fiscal_month == 0) or
                    ('Not Selected' in financial_format or len(financial_format) == 0) or 
                    ('Unable to Determine' in number_format or len(number_format) == 0)):
                    save_status = False
                    st.error("Please check the required fields.", icon="🚨")

                # error message
                unnamed_error = []
                nothing_error = []

                # financial statement
                income_statement_json = []
                balance_statement_json = []
                cash_flow_statement_json = []

                # loop through each tables in the dataframe list
                for table in range(total_num_tables):
                    big_col = []
                    big_row = []
                    header_big_row = []
                    new_col_list = []
                    new_row_list = []
                    yr_qtr = []
                    matched_column_headers = []
                    matched_list_row = []
                    matched_dict_col = {}
                    # multiple selected headers
                    if len(confirm_headers_list[table]) > 1:
                        for colname in dataframe_list[table]:                                                           
                            new_col_list = merge_col_cells(confirm_headers_list[table], table)
                        
                        # merge the text in each column into one big column
                        new_col_list.insert(0, dataframe_list[table].index)
                        big_col = concat_lists(new_col_list)
                            
                    # single header
                    elif len(confirm_headers_list[table]) == 1:
                        # return just the confirmed header
                        confirmed_header = confirm_headers_list[table][0]
                        new_col_list.append(dataframe_list[table][confirmed_header])
                        new_col_list.insert(0, dataframe_list[table].index)
                        big_col = concat_lists(new_col_list)

                    # no header selected (at least 1 header is required)
                    else:
                        save_status = False

                    # more than 1 selected rows
                    if len(confirm_rows_list[table]) > 0:
                        big_row = merge_row_cells(confirm_rows_list[table], table)
                    
                    # no rows selected -> search through headers
                    else:
                        big_row = list(dataframe_list[table].columns)
                    
                    # search through (col) for financial word
                    if 'Not Selected' not in financial_format and len(financial_format) != 0:
                        col_words = get_financial_words_col(financial_format[table])
                        for item in list_all_lower(big_col):
                            for key, synonyms in col_words.items():
                                if key in item:
                                    if key not in matched_dict_col:
                                        matched_dict_col[key] = []
                                    matched_dict_col[key].append(item)
                                for x in synonyms:
                                    if x.lower() in item:
                                        if key not in matched_dict_col:
                                            matched_dict_col[key] = []
                                        matched_dict_col[key].append(item)

                        # search through (row) for financial word
                        row_words = get_financial_words_row(financial_format[table])
                        for item in big_row:
                            for key, synonyms in row_words.items(): 
                                if key in item.lower():
                                    matched_list_row.append(item)
                                for x in synonyms:
                                    if x.lower() in item.lower():
                                        matched_list_row.append(item)
                
                    # check if matched list row length more than 0
                    if len(matched_list_row) > 0:
                        # found something in row
                        for i in range(len(matched_list_row)):
                            matched_list_row[i] = str(matched_list_row[i]).split()
                        
                        # check whether yearly or quarterly format
                        is_quarterly = False
                        for item in list(dataframe_list[table].columns):
                            if 'q' in item.lower():
                                is_quarterly = True

                        if is_quarterly == False:
                            for i in range(len(matched_list_row)):
                                matched_column_headers.append(matched_list_row[i][0])
                        else:
                            for i in range(len(matched_list_row)):
                                join_year_qtr = str(matched_list_row[i][0]) + " " + (str(matched_list_row[i][1]))
                                matched_column_headers.append(join_year_qtr)
                        
                    else:
                        # no keywords found, will take the values of year and quarter e.g. 2020 or 2020 Q1
                        # st.info("Unable to locate keywords (e.g. Total) in the headers or rows selected", icon="ℹ️")
                        # get the years/ quarters in the statement
                        for colname in dataframe_list[table]:
                            if colname not in confirm_headers_list[table]:
                                # year
                                if ("_" not in colname) and ("Unnamed:" not in colname) and (len(colname) == 4):
                                    yr_qtr.append(colname)
                                # quarter; assuming there are only 4 quarters so len will always be 7 e.g. 2020 Q1 never 2020 Q11
                                if ('q' in colname.lower()) and ("_" not in colname) and ("Unnamed:" not in colname) and (len(colname) == 7):
                                    yr_qtr.append(colname)
                        matched_column_headers = yr_qtr

                    # using col headers and row id -> identify the cell and append to the col financial keyword
                    # if len of each keyword has more than 1 result -> take the first result
                    result_dict = {}
                    is_unnamed = False
                    for date in matched_column_headers:
                        if "_" in date:
                            year_quarter, parts = date.split("_")
                        else:
                            # check if it is unnamed
                            # unnamed cannot be used as a column header, because even if retrieved the value what year/ month am I going to store it by
                            if "unnamed" in date:
                                is_unnamed = True
                            year_quarter = date
                        
                        if year_quarter not in result_dict:
                            result_dict[year_quarter] = {}

                        for key, values in matched_dict_col.items():
                            # always take the first result in for the each financial keyword
                            row_id = values[0]

                            # last row id of the table
                            last_row_id = dataframe_list[table].last_valid_index() 

                            # if row_id is not numeric or the length of the row_id is more than the total row_id of the table -> high chance is a string
                            if row_id.isnumeric() == False or len(row_id) > last_row_id:
                                row_id = int(row_id.split()[0])
                            
                            # save only financial key to dictionary and make sure the date exist in the column headers before extracting
                            if "unnamed" not in date and date in list(dataframe_list[table].columns):                     
                                cell = dataframe_list[table].loc[row_id][str(date)]
                                if key in result_dict[year_quarter]:
                                    # check if space -> get the index and capitalise the next letter
                                    new_key = remove_space_caps_next_letter(key)
                                    result_dict[year_quarter][new_key].append(cell)
                                else:
                                    new_key = remove_space_caps_next_letter(key)
                                    result_dict[year_quarter][new_key] = [cell]                               

 
                    # saving data in json when there is extracted header values e.g. year/ quarter
                    unnamed_error.append(is_unnamed)
                    extracted_nothing = False
                    # result_dict
                    if len(result_dict) > 0:
                        for yr_qtr, fin_words in result_dict.items():
                            # saving data in json when there is extracted cell values
                            if len(result_dict[yr_qtr]) > 0:

                                # save basic format
                                basic_format = get_json_format()
                                basic_format["currency"] = currency[0:3]
                                basic_format["fiscal_start_month"] = fiscal_month

                                # save per financial statement
                                financial_statement = financial_format[table].lower().replace(" ", "_")
                                
                                # for each year/ qtr
                                # result_dict
                                for keyword in result_dict[yr_qtr]:
                                    
                                    financial_statement_format = get_json_financial_format(financial_statement)
                                    
                                    # loop through the list of financial words retrieved from table and append it to json format
                                    for format_words in financial_statement_format:
                                        if format_words == "year":
                                            financial_statement_format[format_words] = yr_qtr

                                        elif format_words == "numberFormat":
                                            financial_statement_format[format_words] = number_format[table]

                                        elif keyword == format_words:
                                            financial_statement_format[keyword] = fin_words[keyword][0]
                                
                                income_statement_json.append(financial_statement_format)
                            
                            else:
                                extracted_nothing = True
                                nothing_error.append(True)

                                                        
                income_statement_json

                # append json and check if exist (if same sheet) or not

                basic_format

                # display error msg outside of table loop
                # unnamed_error
                # nothing_error
                # st.info("You might want to rename the unnamed columns to either a year or quarter for it to be saved.", icon="ℹ️")
                # st.error("Nothing was extracted. Please check financial words dictionary or your table values and try again.", icon="🚨")

                            
                    
                    # single selected header
                    # else:
                    #     st.write("single")
                    # for column in range(len(confirm_headers_list[table])):
                    #     st.write(confirm_headers_list[table][column])

                
            # # Save into DB
            # if session_state["text_option"] == True:
            #     if st.button('Submit'):
            #         if com_name:
            #             add_com = add_company(com_id, com_name)
            #             if (add_com["message"] == "Added"):
            #                 st.success("Company Added", icon="✅")
            #                 save_file(com_id, session_state["uploaded_file"], com_name)
            #             else:
            #                 st.error('Error adding company. Please try again later', icon="🚨")
            #         else:
            #             # If company name not entered
            #             st.error("Please enter a company name in Upload Report Page", icon="🚨")
            # else:
            #     if st.button('Submit'):
            #         save_file(selected_comID, session_state["uploaded_file"], selected_comName)

    # no files was uploaded
    else:
        st.error('Please upload a file for extraction.', icon="🚨")