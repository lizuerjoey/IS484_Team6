import streamlit as st
import re
import base64
import os
from datetime import datetime
import pandas as pd
import time

from streamlit import session_state

from request import (
    get_symbols,
    add_company,
    add_file,
    get_financial_words_col,
    get_financial_words_row,
    get_json_financial_format,
    get_json_format,
    insert_data,
    get_allFiles
)

# retrieve from upload files page
com_name = session_state["com_name"]
com_id = session_state["com_id"]
selected_comName = session_state["selected_comName"]
selected_comID = session_state["selected_comID"]

# scroll position
if "scroll_pos" not in session_state:
    session_state["scroll_pos"] = 0

temp_path = "./temp_files"
dir = os.listdir(temp_path)

def remove_space_caps_next_letter(key):
    new_key = "".join(word.capitalize() for word in key.split())
    first_letter = key[0].lower()
    new_key = first_letter + new_key[1:]
    return new_key

def list_all_lower(my_list):
    return [x.lower() for x in my_list]

def get_total_num_tables(df):
    session_state["total_num_tables"] = len(df)
    return session_state["total_num_tables"]

# check if same type of sheet
# same type -> check for each year
# for each year match the keyword and take the value if the keyword is empty
# if keyword exist, average the second value
def merge_sheets(sheet_lists):
    # create a new dictionary to hold the merged results
    merged_dict = {}
    aggregation_dict = {}
    # same_sheet_multiple_values_dict = {}
    
    # iterate over each sheet in the list
    for sheet in sheet_lists:

        # iterate over each data(s) extracted in the list 
        val_count = 0
        aggregated_text = ""
        aggregated_value = 0       
        for data_index in range(len(sheet)):
            year = sheet[data_index]['year']
            
            if year in merged_dict:
                
                
                #  loop through for the financial keywords
                for key, val in sheet[data_index].items():
                    
                    # if the value is a float and exist in merge dict -> compute the average 
                    if isinstance(val, float) and isinstance(merged_dict[year][key], float):
                        
                        st.write("IN")
                        print(val)

                        aggregated_value = merged_dict[year][key]
                        aggregated_text += str(merged_dict[year][key])

                        aggregated_value += val
                    
                        aggregated_text += " + " + str(val)
                
                        st.write("agg: " + str(aggregated_value))

                        val_count += 1
                        
            else:
                merged_dict[year] = sheet[data_index]
                print(sheet[data_index])
                aggregation_dict[year] = ""
                # same_sheet_multiple_values_dict[year] = []

        st.write(val_count)
        # print(len(sheet_lists))
        # if (val_count == len(sheet_lists)-1):
            
        #     merged_dict[year][key] += aggregated_value / len(sheet_lists)
        #     st.write(merged_dict[year][key])
        #     aggregated_text += "/ " + str(len(sheet_lists))
                
        #     print(val_count)
        #     st.write(aggregated_text)
        
        
        # print(merged_dict)

        new_merged_list = []
        for key, val in merged_dict.items():
            new_merged_list.append(val)

    return new_merged_list

def concat_lists(lists):
    result = []
    for items in zip(*lists):
        result.append(" ".join(str(item) for item in items if not pd.isnull(item)))
    return result

