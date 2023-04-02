import streamlit as st
from request import(
    add_synonym,
    get_dict,
) 
import streamlit_scrollable_textbox as stx
from streamlit_tags import st_tags
import json

st.header("Dictionary")

get_options = get_dict()["data"]
financial_sheet = []
for option in get_options:
    if option[2] not in financial_sheet:
        financial_sheet.append(option[2])

sheet = st.selectbox(
            'Type of Statement:',
            financial_sheet)
error = False

if sheet is not None:
    financial_words = []
    for option in get_options:
        if option[2] == sheet and  option[3] not in financial_words :
            financial_words.append(option[3].capitalize())
    financial_words.sort()
    selected_word = st.selectbox(
        'Select a Financial Word:',
        financial_words)
    
    if selected_word is not None:
       
        synonyms = []
        id = 0
        for option in get_options:
            if option[2] == sheet and option[3] == selected_word.lower():
                if option[4]!="":
                    synonyms = json.loads(option[4])
                    synonyms_list = []
                    for i in synonyms:
                        synonyms_list.append(i.capitalize())
                else:
                    synonyms_list = []

                synonyms = st_tags(
                    label='Edit Synonyms:',
                    text='Press enter to confirm the addition of new word',
                    value=synonyms_list)
                id = option[0]
                st.info("Synonyms added must be unique.", icon="ℹ️")

                count = 0
                if (len(synonyms) > 1):
                    for word in synonyms:
                        if word.lower() == synonyms[len(synonyms)-1].lower():
                            count += 1
                            error = False
                        if count > 1:
                            st.error(word + ' already exists in another format. Please delete either one.', icon="🚨")
                            error = True

        if st.button('Submit'):
            if error == False:
                data = add_synonym(id, synonyms)
                if (data["message"] == "Updated"):
                    st.success("Dictionary Updated Successfully!", icon="✅")
            else:
                st.error('Unable to submit, please check the synonyms you are adding.', icon="🚨")
                    
############## CSS
st.markdown("""
    <style>

    p {
        font-size: 14px !important;
    }   
    #root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(4) > div > div > p {
        margin-bottom: 8px !important;
    }

    </style>
""", unsafe_allow_html=True)
