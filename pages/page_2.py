import streamlit as st
from st_keyup import st_keyup
import base64
from request import(
    get_allFiles
)
st.header("Files")

# Search Function
value = st_keyup("Search", placeholder="Search here...", label_visibility="collapsed")

st.write(value)
################## FILES
data = get_allFiles()["data"]

display_list = []

for file in data:
    # DECODE FILES
    file[2] = base64.b64decode(file[2].encode("ascii")).decode("ascii")
    # Check if value in array
    if( value.lower() in file[1].lower()) or (value.lower() in file[2].lower()):
        display_list.append(file)

if display_list == []:
    display_list = data

st.write(display_list)