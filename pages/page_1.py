import streamlit as st
import pandas as pd
import os
import hashlib
import random
from datetime import datetime
import base64
from request import(
    get_all_companies,
    add_file,
    add_company
)

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
        # Generate Company ID
        my_hash = hashlib.md5(com_name.encode('utf-8')).hexdigest()
        length = len(my_hash)
        com_ID = initials(com_name) + "-"
        for i in range(4):
            rad_num = random.randint(0,length-1)
            com_ID += my_hash[rad_num] 
            
        # print(com_ID)

# else:
#     print(selected_comID)

now = datetime.now()
date_time = str(now.strftime("%d%m%Y%H%M%S"))

#################### Upload File
uploaded_file = st.file_uploader("Choose a file", label_visibility="collapsed")

def save_file_to_temp (uploaded_file): 
    # Upload into directory
    with open(os.path.join("temp_files",uploaded_file.name),"wb") as f: 
        f.write(uploaded_file.getbuffer())

def save_file (ID, uploaded_file, com_name):

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

if uploaded_file is not None:
    # File Size limit
    limit = 2*(10**9)
    # Check file type
    position = uploaded_file.type.find("/")
    file_type = uploaded_file.type[position+1: ]
    # Accepted File Type
    supported_file_type=["pdf", "png", "jpg", "jpeg"]

    if (file_type not in supported_file_type):
        st.error("Unsupported File Type", icon="🚨")
    # Check file size
    elif (uploaded_file.size>limit):
        st.error("File Size more than 200MB", icon="🚨")
    else:
        # Check if the temp folder is empty
        temp_path = "./temp_files"
        dir = os.listdir(temp_path)
        if len(dir) > 0:
            for f in os.listdir(temp_path):
                if (f != "test.txt"):
                    os.remove(os.path.join(temp_path, f))
        save_file_to_temp(uploaded_file)
        
        # Save into DB
        if st.session_state['text_option'] == True:
            if st.button('Submit'):
                if com_name:
                    add_com = add_company(com_ID, com_name)
                    if (add_com["message"] == "Added"):
                        st.success("Company Added", icon="✅")
                        save_file(com_ID, uploaded_file, com_name)
                    else:
                        st.error('Error adding company. Please try again later', icon="🚨")
                else:
                    # If company name not entered
                    st.error("Please enter a company name", icon="🚨")
        else:

            if st.button('Submit'):
                save_file(selected_comID, uploaded_file, selected_comName)
                

############## CSS
st.markdown("""
    <style>

    div > div:nth-child(5) > div > button,  div > div:nth-child(4) > div > button
    {
        float: right;
    }

    </style>
""", unsafe_allow_html=True)