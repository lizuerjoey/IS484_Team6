import streamlit as st
import pandas as pd
import numpy as np
import os
import tabula
import base64
import time
from st_clickable_images import clickable_images
from request import(
    get_all_companies,
    add_file
)

st.set_page_config(
    page_title="HELLO"
)

st.write("THIS IS Main PG")
get_options = get_all_companies()["data"]
st.write(get_options)

