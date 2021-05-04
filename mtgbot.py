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
        
        front_index = -1
        rear_index = -1
        
        #finding cards from raw html text
        for i, j in enumerate(raw_list):
            if j == 'Weekly' and front_index == -1:
                front_index = i
            elif j == 'Weekly' and front_index != -1:
                rear_index = i
                break;
        
        if front_index == -1 or rear_index == -1:
            print("error in parsing text")
        
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
            if float(row[4][:-1]) >= .50 or float(row[6][:-1]) < 0: #Checking if Daily change >= 50 cents or if Weekly change is negative (Down Trend)
                if len(row[0]) != largest_card: 
                    card_list.append((row[0] + '  ' + '\t' + 'Current Price: ' + 
                                      row[3] + '  ' + '\t' + 'Daily Price Trend: ' + 
                                      row[4] + '  ' + '\t' + 'Weekly Price Trend: ' + 
                                      row[6]).expandtabs(60 + largest_card - len(row[0])))
                else:
                    card_list.append((row[0] + '  ' + '\t' + 'Current Price: ' + 
                                      row[3] + '  ' + '\t' + 'Daily Price Trend: ' + 
                                      row[4] + '  ' + '\t' + 'Weekly Price Trend: ' + 
                                      row[6]).expandtabs(60))
        return card_list

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
        
#create general popup message
def popup_msg(header, msg, d):
    toaster = ToastNotifier()
    toaster.show_toast(header, msg, duration = d)
    
###############################################################################  


print("Note: Current single card build does not support Extended, Foreign Language, specific land numbers, or other specialty tag cards. Functionality coming soon.")
print()
print("Looking for my_list.txt file...")

run_list = True
today = date.today()
column_name = 'Price ' + str(today) + "1"

if path.isfile('my_list.txt') and run_list == True:
    print("Found list.")
    print()
    
    text_file = open("my_list.txt", "r")
    list1 = text_file.readlines()
    
    card_name_list = []
    price_list = []
    for url in list1:
        ret = single_card_request(1,url)
        
        if 'Bad url' in ret:
            bad_url_index = list1.index(url)
            popup_msg("MTGBot Error", "Bad Url at: " + str(bad_url_index), 5)
        else:
            card_name_list.append(ret[0])
            price_list.append(ret[1])
    
    
    #create excel file if it doesn't exist
    if path.isfile('demo.xlsx') == False:
        dict = {'Card name': card_name_list, 'Price ' + str(today): price_list}
        
        df = pd.DataFrame(dict)
        
        writer = pd.ExcelWriter('demo.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Test ' + str(today), index = False)
        writer.save()
        
    elif path.isfile('demo.xlsx') == True:
        
        df = pd.DataFrame({'Card name': card_name_list, column_name: price_list})
        
        writer = pd.ExcelWriter('demo.xlsx', engine='openpyxl')
        
        # try to open an existing workbook
        writer.book = load_workbook('demo.xlsx')
        
        # copy existing sheets
        writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
        
        # read existing file
        reader = pd.read_excel(r'demo.xlsx')
                
        #new card precheck ==> allows for new cards to be added and program to be rerun on the same day(/column)
        new_card_flag = False
        for card in card_name_list:
            if card not in reader.values:
                new_card_flag = True
                    
        #check if column exists
        if (column_name) not in reader.columns or new_card_flag == True:
            #create new column
            reader[column_name] = 'NaN'
            for index1, row1 in df.iterrows():
                for index2, row2 in reader.iterrows():
                    if row1['Card name'] == row2['Card name']:
                        reader.at[index2, column_name] = row1[column_name]
                            
            #check for new cards
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
        
        os.remove('demo.xlsx')
        
        #write to file
        writer = pd.ExcelWriter('demo.xlsx', engine='xlsxwriter')
        reader.to_excel(writer, sheet_name='Main Sheet', index = False)
        
        writer.save()
                
elif run_list == True:
    print("no input list found")
    
    
##############################################################################
    
#modern_list = full_list_request(1,'https://www.mtggoldfish.com/index/modern#paper')
#expedition_list = full_list_request(1,'https://www.mtggoldfish.com/index/EXP#paper')


# user = 'youremail@gmail.com'
# app_pass = 'your_google_apps_password'
# recp = 'where_to_send@gmail.com'
# sub = 'MTGBot: Trending Magic Cards'
# msg = [modern_list, expedition_list]
# names = ['Modern', 'Expedition Lands']
#send_email(user, app_pass, recp, sub, msg, names)

#popup_msg()



#Refer to line 60 and 69 ;) for changes to your trends
