import PyPDF2
import re
import spacy

def spacy_extraction(data, input):
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

    data['sentences'] = sentences_list
    return data
