# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import smtplib

def web(page,WebUrl):
    if(page>0):
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = WebUrl
        code = requests.get(url, headers=headers)
        plain = code.text
        s = BeautifulSoup(plain, "html.parser")
        text = (s.text)
        combinedText = text.splitlines()
        
        
        raw_list = [x for x in combinedText if x != '']
        
        
        #print(raw_list)
        front_index = -1
        rear_index = -1
                
        for i, j in enumerate(raw_list):
            if j == 'Weekly' and front_index == -1:
                front_index = i
            elif j == 'Weekly' and front_index != -1:
                rear_index = i
                break;
        
        if front_index == -1 or rear_index == -1:
            print("error in parsing text")
        
        print(front_index)
        print(raw_list[front_index])
                
        print(rear_index)
        print(raw_list[rear_index])
        
        #trim up to card start and end
        #389
        trim = raw_list[front_index + 2:rear_index - 8]

        card_map = list(chunks(trim, 8))
        
        largest_card = 0;
        for row in card_map:
            if float(row[4][:-1]) >= .50 or float(row[6][:-1]) < 0:
                if len(row[0]) > largest_card:
                    largest_card = len(row[0])
                    print (largest_card)
                    print(row[0])
        
        #print(*card_map, sep = "\n") 
        card_list = [];
        for row in card_map:
            if float(row[4][:-1]) >= .50 or float(row[6][:-1]) < 0:
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
             
        
# Create a function called "chunks" with two arguments, l and n:
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

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
            
        
modern_list = web(1,'https://www.mtggoldfish.com/index/modern#paper')
expedition_list = web(1,'https://www.mtggoldfish.com/index/EXP#paper')
user = 'youremail@gmail.com'
app_pass = 'your_google_apps_password'
recp = 'where_to_send@gmail.com'
sub = 'MTGBot: Daily Trending Magic Cards'
msg = [modern_list, expedition_list]
names = ['Modern', 'Expedition Lands']

send_email(user, app_pass, recp, sub, msg, names)
