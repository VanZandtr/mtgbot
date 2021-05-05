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

price_lists_names = []
run_list = True
today = str(date.today()) + " " +  str(random.randint(0,100))
my_list_file_name = 'my_list_report.xlsx'

#create general popup message
def popup_msg(header, msg, d):
    toaster = ToastNotifier()
    toaster.show_toast(header, msg, duration = d)

def full_list_request(page,WebUrl):
    
    if(page>0):
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = WebUrl
        code = requests.get(url, headers=headers)
        plain = code.text
        s = BeautifulSoup(plain, "html.parser")
        text = (s.text)
        combinedText = text.splitlines()
        
        
        raw_list = [x for x in combinedText if x != '']#removes random empty spaces in list
        
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
        
        #finds longest card name ----> help tab spacing slightly by offseting by longest card name
        largest_card = 0;
        for row in card_map:
            if float(row[4][:-1]) >= .50 or float(row[6][:-1]) < 0: #Checking if Daily change >= 50 cents or if Weekly change is negative (Down Trend)
                if len(row[0]) > largest_card:
                    largest_card = len(row[0])
                    print (largest_card)
                    print(row[0])
        
        #Search and create output format
        card_list = [];
        for row in card_map:
            card_data = []
            if float(row[4][:-1]) >= .50 or float(row[6][:-1]) < 0: #Checking if Daily change >= 50 cents or if Weekly change is negative (Down Trend)
                for i in range(0, len(row)):
                    card_data.append(row[i])
                card_list.append(card_data)
        
        df = pd.DataFrame(card_list,columns=['Card Name', 'Test1', 'Test2', 'Test3', 'Test4', 'Test5', 'Test6', 'Test6'])
        return df

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
        
        for x in string_list:
            #print(x)
            
            if x == "TCGplayer Market Price":
                
                
                index = string_list.index(x)
                
                tcg_player_market.append(string_list[index])
                tcg_player_market.append(string_list[index + 1])
                tcg_player_market.append(string_list[index + 2])
                tcg_player_market.append(string_list[index + 3])
                tcg_player_market.append(string_list[index + 4])
                break
            
            if x == "TCGplayer Mid":
                index = string_list.index(x)
                
                tcg_player_mid.append(string_list[index])
                tcg_player_mid.append(string_list[index + 1])
                tcg_player_mid.append(string_list[index + 2])
                tcg_player_mid.append(string_list[index + 3])
                tcg_player_mid.append(string_list[index + 4])
                break
        
        
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
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

#email sender
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
        

    
###############################################################################  

print("Looking for my_list.txt file...")

column_name = 'Price ' + str(today)
my_list = []
price_lists = []
card_name_list = []
price_list = []


if path.isfile('my_list.txt'):
    print("Found my_list.txt")
    print()
    
    if os.stat('my_list.txt').st_size == 0:
        print("my_list.txt is empty")
    
    text_file = open("my_list.txt", "r")
    my_list = text_file.readlines()


for url in my_list:
    ret = single_card_request(1,url)
    
    if 'Bad url' in ret:
        bad_url_index = my_list.index(url)
        popup_msg("MTGBot Error", "Bad Url at: " + str(bad_url_index), 5)
        
    else:
        card_name_list.append(ret[0])
        price_list.append(ret[1])

if path.isfile(my_list_file_name) == False and len(my_list) != 0:
    dict = {'Card name': card_name_list, 'Price ' + str(today): price_list}
    
    df = pd.DataFrame(dict)
    
    df.to_excel (my_list_file_name, index = False)
    
    
    
elif path.isfile(my_list_file_name) == True and len(my_list) != 0:
    
    df = pd.DataFrame({'Card name': card_name_list, column_name: price_list})
    
    writer = pd.ExcelWriter(my_list_file_name, engine='openpyxl')
    
    # try to open an existing workbook
    writer.book = load_workbook(my_list_file_name)
    
    # copy existing sheets
    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
    
    # read existing file
    reader = pd.read_excel(my_list_file_name)
            
    #new card precheck ==> allows for new cards to be added and program to be rerun on the same day(/column)
    new_card_flag = False
    for card in card_name_list:
        print(card)
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
                    reader.at[index2, column_name] = row1[column_name]
                        
        #check for new cards
    elif new_card_flag == True:
        for card in card_name_list:
            if card not in reader.values:
                reader = reader.append({'Card name': card, column_name: price_list[card_name_list.index(card)]}, ignore_index=True)
                
    else:
        print("Today is done")
        sys.exit()
    
    #delete file
    try:
        writer.close()
    except:
        print("Please close the file")
        popup_msg("MTGBot Error: Exiting", "Please close the excel sheet and rerun", 5)
        sys.exit()
    
    os.remove(my_list_file_name)
    
    #write to file
    writer = pd.ExcelWriter(my_list_file_name, engine='xlsxwriter')
    reader.to_excel(writer, sheet_name='Main Sheet', index = False)
    
    writer.save()
    
    

        
    
    
##############################################################################

if path.isfile('price_lists.txt'):
    print("Found price_lists.txt")
    print()
    
    if os.stat('price_lists.txt').st_size == 0:
        print("price_lists.txt is empty")
    
    text_file = open("price_lists.txt", "r")
    price_lists = text_file.readlines()

name_index = 0
for url in price_lists:
    ret_msg = full_list_request(1,url)
    
    characters_to_remove = "*./\[]:;|,"
    fn = (str(price_lists_names[name_index]) + today)
    for c in characters_to_remove:
        fn = fn.replace(c, "")
    fn = fn.strip(' \n\t')
    
    fn = fn + ".xlsx"
    
    ret_msg.to_excel (fn, index = False)
    name_index += 1
    


# user = 'youremail@gmail.com'
# app_pass = 'your_google_apps_password'
# recp = 'where_to_send@gmail.com'
# sub = 'MTGBot: Trending Magic Cards'
# msg = [modern_list, expedition_list]
# names = ['Modern', 'Expedition Lands']
#send_email(user, app_pass, recp, sub, msg, names)

#popup_msg()



#Refer to line 60 and 69 ;) for changes to your trends
