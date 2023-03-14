import streamlit as st
from streamlit import session_state
import os
import shutil
from pages.page_4 import (
    get_file_type,
    viewer_func,
    get_currency_list
)
from extraction.pdf_to_image import (convert_file)
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

# check if file was uploaded
if st.session_state['text_option'] == True and session_state['upload_file_status']:
    st.header(com_name)
else:
    st.header(selected_comName)

st.subheader('Basic Form Data')
col1, col2 = st.columns(2)

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


origin = './temp_files/'
target = './selected_files/'
files = os.listdir(origin)
files_target = os.listdir(target)
for file in files_target:
    if file=="file.pdf":
        os.remove(target+file)

if "selected_pages.pdf" not in files and "file.pdf" not in files_target:
    for file in files:
        if file!="test.txt" and file.endswith(".pdf"):
            file_type = get_file_type(file)
            shutil.copy(origin+file, target)
            os.rename(target+file, target+"file"+file_type)
dfs = convert_file()
for i in range(len(dfs)):
    # Check dfs[i][0] or dfs[0][i]
    statement, format, is_df_empty = viewer_func(dfs[i][0], i, "btnclicked")
