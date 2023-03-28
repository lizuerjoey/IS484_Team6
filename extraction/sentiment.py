# import PyPDF2
# from PyPDF2 import PdfReader
# import json 
# import pandas as pd
# import numpy as np
import nltk
# from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 

#get image from temp_file
# temp_path = "./temp_files"
# dir = os.listdir(temp_path)
# if len(dir) > 1:
#     # Check if file type uploaded to temp files is an image
#     file_paths = glob.glob("./temp_files/*")
#     count = 0
#     for path in file_paths:
#         file_type = get_file_type(path)
#         if file_type == '.pdf': 
#             file_path = glob.glob("./temp_files/*.pdf")[0]
#             input= file_path
#             #file_name = get_file_name(file_path)


# pdf = open(input, "rb")
# reader = PdfReader(pdf)
# pdf_reader = PyPDF2.PdfReader(pdf)
# total_pages = pdf_reader.numPages

# nltk.download('punkt') # Download the 'punkt' package if you haven't already

# sentences_list = []
# for i in range(total_pages):
#     page = pdf_reader.getPage(i)
#     text = page.extractText()
#     sentences = nltk.sent_tokenize(text)
#     sentences_list.extend(sentences)
# print(sentences_list)



wordnet_lemmatizer = WordNetLemmatizer()
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')
import string
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize 
import re


# toggle this to display entire text in col
# pd.set_option('display.max_colwidth', 100)

#Function to clean text with lematisation 

def clean_text(text):
    # Lowercase, Remove Non-alphanumeric characters, Punctuations, Numbers & Stopwords
    text = text.lower()
    text = re.sub('[^A-Za-z\s]+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text) 

    #remove stopwords 
   # stop = stopwords.words('english')
    #text = ' '.join([word for word in text.split() if word not in (stop)])
    
    #word stemming 
    # ps = PorterStemmer() 
    # words = word_tokenize(text)
    # stem_text = ' '.join([ps.stem(w) for w in words])

    # lemmentization is preferred to keep the context of the word 
    #lemmentise words 
    word_list = nltk.word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    lemmatized_output = ' '.join([lemmatizer.lemmatize(w) for w in word_list])

    return lemmatized_output

# cleaned_sentences=[]
# for sentence in sentences_list:
#     cleaned_sentence = clean_text(sentence)
#     cleaned_sentences.append(cleaned_sentence)
# print(cleaned_sentences)
# print(len(cleaned_sentences))

# from transformers import BertTokenizer, BertForSequenceClassification
# from transformers import pipeline
# from transformers import AutoTokenizer

# model1 = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
# tokenizer1 = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")

# nlp = pipeline("sentiment-analysis", model=model1, tokenizer=tokenizer1)


# results1 = nlp(cleaned_sentences)
# print(results1)

# import seaborn as sns
# df1=pd.DataFrame(results1)
# df1['text']=cleaned_sentences
# print(df1)
# sns.countplot(x='label', data=df1)
# for index, row in df1.iterrows():
#     if row['score'] == df1['score'].max():
#         print(row['text'],round(df1['score'].max(),2))
#     if row['score'] == df1['score'].min():
#         print(row['text'],round(df1['score'].min(),2))