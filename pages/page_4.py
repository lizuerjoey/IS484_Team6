import streamlit as st
# import camelot.io as camelot
import camelot
import PyPDF2
import os
from st_aggrid import AgGrid
import glob
import pandas as pd
import openpyxl
from openpyxl import load_workbook
import boto3
import io
from PIL import Image
from dotenv import load_dotenv

################## START-IMAGE FUNCTIONS ##################

load_dotenv()

ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_KEY")

def map_blocks(blocks, block_type):
    return {
        block['Id']: block
        for block in blocks
        if block['BlockType'] == block_type
    }

def get_children_ids(block):
    for rels in block.get('Relationships', []):
        if rels['Type'] == 'CHILD':
            yield from rels['Ids']

################## END-IMAGE FUNCTIONS ##################

number = [            
            "Unable to Determine",
            "Thousand",
            "Million",
            "Billion",
            "Trillion",
            "Quadrillion"
        ]

def get_file_name (file):
    filename = os.path.splitext(file)[0]
    return filename

def get_file_type (file):
    filetype = os.path.splitext(file)[1]
    return filetype

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

def get_number_format (excel_path):
    num_array = []
    workbook = load_workbook(excel_path)
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        print(f"Title = {sheet.title}")
        for value in sheet.iter_rows(values_only=True):
            for cell in value:
                if cell is None:
                    continue

                if "thousand" in str(cell).lower():
                    num_array.append(1)

                if "million" in str(cell).lower():
                    num_array.append(2)

                if "billion" in str(cell).lower():
                    num_array.append(3)

                if "trillion" in str(cell).lower():
                    num_array.append(4)

                if "quadrillion" in str(cell).lower():
                    num_array.append(5)            

                # # if cannot find any
                # if "thousand" not in str(cell).lower() and "million" in str(cell).lower() and "billion" in str(cell).lower() and "trillion" in str(cell).lower() and "quadrillion" in str(cell).lower():
                #     print("IN")
                #     num_array.append(0)
    
    index = 0
    if len(num_array) > 0:
        # get the first index because it is the first to retrieve
        index = num_array[0]
    else:
        index = 0 # unable to determine
    
    return index

def sort_num_list(index):
    format = number.pop(index)
    number.insert(0, format)
    return number

def extract_tables (tables):
    for i in range(len(tables)):
        tablenum = i + 1
        st.subheader('Extracted Table ' + str(tablenum))
        option = st.selectbox('Select a Financial Statement:', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), key=str(i))
        # st.write('You selected:', option)
        
        tables[i].to_excel(file_name + ".xlsx")
        num_format = get_number_format(file_name + ".xlsx")

        new_num_list = sort_num_list(num_format)
        selected = st.selectbox("Number Format:", new_num_list, key="x" + str(i))

        tables[i].to_csv(file_name + ".csv")
        df = pd.read_csv(file_name + ".csv")
        AgGrid(df, editable=True)

# Initialization
if 'pg_input' not in st.session_state:
    st.session_state['pg_input'] = ''

if 'status' not in st.session_state:
    st.session_state['status'] = False

temp_path = "./temp_files"
dir = os.listdir(temp_path)

# if temp_files is not empty then extract
if len(dir) > 1:
    st.subheader('Currency')

    file_paths = glob.glob("./temp_files/*")
    count = 0
    for path in file_paths:
        file_type = get_file_type(path)

        # file is pdf
        if file_type == '.pdf':
            file_path = glob.glob("./temp_files/*.pdf")[0]
            file_name = get_file_name(file_path)
            totalpages = get_total_pgs_PDF(file_path)

            # single page pdf
            if (totalpages == 1):
                tables = check_tables_single_PDF(file_path)
                extract_tables(tables)
            
            # multi page pdf
            else:
                pg_input = st.session_state.pg_input
                status = st.session_state.status

                # user input is successful on page 3
                if (status == True and pg_input != ''):
                    tables = check_tables_multi_PDF(file_path, str(pg_input))
                    extract_tables(tables)
                    
                else:
                    st.error("Please specify the pages you want to extract.", icon="🚨")

        # file is image
        elif file_type == '.png' or file_type == '.jpg' or file_type == '.jpeg' and file_type != '.txt':
            file_path = glob.glob("./temp_files/*" + file_type)[0]
            file_name = get_file_name(file_path)

            im = Image.open(file_path)

            buffered = io.BytesIO()
            im.save(buffered, format='PNG')

            client = boto3.client('textract',aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY, region_name= 'us-east-1')
            response = client.analyze_document(
                Document={'Bytes': buffered.getvalue()},
                FeatureTypes=['TABLES']
            )

            blocks = response['Blocks']
            tables = map_blocks(blocks, 'TABLE')
            cells = map_blocks(blocks, 'CELL')
            words = map_blocks(blocks, 'WORD')
            selections = map_blocks(blocks, 'SELECTION_ELEMENT')

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

            # check if dataframe is empty
            if len(dataframes) < 1:
                st.error('Please upload an image with a table.', icon="🚨")

            else:
                # if dataframe is not empty (manage to extract some things out)
                st.subheader('Extracted Table 1')
                option = st.selectbox('Select a Financial Statement:', ('Not Selected', 'Income Statement', 'Balance Sheet', 'Cash Flow'), key=str(i))

                dataframe.to_excel(file_name + ".xlsx")
                num_format = get_number_format(file_name + ".xlsx")
                new_num_list = sort_num_list(num_format)
                selected = st.selectbox("Number Format:", new_num_list, key="x" + str(i))
                
                AgGrid(dataframe, editable=True)

# no files was uploaded
else:
    st.error('Please upload a file for extraction.', icon="🚨")
