import streamlit as st
from st_keyup import st_keyup
import base64
import os
import pandas as pd
from PIL import Image
import PyPDF2
import glob
import math
from request import(
    get_allFiles
)

#print(PyPDF2.__version__)

# Initialization
if 'page' not in st.session_state:
    st.session_state['page'] = 0

# Get total page of PDF
def get_total_pgs_PDF (file):
    file = open(file, 'rb')
    pdf = PyPDF2.PdfFileReader(file)
    pages = pdf.numPages
    return pages

temp_path = "./temp_files"
dir = os.listdir(temp_path)

if len(dir) > 1:
    file_path = glob.glob("./temp_files/*.pdf")[0]
    pdfReader = PyPDF2.PdfReader(file_path)
    totalpages = len(pdfReader.pages)
    print(f"Total Pages: {totalpages}")

# Display icon according to file type
def display_icon (file_type):
    if file_type == "pdf":
        image = Image.open(os.path.join("assets","pdf.png"))
        st.image(image)

def paginations(display_list, page):
    start = page*10
    end = ((page+1)*10)
    if (len(display_list)<end):
        end = len(display_list)
    display = display_list[start:end]
    if display == []:
        st.session_state['page'] = 0
        display = display_list[0:9]
    return display

# Display files
def view(fid, file, file_type, company): 
    #print(fid)
    with open(os.path.join("upload_files",file),"rb") as f: 
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        col1, col2 =st.columns([4,15])
        with col1:
            display_icon(file_type)
        with col2:
            st.header(company)
            st.text(file_name)
        if file_type =="pdf":
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="800" height="1200" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)

st.header("Extract File")

############## User input
num_page_input = st.text_input("Select page(s) you want to extract tables from:", placeholder="Enter page number here..")

st.text("Example: \n 1,3,6: Specific pages \n 1-6: A range of pages \n 1-end: All Pages")

status = False

if st.button('Proceed'):
    print(num_page_input)
    
    if num_page_input.isdigit() == True and int(num_page_input) > 0 and int(num_page_input) <= totalpages:
        status = True
        
    elif "," in num_page_input: 
        num_page_input = num_page_input.split(',')
        i = 0
        while i < len(num_page_input):
            if int(num_page_input[i]) <= totalpages:
                status = True
            else: 
                break
            i += 1

    elif "-end" in num_page_input:
        num_page_input = num_page_input.split('-')
        if num_page_input[0].isdigit() == True and int(num_page_input[0])>0 and int(num_page_input[0]) < totalpages:
            status = True
        else:
            st.error('Incorrect range. Please try again', icon="🚨")
        
    else:
        st.error('Incorrect format. Please try again', icon="🚨")
    
    if status == True:
        st.success("Successful", icon="✅")

st.text("")

placeholder = st.empty()
state = False
with placeholder.container():

    ################## FILES
    data = get_allFiles()["data"]

    display_list = []

    for file in data:
        # DECODE FILES
        file[2] = base64.b64decode(file[2].encode("ascii")).decode("ascii")
       
    if display_list == []:
        display_list = data

    maxPage = math.ceil(len(display_list)/10)-1
    
    display_list = paginations(display_list, st.session_state['page'])
    # Loop through the list of files  
    for display in display_list:
        fid = display[0]
        company = display[1]
        file_name = display[2]
        file_type = display[3]
        
view(fid, file_name, file_type, company)


