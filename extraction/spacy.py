import streamlit as st
import PyPDF2
from PyPDF2 import PdfReader
from PyPDF2 import PdfFileReader
import re
import spacy

from request import (
    insert_extracted_data_nlp,
)

def spacy_extraction(uploaded_file, temp_path, uploaded_file_name, fid, ID):
    if "pdf" in uploaded_file.type:
        status="processing nlp"
        input=temp_path+"/"+str(uploaded_file.name)
        st.write(input)

        with open(input, "rb") as pdf_file:
            content = ''
            pdf_reader= PyPDF2.PdfFileReader(pdf_file)
            num_pages = pdf_reader.numPages
            
            for i in range(0,num_pages):
                content+= pdf_reader.getPage(i).extractText() + '\n'
            content = ' '.join(content.replace(u'\xa0', ' ').strip().split())
            page_number_removal = r"\d{1,3} of \d{1,3}"
            page_number_removal_pattern = re.compile(page_number_removal, re.IGNORECASE)
            content = re.sub(page_number_removal_pattern, '',content)

            nlp = spacy.load('en_core_web_sm')
            doc = nlp(content)
            sentences_list = [[],[],[]]
            
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    if ent.text not in sentences_list[0]:
                        sentences_list[0].append(ent.text)

                elif ent.label == "PRODUCT":
                    if ent.text not in sentences_list[1]:
                        sentences_list[1].append(ent.text)

                elif ent.label == "GPE":
                    if ent.text not in sentences_list[2]:
                        sentences_list[2].append(ent.text)
            print(sentences_list)

        data = {
            "file_name": uploaded_file_name,
            "nlp_dataframe": "",
            "sentences": []
            }

        data['sentences'].append(sentences_list)

        nlp_df = insert_extracted_data_nlp(fid,ID,data)

        if nlp_df["message"]=="Added":
            pdf_file.close() # close the file when nlp processing is done
            status="pass"
            st.success("Successfull Inserted NLP Data!", icon="✅")
        else:
            status="fail"
            st.error('Error inserting nlp dataframe into database. Please try again later.', icon="🚨")

    return status