def save_file (ID, uploaded_file, com_name, json):

    # uploaded_file_name = os.path.basename(uploaded_file_path)
    uploaded_file_name = uploaded_file.name

    now = datetime.now()
    date_time = str(now.strftime("%d%m%Y%H%M%S"))

    # Upload into directory
    # pdfWriter = PyPDF2.PdfWriter()
    with open(os.path.join("upload_files", uploaded_file_name),"wb") as f: 
        # pdfWriter.write(uploaded_file_name) 
        f.write(uploaded_file.getbuffer())     

    # Change file name to directory before saving into DB
    old_path = os.path.join("upload_files",uploaded_file_name)
    new_file_name = com_name.replace(" ", "") +"_" + date_time +"_" + uploaded_file_name
    new_path = os.path.join("upload_files",new_file_name)
    os.rename(old_path, new_path)

    # Encode file details before saving in the database
    new_file_name = base64.b64encode(new_file_name.encode("ascii")).decode("ascii")

    # split the file type by / and take the last
    file_type = uploaded_file.type.split("/")[-1]

    # Call API to add file into database
    add_com = add_file(ID, new_file_name, file_type)

    if (add_com["message"] == "Added"):

        # call API to retrieve all files -> last file should be the most updated
        all_files = get_allFiles()
        last_file = len(all_files["data"]) - 1
        fid = all_files["data"][last_file][0]

        # call API to insert json data
        result = insert_data(fid, ID, json)

        if (result["message"] == "Added"):
            st.success("Successful Extraction!", icon="✅")
            st.success("Saved File!", icon="✅")

            # delete everything except test.txt from temp folder
            if len(dir) > 0:
                for f in os.listdir(temp_path):
                    if (f != "test.txt"):
                        os.remove(os.path.join(temp_path, f))
            # wait for 3 sec
            time.sleep(3)
            # clear session state cache
            st.session_state["extract_state"] = False
            session_state["com_name"] = ""
            session_state["com_id"] = ""
            session_state["selected_comName"] = ""
            session_state["selected_comID"] = ""
            st.session_state['text_option'] = False

            # refresh the page
            st.experimental_rerun()
            
        else:
            st.error('Error inserting extraction into database. Please try again later.', icon="🚨")

    else:
        st.error('Error adding file. Please try again later.', icon="🚨")

def merge_col_cells(confirm_headers_table, table, dataframe_list, colname, new_col_list):
   
    # check each column selected for merged cells
    if colname in confirm_headers_table:
        # check if each cell is blank
        empty = 0
        keyword = 0
        replace_keyword = ""
        index = -1
        colvalues = dataframe_list[table][colname].values
        
        for cell in colvalues:
            index += 1
            
            # first few cells is empty
            if keyword == 0 and (pd.isnull(cell) == True or str(cell) == "None" or str(cell) == " "):
                empty += 1

            # first few cells is empty but a cell with keyword is found
            elif empty > 0 and pd.isnull(cell) == False and str(cell) != "None" and str(cell) != " " and str(cell) != "":
                replace_keyword = str(cell)
                keyword += 1
                empty = 0

            # first cell contains a keyword and not empty
            elif empty == 0 and str(cell) != "None" and str(cell) != " " and str(cell) != "":
                replace_keyword = str(cell)
                keyword += 1

            # check if cell below keyword is another keyword
            elif keyword > 0 and empty == 0:
                # another keyword or edited and became empty string or None               dataframe_list              
                if pd.isnull(cell) == False and str(cell) != "None" and str(cell) != " " and str(cell) != "":
                    keyword += 1
                    replace_keyword = str(cell)
                
                # empty cell
                if str(cell) == "None" or str(cell) == " " or str(cell) == "":
                    colvalues[index] = replace_keyword
        
        new_col_list.append(colvalues)
        
    return new_col_list

