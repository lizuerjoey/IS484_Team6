import fitz
import os
from extraction.aws_image import (image_extraction)

def convert_file():
    # To get better resolution
    zoom_x = 2.0  # horizontal zoom
    zoom_y = 2.0  # vertical zoom
    mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

    pdffile = "./selected_files/selected_pages.pdf"
    doc = fitz.open(pdffile) # open document
    for i in range(len(doc)):
        page = doc.load_page(i)  
        pix = page.get_pixmap(matrix=mat) # render page to an image
        output = "./temp_files/image-" + str(i) + ".jpeg"
        pix.save(output) # store image as a PNG
    doc.close()

    temp_path = "./temp_files"
    dir = os.listdir(temp_path)
    df = []
    if len(dir) > 0:
        for file in os.listdir(temp_path):
            if (file != "test.txt" and file.endswith('.jpeg')):
                extracted_data = image_extraction(os.path.join("temp_files",file))
                df.append(extracted_data)
        return df
    
        


    