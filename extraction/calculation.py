from request import (
    retrieve_data
)
import json
# TO NOTE:
# curr_statement passes in balance_sheet or income_statement ONLY
# financial words must corresponds to the string of JSON stored in the DB ONLY

def cross_stmt_calculation(curr_statement, year, financial_words, curr_value, company_id, compared_value):
    
    compared_stmt = "income_statement"
    if curr_statement == "income_statement":
        compared_stmt = "balance_sheet"
    

    all_extracted_results  = retrieve_data(company_id)["data"]
    for i in all_extracted_results:
        result = json.loads(i[3])
        
        curr_statement_financial_value = curr_value
        num_of_year = 1

        for i in result[curr_statement]:
            if i["year"] == str(year):
                curr_statement_financial_value+=i[financial_words]
                if i[financial_words] != 0:
                    num_of_year+=1
        
        
        
    avg_curr_value = curr_statement_financial_value/num_of_year

        # print(result[curr_statement])