import streamlit as st
import glob
import os
import io
#cropper page
#pip install streamlit-cropper
from streamlit_cropper import st_cropper
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
#st.set_option('deprecation.showfileUploaderEncoding', False)
st.subheader("Image Cropper")
#update_immediately = st.sidebar.checkbox(label="Update Image", value= True)

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



#if not update_immediately:
#    st.write("Double click to save cropped image")
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
    switch_page("preview extracted data")  



#must i del temp file image?

#invoke aws, ADD TO PAGE 4

#
                #file is image
#                if file_type == '.jpeg' and file_type != '.txt':
#                    file_path = glob.glob("./cropped_images/*" + file_type)[0]
#                    for images in file_path:
#                        file_name = get_file_name(file_path)
#                        is_image = True
#                        dataframes = image_extraction(file_path)
#reset cropped images file