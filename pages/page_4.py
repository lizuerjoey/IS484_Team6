import streamlit as st
import camelot.io as camelot
import PyPDF2
import os
from st_aggrid import AgGrid
import glob
import pandas as pd

pages = "1"
fname = ""

def extract_PDF (file, page):
    tables = camelot.read_pdf(file, pages=page, flavor="stream", edge_tol=100, row_tol=10)
    tables[0].to_csv(file + ".csv")
    return tables[0].df

temp_path = "./temp_files"
dir = os.listdir(temp_path)

# if temp_files is not empty then extract
if len(dir) > 0:
    # retrieve the file from temp_files
    # get the first (because there will always be only one) file in the list of all files of temp_files directory
    file_path = glob.glob("./temp_files/*")[0]

    df = extract_PDF(file_path, pages)
    st.dataframe(df)

    df2 = pd.read_csv(file_path + ".csv")
    AgGrid(df2)