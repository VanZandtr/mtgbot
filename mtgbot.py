# -*- coding: utf-8 -*-
#Owner: VanZandtr, Github: https://github.com/VanZandtr/mtgbot/

import requests
from bs4 import BeautifulSoup
import smtplib
from win10toast import ToastNotifier
import re

#web parser
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

def single_card_request(page,WebUrl, card_set=None, foil=False):
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

        temp_list = []
        
        for x in string_list:
            
            
            if x == "TCGplayer Market Price":
                
                index = string_list.index(x)
                
                temp_list.append(string_list[index])
                temp_list.append(string_list[index + 1])
                temp_list.append(string_list[index + 2])
                temp_list.append(string_list[index + 3])
                temp_list.append(string_list[index + 4])
                break
        

        card_name = string_list[0]
        
        print(card_name)
        result = re.findall('\d*\.?\d+', temp_list[2])
        price = result[0]
        print(price)
        print()
        
        
        
        
        
                    
        #logic for no set name given --> all set prices
             
        
# Create a function called "chunks" with two arguments, l and n used to group cards with their respective elements
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

def popup_msg():
    toaster = ToastNotifier()
    toaster.show_toast("Mtg Bot Notification", "test", duration = 10)
    
print("Note: Current single card build does not support Extended, Foreign Language, specific land numbers, or other specialty tag cards. Functionality coming soon.")
    
#modern_list = full_list_request(1,'https://www.mtggoldfish.com/index/modern#paper')
#expedition_list = full_list_request(1,'https://www.mtggoldfish.com/index/EXP#paper')

print()

test_url = "https://www.mtggoldfish.com/price/Strixhaven+Mystical+Archive:Foil/Demonic+Tutor-japanese#paper"
#non-foil good check
#nf_good_test = single_card_request(1,test_url, "stx")

#foil good check
f_good_test = single_card_request(1,test_url, "stx", True)

#card with foil, but ask for non-foil
#f_good_test = single_card_request(1,test_url, "stx")


# user = 'youremail@gmail.com'
# app_pass = 'your_google_apps_password'
# recp = 'where_to_send@gmail.com'
# sub = 'MTGBot: Trending Magic Cards'
# msg = [modern_list, expedition_list]
# names = ['Modern', 'Expedition Lands']
#send_email(user, app_pass, recp, sub, msg, names)

popup_msg()

#Refer to line 60 and 69 ;) for changes to your trends ----> these should be the identical
