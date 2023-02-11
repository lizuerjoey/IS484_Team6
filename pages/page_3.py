import streamlit as st
from st_keyup import st_keyup
import os
from PIL import Image
import PyPDF2
import glob
import base64

# Get file type
def get_file_type (file):
    filetype = os.path.splitext(file)[1]
    return filetype

# Get total page of PDF
def get_total_pgs_PDF (file):
    file = open(file, 'rb')
    pdf = PyPDF2.PdfFileReader(file)
    pages = pdf.numPages
    return pages

# Display PDF
def displayPDF (file, file_type):
    with open(file,"rb") as f: 
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        if file_type ==".pdf":
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="800" height="1200" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)

# Initialization
if 'pg_input' not in st.session_state:
    st.session_state['pg_input'] = ''

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

                        # Save successful user input to session, to retrieve in page 4
                        st.session_state['pg_input'] = num_page_input

                st.text("")

                displayPDF(file_path, file_type)

            else: 
                st.error('Uploaded file is a single-page pdf, there is no need to select pages for extraction. Please proceed to "Preview Extracted Data" page.', icon="🚨")

        # If file_type is not pdf    
        elif file_type != ".csv":
            count += 1; 
    
    # Check if image was uploaded
    if count > 1:
        st.error('Uploaded file is either a png, jpg or jpeg, please try again with a multi-page pdf.', icon="🚨")

# Check if any supported file was uploaded
else:
    st.error('Please upload a multi-page pdf file to select pages for extraction.', icon="🚨")



