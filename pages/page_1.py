import streamlit as st
import pandas as pd
import os
import hashlib
import random
from request import(
    get_all_companies,
    add_file,
    add_company
)
st.header("Company Name")

################## Company Name
get_options = get_all_companies()["data"]

# Initialization
if 'text_option' not in st.session_state:
    st.session_state['text_option'] = False

if 'disable_dropdown' not in st.session_state:
    st.session_state['disable_dropdown'] = False

if 'disable_btn' not in st.session_state:
    st.session_state['disable_btn'] = False    

if len(get_options) == 0:
    st.session_state['text_option'] = True
else:
    options = list(range(len(get_options)))
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

    # Get Selected Company ID    
    selected_comID = get_options[option][0]
    
# Get Company Name Initial
def initials(full_name):
    if (len(full_name) == 0):
      return
   
    initial  = ''.join([name[0].upper()for name in full_name.split(' ')])
    return initial
               
if st.session_state['text_option'] == True:
    
    if len(get_options) >= 0:
        
        col1, col2 = st.columns([10,2])
        with col1:
            com_name = st.text_input(
                "Company Name:",
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
            key="col12",
            label_visibility="collapsed"
        )
        
    # Get Company Name
    st.write(com_name)
    if com_name:
        # Generate Company ID
        my_hash = hashlib.md5(com_name.encode('utf-8')).hexdigest()
        length = len(my_hash)
        com_ID = initials(com_name) + "-"
        for i in range(4):
            rad_num = random.randint(0,length)
            com_ID += my_hash[rad_num] 
            
        st.write(com_ID)

st.write(selected_comID)

#################### Upload File
uploaded_file = st.file_uploader("Choose a file", label_visibility="collapsed")
def save_file (ID, uploaded_file):
    # Change file name before saving into DB and directory

    # Upload into directory
        with open(os.path.join("upload_files",uploaded_file.name),"wb") as f: 
            f.write(uploaded_file.getbuffer())   

    # Encode file details before saving in the database
    
    # Call API
        add_com = add_file(ID, uploaded_file.name, file_type)

        
        if (add_com["message"] == "Added"):
            st.success("Saved File", icon="✅")
        else:
            st.error('Error adding file. Please try again later', icon="🚨")

if uploaded_file is not None:
    # Check file type
    position = uploaded_file.type.find("/")
    file_type = uploaded_file.type[position+1: ]

   # Preview Data


    # Save into DB
    if st.session_state['text_option'] == True:
        if st.button('Submit'):
            if com_name:
                add_com = add_company(com_ID, com_name)
                if (add_com["message"] == "Added"):
                    st.success("Comapny Added", icon="✅")
                    save_file(com_ID, uploaded_file)
                else:
                    st.error('Error adding company. Please try again later', icon="🚨")
            else:
                # If company name not entered
                st.error("Please enter a company name")
    else:
        if st.button('Submit'):
            save_file(selected_comID, uploaded_file)
