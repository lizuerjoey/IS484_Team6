import streamlit as st
import pandas as pd
from st_pages import Page, show_pages, add_page_title
import json
import re
from datetime import date, datetime
import os
from request import(
    get_all_companies,
    get_currencies,
    get_symbols,
    retrieve_data,
    get_months
)
st.set_page_config(layout="wide")
# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("main.py", "Dashboard", ":chart_with_upwards_trend:"),
        Page("pages/page_1.py", "Upload Reports", ":open_file_folder:"),
        Page("pages/page_3.py", "Select Pages (PDF)", ":page_facing_up:"),
        Page("pages/page_4.py", "Preview Extracted Data", ":pencil2:"),
        Page("pages/page_2.py", "Search Files", ":eye:"),
        Page("pages/page_5.py", "Dictionary", ":book:"),
        Page("pages/page_6.py","Image Cropper"),
        Page("pages/page_7.py","Try AWS")
    ]
)

get_options = get_all_companies()["data"]

# COMPANY
if (len(get_options) == 0):
    st.header("No company available..")
    st.write("Please add a company and upload reports.")
else:
    format_df = {
        "company":[],
        "base_currency":[],
        "currency_to_convert":[],
        "start":[],
        "end":[],
        "fiscal_month":[],
        "datetime":[]
    }
    company_col, base_currency_col, currency_col = st.columns(3)
    with company_col:
        options = list(range(len(get_options)))
        option = st.selectbox(
            'Company',
            options, format_func=lambda x: get_options[x][1])
            
        # Get Selected Company ID    
        selected_comID = get_options[option][0]
        selected_comName = get_options[option][1]

        format_df["company"].append(selected_comName)

        # Retrieve data
        get_data = retrieve_data(selected_comID)
        print(type(get_data))
    with base_currency_col:
        
        symbols = get_symbols()
        data = json.loads(get_data["data"][0][3])
        base_code = data["currency"]
        st.markdown("""
                    <span style='font-size: 14px;'>Base Currency</span>
                """, unsafe_allow_html=True)
        st.write(base_code + " ("  + symbols[base_code] + ")")
        format_df["base_currency"].append(base_code)

    # CURRENCY
    with currency_col:
        code = ["Remain Unchange"]
        for key, value in symbols.items():
            code.append(key + "(" + value + ")")

        option = st.selectbox(
            'Currency to convert',
            code)
        format_df["currency_to_convert"].append(option)

        if option!= "Remain Unchange":
            symbol_to_covert = option[:option.find("(")]
            currencies = get_currencies(base_code)
            exchange_rate = currencies["conversion_rates"][symbol_to_covert]
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            st.write(str(date.today()) + " " + current_time)
        else:
            exchange_rate = 1

    
    year = []
    for data in get_data["data"]:
        result = json.loads(data[3])
        # START/END YEAR
        for income_stat in result["income_statement"]:
            if income_stat["year"] not in year:
                year.append(income_stat["year"])
        for balance_sht in result["income_statement"]:
            if balance_sht["year"] not in year:
                    year.append(balance_sht["year"])
        for cashflow in result["cash_flow"]:
            if cashflow["year"] not in year:
                    year.append(cashflow["year"])
        for other_metrices in result["other_metrics"]:
            if other_metrices["year"] not in year:
                    year.append(other_metrices["year"])
        year.sort()

    fiscal_month, start_col, end_col = st.columns(3)
    with fiscal_month:
        st.markdown("""
                    <span style='font-size: 14px;'>Fiscal Start Month</span>
                """, unsafe_allow_html=True)
        fiscal_start_mnth = result["fiscal_start_month"]
     
        st.write(get_months(fiscal_start_mnth))
        format_df["fiscal_month"].append(get_months(fiscal_start_mnth))

    with start_col:
        start_year = st.selectbox(
            'Start Year',
            year)
    endYear = []
    
    format_df["start"].append(start_year)

    if year.index(start_year) != len(year)-1:
        for y in year[year.index(start_year)+1:]:
            if len(start_year) == len(y) :
                endYear.append(y)

    with end_col:
        end_year = st.selectbox(
            'End Year',
            endYear)
        format_df["end"].append(end_year)
    if endYear == []:
        st.error("End year must not be empty", icon="🚨")
    elif int(end_year[:4]) > date.today().year:
        st.error("End year must not be later than " + str(date.today().year), icon="🚨")
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
        assets = {
            "year": [],
            "totalCurrentAssets": [],
            "totalNonCurrentAssets":[]
        }
        balance_sheet_metric = {
            "year": [],
            "debt": [],
            "cash": []
        }
        liabilities = {
            "year": [],
            "totalCurrentLiabilties":[],
            "totalNonCurrentLiabitilies":[],   
        }
        cashflow = {
            "year":[],
            "operatingNetCashFlow":[],
            "investingNetCashFlow":[],
            "financingNetCashFlow":[]
        }
        other_metrics = {
            "year":[],
            "returnOnAsset": [],
            "netInterestMargin": [],
            "netInterestIncomeRatio": [],
            "costIncomeRatio": [],
            "ebidta":[],
        }

        is_numForm = ""
        bs_numForm = ""
        cf_numForm = ""
        om_numForm = ""

        for data in get_data["data"]:
            result = json.loads(data[3])
            # INCOME STATEMENT
            for income_stat in result["income_statement"]:
                is_numForm = income_stat["numberFormat"]
                if income_stat["year"]>=start_year and income_stat["year"]<=end_year and len(income_stat["year"]) == len(start_year):
                    grossPL = income_stat["grossProfit"] - income_stat["grossLoss"]
                    netPL = income_stat["netProfit"] - income_stat["netLoss"]
                    if str(income_stat["year"]) in income_statement["Year"]:
                        position = income_statement["Year"].index(str(income_stat["year"]))
                        if ((income_statement["Revenue"][position] + income_stat["revenue"]*exchange_rate)!=0):
                            income_statement["Revenue"][position] = (income_statement["Revenue"][position] + income_stat["revenue"]*exchange_rate)/2
                        if((income_statement["Cost"][position] + income_stat["cost"]*exchange_rate)):
                            income_statement["Cost"][position] = (income_statement["Cost"][position] + income_stat["cost"]*exchange_rate)/2
                        if ((income_statement["GrossProfitLoss"][position] + grossPL*exchange_rate)!=0):
                            income_statement["GrossProfitLoss"][position] = (income_statement["GrossProfitLoss"][position] + grossPL*exchange_rate)/2
                        if ((income_statement["NetProfitLoss"][position] + netPL*exchange_rate)):
                            income_statement["NetProfitLoss"][position] = (income_statement["NetProfitLoss"][position] + netPL*exchange_rate)/2
                    else:
                        income_statement["Year"].append(str(income_stat["year"]))
                        income_statement["Revenue"].append(income_stat["revenue"]*exchange_rate)
                        income_statement["Cost"].append(income_stat["cost"]*exchange_rate)
                        income_statement["GrossProfitLoss"].append(grossPL*exchange_rate)
                        income_statement["NetProfitLoss"].append(netPL*exchange_rate)
            
            # Create Dataframe
            df_is = pd.DataFrame(data=income_statement)
            df_is.rename({'GrossProfitLoss': 'Gross Profit/Loss', 'NetProfitLoss': 'Net Profit/Loss'}, axis=1, inplace=True)
            
            # BALANCE SHEET
            for balance_sheet_result in result["balance_sheet"]:
                bs_numForm = balance_sheet_result["numberFormat"]
                if balance_sheet_result["year"]>=start_year and balance_sheet_result["year"]<=end_year  and len(balance_sheet_result["year"]) == len(start_year):

                    if balance_sheet_result["year"] in balance_sheet["year"]:
                        position = balance_sheet["year"].index(str(balance_sheet_result["year"]))
                        if ((balance_sheet["totalEquities"][position] + balance_sheet_result["totalEquities"])!=0):
                            balance_sheet["totalEquities"][position] = (balance_sheet["totalEquities"][position] + balance_sheet_result["totalEquities"])/2
                        if ((balance_sheet["totalLiabilities"][position] + balance_sheet_result["totalLiabilities"])!=0):
                            balance_sheet["totalLiabilities"][position] = (balance_sheet["totalLiabilities"][position] + balance_sheet_result["totalLiabilities"])/2
                        if ((balance_sheet["totalAssets"][position] + balance_sheet_result["totalAssets"])!=0):
                            balance_sheet["totalAssets"][position] = (balance_sheet["totalAssets"][position] + balance_sheet_result["totalAssets"])/2
                        if ((assets["totalCurrentAssets"][position]+balance_sheet_result["totalCurrentAssets"])!=0):
                            assets["totalCurrentAssets"][position] = (assets["totalCurrentAssets"][position]+balance_sheet_result["totalCurrentAssets"])/2
                        if ((assets["totalNonCurrentAssets"][position]+balance_sheet_result["totalNonCurrentAssets"])!=0):
                            assets["totalNonCurrentAssets"][position] = (assets["totalNonCurrentAssets"][position]+balance_sheet_result["totalNonCurrentAssets"])/2
                        if ((liabilities["totalCurrentLiabilties"][position]+balance_sheet_result["totalCurrentLiabilties"])!=0):
                            liabilities["totalCurrentLiabilties"][position] = (liabilities["totalCurrentLiabilties"][position]+balance_sheet_result["totalCurrentLiabilties"])/2
                        if ((liabilities["totalNonCurrentLiabitilies"][position]+balance_sheet_result["totalNonCurrentLiabitilies"])!=0):
                            liabilities["totalNonCurrentLiabitilies"][position] = (liabilities["totalNonCurrentLiabitilies"][position]+balance_sheet_result["totalNonCurrentLiabitilies"])/2
                        if ((balance_sheet_metric["debt"][position]+balance_sheet_result["debt"])!=0):
                            balance_sheet_metric["debt"][position] = (balance_sheet_metric["debt"][position]+balance_sheet_result["debt"])/2
                        if ((balance_sheet_metric["cash"][position]+balance_sheet_result["cash"])!=0):
                            balance_sheet_metric["cash"][position] = (balance_sheet_metric["cash"][position]+balance_sheet_result["cash"])/2
                    else:
                        balance_sheet["year"].append(str(balance_sheet_result["year"]))
                        balance_sheet["totalEquities"].append(balance_sheet_result["totalEquities"]*exchange_rate)
                        balance_sheet["totalLiabilities"].append(balance_sheet_result["totalLiabilities"]*exchange_rate)
                        balance_sheet["totalAssets"].append(balance_sheet_result["totalAssets"]*exchange_rate)
                        assets["year"].append(str(balance_sheet_result["year"]))
                        assets["totalCurrentAssets"].append(balance_sheet_result["totalCurrentAssets"]*exchange_rate)
                        assets["totalNonCurrentAssets"].append(balance_sheet_result["totalNonCurrentAssets"]*exchange_rate)
                        liabilities["year"].append(str(balance_sheet_result["year"]))
                        liabilities["totalCurrentLiabilties"].append(balance_sheet_result["totalCurrentLiabilties"]*exchange_rate)
                        liabilities["totalNonCurrentLiabitilies"].append(balance_sheet_result["totalNonCurrentLiabitilies"]*exchange_rate)
                        balance_sheet_metric["year"].append(str(balance_sheet_result["year"]))
                        balance_sheet_metric["debt"].append(balance_sheet_result["debt"]*exchange_rate)
                        balance_sheet_metric["cash"].append(balance_sheet_result["cash"]*exchange_rate)
    
    

            # Create Dataframe    
            df_bs = pd.DataFrame(data=balance_sheet)
            df_bs.rename({'year': 'Year', 'totalEquities': 'Total Equities', 'totalLiabilities': 'Total Liabilities', 'totalAssets':'Total Assets'}, axis=1, inplace=True)

            df_assets = pd.DataFrame(data=assets)
            df_assets.rename({'year': 'Year', 'totalCurrentAssets': 'Current Assets', 'totalNonCurrentAssets': 'Non-Current Assets'}, axis=1, inplace=True)
            
            df_liabilities = pd.DataFrame(data=liabilities)
            df_liabilities.rename({'year': 'Year', 'totalCurrentLiabilties': 'Current Liabilities', 'totalNonCurrentLiabitilies': 'Non-Current Liabilities'}, axis=1, inplace=True)


            # CASHFLOW
            for cashflow_result in result["cash_flow"]:
                cf_numForm = cashflow_result["numberFormat"]
                if cashflow_result["year"]>=start_year and cashflow_result["year"]<=end_year  and len(cashflow_result["year"]) == len(start_year):
                    if cashflow_result["year"] in cashflow["year"]:
                        position = cashflow["year"].index(str(cashflow_result["year"]))
                        if ((cashflow["operatingNetCashFlow"][position] + cashflow_result["operatingNetCashFlow"])!=0):
                            cashflow["operatingNetCashFlow"][position] = (cashflow["operatingNetCashFlow"][position] + cashflow_result["operatingNetCashFlow"])/2
                        if ((cashflow["investingNetCashFlow"][position] + cashflow_result["investingNetCashFlow"])!=0):
                            cashflow["investingNetCashFlow"][position] = (cashflow["investingNetCashFlow"][position] + cashflow_result["investingNetCashFlow"])/2
                        if ((cashflow["financingNetCashFlow"][position] + cashflow_result["financingNetCashFlow"])):
                            cashflow["financingNetCashFlow"][position] = (cashflow["financingNetCashFlow"][position] + cashflow_result["financingNetCashFlow"])/2
                    else:
                        cashflow["year"].append(str(cashflow_result["year"]))
                        cashflow["operatingNetCashFlow"].append(cashflow_result["operatingNetCashFlow"]*exchange_rate)
                        cashflow["investingNetCashFlow"].append(cashflow_result["investingNetCashFlow"]*exchange_rate)
                        cashflow["financingNetCashFlow"].append(cashflow_result["financingNetCashFlow"]*exchange_rate)
            
            # Create Dataframe
            df_cf = pd.DataFrame(data=cashflow)
            df_cf.rename({'year': 'Year', 'operatingNetCashFlow': 'Operating Net Cash Flow', 'investingNetCashFlow': 'Investing Net Cash Flow', 'financingNetCashFlow':'Financing Net Cash Flow'}, axis=1, inplace=True)

            # OTHER METRICES
            for other_metrics_result in result["other_metrics"]:
                om_numForm = other_metrics_result["numberFormat"]
                if other_metrics_result["year"]>=start_year and other_metrics_result["year"]<=end_year  and len(other_metrics_result["year"]) == len(start_year):
                    if other_metrics_result["year"] in  other_metrics["year"]:
                        position = other_metrics["year"].index(str(other_metrics_result["year"]))
                        if ((other_metrics["returnOnAsset"][position] + other_metrics_result["returnOnAsset"])!=0):
                            other_metrics["returnOnAsset"][position] = (other_metrics["returnOnAsset"][position] + other_metrics_result["returnOnAsset"])/2
                        if ((other_metrics["netInterestMargin"][position] + other_metrics_result["netInterestMargin"])!=0):
                            other_metrics["netInterestMargin"][position] = (other_metrics["netInterestMargin"][position] + other_metrics_result["netInterestMargin"])/2
                        if ((other_metrics["netInterestIncomeRatio"][position] + other_metrics_result["netInterestIncomeRatio"])):
                            other_metrics["netInterestIncomeRatio"][position] = (other_metrics["netInterestIncomeRatio"][position] + other_metrics_result["netInterestIncomeRatio"])/2
                        if ((other_metrics["costIncomeRatio"][position] + other_metrics_result["costIncomeRatio"])!=0):
                            other_metrics["costIncomeRatio"][position] = (other_metrics["costIncomeRatio"][position] + other_metrics_result["costIncomeRatio"])/2
                        if ((other_metrics["ebidta"][position] + other_metrics_result["ebidta"])!=0):
                            other_metrics["ebidta"][position] = (other_metrics["ebidta"][position] + other_metrics_result["ebidta"])/2
                    else:
                        other_metrics["year"].append(str(other_metrics_result["year"]))
                        other_metrics["returnOnAsset"].append(other_metrics_result["returnOnAsset"]*exchange_rate)
                        other_metrics["netInterestMargin"].append(other_metrics_result["netInterestMargin"]*exchange_rate)
                        other_metrics["netInterestIncomeRatio"].append(other_metrics_result["netInterestIncomeRatio"]*exchange_rate)
                        other_metrics["costIncomeRatio"].append(other_metrics_result["costIncomeRatio"]*exchange_rate)
                        other_metrics["ebidta"].append(other_metrics_result["ebidta"]*exchange_rate)
            # Create Dataframe
            df_om = pd.DataFrame(data=other_metrics)
            df_om.rename({'year': 'Year', 'returnOnAsset': 'Return On Asset', 'netInterestMargin': 'Net Interest Margin', 'netInterestIncomeRatio':'Net Interest Income Ratio', "costIncomeRatio":"Cos tIncome Ratio", "ebidta": "EBIDTA"}, axis=1, inplace=True)
        
        if len(income_statement["Year"])<2 and len(balance_sheet["year"])<2 and len(cashflow["year"])<2 and len(other_metrics["year"])<2:
            st.error("Please upload more reports", icon="🚨")
            
        # Show Graph
        if not df_is.empty and len(income_statement["Year"])>=2:  
            ### INCOME STATEMENT 
            st.subheader("Income Statement (in " + is_numForm + ")")
            st.line_chart(df_is, x="Year")

            #### METRICES
            ###### BASE AND CURRENT YEAR
            res = [eval(i) for i in income_statement["Year"]]
            base_year_position = income_statement["Year"].index(str(min(res)))
            current_year_position = income_statement["Year"].index(str(max(res)))
            col1, col2 = st.columns(2)
            col3, col4 =st.columns(2)
            
            ###### REVENUE
            with col1:
                revenue_ratio=0
                if (income_statement["Revenue"][base_year_position]!=0):
                    revenue_ratio = ((income_statement["Revenue"][current_year_position] - income_statement["Revenue"][base_year_position])/income_statement["Revenue"][base_year_position])*100
                st.metric(label="Revenue", value=income_statement["Revenue"][current_year_position], delta=str(revenue_ratio)+"%")

            ###### COST
            with col2:
                cost_ratio = 0 
                if (income_statement["Cost"][base_year_position]!=0):
                    cost_ratio = ((income_statement["Cost"][current_year_position] - income_statement["Cost"][base_year_position])/income_statement["Cost"][base_year_position])*100
                st.metric(label="Cost", value=income_statement["Cost"][current_year_position], delta=str(cost_ratio)+"%", delta_color="inverse")

            ###### GROSS PROFIT/LOSS
            with col3:
                gross_ratio = 0
                if (income_statement["GrossProfitLoss"][base_year_position]!=0):
                    gross_ratio = ((income_statement["GrossProfitLoss"][current_year_position] - income_statement["GrossProfitLoss"][base_year_position])/income_statement["GrossProfitLoss"][base_year_position])*100
                st.metric(label="Gross Profit/Loss", value=income_statement["GrossProfitLoss"][current_year_position], delta=str(gross_ratio)+"%")

            ###### NET PROFIT/LOSS
            with col4:
                net_ratio = 0
                if (income_statement["NetProfitLoss"][base_year_position]!=0):
                    net_ratio = ((income_statement["NetProfitLoss"][current_year_position] - income_statement["NetProfitLoss"][base_year_position])/income_statement["NetProfitLoss"][base_year_position])*100
                st.metric(label="Net Profit/Loss", value=income_statement["NetProfitLoss"][current_year_position], delta=str(net_ratio)+"%")
        
        ### BALANCE SHEET
        if not df_bs.empty and len(balance_sheet["year"])>=2: 
            st.subheader("Balance Sheet (in " + bs_numForm + ")")
            st.line_chart(df_bs, x="Year")

            assets_col, liabilities_col = st.columns(2)

            with assets_col:
                ###### ASSETS
                st.markdown("""
                    <span style='font-weight: 700;'>Total Assets</span>
                """, unsafe_allow_html=True)
                st.bar_chart(df_assets, x="Year")
            with liabilities_col:
                ###### LIABILITIES
                st.markdown("""
                    <span style='font-weight: 700;'>Total Liabilities</span>
                """, unsafe_allow_html=True)
                st.bar_chart(df_liabilities, x="Year")
                
            # DEBT/CASH
            debt_col, cash_col = st.columns(2)

            res = [eval(i) for i in balance_sheet_metric["year"]]
            base_year_position = balance_sheet_metric["year"].index(str(min(res)))
            current_year_position = balance_sheet_metric["year"].index(str(max(res)))
            
            with debt_col:
                debt_ratio = ((balance_sheet_metric["debt"][current_year_position] - balance_sheet_metric["debt"][base_year_position])/balance_sheet_metric["debt"][base_year_position])*100
                st.metric(label="Debt", value=balance_sheet_metric["debt"][current_year_position], delta=str(debt_ratio)+"%",  delta_color="inverse")
            with cash_col:
                cash_ratio = ((balance_sheet_metric["cash"][current_year_position] - balance_sheet_metric["cash"][base_year_position])/balance_sheet_metric["cash"][base_year_position])*100
                st.metric(label="Cash", value=balance_sheet_metric["cash"][current_year_position], delta=str(cash_ratio)+"%")


        ### CASH FLOW
        if not df_cf.empty and len(cashflow["year"])>=2: 
            st.subheader("Cash Flow (in " + cf_numForm + ")")
            st.bar_chart(df_cf, x="Year")
        ### OTHER METRICS
        if not df_om.empty and len(other_metrics["year"])>=2: 
            st.subheader("Other Metrics (in " + om_numForm + ")")
            ###### BASE AND CURRENT YEAR
            res = [eval(i) for i in other_metrics["year"]]
            base_year_position = other_metrics["year"].index(str(min(res)))
            current_year_position = other_metrics["year"].index(str(max(res)))
            roa_col, nim_col = st.columns(2)
            nii_col, cir_col, ebidta_col = st.columns(3)

            with roa_col:
                returnOnAsset_ratio = ((other_metrics["returnOnAsset"][current_year_position] - other_metrics["returnOnAsset"][base_year_position])/other_metrics["returnOnAsset"][base_year_position])*100
                st.metric(label="Return on Asset", value=other_metrics["returnOnAsset"][current_year_position], delta=str(returnOnAsset_ratio)+"%")
            with nim_col:
                netInterestMargin_ratio = ((other_metrics["netInterestMargin"][current_year_position] - other_metrics["netInterestMargin"][base_year_position])/other_metrics["netInterestMargin"][base_year_position])*100
                st.metric(label="Net Interest Margin", value=other_metrics["netInterestMargin"][current_year_position], delta=str(netInterestMargin_ratio)+"%")
            with nii_col:
                netInterestIncome_ratio = ((other_metrics["netInterestIncomeRatio"][current_year_position] - other_metrics["netInterestIncomeRatio"][base_year_position])/other_metrics["netInterestIncomeRatio"][base_year_position])*100
                st.metric(label="Net Interest Income", value=other_metrics["netInterestIncomeRatio"][current_year_position], delta=str(netInterestIncome_ratio)+"%")
            with cir_col:
                costIncome_ratio = ((other_metrics["costIncomeRatio"][current_year_position] - other_metrics["costIncomeRatio"][base_year_position])/other_metrics["costIncomeRatio"][base_year_position])*100
                st.metric(label="Cost Income", value=other_metrics["costIncomeRatio"][current_year_position], delta=str(costIncome_ratio)+"%")
            with ebidta_col:
                ebidta_ratio = ((other_metrics["ebidta"][current_year_position] - other_metrics["ebidta"][base_year_position])/other_metrics["ebidta"][base_year_position])*100
                st.metric(label="EBIDTA", value=other_metrics["ebidta"][current_year_position], delta=str(ebidta_ratio)+"%")
    
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    format_df["datetime"].append(str(date.today()) + " " + current_time)
    df = pd.DataFrame(data=format_df)
    df.rename({'company': 'Company', 'base_currency': 'Base Currency', 'currency_to_convert': 'Currency To Convert', 'start':'Start Year', "end":"End Year", "fiscal_month": "Fiscal Month", "datetime": "Date/Time"}, axis=1, inplace=True)

    # CONVERT TO EXCEL SHEET
    with pd.ExcelWriter(os.path.join("temp_files",'output.xlsx')) as writer:
        df.to_excel(writer, sheet_name='Main')
        if not df_bs.empty:
            bs=df_bs.merge(df_assets, how="right")
            bs=df_bs.merge(df_liabilities, how="right")
            bs = df_bs.transpose()
            new_header = df_bs.iloc[0] #grab the first row for the header
            df_bs = df_bs[1:] #take the data less the header row
            df_bs.columns = new_header #set the header row as the df header
            st.subheader("Balance Sheet (in " + bs_numForm + ")")
            df_bs
            bs.to_excel(writer, sheet_name='Balance Sheet')

        if not df_is.empty:
            df_is = df_is.transpose()
            new_header = df_is.iloc[0] #grab the first row for the header
            df_is = df_is[1:] #take the data less the header row
            df_is.columns = new_header #set the header row as the df header
            st.subheader("Income Statement (in " + is_numForm + ")")
            df_is
            df_is.to_excel(writer, sheet_name='Income Statement')

        if not df_cf.empty:
            df_cf = df_cf.transpose()
            new_header = df_cf.iloc[0] #grab the first row for the header
            df_cf = df_cf[1:] #take the data less the header row
            df_cf.columns = new_header #set the header row as the df header
            st.subheader("Cash Flow (in " + cf_numForm + ")")
            df_cf
            df_cf.to_excel(writer, sheet_name='Cash Flow Statement')

        if not df_om.empty:
            df_om = df_om.transpose()
            new_header = df_om.iloc[0] #grab the first row for the header
            df_om = df_om[1:] #take the data less the header row
            df_om.columns = new_header #set the header row as the df header
            st.subheader("Other Metrics (in " + is_numForm + ")")
            df_om
            df_om.to_excel(writer, sheet_name='Other Metrics')
    
    # DOWNLOAD EXCEL SHEET
    with open(os.path.join("temp_files",'output.xlsx'), "rb") as file:
        btn = st.download_button(
                label="Download Excel 📥",
                data=file,
                file_name="Download.xlsx",
                mime="text/xlsx"
            )
    