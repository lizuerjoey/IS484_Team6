import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
import time
from st_clickable_images import clickable_images
from st_pages import Page, show_pages, add_page_title
import json
import re
from datetime import date
from request import(
    get_all_companies,
    get_currencies,
    get_symbols,
    retrieve_data,
    insert_data
)

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("main.py", "Dashboard", "💹"),
        Page("pages/page_1.py", "Upload Reports", ":book:"),
        Page("pages/page_4.py", "Preview", ":book:"),
        Page("pages/page_2.py", "Files", ":page_facing_up:")
    ]
)
get_options = get_all_companies()["data"]
if (len(get_options) == 0):
    st.text("No company available")
else:
    options = list(range(len(get_options)))
    option = st.selectbox(
        'Company',
        options, format_func=lambda x: get_options[x][1])
        
    # Get Selected Company ID    
    selected_comID = get_options[option][0]
    selected_comName = get_options[option][1]


    # Retrieve data
    get_data = retrieve_data(selected_comID)
    print(type(get_data))

    # Currency
    symbols = get_symbols()

    code = ["Remain Unchange"]
    for key, value in symbols["symbols"].items():
        code.append(key + "(" + value + ")")

    print(code)
    option = st.selectbox(
        'Currency to convert',
        code)
       
    if option!= "Remain Unchange":
        symbol_to_covert = option[:option.find("(")]
        st.write('You selected:', symbol_to_covert)

        currencies = get_currencies(symbol_to_covert)
        exchange_rate = currencies["rates"][symbol_to_covert]
    else:
        exchange_rate = 1
    # Start/End Year
    year = []
    print(type(get_data["data"][0][3]))
    for data in get_data["data"]:
        result = json.loads(data[3])
        base_currency = result["currency"]
        print(base_currency)

        for income_stat in result["income_statement"]:
            if income_stat["year"] not in year:
                year.append(income_stat["year"])
        if result["balance_sheet"]["year"] not in year:
                year.append(result["balance_sheet"]["year"])
        if result["cash_flow"]["year"] not in year:
                year.append(result["cash_flow"]["year"])
        if result["other_metrics"]["year"] not in year:
                year.append(result["other_metrics"]["year"])
        year.sort()

    start_year = st.selectbox(
        'Start Year',
        year)

    if year.index(start_year) == len(year)-1:
        endYear = []
    else:
        endYear = year[year.index(start_year)+1:]
    end_year = st.selectbox(
        'End Year',
        endYear)
    if endYear == []:
        st.error("Must be 2 or more years", icon="🚨")
        print(date.today().year)
        print(type(date.today().year))
    elif end_year == date.today().year:
        st.error("End date cannot be this year", icon="🚨")
        # Quarter
    else:    
        # Aggregrated value
        income_statement = {
            "Year": [],
            "Revenue": [],
            "Cost":[],
            "GrossProfitLoss":[],
            "NetProfitLoss":[]
        }
        balance_sheet = {
            "year": [],
            "totalEquities":[],
            "totalLiabilities":[],
            "totalAssets":[]
        }
        for data in get_data["data"]:
            result = json.loads(data[3])
            for income_stat in result["income_statement"]:
                if income_stat["year"]>=start_year and income_stat["year"]<=end_year:
                    grossPL = income_stat["grossProfit"] - income_stat["grossLoss"]
                    netPL = income_stat["netProfit"] - income_stat["netLoss"]
                    if str(income_stat["year"]) in income_statement["Year"]:
                        position = income_statement["Year"].index(str(income_stat["year"]))
                        income_statement["Revenue"][position] = (income_statement["Revenue"][position] + income_stat["revenue"]*exchange_rate)/2
                        income_statement["Cost"][position] = (income_statement["Cost"][position] + income_stat["cost"]*exchange_rate)/2
                        income_statement["GrossProfitLoss"][position] = (income_statement["GrossProfitLoss"][position] + grossPL*exchange_rate)/2
                        income_statement["NetProfitLoss"][position] = (income_statement["NetProfitLoss"][position] + netPL*exchange_rate)/2

                    else:
                        income_statement["Year"].append(str(income_stat["year"]))
                        income_statement["Revenue"].append(income_stat["revenue"]*exchange_rate)
                        income_statement["Cost"].append(income_stat["revenue"]*exchange_rate)
                        income_statement["GrossProfitLoss"].append(grossPL*exchange_rate)
                        income_statement["NetProfitLoss"].append(netPL*exchange_rate)

            
            balance_sheet_result = result["balance_sheet"]
                
            if balance_sheet_result["year"]>=start_year and balance_sheet_result["year"]<=end_year:

                if str(balance_sheet_result["year"]) in balance_sheet["year"]:
                    position = balance_sheet["year"].index(str(balance_sheet_result["year"]))
                    balance_sheet["totalEquities"][position] = (balance_sheet["totalEquities"][position] + balance_sheet_result["totalEquities"])/2
                    balance_sheet["totalLiabilities"][position] = (balance_sheet["totalLiabilities"][position] + balance_sheet_result["totalLiabilities"])/2
                    balance_sheet["totalAssets"][position] = (balance_sheet["totalAssets"][position] + balance_sheet_result["totalAssets"])/2
                else:
                    balance_sheet["year"].append(str(balance_sheet_result["year"]))
                    balance_sheet["totalEquities"].append(balance_sheet_result["totalEquities"]*exchange_rate)
                    balance_sheet["totalLiabilities"].append(balance_sheet_result["totalLiabilities"]*exchange_rate)
                    balance_sheet["totalAssets"].append(balance_sheet_result["totalAssets"]*exchange_rate)


    

        # Create Dataframe
        print("DF")
        df_is = pd.DataFrame(data=income_statement)
        df_is.rename({'GrossProfitLoss': 'Gross Profit/Loss', 'NetProfitLoss': 'Net Profit/Loss'}, axis=1, inplace=True)
        print(df_is)
            
        df_bs = pd.DataFrame(data=balance_sheet)
        df_bs.rename({'year': 'Year', 'totalEquities': 'Total Equities', 'totalLiabilities': 'Total Liabilities', 'totalAssets':'Total Assets'}, axis=1, inplace=True)

        print(df_bs)
        # Show Graph
        ### INCOME STATEMENT 
        st.subheader("Income Statement")
        st.line_chart(df_is, x="Year")

        #### METRICES
        ###### BASE AND CURRENT YEAR
        res = [eval(i) for i in income_statement["Year"]]
        base_year_position = res.index(min(res))
        current_year_position = res.index(max(res))
        col1, col2 = st.columns(2)
        col3, col4 =st.columns(2)
        
        ###### REVENUE
        with col1:
            revenue_ratio = ((income_statement["Revenue"][current_year_position] - income_statement["Revenue"][base_year_position])/income_statement["Revenue"][base_year_position])*100
            st.metric(label="Revenue", value=income_statement["Revenue"][current_year_position], delta=str(revenue_ratio)+"%")

        ###### COST
        with col2:
            cost_ratio = ((income_statement["Cost"][current_year_position] - income_statement["Cost"][base_year_position])/income_statement["Cost"][base_year_position])*100
            st.metric(label="Cost", value=income_statement["Cost"][current_year_position], delta=str(cost_ratio)+"%", delta_color="inverse")

        ###### GROSS PROFIT/LOSS
        with col3:
            gross_ratio = ((income_statement["GrossProfitLoss"][current_year_position] - income_statement["GrossProfitLoss"][base_year_position])/income_statement["GrossProfitLoss"][base_year_position])*100
            st.metric(label="Gross Profit/Loss", value=income_statement["GrossProfitLoss"][current_year_position], delta=str(gross_ratio)+"%")

        ###### NET PROFIT/LOSS
        with col4:
            net_ratio = ((income_statement["NetProfitLoss"][current_year_position] - income_statement["NetProfitLoss"][base_year_position])/income_statement["NetProfitLoss"][base_year_position])*100
            st.metric(label="Net Profit/Loss", value=income_statement["NetProfitLoss"][current_year_position], delta=str(net_ratio)+"%")


        ### BALANCE SHEET
        st.subheader("Balance Sheet")
        st.line_chart(df_bs, x="Year")

