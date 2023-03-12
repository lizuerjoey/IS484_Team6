import streamlit as st
import glob
import os
import io
#cropper page
#pip install streamlit-cropper
from streamlit_cropper import st_cropper
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
st.subheader("Image Cropper")


def get_file_type (file):
    filetype = os.path.splitext(file)[1]
    return filetype

#get image from temp_file
temp_path = "./temp_files"
dir = os.listdir(temp_path)
if len(dir) > 1:
    # Check if file type uploaded to temp files is an image
    file_paths = glob.glob("./temp_files/*")
    count = 0
    for path in file_paths:
        file_type = get_file_type(path)
        if file_type == '.jpeg': 
            file_path = glob.glob("./temp_files/*.jpeg")[0]
            img= Image.open(file_path)
           # st.image(img)
        elif file_type =='.jpg':
            file_path = glob.glob("./temp_files/*.jpg")[0]
            img= Image.open(file_path)
        elif file_type=='.png':
            file_path= glob.glob("./temp_files/*.png")[0]
            img= Image.open(file_path)


#show on screem
cropped_image= st_cropper(img)
st.write("Preview")
test = cropped_image.thumbnail((450,450))
st.image(cropped_image)
st.write("Do you want to save the cropped image?")
crop_yes = st.button("Yes")
if "count" not in st.session_state:
    st.session_state.count=0
if crop_yes:
    st.session_state.count+=1
    path =(f"./temp_files/new_image{st.session_state.count}.jpeg")
    cropped_image.save(path)
    crop_yes = False

    
st.write("Are you done with cropping?")
fin_crop= st.button("Preview Extracted Data", key="previewimg")
if fin_crop:
    os.remove(file_path)
    switch_page("preview extracted data")  