def save_json_to_db(dataframe_list, search_col_list_check, currency, fiscal_month, financial_format, number_format, confirm_headers_list, confirm_search_col_list, delete_list):      
    save_status = False
    total_num_tables = get_total_num_tables(dataframe_list)
    big_col = []
    big_row = []
    no_search_col_error = []
    header_big_row = []
    new_col_list = []
    new_row_list = []
    yr_qtr = []
    searched_col = []
    # matched_column_headers = []
    matched_list_row = []
    matched_dict_col = {}

    # below are required fields; if at least one field is not correct -> cannot save to json             
    if ((False in search_col_list_check) or 
        (currency == 'Not Selected') or (str(fiscal_month) == " ") or
        ('Not Selected' in financial_format) or 
        ('Unable to Determine' in number_format)):
        save_status = False
        st.error("Please check the required fields.", icon="🚨")
        session_state["extract_state"] = False
    else:
        save_status = True

    # error message
    incorrect_format_error = []
    nothing_error = []

    # save multiple values list
    big_identified_values_list = []

    # saving to db
    all_tables_json_list = []
    table_count = -1

    # if all required fields are filled & total number of tables to extract is 0
    # if save_status == True and total_num_tables <= 0:
    #     st.error("No tables were selected for extraction, please check your delete tables selection.", icon="🚨")

    # if all required fields are filled & total number of tables to extract is not 0
    if save_status == True and total_num_tables > 0:
        
        # loop through each tables in the dataframe list
        for table in range(total_num_tables):
            # table count
            table_count += 1

            # searching through table
            big_col = []
            big_row = []
            header_big_row = []
            new_col_list = []
            new_row_list = []
            yr_qtr = []
            matched_column_headers = []
            matched_list_row = []
            matched_dict_col = {}

            # saving data to db each table
            table_json_list = []
            found_count_list = []

            # multiple selected headers
            if len(confirm_headers_list[table]) > 1:
                for colname in dataframe_list[table]:                                                           
                    new_col_list = merge_col_cells(confirm_headers_list[table], table, dataframe_list, colname, new_col_list)
                
                # merge the text in each column into one big column
                new_col_list.insert(0, dataframe_list[table].index)
                big_col = concat_lists(new_col_list)
                    
            # single header
            elif len(confirm_headers_list[table]) == 1:
                # return just the confirmed header
                confirmed_header = confirm_headers_list[table][0]
                new_col_list.append(dataframe_list[table][str(confirmed_header)])
                new_col_list.insert(0, dataframe_list[table].index)
                big_col = concat_lists(new_col_list)

            # no header selected (at least 1 header is required)
            else:
                save_status = False

            # more than 1 searched col
            if len(confirm_search_col_list[table]) > 0:
                # big_row = merge_row_cells(confirm_search_col_list[table], table)
                searched_col = confirm_search_col_list[table]

            # no col to search selected -> save table id
            else:
                no_search_col_error.append(table)
            
            # search through (col) for financial word
            if financial_format[table] != "Not Selected":
                col_words = get_financial_words_col(financial_format[table])
                for item in list_all_lower(big_col):
                    for key, synonyms in col_words.items():
                        if key in item:
                            if key not in matched_dict_col:
                                matched_dict_col[key] = []
                            matched_dict_col[key].append(item)
                        for x in synonyms:
                            if x.lower() in item:
                                if key not in matched_dict_col:
                                    matched_dict_col[key] = []
                                matched_dict_col[key].append(item)

            # using col headers and row id -> identify the cell and append to the col financial keyword
            # if len of each keyword has more than 1 result -> take the first result (first few rows usually contains total)
            result_dict = {}

            # check if multiple values identified for 1 keyword
            multiple_row_id_dict = {}
            identified_multiple_values_dict = {}

            new_format = financial_format[table].lower().replace(" ", "_")

            if new_format not in identified_multiple_values_dict:
                identified_multiple_values_dict[new_format] = {}

            # change this to regular expression
            pattern = r'^\d{4}( Q[1-4])?$'

            is_nothing = False
            is_incorrect = False
            year_quarter = ""
            for date in searched_col:
                if "_" in date:
                    year_quarter, parts = date.split("_")
                else:
                    # check if it is the correct format
                    # incorrect date format e.g. Unnamed cannot be used as a column header, because even if retrieved the value what year/ month am I going to store it by
                    if re.match(pattern, date):
                        year_quarter = date
                    else:
                        is_incorrect = True
                        continue
                
                if year_quarter not in result_dict:
                    result_dict[year_quarter] = {}
                
                # store row_id for multiple
                if year_quarter not in multiple_row_id_dict:
                    multiple_row_id_dict[year_quarter] = {}

                # store values extracted for multiple
                
                if year_quarter not in identified_multiple_values_dict[new_format]:
                    identified_multiple_values_dict[new_format][year_quarter] = {}

                for key, values in matched_dict_col.items():
                    
                    # always take the first result in for the each financial keyword (first few rows usually contains total)
                    # identified the same financial keyword more than once
                    row_id = values[0]

                    # last row id of the table
                    last_row_id = dataframe_list[table].last_valid_index() 

                    # re-format the key
                    new_key = remove_space_caps_next_letter(key)

                    for row_num in values:
                        # if row_id is not numeric or the length of the row_id is more than the total row_id of the table -> high chance is a string
                        if row_num.isnumeric() == False or len(row_num) > last_row_id:
                            row_num = int(row_num.split()[0])
                        
                        # create a dict to store the multiple row id for each financial keyword identified
                        if new_key not in multiple_row_id_dict[year_quarter]:
                            multiple_row_id_dict[year_quarter][new_key] = [row_num]
                        else:
                            if row_num not in multiple_row_id_dict[year_quarter][new_key]:
                                multiple_row_id_dict[year_quarter][new_key].append(row_num)

                    # if row_id is not numeric or the length of the row_id is more than the total row_id of the table -> high chance is a string
                    if row_id.isnumeric() == False or len(row_id) > last_row_id:
                        row_id = int(row_id.split()[0])
                    
                    # save only financial key to dictionary and make sure the date exist in the column headers before extracting
                    if date in list(dataframe_list[table].columns):                     
                        cell = dataframe_list[table].loc[row_id][str(date)]
                        if new_key in result_dict[year_quarter]:
                            # check if space -> get the index and capitalise the next letter
                            result_dict[year_quarter][new_key].append(cell)
                        else:
                            result_dict[year_quarter][new_key] = [cell]

                        # locate/ identify the (multiple) values
                        # need to check _1 pagination
                        for mul_row_id in multiple_row_id_dict[date][new_key]:
                            mul_cell = dataframe_list[table].loc[mul_row_id][str(date)]
                            if new_key not in identified_multiple_values_dict[new_format][year_quarter]:
                                identified_multiple_values_dict[new_format][year_quarter][new_key] = [mul_cell]
                            else:
                                if mul_row_id not in identified_multiple_values_dict[new_format][year_quarter][new_key]:
                                    identified_multiple_values_dict[new_format][year_quarter][new_key].append(mul_cell)
            
            big_identified_values_list.append(identified_multiple_values_dict)
        
            # saving data in json when there is extracted header values e.g. year/ quarter
            if len(result_dict) > 0:
                basic_format = get_json_format()
                for yr_qtr, fin_words in result_dict.items():

                    # define the regular expression pattern
                    pattern = r'^\d{4}( Q[1-4])?$'

                    # match the format of year or year quarter
                    if re.match(pattern, yr_qtr):
                        is_incorrect = False

                        # saving data in json when there is extracted cell values
                        if len(result_dict[yr_qtr]) > 0:
                            is_nothing = False

                            # save per financial statement
                            financial_statement = financial_format[table].lower().replace(" ", "_")
                            
                            # for each year/ qtr
                            financial_statement_format = get_json_financial_format(financial_statement)
                            for keyword in result_dict[yr_qtr]:
                                # loop through the list of financial words retrieved from table and append it to json format
                                for format_words in financial_statement_format:
                                    if format_words == "year":
                                        financial_statement_format[format_words] = yr_qtr

                                    elif format_words == "numberFormat":
                                        financial_statement_format[format_words] = number_format[table].lower()

                                    elif keyword == format_words:
                                        none_count = 0
                                        for i in range(len(fin_words[keyword])):
                                            
                                            if fin_words[keyword][i] == None or fin_words[keyword][i] is None or fin_words[keyword][i] == 'None' or fin_words[keyword][i] == "":
                                                none_count += 1
                                                continue
                                            else:
                                                # check multiple value here!!!
                                                if none_count != len(fin_words[keyword]):
                                                    
                                                    # extracted_value = fin_words[keyword][i]

                                                    if (("(" in fin_words[keyword][i]) or
                                                        (")" in fin_words[keyword][i]) or 
                                                        ("," in fin_words[keyword][i])):
                                                        fin_words[keyword][i] = fin_words[keyword][i].replace("(", "")
                                                        fin_words[keyword][i] = fin_words[keyword][i].replace(")", "")
                                                        fin_words[keyword][i] = fin_words[keyword][i].replace(",", "")
 
                                                    financial_statement_format[keyword] = float(fin_words[keyword][i])
                                                # else:
                                                #     none_count
                                                                                                
                            # append all the data extracted for each dates
                            table_json_list.append(financial_statement_format)
                            
                            # save basic format
                            basic_format = get_json_format()
                            for format_words in basic_format:
                                if format_words == "currency":
                                    basic_format[format_words] = currency[0:3]

                                elif format_words == "fiscal_start_month":
                                    basic_format[format_words] = fiscal_month

                                # check which financial statement this table belongs to
                                elif format_words == financial_statement:
                                    basic_format[format_words] = table_json_list

                        # no extracted cell values
                        else:
                            basic_format = get_json_format()
                            for format_words in basic_format:
                                if format_words == "currency":
                                    basic_format[format_words] = currency[0:3]

                                elif format_words == "fiscal_start_month":
                                    basic_format[format_words] = fiscal_month

                            is_nothing = True

                    # for column header that is not in the correct format e.g. unnamed
                    else:
                        is_incorrect = True

                    
                # append basic format for each table
                all_tables_json_list.append(basic_format)
            
            # couldn't search anything in headers
            elif len(result_dict) == 0:
                is_nothing = True
                basic_format = get_json_format()
            
            # result_dict
            # append nothing extracted error for each table
            nothing_error.append(is_nothing)
            incorrect_format_error.append(is_incorrect)

            # is_incorrect
            # is_nothing

            # basic_format
        
        # for each financial statements
        income_statement_list = []
        balance_sheet_list = []
        cash_flow_list = []             

        # for each table json
        for json in all_tables_json_list:
            if len(json) > 0:                    
                if len(json["income_statement"]) > 0:
                    income_statement_list.append(json["income_statement"])
                elif len(json["balance_sheet"]) > 0:
                    balance_sheet_list.append(json["balance_sheet"])
                elif len(json["cash_flow"]) > 0:
                    cash_flow_list.append(json["cash_flow"])

        # got more than 1 json data extracted under the same financial statement
        if len(income_statement_list) > 0:
            income_statement_json = merge_sheets(income_statement_list)
        else:
            income_statement_json = income_statement_list

        if len(balance_sheet_list) > 0:
            balance_sheet_json = merge_sheets(balance_sheet_list)
        else:
            balance_sheet_json = balance_sheet_list

        if len(cash_flow_list) > 0:
            cash_flow_json = merge_sheets(cash_flow_list)
        else:
            cash_flow_json = cash_flow_list

        # check if there is result saved in the json variable, if no data was extracted -> extract empty json from api
        if len(income_statement_json) > 0: 
            basic_format["income_statement"] = income_statement_json
        else:
            # only have length 0
            basic_format["income_statement"] = []
        
        if len(balance_sheet_json) > 0: 
            basic_format["balance_sheet"] = balance_sheet_json
        else:
            # only have length 0
            basic_format["balance_sheet"] = []

        if len(cash_flow_json) > 0:
            basic_format["cash_flow"] = cash_flow_json
        else:
            # only have length 0
            basic_format["cash_flow"] = []               
            
        # incorrect_format_error
        for table in range(len(incorrect_format_error)):
            if incorrect_format_error[table] == True:
                table_num = table + 1
                if table_num in delete_list:
                    table_num += 1
                st.info("Data was detected but the column header is not a year or year and quarter. You might want to rename it in Table " + str(table_num) + " for this data to be saved.", icon="ℹ️")
            
        no_extraction = 0
        # nothing_error
        for table in range(len(nothing_error)):
            if nothing_error[table] == True:
                table_num = table + 1
                if table_num in delete_list:
                    table_num += 1
                st.error("Table " + str(table_num) + " could not extract any data. Please check your table values, headers or the financial words dictionary and try again later.", icon="🚨")
                no_extraction += 1
        
        # no_extraction
        # at least 1 table could extract something
        if no_extraction < len(nothing_error):
            # Save into DB

            with st.form("Preview Value"):
                for data in basic_format:
                    # looping through each financial statement
                    if data != "currency" and data != "fiscal_start_month" and data != "other_metrics":
                        sheet_json = basic_format[data]
                        sheet = data
                        new_sheet = data.title().replace("_", " ")
                        st.markdown('**' + new_sheet + '**')

                        if len(sheet_json) <= 0:
                            st.info("This financial sheet was not selected for the extracted table(s) above.", icon="ℹ️")
                        
                        new_dict = {}                       
                        
                        for i in range(len(sheet_json)):
                            st.write(sheet_json[i]["year"] + ":")
                            date = sheet_json[i]["year"]
                            
                            # looping the columns for each metrics
                            cols = st.columns(3)
                            x = 0
                            json = {}
                            display_list = []
                            value_dict = {}
                            retrieved_value = {}
                            for word in sheet_json[i]:
                                if word != "year" and word != "numberFormat":

                                    new_word = word

                                    for each_sheet_dict in big_identified_values_list:
                                        for each_sheet_key in each_sheet_dict:
                                            for each_sheet_date in each_sheet_dict[each_sheet_key]:
                                                
                                                for each_sheet_value in each_sheet_dict[each_sheet_key][each_sheet_date]:
                                                    if str(date) == str(each_sheet_date):
                                                        if word == each_sheet_value:

                                                            # st.write(word)
                                                            if word not in value_dict:
                                                                value_dict[word] = []
                                                            
                                                            value_dict[word].extend(each_sheet_dict[each_sheet_key][each_sheet_date][each_sheet_value])                                                                
                                                            
                                                            # more than 1 means other than itself, there are other values identified
                                                            if len(value_dict[word]) > 1: 
                                                                new_word = f"<span class='other-highlight'>{word}</span>"

                                    
                                    x += 1

                                    col = cols[x % 3]

                                    col.markdown(new_word, unsafe_allow_html=True)
                                    value = col.text_input(word, sheet_json[i][word], key=sheet + date + word, label_visibility='collapsed')
                                    if word not in retrieved_value:
                                        if (value != '0'):
                                            retrieved_value[word] = value

                                    if word not in json:
                                        json[word] = value     

                            display_values = "<div class='multiple-identified-box'><b>⭐ Other values identified:</b>"
                            display_values += "\n\nOur extraction usually takes the first value in the extracted list when multiple values are identified. Hence, below is a list of other values that were identified due to multiple financial keywords found in the columns to search."
                            for og_k, og_v in retrieved_value.items():
                                for k, v_list in value_dict.items():
                                    if (og_k == k):
                                        display_values += "<li><b><span class='other-highlight'>" + k + "</span></b>: "

                                        count = 0
                                        for v in v_list:
                                            
                                            if (("(" in v) or
                                                (")" in v) or 
                                                ("," in v)):
                                                v = v.replace("(", "")
                                                v = v.replace(")", "")
                                                v = v.replace(",", "")
                                            
                                            if (float(og_v) != float(v)):
                                                display_values += str(v)
                                                count += 1
                                                if (count != len(v_list)):
                                                    display_values += ", "
                                             
                                        display_values += "</li>"
                            display_values += "</div>"

                            st.markdown(display_values, unsafe_allow_html=True)                              
                                
                            st.warning("**Values are aggregated:** \n\n **grossProfit:** 132.2 + 19.9 = 400")            

                            
                
                submitted = st.form_submit_button("Submit")

                if submitted:
                    # st.write("clicked")
                    if session_state["text_option"] == True:
                        if com_name:
                            add_com = add_company(com_id, com_name)
                            if (add_com["message"] == "Added"):
                                st.success("Company Added", icon="✅")
                                save_file(com_id, session_state['og_uploaded_file'], com_name, basic_format)
                            else:
                                st.error('Error adding company. Please try again later.', icon="🚨")
                        else:
                            # If company name not entered
                            st.error("Please enter a company name in Upload Report Page.", icon="🚨")
                    else:
                        save_file(selected_comID, session_state['og_uploaded_file'], selected_comName, basic_format)
    

st.markdown("""
<style>
.my-class {
  margin-bottom: 0px !important;
}

.my-class:has(p) {
  color: red !important;
}

.other-highlight {
    background: yellow;
    font-weight: bold 
}

.multiple-identified-box {
    background: rgba(255, 227, 18, 0.1);
    padding: 16px;
    margin-bottom: 16px;
    color: rgb(146, 108, 5) 
}

</style>
""", unsafe_allow_html=True)           