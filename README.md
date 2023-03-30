# IS484 T06

## Pre-Requisites

* Python 3.10
* Pip


## Environment Setup
To install dependencies, run:
```pip install -r requirements.txt```
```python -m spacy download en_core_web_sm```

## Database Configuration
This project uses PostgreSQL (https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) <br>
To use PostgreSQL database, you will need to create an ```.env``` file and add ```POSTGRESQL_CONNECTION_STRING = "postgresql://<Username>:<Password>@<Servername>:<Port>/<DB>"``` into your ```.env``` file 

## API Keys
You will need to create your APIs and store the API keys in your ```.env``` file. 

### EXCHANGE RATE
Website: https://www.exchangerate-api.com/ <br>
Store API Key as ``` EXCHANGE_RATE_API_KEY = "<Your API Key>" ```<br>

### AWS
Website: https://aws.amazon.com/textract/ <br>
Store AWS Access Key as ``` AWS_ACCESS_KEY = "<Your Access Key>" ``` <br>
Store AWS Secret Key as ``` AWS_SECRET_KEY = "<Your Secret Key>" ``` <br>

### PDF COMPRESSOR
Website: https://developer.ilovepdf.com <br>
Store API Key as  ``` COMPRESSED_PDF_KEY = "<Your API Key>" ``` <br>

## Getting Started
1. Run ```python api/load_db.py``` to load all the necessary tables into the database.
2. Run ```python api/api.py```
3. Open another terminal and run ```streamlit run main.py```
