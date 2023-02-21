import streamlit as st
import pandas as pd
import os
import hashlib
import random
import PyPDF2
import glob
from streamlit_extras.switch_page_button import switch_page
from request import(
    get_all_companies,
) 

# Get file type
def get_file_type (file):
    filetype = os.path.splitext(file)[1]
    return filetype

st.header("Upload Reports")

################## Company Name
get_options = get_all_companies()["data"]

# Initialization
if 'text_option' not in st.session_state:
    st.session_state['text_option'] = False

if 'disable_dropdown' not in st.session_state:
    st.session_state['disable_dropdown'] = False

if 'disable_btn' not in st.session_state:
    st.session_state['disable_btn'] = False    

## -- input new company name -- ##
if 'com_name' not in st.session_state:
    st.session_state['com_name'] = ""

if 'com_id' not in st.session_state:
    st.session_state['com_id'] = ""

## -- choose from dropdown list -- ##
if 'selected_comName' not in st.session_state:
    st.session_state['selected_comName'] = ""

if 'selected_comID' not in st.session_state:
    st.session_state['selected_comID'] = ""


if len(get_options) == 0:
    st.session_state['text_option'] = True

elif len(get_options) > 0:
    options = list(range(len(get_options)))
    st.text("Company Name: ")
    col1, col2 = st.columns([10,2])
    with col1:
        placeholder = st.empty()
        option = placeholder.selectbox(
            'Company Name',
            options, format_func=lambda x: get_options[x][1], disabled=st.session_state['disable_dropdown'], label_visibility="collapsed")
    with col2:
        # Disable 'Add New' button
        btn_placeholder = st.empty()
        if btn_placeholder.button('Add New'):
            st.session_state['disable_btn'] = True
            btn_placeholder.button('Add New', key="disabled_btn", disabled=st.session_state['disable_btn'])
            st.session_state['disable_dropdown'] = True

        # Disable Dropdown 
        if st.session_state['disable_dropdown'] == True:
            st.session_state['text_option'] = True
            option = placeholder.selectbox(
            'Company Name',
            options, key="disabled_select", format_func=lambda x: get_options[x][1], disabled=st.session_state['disable_dropdown'], label_visibility="collapsed")

    if st.session_state['text_option'] == False:
        # Get Selected Company ID    
        selected_comID = get_options[option][0]
        selected_comName = get_options[option][1]
        st.session_state['selected_comName'] = selected_comName
        st.session_state['selected_comID'] = selected_comID

# Get Company Name Initial
def initials(full_name):
    if (len(full_name) == 0):
      return
   
    initial  = ''.join([name[0].upper()for name in full_name.split(' ')])
    return initial
               
if st.session_state['text_option'] == True:
    
    if len(get_options) > 0:
        
        col1, col2 = st.columns([10,2])
        with col1:
            com_name = st.text_input(
                "Company Name:",
                placeholder = "Enter Company Name",
                key="col1",
                label_visibility="collapsed"
            )
        with col2:
            if st.button(':heavy_multiplication_x:'):
                if st.session_state['disable_dropdown']:
                    st.session_state['disable_dropdown'] = False
                    st.session_state['text_option'] = False
                    st.experimental_rerun()
    else:
        com_name = st.text_input(
            "Company Name:",
            placeholder = "Enter Company Name",
            key="col12",
            label_visibility="collapsed"
        )
        
    # Get Company Name
    # print(com_name)
    if com_name:
        # Save Company Name
        st.session_state['com_name'] = com_name

        # Generate Company ID
        my_hash = hashlib.md5(com_name.encode('utf-8')).hexdigest()
        length = len(my_hash)
        com_ID = initials(com_name) + "-"
        for i in range(4):
            rad_num = random.randint(0,length-1)
            com_ID += my_hash[rad_num] 
        
        st.session_state['com_id'] = com_ID    
        # print(com_ID)

# else:
#     print(selected_comID)

#################### Upload File
uploaded_file = st.file_uploader("Choose a file", label_visibility="collapsed")

def save_file_to_temp (uploaded_file): 
    # Upload into directory
    with open(os.path.join("temp_files",uploaded_file.name),"wb") as f: 
        f.write(uploaded_file.getbuffer())   

if uploaded_file is not None:
    # File Size limit
    limit = 2*(10**9)
    # Check file type
    position = uploaded_file.type.find("/")
    file_type = uploaded_file.type[position+1: ]
    # Accepted File Type
    supported_file_type=["pdf", "png", "jpg", "jpeg"]

    # Check if the temp folder is empty
    temp_path = "./temp_files"
    dir = os.listdir(temp_path)

    if (file_type not in supported_file_type):
        st.error("Unsupported File Type", icon="🚨")
    # Check file size
    elif (uploaded_file.size>limit):
        st.error("File Size more than 200MB", icon="🚨")
    else:
        if len(dir) > 0:
            for f in os.listdir(temp_path):
                if (f != "test.txt"):
                    os.remove(os.path.join(temp_path, f))
        save_file_to_temp(uploaded_file)
    
    # Check if user uploaded a file into temp files
    if len(dir) > 1:
        # Check if file type uploaded to temp files is a PDF
        file_paths = glob.glob("./temp_files/*")
        count = 0
        txtcount = 0
        for path in file_paths:
            file_type = get_file_type(path)

            if file_type == '.pdf':
                file_path = glob.glob("./temp_files/*.pdf")[0]
                pdfReader = PyPDF2.PdfReader(file_path)
                totalpages = len(pdfReader.pages)
                
                if totalpages > 1:
                    # uploaded file is multi pdf -> select
                    multipgpdf = st.button("Select Pages (PDF)", key="multipgpdf")
                    if multipgpdf:
                        switch_page("select pages (pdf)")
                else:
                    # uploaded file is single pg -> preview
                    previewpdf = st.button("Preview Extracted Data", key="previewpdf")
                    if previewpdf:
                        switch_page("preview extracted data")
            
            
            elif (file_type == '.png' or file_type == '.jpg' or file_type == '.jpeg') and not (uploaded_file.name.endswith('.csv') or uploaded_file.name.endswith('.xlsx')):
                st.write(uploaded_file.name.endswith('.csv')) 
                previewimg = st.button("Preview Extracted Data", key="previewimg")
                if previewimg:
                    switch_page("preview extracted data")                

############## CSS
st.markdown("""
    <style>

    div > div:nth-child(5) > div > button,  div > div:nth-child(4) > div > button
    {
        float: right;
    }

    </style>
""", unsafe_allow_html=True)