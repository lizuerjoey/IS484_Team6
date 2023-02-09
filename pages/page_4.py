import streamlit as st
import camelot.io as camelot
import PyPDF2
import os
from st_aggrid import AgGrid
import glob
import pandas as pd
import boto3
import io 
from PIL import Image

# if 1 pg -> display tables
    # check if more than 1 table

# if more than 1pg -> call from sakinah
    # check if more than 1 table

def textract_api (file):
    im = Image.open(file)
    buffered = io.BytesIO()
    im.save(buffered, format='PNG')
    client = boto3.client('textract',aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY, region_name= 'us-east-1')
    response = client.analyze_document(Document={'Bytes': buffered.getvalue()},FeatureTypes=['TABLES'])

def map_blocks(blocks, block_type):
    return {
        block['Id']: block
        for block in blocks
        if block['BlockType'] == block_type
    }
blocks = response['Blocks']
tables = map_blocks(blocks, 'TABLE')
cells = map_blocks(blocks, 'CELL')
words = map_blocks(blocks, 'WORD')
selections = map_blocks(blocks, 'SELECTION_ELEMENT')

def get_children_ids(block):
    for rels in block.get('Relationships', []):
        if rels['Type'] == 'CHILD':
            yield from rels['Ids']

dataframes = []


for table in tables.values():

    # Determine all the cells that belong to this table
    table_cells = [cells[cell_id] for cell_id in get_children_ids(table)]

    # Determine the table's number of rows and columns
    n_rows = max(cell['RowIndex'] for cell in table_cells)
    n_cols = max(cell['ColumnIndex'] for cell in table_cells)
    content = [[None for _ in range(n_cols)] for _ in range(n_rows)]

    # Fill in each cell
    for cell in table_cells:
        cell_contents = [
            words[child_id]['Text']
            if child_id in words
            else selections[child_id]['SelectionStatus']
            for child_id in get_children_ids(cell)
        ]
        i = cell['RowIndex'] - 1
        j = cell['ColumnIndex'] - 1
        content[i][j] = ' '.join(cell_contents)
        

    # We assume that the first row corresponds to the column names
    dataframe = pd.DataFrame(content[1:], columns=content[0])
    dataframes.append(dataframe)
    print(dataframe)



    







def get_total_pgs_PDF (file):
    file = open(file, 'rb')
    pdf = PyPDF2.PdfFileReader(file)
    pages = pdf.numPages
    return pages

def check_tables_single_PDF (file):
    tables = camelot.read_pdf(file, pages="1", flavor="stream", edge_tol=100, row_tol=10)
    return (tables)

def check_tables_multi_PDF (file, pages):
    tables = camelot.read_pdf(file, pages=pages, flavor="stream", edge_tol=100, row_tol=10)
    return (tables)

st.subheader('Number Format & Currency')

temp_path = "./temp_files"
dir = os.listdir(temp_path)

# if temp_files is not empty then extract
if len(dir) > 1:
    #!!!!!!!!!!!!!!!!!!!
    # check file path
    # pdf -> camelot
    # jpg/ jpeg/ png -> aws
    #!!!!!!!!!!!!!!!!!!!

    # retrieve the file from temp_files
    # get the first (because there will always be only one) pdf file in the list of all files of temp_files directory
    file_path = glob.glob("./temp_files/*.pdf")[0]

    totalpages = get_total_pgs_PDF(file_path)

    if (totalpages == 1):
        tables = check_tables_single_PDF(file_path)


        for i in range(len(tables)):

            tablenum = i + 1
            st.subheader('Extracted Table ' + str(tablenum))
            option = st.selectbox('Select a Financial Statement', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), label_visibility='collapsed', key=str(i))
            # st.write('You selected:', option)
            tables[i].to_csv(file_path + ".csv")
            df = pd.read_csv(file_path + ".csv")
            AgGrid(df, editable=True)
    
    # else:
        # get page number from sakinah
        # tables = check_tables_single_PDF(file_path)

