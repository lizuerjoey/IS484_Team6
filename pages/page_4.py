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
from request import (
        get_symbols,
        add_company,
        add_file,
        get_financial_words
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

if 'financial_format' not in session_state:
    session_state['financial_format'] = []

if 'number_format' not in session_state:
    session_state['number_format'] = []

if 'fiscal_month' not in session_state:
    session_state['fiscal_month'] = []

currency = ""
confirm_headers_list = []
dataframe_list = []
is_df_empty = []
button_clicked = False

if 'dataframes' not in session_state:
    session_state['dataframes'] = []

if 'column_input' not in st.session_state:
    st.session_state['column_input'] = False

if 'column_del' not in st.session_state:
    st.session_state['column_del'] = False

com_name = session_state["com_name"]
com_id = session_state["com_id"]
selected_comName = session_state["selected_comName"]
selected_comID = session_state["selected_comID"]

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

    c1,c2 = st.columns([3,1])
    with c1:
        st.subheader('Extracted Table ' + str(num+1))

    # check if an empty dataframe is extracted
    if dataframe.empty:
        is_df_empty.append(True)
        df_empty_msg = "Empty dataframe, please upload a pdf with a filled table or Try AWS."
        st.error(df_empty_msg, icon="🚨")
    else:
        is_df_empty.append(False)
        
        # with c2:
        #     delete_table = st.button("🗑", key="trash -" + str(num))

        # if delete_table:
        #     st.success("Table successfully deleted")
        
        # financial statement ddl
        option = st.selectbox('Select a Financial Statement:', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), key=id+str(num))
        
        if option != "Not Selected":
            session_state['financial_format'].append(option)

        num_format = get_number_format("./temp_files/" + str(num) + ".xlsx")

        col1, col2 = st.columns(2)

        # number format ddl
        with col1:
            new_num_list = sort_num_list(num_format)
            options = list(range(len(new_num_list)))
            i = st.selectbox("Number Format:", options, format_func=lambda x: new_num_list[int(x)], key="format -" + id + str(num))
            if new_num_list[i] != "Unable to Determine":
                session_state['number_format'].append(new_num_list[i])

        # fiscal month ddl
        with col2:
            selected = st.selectbox("Fiscal Month:", month, key="fiscalmnth -" + id + str(num))
            if selected != "Not Selected":
                session_state['fiscal_month'].append(selected)
        
        st.subheader("Edit Headers")

        col1, col2 = st.columns(2)
                
        with col1:
            options = st.multiselect('Select Columns to Delete:',
            list(dataframe.columns),
            )
            st.session_state['column_del'] = True
                
            for col_option in options:
                dataframe.drop(col_option, axis=1, inplace=True)
                
            # st.write('You selected:', options)
            #st.write("existing: ",list(dataframe.columns))
                
        with col2:
            options = st.multiselect('Select Column Header(s) to Rename:', list(dataframe.columns))

            for i in range(len(options)):
                column_name = st.text_input("Enter New Header Name for "+ str(options[i]), placeholder= options[i], key="table -" + str(num) + str(i))
                st.session_state['column_input'] = True

                dataframe.rename(columns = {options[i]: column_name}, inplace = True) 

        # st.write('You selected:', options)
        #st.write("existing: ",list(dataframe.columns))

        # get column headers
        column_headers = list(dataframe.columns)

        confirm_headers_tooltip = "Select the columns with all rows consisting of financial keywords in your word dictionary e.g. Revenue, Liabilities, Operating Net Cash Flow etc."
        confirm_headers = st.multiselect(
        'Select the Column(s) with Financial Statement Keywords:',
        column_headers,
        column_headers[0], help=confirm_headers_tooltip ,key="confirm_headers -" + str(num))

        confirm_headers_list.append(confirm_headers)


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
        confirm_rows_tooltip = "Select the rows if there are rows below column headers which consist of text e.g. 1Q, 1st Half, Total etc."
        confirm_rows = st.multiselect(
        'Select the Row(s) with Keywords:',
            row_list, help=confirm_rows_tooltip, key="confirm_rows -" + str(num))

    return (option, selected, is_df_empty)

def total_num_tables(df):
    session_state["total_num_tables"] = len(df)
    return session_state["total_num_tables"]

def extract_tables (tables):
    # CHECK ACCURACY
    accuracy = []
    session_state['financial_format'] = []
    session_state['number_format'] = []
    session_state['fiscal_month'] = []
    confirm_headers_list = []
    if len(tables) == 0:
        st.error('Please upload a pdf with a table.', icon="🚨")
    else:
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

def concat_lists(lists):
    result = []
    for items in zip(*lists):
        result.append(" ".join(str(item) for item in items if not pd.isnull(item)))
    return result

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

if st.session_state["text_option"] == True:
    st.header(com_name)
else:
    st.header(selected_comName)

temp_path = "./temp_files"
dir = os.listdir(temp_path)

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

            # single page pdf
            if (totalpages == 1):

                # currency
                st.subheader('Currency')
                currency_list = get_currency_list()
                option = st.selectbox('Select a Currency:', currency_list, key="currency_singlepg_pdf")
                if option != "Not Selected":
                    currency = option
                
                # try aws button
                button_clicked = False
                btn_placeholder = st.empty()
                with btn_placeholder.container():
                    if session_state["status"]:
                        if (st.button("Try AWS", key="aws_singlepg_pdf")):
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
                    # currency
                    st.subheader('Currency')
                    currency_list = get_currency_list()
                    option = st.selectbox('Select a Currency:', currency_list, key="currency_multipg_pdf")
                    if option != "Not Selected":
                        currency = option

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

    # if at least 1 dataframe is not empty
    if False in is_df_empty:
        # show extract button
        if st.button("Extract", key="extract"):
            st.write(is_df_empty)
            dataframe_list[0]
            # session_state['dataframes']
            # below are required fields --> REMEBER TO CHECK FOR EMPTY
            # st.write(session_state['financial_format'])
            # st.write(session_state['number_format'])
            # st.write(session_state['fiscal_month'])
            # st.write(session_state['currency'])
            

            total_num_tables = total_num_tables(dataframe_list)
            big_col = []
            new_col_list = []
            for table in range(total_num_tables):
                # multiple selected headers
                if len(confirm_headers_list[table]) > 1:
                    
                    # check each column selected for merged cells
                    for colname in dataframe_list[table]:
                        if colname in confirm_headers_list[table]:
                            
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

                        # merge the text in each column into one big column
                        big_col = concat_lists(new_col_list)

                        big_col
        
                        # search through the word dictionary
                        # Retrieve the income statement financial words
                        income_statement_words = get_financial_words("Income Statement")
                        st.write(income_statement_words)


                        
                
                # single selected header
                else:
                    st.write("single")
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