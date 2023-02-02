import streamlit as st
import camelot.io as camelot
import PyPDF2

# print("PyPDF2==" + PyPDF2.__version__)

# # import matplotlib

def get_file_path (file_path):
    print("++++++++++")
    print(file_path.name)
    tables = camelot.read_pdf(file_path.name, pages="1")
    # tables[0].df
    # # st.write("Hello")