# -*- coding: utf-8 -*-
#Owner: VanZandtr, Github: https://github.com/VanZandtr/mtgbot/

import requests
from bs4 import BeautifulSoup
import smtplib
from win10toast import ToastNotifier
import re
import os.path
from os import path
import pandas as pd
from datetime import date
from openpyxl import load_workbook
import sys
import random
import operator
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time


########################## Global Vars ########################################
ops = {"<": operator.lt, ">": operator.gt, "<=": operator.le, ">=": operator.ge, "=": operator.eq, "==": operator.eq}
price_lists_names = []
today = str(date.today())
my_list_file_path = '.\\excels\\single_card_list_report.xlsx'

####################### Methods ###############################################

#create general popup message
def popup_msg(header, msg, d):
    toaster = ToastNotifier()
    toaster.show_toast(header, msg, duration = d)

#Generate and send an email
def send_email(user, pwd, recipient, subject, body, tags=None):
    
    try:
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = user
        message["To"] = recipient
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        filename = body  # In same directory as script
        
        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        
        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()
        
        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(user, pwd)
            server.sendmail(user, recipient, text)
    except:
        popup_msg("MTGBot Error:", "Error sending email. Please recheck email_settings.txt file", 10)
        return


def get_email_settings():
    #check if price lists are given
    if path.isfile('./files_to_change/email_settings.txt'):
        pass
    else:
        popup_msg("MTGBot Error:", "Error getting email detatils. Please redownload email_settings.txt file", 10)
        return
    
    #get lines
    text_file = open("./files_to_change/email_settings.txt", "r")
    email_lines = text_file.readlines()
    
    #remove newlines and split by :
    email_lines = [i.rstrip() for i in email_lines]
    
    
    counter = 0
    from_gmail = ""
    password = ""
    to_gmail = ""
    subject = ""
    for i in email_lines:
        if counter == 0:
            from_gmail = i.split('=')[1]
        elif counter == 1:
            password = i.split('=')[1]
        elif counter == 2:
            to_gmail = i.split('=')[1]
        elif counter == 3:
            subject = i.split('=')[1]
        counter += 1
            
    return from_gmail, password, to_gmail, subject
    

#Generate a Dataframe of a card list from an MTGGoldfish web scrap
def full_list_request(page, WebUrl, rarity = None, price_op= None, price= None, 
                                    daily_price_change_op= None, daily_price_change= None,
                                    daily_percent_change_op= None, daily_percent_change= None,
                                    weekly_price_change_op= None, weekly_price_change= None,
                                    weekly_percent_change_op= None, weekly_percent_change= None):
    
    if(page>0):
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = WebUrl
        code = requests.get(url, headers=headers)
        plain = code.text
        s = BeautifulSoup(plain, "html.parser")
        text = (s.text)
        combinedText = text.splitlines()
        
        #removes random empty spaces in list
        raw_list = [x for x in combinedText if x != '']
        
        if len(raw_list) < 4:
            popup_msg("MTGBot Error", "Bad url", 10)
            sys.exit()
        
        front_index = -1
        rear_index = -1
        
        price_lists_names.append(str(raw_list[0]))
        
        #finding cards from raw html text
        for i, j in enumerate(raw_list):
            if j == 'Weekly' and front_index == -1:
                front_index = i
            elif j == 'Weekly' and front_index != -1:
                rear_index = i
                break;
        
        if front_index == -1 or rear_index == -1:
            popup_msg("MTGBot Error", "Price list parsing error", 10)
            sys.exit()
        
        #trim up to where cards start and end
        trim = raw_list[front_index + 2:rear_index - 7]
        
        card_map = list(chunks(trim, 8))
        
        #Search and create output format
        card_list = [];
        for row in card_map:
            card_data = []
            
            if rarity:
                if row[2] != rarity.replace(" ", "") :
                    continue
            
            if price_op and price:
                if ops[price_op.replace(" ", "")](float(row[3]), float(price.replace(" ", ""))):
                    pass
                else:
                    continue
                
            if daily_price_change_op and daily_price_change:
                if ops[daily_price_change_op.replace(" ", "")](float(row[4].replace("+", "")), float(daily_price_change.replace(" ", ""))):
                    pass
                else:
                    continue
            
            if daily_percent_change_op and daily_percent_change:
                if ops[daily_price_change_op.replace(" ", "")](float(row[5].replace("+", "").replace("%", "")), float(daily_price_change.replace(" ", ""))):
                    pass
                else:
                    continue
            
            if weekly_price_change_op and weekly_price_change:
                if ops[weekly_price_change_op.replace(" ", "")](float(row[6].replace("+", "")), float(weekly_price_change.replace(" ", ""))):
                    pass
                else:
                    continue
            
            if weekly_percent_change_op and weekly_percent_change:
                if ops[weekly_percent_change_op.replace(" ", "")](float(row[7].replace("+", "").replace("%", "")), float(weekly_percent_change.replace(" ", ""))):
                    pass
                else:
                    continue
            
            for i in range(0, len(row)):
                card_data.append(row[i])
            card_list.append(card_data)
        
        df = pd.DataFrame(card_list,columns=['Card Name', 'Set Name', 'Rarity', 'Current Price', 'Daily Price Change',
                                             'Daily Percent Change', 'Weekly Price Change', 'Weekly Percent Change'])
        return df

