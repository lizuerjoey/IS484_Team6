import streamlit as st
from streamlit import session_state
import os
import shutil
from pages.page_4 import (
    get_file_type,
    viewer_func,
    get_currency_list,
)
from extraction.pdf_to_image import (convert_file)
from extraction.saving import (save_json_to_db)
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
if "text_option" not in st.session_state:
    session_state['text_option'] = False

if "upload_file_status" not in st.session_state:
    session_state['upload_file_status'] = True

if "extract_state_aws" not in session_state:
    session_state["extract_state_aws"] = False
    
if ("com_name" and "selected_comName" and "com_id" and "selected_comID") not in st.session_state:
    st.session_state['com_name'] = ""
    st.session_state['com_id'] = ""
    st.session_state['selected_comName'] = ""
    session_state['selected_comID'] = ""

# retrieve from upload files page
com_name = session_state["com_name"]
com_id = session_state["com_id"]
selected_comName = session_state["selected_comName"]
selected_comID = session_state["selected_comID"]

origin = './temp_files/'
target = './selected_files/'
files = os.listdir(origin)
files_target = os.listdir(target)

if "selected_pages.pdf" not in files and "file.pdf" not in files_target:
    for file in files:
        if file!="test.txt" and file.endswith(".pdf"):
            file_type = get_file_type(file)
            shutil.copy(origin+file, target)
            os.rename(target+file, target+"file"+file_type)

selected_path = "./selected_files"
dir2 = os.listdir(selected_path)


if "selected_pages.pdf" in files or "file.pdf" in files_target or len(dir2) > 1:
    
    # check if file was uploaded
    if st.session_state['text_option'] == True and session_state['upload_file_status']:
        st.header(com_name)
    else:
        st.header(selected_comName)
    fiscal_month = 0

    st.subheader('Basic Form Data')
    col1, col2 = st.columns(2)

    currency = ""
    with col1:
        currency_list = get_currency_list()
        option = st.selectbox('Select a Currency:', currency_list, key="currency_singlepg_pdf")
        if option != "Not Selected":
            currency = option
        else:
            st.warning("Currency is a required field", icon="⭐")

    with col2:
        month_list = list(range(len(month)))
        selected = st.selectbox("Fiscal Start Month:", month_list, format_func=lambda x: month[int(x)], key="fiscalmnth")
        if selected != 0:
            fiscal_month = selected
        else:
            st.warning("Fiscal Start Month is a required field.", icon="⭐")

    dfs = convert_file()
    dataframe_list = []
    search_col_list_check = []
    confirm_search_col_list = []
    is_df_empty_list = []
    confirm_headers_list = []
    num_format_list = []
    check_format = ""
    financial_format = []
    num_format = ""
    delete_list = []

    # image_viewer(dfs)
    for i in range(len(dfs)):
        new_df, statement, format, is_df_empty, search_col_check, confirm_headers, search_col, delete = viewer_func(dfs[i], i, "btnclicked", num_format, "pdfimg")
        num_format = format
        search_col_list_check=search_col_check
        if not delete:
            financial_format.append(statement)
            dataframe_list.append(new_df)
            confirm_search_col_list+=search_col
            is_df_empty_list.append(is_df_empty)
            confirm_headers_list.append(confirm_headers)
            num_format_list.append(format)
        else:
            delete_list.append(i+1)


    # all tables were selected to not be extracted
    if (len(is_df_empty_list) == 0):
        st.error("No tables were selected for extraction, please check your delete tables selection.", icon="🚨")

    if False in is_df_empty_list:
        if st.button("Extract", key="extract") or session_state["extract_state_aws"]:
            # save extract button session
            session_state["extract_state_aws"] = True
            save_json_to_db(dataframe_list, search_col_list_check, currency, fiscal_month, financial_format, num_format_list, confirm_headers_list, confirm_search_col_list, delete_list)                        


else:
    st.error('Please upload a file for extraction.', icon="🚨")