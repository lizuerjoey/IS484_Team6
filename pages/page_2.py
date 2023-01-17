import streamlit as st
from st_keyup import st_keyup
import base64
import os
import pandas as pd
from PIL import Image
from request import(
    get_allFiles
)
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
def view(fid, file, file_type): 
    st.write(fid)
    with open(os.path.join("upload_files",file),"rb") as f: 
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        if file_type =="pdf":
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="800" height="1000" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)

        if file_type == "png" or file_type == "jpeg" or file_type== "jpg":
            # dfs = pd.read_csv(os.path.join("upload_files",file))
            # st.write(dfs)
            st.image()

placeholder = st.empty()
state = False
with placeholder.container():
    # View All Files
    for display in display_list:
        fid = display[0]
        company = display[1]
        file_name = display[2]
        file_type = display[3]
        col1, col2, col3 = st.columns([4,15,3])
        with col1:
            if file_type == "pdf":
                    image = Image.open(os.path.join("assets","pdf.png"))
            if file_type == "png" or file_type == "jpeg" or file_type== "jpg":
                image = Image.open(os.path.join("assets","picture.png"))
            st.image(image)
        with col2:
            st.subheader(company)
            st.write(file_name)
        with col3: 
            btn = st.button("View", key=str(fid))
        #If btn is pressed 
        if btn:  
            state = True
            break
if state:
    #This would empty everything inside the container
    placeholder.empty()
    with placeholder.container():
        view(fid, file, file_type)

############## CSS
st.markdown("""
    <style>

    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(3) > div > div 
    {
        background-color: #F0F2F6;
    }
    
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div > div > div > div.css-bzyszk.e1tzin5v2
    {
        margin: auto;
        display: flex;
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(3) > div > div > div.css-bzyszk.e1tzin5v2 > div:nth-child(1) > div > div > div > div    
    {
        justify-content: center;
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(3) > div > div > div.css-o7qwft.e1tzin5v2 > div:nth-child(1) > div > div:nth-child(2) > div > div > p    {
        padding-bottom: 10px;
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(3) > div > div > div.css-yksnv9.e1tzin5v2 
    {
        display: flex;
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)