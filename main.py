import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import time
from st_clickable_images import clickable_images
from st_pages import Page, show_pages, add_page_title
from request import(
    get_all_companies,
    add_file
)



st.write("THIS IS Main PG")

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("main.py", "Dashboard", "💹"),
        Page("pages/page_1.py", "Upload Reports", ":book:"),
        Page("pages/page_2.py", "Files", ":page_facing_up:"),
    ]
)
get_options = get_all_companies()["data"]
st.write(get_options)