#check if price thresholds are met
def check_price_thresholds(c_list, p_list, s_list, t_list):
    for i in range(0, len(p_list)):
        try:
            curr_price = float(p_list[i])
            curr_threshold = float(t_list[i])
        except:
            continue

        if s_list[i] == '<':
            if curr_price < curr_threshold:
                popup_msg("MTGBot Price Alert!", c_list[i] + " is less than "+ t_list[i] + "!", 10)
        elif s_list[i] == '>':
            if curr_price > curr_threshold:
                popup_msg("MTGBot Price Alert!", c_list[i] + " is greater than " + t_list[i] + "!", 10)
        elif s_list[i] == '=' or s_list[i] == '==':
            if curr_price == curr_threshold:
                popup_msg("MTGBot Price Alert!", c_list[i] + " is " + t_list[i] + "!", 10)
        elif s_list[i] == '>=':
            if curr_price >= curr_threshold:
                popup_msg("MTGBot Price Alert!", c_list[i] + " is greater than or equal to " + t_list[i] + "!", 10)
        elif s_list[i] == '<=':
            if curr_price <= curr_threshold:
                popup_msg("MTGBot Price Alert!", c_list[i] + " is less than or equal to " + t_list[i] + "!", 10)

#run price lists with no settings                
def get_set_list_without_settings():
    #check if price lists are given
    if path.isfile('./files_to_change/price_lists.txt'):
        print("Found price_lists.txt")
        print()
        
        #check if price lists is empty
        if os.stat('./files_to_change/price_lists.txt').st_size == 0:
            print("price_lists.txt is empty")
        
        text_file = open("./files_to_change/price_lists.txt", "r")
        price_lists = text_file.readlines()
    
    #run all the price lists given in the file
    name_index = 0
    for url in price_lists:
        ret_msg = full_list_request(1,url)
        
        #remove illegal file characters / format filename
        characters_to_remove = "*./\[]:;|,"
        fn = (str(price_lists_names[name_index]) + today)
        for c in characters_to_remove:
            fn = fn.replace(c, "")
        fn = fn.strip(' \n\t')
        fn = '.\\excels\\' + fn + ".xlsx"
        
        ret_msg.to_excel (fn, index = False)
        name_index += 1
        

