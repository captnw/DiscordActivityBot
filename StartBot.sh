# In order to run the bot, you would need to configure the secretTextfile.py and put your BOT_TOKEN, Discord owner id, and other settings
# Running this shell script assumes that you have python, pip, and the pipenv python package installed.
# This script would install the required dependencies listed in the Pipfile (if they're not installed already)
# unless the process exists normally (user invokes =Die to kill bot) 
# or the user sends a SIGINT to the process (twice, one for bot.py script, and one to exit the pipenv (virtual environment))

TIMEOUT="5s"
ZERO=0

pipenv install

while : ; do
    pipenv run python bot.py 
    if [ $? -eq 0 ]
    then
        echo "Program exited normally, now exiting normally."
        exit 0
    fi
    echo "Restarting in $TIMEOUT"
    sleep $TIMEOUT
done