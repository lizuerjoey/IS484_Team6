# IS484 T06

## Pre-Requisites
-- Python 3.7 - 3.10 <br>
-- Pip

## Environment Setup
To install dependencies, run:
```pip install -r requirements.txt```

## Database Configuration
This project uses PostgreSQL (https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) <br>
To use PostgreSQL database, you will need to create an ```.env``` file and add ```POSTGRESQL_CONNECTION_STRING = "postgresql://<Username>:<Password>@<Servername>:<Port>/<DB>"``` into your .env file 

## API Keys
You will need to create (https://www.exchangerate-api.com/) and store your API Key as ``` EXCHANGE_RATE_API_KEY = "<Your API Key>" ```<br>

## Getting Started
1. Run ```python api/load_db.py``` to load all the necessary tables into the database.
2. Run ```python api/api.py```
3. Open another terminal and run ```streamlit run main.py```