#run price lists with settings
def get_set_list_with_settings():
    if path.isfile('./files_to_change/settings.txt'):
        print("Found settings.txt")
        print()
    
        #check if price lists is empty
        if os.stat('./files_to_change/settings.txt').st_size == 0:
            print("settings.txt is empty")
            get_set_list_without_settings()
            return
    else:
        get_set_list_without_settings()
        return
        
    
    text_file = open("./files_to_change/settings.txt", "r")
    settings_list = text_file.readlines()
    
    #remove newlines and split by :
    settings_list = [i.rstrip() for i in settings_list]
    settings_list = [i.split(':') for i in settings_list]
    
    rarity = ""
    
    price_op = ""
    price = 0.00
    
    daily_price_change_op = ""
    daily_price_change = 0.00
    
    daily_percent_change_op = ""
    daily_percent_change = ""
    
    weekly_price_change_op = ""
    weekly_price_change = 0.00
    
    weekly_percent_change_op = ""
    weekly_percent_change = ""
    
    for setting in settings_list:
        if setting[0] == 'Rarity':
            if setting[1] != '':
                rarity = setting[1]
                
        elif setting[0] == 'Price':
            if setting[1] != '':
                split_list = setting[1].split( )
                if len(split_list) != 2:
                    print(split_list)
                    popup_msg("MTGBot Error", "Bad Price setting. Please make sure format is: \"Price: operator price\" ", 10)
                    sys.exit()
                else:
                    price_op = split_list[0]
                    price = split_list[1]
                
        elif setting[0] == 'Daily Price Change':
            if setting[1] != '':
                split_list = setting[1].split( )
                if len(split_list) != 2:
                    popup_msg("MTGBot Error", "Bad Daily Price Change setting. Please make sure format is: \"Daily Price Change: operator price\" ", 10)
                    sys.exit()
                else:
                    daily_price_change_op = split_list[0]
                    daily_price_change = split_list[1]
                
        elif setting[0] == 'Daily Percent Change':
            if setting[1] != '':
                split_list = setting[1].split( )
                if len(split_list) != 2:
                    popup_msg("MTGBot Error", "Bad Daily Percent Change setting. Please make sure format is: \"Daily Percent Change: operator price\" ", 10)
                    sys.exit()
                else:
                    daily_percent_change_op = split_list[0]
                    daily_percent_change = split_list[1]
                
        elif setting[0] == 'Weekly Price Change':
            if setting[1] != '':
                split_list = setting[1].split( )
                if len(split_list) != 2:
                    popup_msg("MTGBot Error", "Bad Daily Percent Change setting. Please make sure format is: \"Daily Percent Change: operator price\" ", 10)
                    sys.exit()
                else:
                    weekly_price_change_op = split_list[0]
                    weekly_price_change = split_list[1]
                
        elif setting[0] == 'Weekly Percent Change':
            if setting[1] != '':
                split_list = setting[1].split( )
                if len(split_list) != 2:
                    popup_msg("MTGBot Error", "Bad Daily Percent Change setting. Please make sure format is: \"Daily Percent Change: operator price\" ", 10)
                    sys.exit()
                else:
                    weekly_percent_change_op = split_list[0]
                    weekly_percent_change = split_list[1]
            
            
    #check if price lists are given
    if path.isfile('./files_to_change/price_lists.txt'):
        print("Found price_lists.txt")
        print()
        
        #check if price lists is empty
        if os.stat('./files_to_change/price_lists.txt').st_size == 0:
            print("price_lists.txt is empty")
        
        text_file = open("./files_to_change/price_lists.txt", "r")
        price_lists = text_file.readlines()
    
    
    #run all the price lists given in the file
    name_index = 0
    for url in price_lists:
        ret_msg = full_list_request(1,url, rarity, price_op, price, 
                                    daily_price_change_op, daily_price_change,
                                    daily_percent_change_op, daily_percent_change,
                                    weekly_price_change_op, weekly_price_change,
                                    weekly_percent_change_op, weekly_percent_change)
        
        #remove illegal file characters / format filename
        characters_to_remove = "*./\[]:;|,"
        fn = (str(price_lists_names[name_index]) + today)
        for c in characters_to_remove:
            fn = fn.replace(c, "")
        fn = fn.strip(' \n\t')
        fn = '.\\excels\\' + fn + ".xlsx"
        
        ret_msg.to_excel (fn, index = False)
        name_index += 1



#Generate a [Name, Price] list from a MTGGoldfish price page scrap
def single_card_request(page,WebUrl):
    
    if(page>0):
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = WebUrl
        code = requests.get(url, headers=headers)
        plain = code.text
        s = BeautifulSoup(plain, "html.parser")
        text = (s.text)
        combinedText = text.splitlines()
        
        return_msg = []
        
        raw_list = [x for x in combinedText if x != '']#removes random empty spaces in list
        
        if len(raw_list) < 4:
            return_msg.append("Bad url")
            return return_msg
            
        
        #logic for card set given
        string_list = [str(x) for x in raw_list]
        
        
        #clean string list
        for x in string_list:
            if x == "-":
                string_list.pop(string_list.index(x))
        
        tcg_player_market = []
        tcg_player_mid = []
        found_seller_flag = False
        
        for x in string_list:
            #print(x)
            
            if x == "TCGplayer Market Price":
                found_seller_flag = True
                
                index = string_list.index(x)
                
                tcg_player_market.append(string_list[index])
                tcg_player_market.append(string_list[index + 1])
                tcg_player_market.append(string_list[index + 2])
                tcg_player_market.append(string_list[index + 3])
                tcg_player_market.append(string_list[index + 4])
                break
            
            if x == "TCGplayer Mid":
                found_seller_flag = True
                
                index = string_list.index(x)
                
                tcg_player_mid.append(string_list[index])
                tcg_player_mid.append(string_list[index + 1])
                tcg_player_mid.append(string_list[index + 2])
                tcg_player_mid.append(string_list[index + 3])
                tcg_player_mid.append(string_list[index + 4])
                break
            
            if x == "Card Kingdom":
                found_seller_flag = True
                
                index = string_list.index(x)
                
                tcg_player_mid.append(string_list[index])
                tcg_player_mid.append(string_list[index + 1])
                tcg_player_mid.append(string_list[index + 2])
                tcg_player_mid.append(string_list[index + 3])
                tcg_player_mid.append(string_list[index + 4])
                break
            
            if x == "eBay - Buy It Now":
                found_seller_flag = True
                
                index = string_list.index(x)
                
                tcg_player_mid.append(string_list[index])
                tcg_player_mid.append(string_list[index + 1])
                tcg_player_mid.append(string_list[index + 2])
                tcg_player_mid.append(string_list[index + 3])
                tcg_player_mid.append(string_list[index + 4])
                break
            
        if found_seller_flag == False:
            return_msg.append("Could not find seller")
            return return_msg
        
        
        temp_list = []
        if len(tcg_player_market) != 0:
            temp_list = tcg_player_market
        else:
            temp_list = tcg_player_mid
        
        card_name = string_list[0]
        result = re.findall('\d*\.?\d+', temp_list[2])
        price = result[0]
        return_msg = [card_name, price]
        
        return return_msg
        
