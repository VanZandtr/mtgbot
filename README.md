# Magic: The Gathering Trending Card Bot (M:TGBot)
## TLDWTR (Too Long Don't Want To Read)
* Step 1: Download Python
* Step 2: Download or fork code
* Step 3: Edit my_list with your single cards and price thresholds (see section #)
* Step 4: Edit price_lists with your format
* Step 5: Edit your price_lists thresholds in settings.txt (optional)(see section #)
* Step 6: Automate your code (optional)(see section #)
* Step 7: Setup email in email_settings.py (optional)
* Step 8: Enjoy!

## Purpose and Goals:
   
Automate a card popularity script that tracks and alerts the user to different price trends based on publicly available price lists and cards, with the goal being that the user will better predict increases/decreases in cards to help the purchasing process.

* Goal 1: Make tracking as streamline, easy to understand, and hands off as possible. Anybody, regardless of coding history, should be able to setup this script fully automated in 5-10 mins (you shouldn't have to ever look at code!)
* Goal 2: Provide a free to use  all-in-one service that magic players or investors can use to realiably, efficiently, and sensibly track their current collection or potential purchases

Please feel free to dm if you feel I can improve upon either of these goals.

## Intro & Features:
I had initially started this code twoish years ago and have since added a ton of features! If you are interested in taking a look at the old code you check out the original code here:  https://github.com/VanZandtr/mtgbot/commit/15a8802cf50556eb99fc6bcae25cdb2f7ca8ef9b and the original reddit post here: https://www.reddit.com/r/mtgfinance/comments/avhbpa/i_created_a_trending_bot/

This Bot can:
* Track individual cards of any type (extended, foil, promo, etc.) given an MTGGoldfish link
* Display pop-up messages when an individual cards has reached a certain threshold
* Track MTGGoldfish set/format price list
* Track certain set/format list cards based on 6 factors given by MTGGoldfish: Rarity, price, daily price change, daily percent change, weekly price change, weekly percent change
* Write individual and list cards to seperate excel files
* Be easily automated into a one touch and down for easy card tracking
* Email you your price lists
* Display pop-up error message to easily trouble shoot your issues
(pic)

## Single Card Setup:
   * Step 1: Obtain links to the cards you want to track (e.g. https://www.mtggoldfish.com/price/Limited+Edition+Alpha/Black+Lotus#paper)  
   * Step 2: Paste list into my_list.txt making sure each card is on a new line  
   (Pic)  
   * Step 3: Add threshold values to the end of each card (valid operators: <, >, <=, >=, = or ==)(optional)  
   (Pic)  
   * Step 4: Run code and find my_list_report excel in /excels  
   (Pic single day)  
   (Pic multi day)  
   * Note 1: if a price reaches a threshold a pop-up message will be displayed  
   (Pic)  
   
## Price List Setup:
   * Step 1: Obtain links to the list you want to track (e.g. https://www.mtggoldfish.com/index/modern#paper)  
   * Step 2: Paste list into price_lists.txt making sure each list is on a new line  
   (Pic)  
   * Step 3: Add threshold values to the setting.txt file (valid operators: <, >, <=, >=, = or ==)(optional)  
   (Pic)  
   * Step 4: Run code and find excel in /excels  
   * Note 1: If a card does not adhere to the settings you provide it will not show up in the excel file  
   (Pic)   

 ## Automation Setup (Windows):
   Refer to link on how to automate a .py file with Task Scheduler:  
   https://www.youtube.com/watch?v=n2Cr_YRQk7o
   (Add pics)
 
 ## Email Setup:
   (Pending)
   
 ## Files:
 * mtgbot.py: main file with all the code
 * my_list.txt: text file to hold single cards and threshold operators and price values
 * price_lists.txt: text file to hold multicard lists
 * settings.txt: text file that holds threshold operators and price/percent values for multicard lists
 * /excel folder: folder where all the excel files are put from mtgbot.py
 * /pictures: pictures for this Readme (you can delete this lol)
 
 ## Final Product:
   (Pending)
  
## Future Changes:

## Preemptive FAQs:
Q1: What mtggoldfish price does the bot use?
A1:

Q2: Can I run both single cards and multicard lists at the same time?
A2: Yep!
(pic)

Q3: I see I can only run the single card list once, why?
Q4:
## About the Author:
