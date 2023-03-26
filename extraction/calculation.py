
import streamlit as st

from request import (
    retrieve_data
)
import json

def get_other_metrics_format():
    other_metrics_format = {
        "year": "",
        "numberFormat": "", 
        "returnOnEquity": 0,
        "returnOnAsset": 0,
        "currentRatio": 0,
        "debtToEquityRatio": 0,
        "netProfitMargin": 0,
        "ebitda": 0
    }
    return other_metrics_format

def calculate_other_metrics(edited_dict, company_id):
    # print(edited_dict)
    # print(company_id)

    big_other_metrics_list = []
    
    date = ""
    fin_sheet = "income_statement"
    other_fin_sheet = "balance_sheet"

    returnOnEquity = 0
    returnOnAsset = 0
    currentRatio = 0
    debtToEquityRatio = 0
    netProfitMargin = 0
    date_list = []

    # check if there are extracted data in income statement
    # if none, check balance statement instead
    if len(edited_dict[fin_sheet]) == 0:
        fin_sheet = "balance_sheet"
        other_fin_sheet = "income_statement"

    if len(edited_dict[fin_sheet]) > 0:
        for each_dict in edited_dict[fin_sheet]:
            other_metrics_format = get_other_metrics_format()
            for key, value in each_dict.items():
                if key == "year":
                    date = value
                    other_metrics_format[key] = value
                    date_list.append(date)
                elif key == "numberFormat":
                    other_metrics_format[key] = value

                if fin_sheet == "income_statement":

                    # (5) Net Profit Margin (%) = Net Income / Total Revenue
                    netProfitMargin = indv_stmt_calculation(fin_sheet, company_id, date, ["netProfit"], ["revenue"], each_dict)

                    # (6) Ebitda (Ratio) = earnings + interest + income tax + depreciation/ amortization
                    ebitda = indv_stmt_calculation(fin_sheet, company_id, date, ["grossProfit", "interest", "incomeTax", "depreciation"], [], each_dict)

                    if key == "netProfit":
                        # (1) ROE (%) = (Net Profit / Total Equity)
                        returnOnEquity = cross_stmt_calculation(fin_sheet, date, "netProfit", value, company_id, "totalEquities", edited_dict[other_fin_sheet])

                        # (2) ROA (%) = (Net Profit / Total Assets)
                        returnOnAsset = cross_stmt_calculation(fin_sheet, date, "netProfit", value, company_id, "totalAssets", edited_dict[other_fin_sheet])
                
                # balance sheet
                else:
                    
                    # (3) Current Ratio = Current Assets / Current Liabilities
                    currentRatio = indv_stmt_calculation(fin_sheet, company_id, date, ["totalCurrentAssets"], ["totalCurrentLiabilties"], each_dict)

                    # (4) Debt-to-equity Ratio = Total Debt / Shareholders' Equity
                    debtToEquityRatio = indv_stmt_calculation(fin_sheet, company_id, date, ["debt"], ["totalEquities"], each_dict)

                    if key == "totalEquities":
                        # (1) ROE (%) = (Net Profit / Total Equity)
                        returnOnEquity = cross_stmt_calculation(fin_sheet, date, "totalEquities", value, company_id, "netProfit", edited_dict[other_fin_sheet])

                    if key == "totalAssets":
                        # (2) ROA (%) = (Net Profit / Total Assets)
                        returnOnAsset = cross_stmt_calculation(fin_sheet, date, "totalAssets", value, company_id, "netProfit", edited_dict[other_fin_sheet])
                
                other_metrics_format["returnOnEquity"] = returnOnEquity
                other_metrics_format["returnOnAsset"] = returnOnAsset
                other_metrics_format["currentRatio"] = currentRatio
                other_metrics_format["debtToEquityRatio"] = debtToEquityRatio
                other_metrics_format["netProfitMargin"] = netProfitMargin
                other_metrics_format["ebitda"] = ebitda

            big_other_metrics_list.append(other_metrics_format)

        # print(big_other_metrics_list)
        # check if the other sheet have extracted data that we missed out
        if len(edited_dict[other_fin_sheet]) > 0:
            for each_dict in edited_dict[other_fin_sheet]:
                other_metrics_format = get_other_metrics_format()
                for key, value in each_dict.items():
                    if key == "year":
                        date = value
                    
                    # if date already exist in other metrics format, don't add
                    if date not in date_list:
                        other_metrics_format["year"] = date

                        if key == "numberFormat":
                            other_metrics_format[key] = value

                        if other_fin_sheet == "income_statement":

                            # (5) Net Profit Margin (%) = Net Income / Total Revenue
                            netProfitMargin = indv_stmt_calculation(other_fin_sheet, company_id, date, ["netProfit"], ["revenue"], each_dict)

                            # (6) Ebitda (Ratio) = earnings + interest + income tax + depreciation/ amortization
                            ebitda = indv_stmt_calculation(other_fin_sheet, company_id, date, ["earnings", "interest", "incomeTax", "depreciation"], [], each_dict)

                            if key == "netProfit":
                                # (1) ROE (%) = (Net Profit / Total Equity)
                                returnOnEquity = cross_stmt_calculation(other_fin_sheet, date, "netProfit", value, company_id, "totalEquities", edited_dict[fin_sheet])

                                # (2) ROA (%) = (Net Profit / Total Assets)
                                returnOnAsset = cross_stmt_calculation(other_fin_sheet, date, "netProfit", value, company_id, "totalAssets", edited_dict[fin_sheet])
                        
                        # balance sheet
                        else:

                            # (3) Current Ratio = Current Assets / Current Liabilities
                            currentRatio = indv_stmt_calculation(other_fin_sheet, company_id, date, ["totalCurrentAssets"], ["totalCurrentLiabilties"], each_dict)

                            # (4) Debt-to-equity Ratio = Total Debt / Shareholders' Equity
                            debtToEquityRatio = indv_stmt_calculation(other_fin_sheet, company_id, date, ["debt"], ["totalEquities"], each_dict)

                            if key == "totalEquities":
                                # (1) ROE (%) = (Net Profit / Total Equity)
                                returnOnEquity = cross_stmt_calculation(other_fin_sheet, date, "totalEquities", value, company_id, "netProfit", edited_dict[fin_sheet])

                            if key == "totalAssets":
                                # (2) ROA (%) = (Net Profit / Total Assets)
                                returnOnAsset = cross_stmt_calculation(other_fin_sheet, date, "totalAssets", value, company_id, "netProfit", edited_dict[fin_sheet])
                        
                        other_metrics_format["returnOnEquity"] = returnOnEquity
                        other_metrics_format["returnOnAsset"] = returnOnAsset
                        other_metrics_format["currentRatio"] = currentRatio
                        other_metrics_format["debtToEquityRatio"] = debtToEquityRatio
                        other_metrics_format["netProfitMargin"] = netProfitMargin
                        other_metrics_format["ebitda"] = ebitda
                    
                big_other_metrics_list.append(other_metrics_format)

        # remove dict that has year empty
        for i in range(len(big_other_metrics_list)):
            if big_other_metrics_list[i]["year"] == '':
                big_other_metrics_list.pop(i)

        # add metrics into edited_dict
        edited_dict["other_metrics"] = big_other_metrics_list

        print(edited_dict)
        
        return edited_dict

    # both income and balance sheet are empty -> can't calculate any other metrics
    return edited_dict

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
# SAMPLE FUNC DATA: indv_stmt_calculation("income_statement",  "AC-05b7", 2018, ["netProfit", "grossProfit"], ["revenue", "cost"], <Income Statement DICT>)
def indv_stmt_calculation(statement, company_id, year, numerator, denominator, statement_object):
    all_extracted_results  = retrieve_data(company_id)["data"]
    numerator_dict = {}
    denominator_dict = {}
    for num in numerator:
        if (num in statement_object):
            numerator_dict = {num: { "year_count": 1, "value": statement_object[num]}}
    for den in denominator:
        if (den in statement_object):
            denominator_dict = {den: { "year_count": 1, "value": statement_object[den]}}

    for i in all_extracted_results:
        result = json.loads(i[3])
        for stmt in result[statement]:
            for i in range(len(numerator)):
                if stmt["year"] == str(year):
                    if numerator[i] not in numerator_dict:
                        numerator_dict[numerator[i]] = {"year_count":1, "value": stmt[numerator[i]]}
                    else:
                        if stmt[numerator[i]] > 0:
                            numerator_dict[numerator[i]]["year_count"] +=1
                        numerator_dict[numerator[i]]["value"] += stmt[numerator[i]]


            for i in range(len(denominator)):
                if stmt["year"] == str(year):
                    if denominator[i] not in denominator_dict:
                        denominator_dict[numerator[i]] = {"year_count":1, "value": stmt[denominator[i]]}
                    else:
                        if stmt[denominator[i]] > 0:
                            denominator_dict[denominator[i]]["year_count"] +=1
                        print(denominator_dict[denominator[i]]["value"])
                        denominator_dict[denominator[i]]["value"] += stmt[denominator[i]]
    total_numerator = 0  
    total_denominator = 0               
    for key in numerator_dict:
        idv_avg = numerator_dict[key]["value"]/numerator_dict[key]["year_count"]
        total_numerator += idv_avg

    for key in denominator_dict:
        idv_avg = denominator_dict[key]["value"]/denominator_dict[key]["year_count"]
        total_denominator += idv_avg

    if total_denominator == 0:
        return float(total_numerator/1)


    return float(total_numerator/total_denominator)