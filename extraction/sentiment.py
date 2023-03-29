import nltk
from nltk.stem import WordNetLemmatizer 

wordnet_lemmatizer = WordNetLemmatizer()
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

import string
import re

#Function to clean text with lematisation 
def clean_text(text):
    # Lowercase, Remove Non-alphanumeric characters, Punctuations, Numbers & Stopwords
    text = text.lower()
    text = re.sub('[^A-Za-z\s]+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text) 

    # lemmentization is preferred to keep the context of the word 
    # lemmentise words 
    word_list = nltk.word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    lemmatized_output = ' '.join([lemmatizer.lemmatize(w) for w in word_list])

    return lemmatized_output