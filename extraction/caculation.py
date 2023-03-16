from request import (
    retrieve_data
)
import json



###### GETTING FROM TWO FINANCIAL SHEET ######
# TO NOTE:
# curr_statement passes in balance_sheet or income_statement ONLY
# financial words must corresponds to the string of JSON stored in the DB ONLY
# SAMPLE FUNC DATA: cross_stmt_calculation("income_statement", 2018, "revenue", 900, "AC-05b7", "totalAssets")
def cross_stmt_calculation(curr_statement, year, curr_financial_words, curr_value, company_id, div_financial_words):
    
    div_stmt = "income_statement"
    if curr_statement == "income_statement":
        div_stmt = "balance_sheet"
    

    all_extracted_results  = retrieve_data(company_id)["data"]
    curr_statement_financial_value = curr_value
    curr_count = 1
    div_count = 1
    div_stmt_financial_value = 0
    for i in all_extracted_results:
        result = json.loads(i[3])
               

        for curr_stmt in result[curr_statement]:
            if curr_stmt["year"] == str(year):
                curr_statement_financial_value+=curr_stmt[curr_financial_words]
                if curr_stmt[curr_financial_words] != 0:
                    curr_count+=1
        
        for stmt in result[div_stmt]:
            if stmt["year"] == str(year):
                div_stmt_financial_value+=stmt[div_financial_words]
                if stmt[div_financial_words] != 0:
                    div_count+=1
        
        
    avg_curr_value = curr_statement_financial_value/curr_count
    avg_div_value = div_stmt_financial_value/div_count

    if (curr_statement == "income_statement"):
        return avg_curr_value/avg_div_value
    else:
        return avg_curr_value/avg_div_value



###### GETTING FROM ONE FINANCIAL SHEET ######
# TO NOTE:
# financial words must corresponds to the string of JSON stored in the DB ONLY
# numerator = ARRAY
# denominator = ARRAY
# curr_fin_val_is_denominator = financial word is denominator or numerator
# SAMPLE FUNC DATA: indv_stmt_calculation("income_statement",  "AC-05b7", 2018, ["netProfit", "grossProfit"], ["revenue", "cost"], "netProfit", 200, False)
def indv_stmt_calculation(statement, company_id, year, numerator, denominator, curr_financial_words, curr_value, curr_fin_val_is_denominator):
    all_extracted_results  = retrieve_data(company_id)["data"]
    numerator_dict = {}
    denominator_dict = {}
    if (curr_fin_val_is_denominator == False):
        numerator_dict = {curr_financial_words: { "year_count": 1, "value": curr_value}}
    else:
        denominator_dict = {curr_financial_words: { "year_count": 1, "value": curr_value}}

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
                        denominator_dict[denominator[i]]["value"] += stmt[denominator[i]]
    total_numerator = 0  
    total_denominator = 0               
    for key in numerator_dict:
        idv_avg = numerator_dict[key]["value"]/numerator_dict[key]["year_count"]
        total_numerator += idv_avg

    for key in denominator_dict:
        idv_avg = denominator_dict[key]["value"]/denominator_dict[key]["year_count"]
        total_denominator += idv_avg

    return total_numerator/total_denominator
