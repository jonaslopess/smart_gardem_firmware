#!/bin/sh
#launcher.sh
sleep 60

cd /home/pi/Desktop/horta
git pull
cd /home/pi/Desktop/horta/firmware
pip3 install -r requirements.txt
sudo python3 main.py &
cd /

