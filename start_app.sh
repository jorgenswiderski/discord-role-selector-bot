#!/bin/sh -x
cd /home/ec2-user/discord-role-selector-bot

# check if a screen session "discord-role-selector-bot" exists
if screen -list | grep -q ".discord-role-selector-bot"; then
	# kill the existing screen session
	screen -S discord-role-selector-bot -X quit
fi

# start the Python application in a new screen session, using the virtual environment
screen -dmS discord-role-selector-bot bash -c 'source env/bin/activate && python3.9 -O main.py'

# sleep for a few seconds to give the application a chance to start
sleep 5

# check if the screen session is still running
if ! screen -list | grep -q ".discord-role-selector-bot"; then
	echo "Python application failed to start"
	exit 1
fi
