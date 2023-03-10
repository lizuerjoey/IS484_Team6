import boto3
import os
from PIL import Image
from dotenv import load_dotenv

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

def image_extraction(image):

    im = Image.open(image)

    import io

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



    import pandas as pd

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

    return dataframes
