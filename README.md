# mtgbot
Magic: The Gathering Trending Card Bot

## Purpose:
   
   Automate a card popularity script that notices and alerts the user to different price trends based on publicly available price lists, with the goal being that the user will better predict increases/decreases in cards to help the purchasing process.
   
## How it Works:

   mtgbot.py will parse any MTGGoldfish List 
   (provided that list contains the form https://www.mtggoldfish.com/index/EXP#paper where EXP is a three letter expansion abbreviation or other acceptable list (modern) followed by the ONLINE/PAPER)

## Setup/Use:

  1.) Once you have obtained the cardlist (via restrictions above), paste the url into web method & set vars (my_list = web(1, "url"))  
  2.) add the vars to "msg" ----> used to add multiple list to a single email  
  3.) add names of each list in the same order as step 2 to "names"  
  4.) login into gmail and set recipient email  
  
      user: your_gmail@gmail.com
      app_pass: your_app_password ----> must be using 2 step-verification and add a password via "generate App password (https://support.google.com/accounts/answer/185833?hl=en)
      recp: where_to_send@gmail.com
      
  5.) run via "python mtgbot.py " or with preferred IDE  
  
 ## Automate:
 
    Linux:  env EDITOR=nano crontab -e 0 12 * * *  /full/path/to/python /full/path/to/script.py #runs everyday at 12
    
    Windows: schtasks.exe /create /TN $taskName /ST $time /SC DAILY /SD $startDate /ED $endDate /TR "powershell.exe -file C:\users\myprofile\desktop\scriptname.ps1 -mode $serviceChoice -list $listChoice"
    
 ## Final Product:
 
![mtgbot Email](https://github.com/VanZandtr/mtgbot/blob/master/mtgbot_pic.PNG)

 ## Additional Options:

  Note: The current script is parsing the Modern List as well as Zendikar Expeditions as an example.
   
  In the web method you can change the index of "row" to obtain different elements of the list.
  
  Row[x]
  0: Card Name  
  1: Set Name  
  2: Rarity  
  3: Price  
  4: Daily Price Change (+/-)  
  5: Daily Percent Change (+/-)  
  6: Weekly Price Change (+/-)  
  7: Weekly Percent Change (+/-)  
  
  I currently have it set so that it will return any Daily Price Change > $.50 OR Weekly Price Change < 0.
  Thus, I want to know if a card is starting to take attention or if a high priced card is declining

## Future Changes:

   * Indentation Fixes
   * Colors and Text Accents (Bold, Italics, etc)
   * Hold and Compare prices over a certain time period (>week)
