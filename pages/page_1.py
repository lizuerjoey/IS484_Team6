import streamlit as st
import pandas as pd
import os
import hashlib
import random
import PyPDF2
import glob
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
from pylovepdf.ilovepdf import ILovePdf
from request import(
    get_all_companies,
) 
from pylovepdf.ilovepdf import ILovePdf
load_dotenv()
COMPRESSED_PDF_KEY = os.getenv("COMPRESSED_PDF_KEY")
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

if 'og_uploaded_file' not in st.session_state:
    st.session_state['og_uploaded_file'] = None

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

        com_name = "" 
        col1, col2 = st.columns([10,2])
        with col1:
            com_name = st.text_input(
                "Company Name:", st.session_state['com_name'],
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
st.session_state['og_uploaded_file'] = uploaded_file

def save_file_to_temp (uploaded_file): 
    # Upload into directory
    with open(os.path.join("temp_files",uploaded_file.name),"wb") as f: 
        f.write(uploaded_file.getbuffer())   

def proceed_next_pg():
    # File Size limit 2mb in bytes
            limit = 2*1000000
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
            
            else:
                if len(dir) > 0:
                    for f in os.listdir(temp_path):
                        if (f != "test.txt"):
                            os.remove(os.path.join(temp_path, f))

                    for f in os.listdir("./selected_files/"):
                        if (f != "test.txt"):
                            os.remove(os.path.join("./selected_files/", f))

                save_file_to_temp(uploaded_file)

            # check if uploaded file is pdf
            if uploaded_file.name.endswith('.pdf'):
                file_path = "./temp_files/" + uploaded_file.name
                pdfReader = PyPDF2.PdfReader(file_path)
                totalpages = len(pdfReader.pages)
                
                if (uploaded_file.size>limit):
                    st.info('File Size is more than 2MB. This will take awhile to load.', icon="ℹ️")
                    print("File Size more than 2MB")
                    file_path = "./temp_files/" + uploaded_file.name
                    # no need error -> compress file here
                    # save back into the original file name
                    # importing the ilovepdf api
                    # public key
                    public_key = COMPRESSED_PDF_KEY

                    # creating a ILovePdf object
                    ilovepdf = ILovePdf(public_key, verify_ssl=True)

                    # assigning a new compress task
                    task = ilovepdf.new_task('compress')

                    # adding the pdf file to the task
                    task.add_file(file_path)

                    # setting the output folder directory
                    # if no folder exist it will create one
                    task.set_output_folder('temp_files')

                    # execute the task
                    task.execute()

                    # download the task
                    task.download()

                    # delete the task
                    task.delete_current_task()
                    new_file_name = uploaded_file.name
                    
                    if len(dir) > 0:
                        for f in os.listdir(temp_path):
                            if (f == uploaded_file.name):
                                os.remove(os.path.join(temp_path, f))
                                
                        for f in os.listdir(temp_path):
                            if (f.endswith(".pdf")):
                                old_path = os.path.join("temp_files",f)
                                new_path = os.path.join("temp_files",new_file_name)
                                os.rename(old_path, new_path)
                                if (os.stat(new_path).st_size>limit): 
                                    st.warning('File size is more than 2 MB after compressing. Please note that you might not be able to view the file in the PDF viewer. You may proceed with the extraction.', icon="⚠️")
                                print(os.stat(new_path).st_size)
                                

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

            # check if uploade file is png/ jpg/ jpeg
            elif uploaded_file.name.endswith('.png') or uploaded_file.name.endswith('.jpg') or uploaded_file.name.endswith('.jpeg'):
                st.write("Does the uploaded image have more than one table?")
                col3, col4 = st.columns([2,22])
                with col3:
                    result_yes = st.button("Yes")
                with col4:
                    result_no = st.button("No")
                
                if result_yes:
                    switch_page("image cropper")
                if result_no:
                    switch_page("preview extracted data")  

if uploaded_file is not None:
    if st.session_state["text_option"]:
        if com_name == "":
            st.error("Please enter a company name", icon="🚨")
        else:
            proceed_next_pg()
    else:
        proceed_next_pg()

                     

############## CSS
st.markdown("""
    <style>

    div > div:nth-child(5) > div > button,  div > div:nth-child(4) > div > button
    {
        float: right;
    }

    </style>
""", unsafe_allow_html=True)