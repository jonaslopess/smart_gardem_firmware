#!/bin/sh
#launcher.sh

cd /
cd home/pi/Desktop/horta
git pull
cd home/pi/Desktop/horta/firmware
pip install -r requirements.txt
sudo python3 main.py &
cd /

