import streamlit as st
from request import(
    add_synonym,
    get_dict
) 
import streamlit_scrollable_textbox as stx
import json
get_options = get_dict()["data"]
financial_sheet = []
for option in get_options:
    if option[2] not in financial_sheet:
        financial_sheet.append(option[2])

sheet = st.selectbox(
            'Type of Statement',
            financial_sheet)

if sheet is not None:
    financial_words = []
    for option in get_options:
        if option[2] == sheet and  option[3] not in financial_words :
            financial_words.append(option[3].capitalize())
    words = st.selectbox(
        'Financial Words',
        financial_words)

    if words is not None:
        
        synonyms = []
        id = 0
        for option in get_options:
            if option[2] == sheet and option[3] == words.lower():
                if option[4]!="":
                    synonyms = json.loads(option[4])
                    list_of_synonyms = "Existing Synonym for '" + words + "':"
                    for i in synonyms:
                        i = i.lower()
                        list_of_synonyms = list_of_synonyms + "\n - " + i.capitalize()
                    stx.scrollableTextbox(list_of_synonyms,height = 150)
                id = option[0]
        synonym = st.text_input(label='Synonym')

        if st.button('Submit'):
            if synonym == "":
                st.error('Please fill in "Financial Words" field.', icon="🚨")
            else:
                if synonym.lower() not in synonyms:
                    synonyms.append(synonym)
                    data = add_synonym(id, synonyms)
                    if (data["message"] == "Updated"):
                        st.success("Dictionary Updated Successfully!", icon="✅")
                else:
                    print("Already in dict")
                    st.error('Word already in Dictionary', icon="🚨")
                    
                
