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


########################## Global Vars ########################################
price_lists_names = []
today = str(date.today())
my_list_file_path = '.\\excels\\my_list_report.xlsx'

####################### Methods ###############################################

#read in settings
def get_settings():
    print("needs implementing")

#create general popup message
def popup_msg(header, msg, d):
    toaster = ToastNotifier()
    toaster.show_toast(header, msg, duration = d)

#Generate a Dataframe of a card list from an MTGGoldfish web scrap
def full_list_request(page,WebUrl):
    
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
        trim = raw_list[front_index + 2:rear_index - 8]
        

        card_map = list(chunks(trim, 8))
        
        #Search and create output format
        card_list = [];
        for row in card_map:
            card_data = []
            if float(row[4][:-1]) >= .50 or float(row[6][:-1]) < 0: #Checking if Daily change >= 50 cents or if Weekly change is negative (Down Trend)
                for i in range(0, len(row)):
                    card_data.append(row[i])
                card_list.append(card_data)
        
        df = pd.DataFrame(card_list,columns=['Card Name', 'Set Name', 'Rarity', 'Current Price', 'Daily Price Change',
                                             'Daily Percent Change', 'Weekly Price Change', 'Weekly Percent Change'])
        return df

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
            
            if x == "eBay = Buy It Now":
                found_seller_flag = True
                
                index = string_list.index(x)
                
                tcg_player_mid.append(string_list[index])
                tcg_player_mid.append(string_list[index + 1])
                tcg_player_mid.append(string_list[index + 2])
                tcg_player_mid.append(string_list[index + 3])
                tcg_player_mid.append(string_list[index + 4])
                break
            
        if found_seller_flag == False:
            return_msg.append("Could not find Seller")
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

#Generate and send an email
def send_email(user, pwd, recipient, subject, body, tags):
    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    
    MESSAGE = ''
    counter = 0;
    for cardList in body:
        MESSAGE += tags[counter] + ': \n'
        MESSAGE += '---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- \n'
        MESSAGE += '\n'.join(cardList)
        MESSAGE+= '\n\n'
        counter +=1
        

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, MESSAGE)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print ('successfully sent the mail')
    except:
        print ("failed to send mail")
        

    
############################# Single Card List Code ###########################

print("Looking for my_list.txt file...")

column_name = 'Price ' + str(today)
my_list = []
price_lists = []
card_name_list = []
price_list = []

#check if my_list exists
if path.isfile('my_list.txt'):
    print("Found my_list.txt")
    print()
    
    #check if my_list is empty
    if os.stat('my_list.txt').st_size == 0:
        print("my_list.txt is empty")
        
    
    text_file = open("my_list.txt", "r")
    my_list = text_file.readlines()

#check for bad urls, skip, and give a popup message
for url in my_list:
    ret = single_card_request(1,url)
    
    if 'Bad url' in ret:
        bad_url_index = my_list.index(url)
        popup_msg("MTGBot Error", "Bad Url at: " + str(bad_url_index), 5)
        
    else:
        card_name_list.append(ret[0])
        price_list.append(ret[1])


#create an excel file if not already made
if path.isfile(my_list_file_path) == False and len(my_list) != 0:
    df = pd.DataFrame()
    df['Card name'] = card_name_list
    df['Average'] = 0.00
    df['Daily Change'] = 0.00
    df[column_name] = price_list
    
    df.to_excel (my_list_file_path, index = False)
    
    
#Change/append to existing file if found  
elif path.isfile(my_list_file_path) == True and len(my_list) != 0:
    df = pd.DataFrame()
    df['Card name'] = card_name_list
    df['Average'] = 0.00
    df[column_name] = price_list
    df['Daily Change'] = 0.00
    ignore_list = ['Card name', 'Average', 'Daily Change']
    # read existing file
    reader = pd.read_excel(my_list_file_path)
            
    #new card precheck ==> allows for new cards to be added and program to be rerun on the same day(/column)
    new_card_flag = False
    for card in card_name_list:
        if card not in reader.values:
            new_card_flag = True
            break
    
                
    #check if column exists
    if (column_name) not in reader.columns:
        #create new column
        reader[column_name] = 'NaN'
        for index1, row1 in df.iterrows():
            for index2, row2 in reader.iterrows():
                if row1['Card name'] == row2['Card name']:
                    reader.at[index2, column_name] = float(row1[column_name])
                    
        #run statistics
        for index, row in reader.iterrows():
            sum_of_prices = 0
            for col in reader.columns:
                if col not in ignore_list:
                    sum_of_prices += float(row[col])
            
            #run statistics only if we have 2 days collected
            if(len(reader.columns) > (len(ignore_list) + 1)):
                #Average $ of all days
                formatted_num = format(sum_of_prices/(len(reader.columns) - 2), '.2f')
                reader.at[index, 'Average'] = float(formatted_num)
                
                #Daily $ change of last 2 days
                today_column = reader.columns[len(reader.columns) - 1]
                yesterday_column = reader.columns[len(reader.columns) - 2]
                formatted_num = format((row[today_column]) - (row[yesterday_column]), '.2f')
                reader.at[index, 'Daily Change'] = float(formatted_num)
            
        
        
                        
    #check for new cards
    elif new_card_flag == True:
        for card in card_name_list:
            if card not in reader.values:
                reader = reader.append({'Card name': card, column_name: price_list[card_name_list.index(card)]}, ignore_index=True)
                
    #Don't rerun the same day (unless we have new cards to add)
    #Note: Older day columns will be filled with NaN or empty spaces       
    else:
        print("Today is done")
        popup_msg("MTGBot", "MTGBot has already run today", 5)
        sys.exit()
    
    #check if cards were removed from list and delete them from the excel
    reader = reader.dropna()
        
    
    #delete file so we can resave cleanly
    #otherwise formatting is really annoying
    try:
        os.remove(my_list_file_path)
    except:
        print("Please close the file")
        popup_msg("MTGBot Error: Exiting", "Please close the excel sheet and rerun", 5)
        sys.exit()
        
    
    #write to file
    reader.to_excel(my_list_file_path, sheet_name='Main Sheet', index = False)
    
    
#############################Large Price Lists Code############################

#check if price lists are given
if path.isfile('price_lists.txt'):
    print("Found price_lists.txt")
    print()
    
    #check if price lists is empty
    if os.stat('price_lists.txt').st_size == 0:
        print("price_lists.txt is empty")
    
    text_file = open("price_lists.txt", "r")
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
    


# user = 'youremail@gmail.com'
# app_pass = 'your_google_apps_password'
# recp = 'where_to_send@gmail.com'
# sub = 'MTGBot: Trending Magic Cards'
# msg = [modern_list, expedition_list]
# names = ['Modern', 'Expedition Lands']
#send_email(user, app_pass, recp, sub, msg, names)

popup_msg("MTGBot", "Your Daily Report is in!", 5)