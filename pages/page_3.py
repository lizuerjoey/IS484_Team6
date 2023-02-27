import streamlit as st
from st_keyup import st_keyup
import os
from PIL import Image
import PyPDF2
import glob
import base64
import shutil
from streamlit_extras.switch_page_button import switch_page

# Get file type
def get_file_type (file):
    filetype = os.path.splitext(file)[1]
    return filetype

# Display PDF
def displayPDF (file, file_type):
    with open(file,"rb") as f: 
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        if file_type ==".pdf":
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="800" height="1200" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)

def save_file_to_selected(uploaded_file): 
    # Upload into directory
    with open(os.path.join("selected_files",uploaded_file.name),"wb") as f: 
        f.write(uploaded_file.getbuffer())

# Initialization
if 'pg_input' not in st.session_state:
    st.session_state['pg_input'] = ''

if 'status' not in st.session_state:
    st.session_state['status'] = False

selected_path = "./selected_files"
selected_dir = os.listdir(selected_path)

# Delete when pdf is saved into the database
for f in os.listdir(selected_path):
    if (f != "test.txt"):
        os.remove(os.path.join(selected_path, f))

temp_path = "./temp_files"
dir = os.listdir(temp_path)

st.subheader("Select Pages (PDF)")

# Check if user uploaded a file into temp files
if len(dir) > 1:
    # Check if file type uploaded to temp files is a PDF
    file_paths = glob.glob("./temp_files/*")
    count = 0
    for path in file_paths:
        file_type = get_file_type(path)

        if file_type == '.pdf':
            file_path = glob.glob("./temp_files/*.pdf")[0]
            pdfReader = PyPDF2.PdfReader(file_path)
            totalpages = len(pdfReader.pages)
            if totalpages > 1:
                
                # Prompt user for page input
                num_page_input = st.text_input("Select page(s) you want to extract tables from:", placeholder="Enter page number here..")
                st.session_state['pg_input'] = num_page_input
                st.text("Example: \n 1,3,6: Specific pages \n 1-6: A range of pages \n 1-end: All Pages")               

                status = False

                col1, col2 = st.columns(2)
                with col1:
                    cfmpg = st.button("Confirm Page", key="confirmpg")
                    
                if cfmpg:
                    print(num_page_input)
                    final_input = []

                    # User input single digit
                    if num_page_input.isdigit() == True and int(num_page_input) > 0 and int(num_page_input) <= totalpages:
                        final_input.append(int(num_page_input)-1)
                        status = True

                    # User input specific pages  (e.g 3,6,7) 
                    elif "," in num_page_input: 
                        num_page_input = num_page_input.split(',')
                        i = 0
                        while i < len(num_page_input):
                            # print(num_page_input[i])
                            if int(num_page_input[i]) <= totalpages and int(num_page_input[i]) > 0:
                                #print(int(num_page_input[i]))
                                status = True

                            else: 
                                status = False
                                break
                            i += 1

                        if status == True:
                            for num in num_page_input:
                                final_input.append(int(num)-1)
                        else:
                            st.error('Page number is out of range. Please try again', icon="🚨")
                        
                    # User input Range (e.g 2-6)
                    elif "-" in num_page_input and "end" not in num_page_input:
                        num_page_input = num_page_input.split('-')
                        
                        if num_page_input[1] == "":
                            st.error('Page number is in the incorrect format. Please try again', icon="🚨")

                        elif num_page_input[0] > num_page_input[1]:
                            st.error('Page number is in the incorrect format. Please try again', icon="🚨")
                        
                        else:
                            i = 0
                            while i < len(num_page_input):
                                if int(num_page_input[i]) <= totalpages and int(num_page_input[i]) > 0:
                                    status = True
                                else:
                                    status = False
                                    break
                                i += 1
                            if status == True:
                                for num in range(int(num_page_input[0])-1, int(num_page_input[1])):
                                    final_input.append(int(num))
                            else:
                                st.error('Page number is out of range. Please try again', icon="🚨")
                    
                    # User input Range but until the last page (e.g 5-end)
                    elif "-end" in num_page_input:
                        num_page_input = num_page_input.split('-')
                        if num_page_input[0].isdigit() == True and int(num_page_input[0])>0 and int(num_page_input[0]) < totalpages:
                            status = True
                            for num in range(int(num_page_input[0])-1, totalpages):
                                final_input.append(num)
                            print(final_input)

                        elif num_page_input[0] == "":
                            st.error('Page number is in the incorrect format. Please try again', icon="🚨")

                        else:
                            st.error('Page number is in the incorrect range. Please try again', icon="🚨")
                    
                    else:
                        st.error('Page number is in the incorrect format. Please try again', icon="🚨")

                    if status != True:
                        st.session_state['status'] = False
                    else:
                        st.success("Successful", icon="✅")
                        st.session_state['status'] = True

                        

                        # When successful page input then change save pdf view
                        pdf = PyPDF2.PdfReader(file_path)
                        

                        # Retrieve user input 
                        selected_pages = final_input 

                        #print(selected_pages)

                        pdfWriter = PyPDF2.PdfWriter()

                        for page_num in selected_pages:
                            pdfWriter.add_page(pdf.pages[page_num])
                        
                        with open(os.path.join("selected_files","selected_pages.pdf"),"wb") as f: 
                            pdfWriter.write(f)
                        
                        origin = './selected_files/'
                        target = './temp_files/'
                        files = os.listdir(origin)
                        files_target = os.listdir(target)
                        for file in files_target:
                            if file=="selected_pages.pdf":
                                os.remove(target+file)
                        for file in files:
                            if file!="test.txt" and file.endswith(".pdf"):
                                file_type = get_file_type(file)
                                shutil.copy(origin+file, target)
                                os.rename(target+file, target+"selected_pages"+file_type)
                                
                st.text("")
                selected_dir = os.listdir(selected_path)
                if (len(selected_dir) > 1):
                    file_path = "./selected_files/selected_pages.pdf"
                displayPDF(file_path, file_type)

                # If pg input is correct, show preview button
                if st.session_state['status'] == True:
                    with col2:
                        previewdata = st.button("Preview Extracted Data", key="previewdata")

                        # If button is clicked, switch page to preview extracted data
                        if previewdata:
                            

                            switch_page("preview extracted data")                    

            else: 
                # Upload one page pdf into selected_files directory
                # origin = './temp_files/'
                # target = './selected_files/'
                # files = os.listdir(origin)
                # for file in files:
                #     if file!="test.txt":
                #         file_type = get_file_type(file)
                #         shutil.copy(origin+file, target)
                #         os.rename(target+file, target+"file"+file_type)
                st.info('Uploaded file is a single-page pdf, there is no need to select pages for extraction. Please proceed to "Preview Extracted Data" page.', icon="ℹ️")

        # If file_type is not pdf    
        elif file_type != ".csv" and file_type != '.xlsx':
            count += 1 
    
    # Check if image was uploaded
    if count > 1:
        st.info('Uploaded file is either a png, jpg or jpeg.', icon="ℹ️")

# Check if any supported file was uploaded
else:
    st.error('Please upload a multi-page pdf file to select pages for extraction.', icon="🚨")


############## CSS
st.markdown("""
    <style>
        #root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v4 > div:nth-child(2) > div:nth-child(1) > div > div > div > button {
            float: right;
            display: flex;
            margin-right: 10px;
        }
    </style>
""", unsafe_allow_html=True)
