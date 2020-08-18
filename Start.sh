#!/bin/sh

TIMEOUT="5s"

while : ; do
    python bot.py 
    echo "Restarting in $TIMEOUT"
    sleep $TIMEOUT
done