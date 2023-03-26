import streamlit as st

from request import (
    retrieve_data
)
import json

def calculate_other_metrics(edited_dict, company_id):
    # print(edited_dict)
    # print(company_id)

    other_metrics_format = {
        "year": "",
        "numberFormat": "", 
        "returnOnEquity": 0,
        "returnOnAsset": 0,
        "currentRatio": 0,
        "debtToEquityRatio": 0,
        "netProfitMargin": 0,
        "ebidta": 0
    }
    
    date = ""
    fin_sheet = "income_statement"
    other_fin_sheet = "balance_sheet"

    returnOnEquity = 0
    returnOnAsset = 0

    # check if there are extracted data in income statement
    # if none, check balance statement instead
    if len(edited_dict[fin_sheet]) == 0:
        fin_sheet = "balance_sheet"
        other_fin_sheet = "income_statement"

    if len(edited_dict[fin_sheet]) > 0:
        for each_dict in edited_dict[fin_sheet]:
            for key, value in each_dict.items():
                if key == "year":
                    date = value
                    other_metrics_format[key] = value
                elif key == "numberFormat":
                    other_metrics_format[key] = value
                elif key == "netProfit" or key == "totalAssets" or key == "totalEquities":
                    npv_te_ta = value

                    if fin_sheet == "income_statement":

                        if key == "totalEquities":
                            # (1) ROE (%) = (Net Profit / Total Equity)
                            returnOnEquity = cross_stmt_calculation(fin_sheet, date, "netProfit", npv_te_ta, company_id, "totalEquities", edited_dict[other_fin_sheet])
                            st.write("ROE: " + str(returnOnEquity))

                        if key == "totalAssets":
                            # (2) ROA (%) = (Net Profit / Total Assets)
                            returnOnAsset = cross_stmt_calculation(fin_sheet, date, "netProfit", npv_te_ta, company_id, "totalAssets", edited_dict[other_fin_sheet])
                    
                    # balance sheet
                    else:
                        if key == "totalEquities":
                            # (1) ROE (%) = (Net Profit / Total Equity)
                            returnOnEquity = cross_stmt_calculation(fin_sheet, date, "totalEquities", npv_te_ta, company_id, "netProfit", edited_dict[other_fin_sheet])

                        if key == "totalAssets":
                            # (2) ROA (%) = (Net Profit / Total Assets)
                            returnOnAsset = cross_stmt_calculation(fin_sheet, date, "totalAssets", npv_te_ta, company_id, "netProfit", edited_dict[other_fin_sheet])
                    
                    other_metrics_format["returnOnEquity"] = returnOnEquity
                    other_metrics_format["returnOnAsset"] = returnOnAsset

            print(other_metrics_format)

    # both income and balance sheet are empty -> can't calculate any other metrics
    return edited_dict

# def ebitda()

###### GETTING FROM TWO FINANCIAL SHEET ######
# TO NOTE:
# curr_statement passes in balance_sheet or income_statement ONLY
# financial words must corresponds to the string of JSON stored in the DB ONLY
# SAMPLE FUNC DATA: cross_stmt_calculation("income_statement", 2018, "revenue", 900, "AC-05b7", "totalAssets")
def cross_stmt_calculation(curr_statement, year, curr_financial_words, curr_value, company_id, div_financial_words, div_dict):

    div_stmt = "income_statement"
    if curr_statement == "income_statement":
        div_stmt = "balance_sheet"
    

    all_extracted_results  = retrieve_data(company_id)["data"]
    curr_statement_financial_value = float(curr_value)

    # retrieved from current statement value hence identified 1 value 
    if curr_statement_financial_value != 0:
        curr_count = 1
    else:
        curr_count = 0
    
    div_count = 0
    div_stmt_financial_value = 0

    # check if current extracted income statement/ balance sheet have value
    for each_dict in div_dict:
        if each_dict["year"] == str(year):
            div_stmt_financial_value += float(each_dict[div_financial_words])
            st.write(each_dict[div_financial_words])
            if each_dict[div_financial_words] != 0:
                div_count+=1

    for i in all_extracted_results:
        result = json.loads(i[3])
    
        for curr_stmt in result[curr_statement]:
            if curr_stmt["year"] == str(year):
                curr_statement_financial_value += float(curr_stmt[curr_financial_words])
                if curr_stmt[curr_financial_words] != 0:
                    curr_count+=1

        # check past statement(s)
        for stmt in result[div_stmt]:
            if stmt["year"] == str(year):
                div_stmt_financial_value += float(stmt[div_financial_words])
                if stmt[div_financial_words] != 0:
                    div_count+=1
    
    avg_curr_value = 0
    avg_div_value = 0
    if curr_count != 0:
        avg_curr_value = curr_statement_financial_value/curr_count
    if div_count != 0:
        avg_div_value = div_stmt_financial_value/div_count

    if (curr_statement == "income_statement"):
        # cannot be divided by 0
        if avg_div_value != 0:
            return avg_curr_value/avg_div_value
        else:
            return 0
    else:
        # cannot be divided by 0
        if avg_curr_value != 0:
            return avg_div_value/avg_curr_value
        else:
            return 0

###### GETTING FROM ONE FINANCIAL SHEET ######
# TO NOTE:
# financial words must corresponds to the string of JSON stored in the DB ONLY
# numerator = ARRAY
# denominator = ARRAY
# SAMPLE FUNC DATA: indv_stmt_calculation("income_statement",  "AC-05b7", 2018, ["netProfit", "grossProfit"], ["revenue", "cost"], <Balance Sheet DICT>, False)
def indv_stmt_calculation(statement, company_id, year, numerator, denominator, statement_object):
    all_extracted_results  = retrieve_data(company_id)["data"]
    numerator_dict = {}
    denominator_dict = {}
    for num in numerator:
        if (num in statement_object):
            numerator_dict = {num: { "year_count": 1, "value": statement_object[num]}}
    for den in denominator:
        if (den in statement_object):
            denominator_dict = {den: { "year_count": 1, "value": den}}

    for i in all_extracted_results:
        result = json.loads(i[3])
        for stmt in result[statement]:
            for i in range(len(numerator)):
                if stmt["year"] == str(year):
                    if numerator[i] not in numerator_dict:
                        numerator_dict[numerator[i]] = {"year_count":1, "value": float(stmt[numerator[i]])}
                    else:
                        if stmt[numerator[i]] > 0:
                            numerator_dict[numerator[i]]["year_count"] +=1
                        numerator_dict[numerator[i]]["value"] += float(stmt[numerator[i]])

            for i in range(len(denominator)):
                if stmt["year"] == str(year):
                    if denominator[i] not in denominator_dict:
                        denominator_dict[numerator[i]] = {"year_count":1, "value": float(stmt[denominator[i]])}
                    else:
                        if stmt[denominator[i]] > 0:
                            denominator_dict[denominator[i]]["year_count"] +=1
                        denominator_dict[denominator[i]]["value"] += float(stmt[denominator[i]])
    total_numerator = 0  
    total_denominator = 0               
    for key in numerator_dict:
        idv_avg = numerator_dict[key]["value"]/numerator_dict[key]["year_count"]
        total_numerator += float(idv_avg)

    for key in denominator_dict:
        idv_avg = denominator_dict[key]["value"]/denominator_dict[key]["year_count"]
        total_denominator += float(idv_avg)

    if total_denominator == 0:
        return total_numerator/1

    return total_numerator/total_denominator
