# mtgbot
Magic: The Gathering Trending Card Bot

Purpose:

mtgbot.py will parse any MTGGoldfish List (provided that list contains the form https://www.mtggoldfish.com/index/EXP#paper where EXP is a three letter expansion abbreviation followed by the ONLINE/PAPER)

Setup/Use:
  1.) Once you have obtained the cardlist (via restrictions above), paste the url into web method (line --- & ---) & rename vars
  2.) add the vars to msg ----> used to add multiple list to a single email
  3.) add names of each list in the same order as step 2
  4.) login into gmail and set recipient email
  
      user: your gmail login name
      app_pass: your app password ----> must be using 2 step-verification and add a password via "generate App password (https://support.google.com/accounts/answer/185833?hl=en)
      recp: where the email will go
      
  5.) run via "python mtgbot.py "
  
 Automate:
    
    Linux:  env EDITOR=nano crontab -e 0 12 * * *  /full/path/to/python /full/path/to/script.py #runs everyday at 12
    
    Windows: schtasks.exe /create /TN $taskName /ST $time /SC DAILY /SD $startDate /ED $endDate /TR "powershell.exe -file C:\users\myprofile\desktop\scriptname.ps1 -mode $serviceChoice -list $listChoice"

  

   
