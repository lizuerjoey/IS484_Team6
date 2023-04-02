import streamlit as st
from st_keyup import st_keyup
import base64
import os
import pandas as pd
from PIL import Image
import math
from request import(
    get_allFiles
)
# Initialization
if 'page' not in st.session_state:
    st.session_state['page'] = 0

# Display icon according to file type
def display_icon (file_type):
    if file_type == "pdf":
        image = Image.open(os.path.join("assets","pdf.png"))
    if file_type == "png" or file_type == "jpeg" or file_type== "jpg":
        image = Image.open(os.path.join("assets","picture.png"))
    if file_type == "csv":
        image = Image.open(os.path.join("assets","csv.png"))
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
    
    with open(os.path.join("upload_files",file),"rb") as f: 
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        col1, col2 =st.columns([4,15])
        with col1:
            display_icon(file_type)
        with col2:
            st.header(company)
            st.text(file_name)
        file_size = os.path.getsize(os.path.join("upload_files",file)) 
        limit = 1*1000000
        if file_size >= limit:
            st.info("File can't be viewed as the file size exit 1MB.", icon="ℹ️")

        if file_type =="pdf":
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1200" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)

        if file_type == "png" or file_type == "jpeg" or file_type== "jpg":
            image = Image.open(os.path.join("upload_files", file_name))
            st.image(image)
        
        if file_type == "csv":
            dfs = pd.read_csv(os.path.join("upload_files",file))
            st.write(dfs)
        
placeholder = st.empty()
state = False
with placeholder.container():
    st.header("Files")

    # Search Function
    value = st_keyup("Search", placeholder="Search here...", label_visibility="collapsed")

    print(value)
    ################## FILES
    data = get_allFiles()["data"]

    display_list = []

    for file in data:
        # DECODE FILES
        file[2] = base64.b64decode(file[2].encode("ascii")).decode("ascii")
        # Check if value in array
        if( value.lower() in file[1].lower()) or (value.lower() in file[2].lower()):
            display_list.append(file)

    if display_list == []:
        display_list = data

    print(display_list)
    if len(display_list) > 0:
        maxPage = math.ceil(len(display_list)/10)-1

        col1, col2, col3 = st.columns(3)
        with col1:
            if (st.session_state['page'] >0):
                prev = st.button("Previous")
                if prev:
                    st.session_state['page'] -=1
                    st.experimental_rerun()
            else:
                st.button("Previous", disabled=True)
        with col3:
            if  (st.session_state['page']<maxPage):
                next = st.button("Next")
                if next:
                    st.session_state['page'] +=1
                    st.experimental_rerun()
            else:
                st.button("Next", disabled=True)
        display_list = paginations(display_list, st.session_state['page'])
    if len(display_list) == 0:
        st.write("No files available")
    # Loop through the list of files  
    for display in display_list:
        fid = display[0]
        company = display[1]
        file_name = display[2]
        file_type = display[3]
        col1, col2, col3 = st.columns([2,15,4])
        with col1:
            display_icon(file_type)
        with col2:
            st.subheader(company)
            st.write(file_name)
        with col3: 
            btn = st.button("View", key=str(fid))
        #If btn is pressed 
        if btn:  
            state = True
            break
    if len(display_list)>0:
        col1, col2, col3 = st.columns(3)
        with col1:
            if (st.session_state['page'] >0):
                prev = st.button("Previous", key="prev")
                if prev:
                    st.session_state['page'] -=1
                    st.experimental_rerun()
            else:
                st.button("Previous", disabled=True, key="prev")
        with col3:
            if  (st.session_state['page']<maxPage):
                next = st.button("Next", key="next")
                if next:
                    st.session_state['page'] +=1
                    st.experimental_rerun()
            else:
                st.button("Next", disabled=True, key="next")

if state:
    #This would empty everything inside the container
    placeholder.empty()
    display_files = st.empty()
    with display_files.container():
        view(fid, file_name, file_type, company)


############## CSS
st.markdown("""
    <style>
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div
    {
        background-color: #F0F2F6;
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div:nth-child(1) > div > div,
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div:nth-child(2),
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div:nth-child(3),
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div:last-child
    {
        background-color: white;
    }

    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div > div.css-bzyszk.e1tzin5v2 > div:nth-child(1) > div > div > div > div,
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(2) > div > div.css-ocqkz7.e1tzin5v4 > div.css-vfhot.e1tzin5v2 > div:nth-child(1) > div > div > div > div
    {
        justify-content: center;
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(n+1) > div > div:nth-child(1) > div > div:nth-child(n+4) 
    {
        padding: 10px;
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div > div:nth-child(3)
    {
        margin: auto;
    }
    h2, h3
    {
        padding-bottom: 0px
    }
   section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div > div:nth-child(3) > div:nth-child(1) > div > div > div > button 
    {
        float: right;
        display: flex;
        margin-right: 10px;
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(1) > div > div:nth-child(4) > div > div > p 
    {
        background-color: white;
        align-self: center;
        
    }
    </style>
""", unsafe_allow_html=True)