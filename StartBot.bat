:: In order to run the bot, you would need to configure the secretTextfile.py and put your BOT_TOKEN, Discord owner id, and other settings
:: Running this batch script assumes that you have python, pip, and the pipenv python package installed.
:: This script would install the required dependencies listed in the Pipfile (if they're not installed already)
:: and then it will keep the bot running infinitely, no matter what, 
:: unless the process exists normally (user invokes =Die to kill bot) 
:: or the user sends a SIGINT to the process (twice, one for bot.py script, and one to exit the pipenv (virtual environment))

pipenv install

:loop
start /wait pipenv run python bot.py
if %errorlevel%==0 goto normalExit
goto loop2

:loop2 
timeout /t 5
goto loop
PAUSE

:normalExit
echo "Program exited normally, now exiting normally."
exit