# Create a function called "chunks" with two arguments, l and n used to group 
# cards with their respective elements
# helper function from list_method
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

    
############################# Single Card List Code ###########################

#for test_day in range(0,7):
print("Looking for single_card_list.txt file...")

#column_name = 'Price ' + str(today) + str(test_day)
column_name = 'Price ' + str(today)

my_list = []
price_lists = []
card_name_list = []
price_list = []

#check if my_list exists
if path.isfile('./files_to_change/single_card_list.txt'):
    print("Found single_card_list.txt")
    print()
    
    #check if my_list is empty
    if os.stat('./files_to_change/single_card_list.txt').st_size == 0:
        print("single_card_list.txt is empty")
        
    
    text_file = open("./files_to_change/single_card_list.txt", "r")
    my_list = text_file.readlines()

split_mylist = []
for url in my_list:
    split_mylist.append(url.split( ))

#check for bad urls, skip, and give a popup message
for url in split_mylist:
    ret = single_card_request(1,url[0])
    
    if "Could not find seller" in ret:
        no_seller_index = my_list.index(url[0])
        popup_msg("MTGBot Error", "Could not find a seller for: " + str(no_seller_index), 5)
        sys.exit()
    
    elif 'Bad url' in ret:
        bad_url_index = my_list.index(url[0])
        popup_msg("MTGBot Error", "Bad Url at: " + str(bad_url_index), 5)
        sys.exit()
        
    else:
        card_name_list.append(ret[0])
        price_list.append(ret[1])

sign_list = []
threshold_list = []
#add values to sign list and threshold list
for arr in split_mylist:
    if len(arr) == 3:
        sign_list.append(arr[1])
        threshold_list.append(arr[2])
    else:
        sign_list.append([])
        threshold_list.append([])


#create an excel file if not already made
if path.isfile(my_list_file_path) == False and len(my_list) != 0:
    df = pd.DataFrame()
    df['Card name'] = card_name_list
    df['Average'] = 0.00
    df['Weekly Change'] = 0.00
    df['Daily Change'] = 0.00
    df['Lowest Price'] = 0.00
    df['Highest Price'] = 0.00
    
    converted_price_list = [float(i) for i in price_list]
    df[column_name] = converted_price_list
    
    #add total row       
    df.at['Total', column_name] = df[column_name].sum()
    
    df.to_excel (my_list_file_path, index = False)
    
    