############## CSS
st.markdown("""
    <style>

    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(n+7) > div 
    {
        width: fit-content;
        padding: 10px 10px 10px 30px;
        border: 1px solid black;
        border-radius: 5px;
        font-weight: 900;
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div > div > div:nth-child(1) > div > div > div > label > div > div > p        
    {
        font-weight: 700;
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div > div > div > div > canvas
    {
        width: fit-content;
        padding: 20px 20px 10px 30px; 
        border: 1px solid black;
        border-radius: 5px;
        
    }
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:last-child > div,
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(9) > div,
    section.main.css-k1vhr4.egzxvld3 > div > div:nth-child(1) > div > div:nth-child(10) > div
    {
        padding: 0px;
        border: 0px;
    }

    </style>
""", unsafe_allow_html=True)
# TESTING
# data = {
#     "currency": "yen",
#     "income_statement": [
#         {
#             "year": 2023,
#             "quarter": None,
#             "revenue": 2000,
#             "cost": 30000,
#             "grossProfit": 5000,
#             "grossLoss": 900,
#             "netProfit": 300,
#             "netLoss": 200,
#             "incomeTax": 8900,
#             "interest": 800,
#             "depreciation": 400
#         }
#     ],
#     "balance_sheet": {
#         "year": 2023,
#         "totalEquitiesAndLiabilities": 100,
#         "totalEquities": 1000,
#         "totalLiabilities": 300,
#         "totalAssets": 4000,
#         "totalCurrentAssets": 3000,
#         "totalNonCurrentAssets": 3000,
#         "debt": 4000,
#         "cash": 300
#     },
#     "cash_flow": {
#         "year": 2023,
#         "operatingNetCashFlow": 300,
#         "investingNetCashFlow": 3000,
#         "financingNetCashFlow": 3000
#     },
#     "other_metrics": {
#         "year": 2023,
#         "returnOnEquity": 3000,
#         "returnOnAsset": 3000,
#         "netInterestMargin": 430,
#         "netInterestIncomeRatio": 3000,
#         "costIncomeRatio": 5000,
#         "ebidta": 3000
#     }
# }

# print(insert_data(5, "AC-1904", data))