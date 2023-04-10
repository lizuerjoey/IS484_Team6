import streamlit as st
import pandas as pd

from PyPDF2 import PdfFileReader

# nlp
import nltk
from transformers import BertForSequenceClassification
from transformers import pipeline
from transformers import AutoTokenizer
from extraction.sentiment import (clean_text)
from extraction.spacy import (spacy_extraction)

from request import (
    insert_extracted_data_nlp,
)

def nlp_extraction(uploaded_file, temp_path, uploaded_file_name, fid, ID, status):
    if "pdf" in uploaded_file.type:
        status="processing nlp"
        input=temp_path+"/"+str(uploaded_file.name)

        with open(input, "rb") as pdf_file:
            pdf_reader= PdfFileReader(pdf_file)
            total_pages = pdf_reader.numPages
            total_words = 0
            for page_num in range(total_pages):
                page = pdf_reader.getPage(page_num)
                text = page.extractText()
                words = text.split()
                total_words += len(words)
        
        if total_words<0:
            st.error('Insufficient words to perform nlp.', icon="🚨")
            status="fail"
        else:
            status="processing nlp"

            nltk.download('punkt') # Download the 'punkt' package if you haven't already

            sentences_list = []
            for i in range(total_pages):
                page = pdf_reader.getPage(i)
                text = page.extractText()
                sentences = nltk.sent_tokenize(text)
                sentences_list.extend(sentences)

            cleaned_sentences=[]
            for sentence in sentences_list:
                cleaned_sentence = clean_text(sentence)
                cleaned_sentences.append(cleaned_sentence)
                
            model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
            tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
            nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
            results = nlp(cleaned_sentences)
            df=pd.DataFrame(results)
            df['text']=cleaned_sentences
            nlp_dict = df.to_dict()
            
            data = {
            "file_name": uploaded_file_name,
            "nlp_dataframe": nlp_dict,
            "sentences": []
            }

            # call (nlp) spacy extraction - list of sentences (append to the json['sentences'])
            spacy_extraction(data, input)

            # call api to insert 
            nlp_df = insert_extracted_data_nlp(fid,ID,data)

            if nlp_df["message"]=="Added":
                pdf_file.close() # close the file when nlp processing is done
                status="pass"
                st.success("Successfull Inserted NLP Data!", icon="✅")
            else:
                status="fail"
                st.error('Error inserting nlp dataframe into database. Please try again later.', icon="🚨")
    
    # if not pdf
    else:
        status="fail"

    return status