#Change/append to existing file if found  
elif path.isfile(my_list_file_path) == True and len(my_list) != 0:
    df = pd.DataFrame()
    df['Card name'] = card_name_list
    df['Average'] = 0.00    
    df['Weekly Change'] = 0.00
    df['Daily Change'] = 0.00
    df['Lowest Price'] = 0.00
    df['Highest Price'] = 0.00
    
    converted_price_list = [float(i) for i in price_list]
    df[column_name] = converted_price_list
    
    ignore_list = ['Card name', 'Average', 'Daily Change', 'Weekly Change', 'Lowest Price', 'Highest Price']
    # read existing file
    reader = pd.read_excel(my_list_file_path)
    
    #remove totals row
    reader.drop(reader.tail(1).index,inplace=True)
    
    #check if any cards were removed
    cards_removed_flag = False
    for value in reader['Card name'].values:
        if value not in card_name_list:
            print("Not found:", value)
            reader = reader[~reader['Card name'].isin([value])]
            cards_removed_flag = True

    #new card precheck ==> allows for new cards to be added and program to be rerun on the same day(/column)
    new_card_flag = False
    for card in card_name_list:
        if card not in reader.values:
            print("found new card")
            new_card_flag = True
            break
    
                
    #check if column exists
    if (column_name) not in reader.columns:
        #create new column
        reader[column_name] = 'NaN'
        for index1, row1 in df.iterrows():
            for index2, row2 in reader.iterrows():
                if row1['Card name'] == row2['Card name']:
                    #reader.at[index2, column_name] = float(row1[column_name]) + float(random.randint(155, 389)/100)
                    reader.at[index2, column_name] = float(row1[column_name])
                    
        #run statistics
        for index, row in reader.iterrows():
            Lowest_price = 99999999999.00
            Highest_price = 0.00
            sum_of_prices = 0.00
            
            for col in reader.columns:
                if col not in ignore_list:
                    
                    current_val = float(row[col])
                    sum_of_prices += current_val
                    
                    if reader.at[index, 'Highest Price'] == 0.00 or current_val > reader.at[index, 'Highest Price']:
                          reader.at[index, 'Highest Price'] = current_val
                          reader['Highest Price'] = reader['Highest Price'].astype('float64')
                        
                    if reader.at[index, 'Lowest Price'] == 0.00 or current_val < reader.at[index, 'Lowest Price']:
                        reader.at[index, 'Lowest Price'] = current_val
                        reader['Lowest Price'] = reader['Lowest Price'].astype('float64')
            
            #run statistics only if we have 2 days collected
            if(len(reader.columns) > (len(ignore_list) + 1)):
                #Average $ of all days
                formatted_num = format(sum_of_prices/(len(reader.columns) - len(ignore_list)), '.2f')
                reader.at[index, 'Average'] = float(formatted_num)
                reader['Average'] = reader['Average'].astype('float64')
                
              
                #Daily $ change of last 2 days
                today_column = reader.columns[len(reader.columns) - 1]
                yesterday_column = reader.columns[len(reader.columns) - 2]
                formatted_num = format(float((row[today_column])) - float((row[yesterday_column])), '.2f')
                reader.at[index, 'Daily Change'] = float(formatted_num)
                reader['Daily Change'] = reader['Daily Change'].astype('float64')
                
            
            #Weekly $ change of last 7 days
            if(len(reader.columns) > (len(ignore_list) + 6)):
                today_column = reader.columns[len(reader.columns) - 1]
                last_weekday_column = reader.columns[len(reader.columns) - 7]
                formatted_num = format(float((row[today_column])) - float((row[last_weekday_column])), '.2f')
                reader.at[index, 'Weekly Change'] = float(formatted_num)
                reader['Weekly Change'] = reader['Weekly Change'].astype('float64')

                                
    #check for new cards or removed cards ON SAME DAY
    elif new_card_flag == True or cards_removed_flag == True :
        if new_card_flag == True:
            for card in card_name_list:
                if card not in reader.values:
                    reader = reader.append({'Card name': card, column_name: price_list[card_name_list.index(card)]}, ignore_index=True)
                    print(reader.tail(2))
                    
        if cards_removed_flag == True:
              print("Card was removed")
              popup_msg("MTGBot", "Card was removed", 5)
            
                
    #Don't rerun the same day (unless we have new cards to add)
    #Note: Older day columns will be filled with NaN or empty spaces       
    else:
        print("Today is done")
        popup_msg("MTGBot", "MTGBot has already run today", 5)
        sys.exit()
    
    
        
    
    #delete file so we can resave cleanly
    #otherwise formatting is really annoying
    try:
        os.remove(my_list_file_path)
    except:
        print("Please close the file")
        popup_msg("MTGBot Error: Exiting", "Please close the excel sheet and rerun", 5)
        sys.exit()
        
    
    #add total row
    reader.at['Total', 'Average'] = reader['Average'].sum()
    #write to file
    reader.to_excel(my_list_file_path, sheet_name='Main Sheet', index = False)
    
    
#############################Large Price Lists Code############################


    
get_set_list_with_settings()
u,p,r,s = get_email_settings()
time.sleep(5)
send_email(u, p, r, s, "./excels/single_card_list_report.xlsx")
check_price_thresholds(card_name_list, price_list, sign_list, threshold_list)
popup_msg("MTGBot", "Your Daily Report is in!", 5)